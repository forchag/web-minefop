#!/usr/bin/env bash
#
# Update a MINEFOP deployment from GitHub.
#
# Pulls the latest code, installs dependencies, applies database migrations,
# compiles the translation catalogue and gathers the static files, then reloads
# the web service. Safe to run repeatedly: every step is idempotent, and the
# script stops at the first failure rather than leaving the site half-updated.
#
#   ./scripts/update.sh                  # update the current branch
#   ./scripts/update.sh --branch main    # switch to and update main
#   ./scripts/update.sh --no-pull        # rebuild without fetching new code
#   ./scripts/update.sh --seed           # also run seed_data (first install)
#   ./scripts/update.sh --check          # report what would change, do nothing
#
# See --help for the full list of options.

set -Eeuo pipefail

# ---------------------------------------------------------------- defaults --
BRANCH=""
DO_PULL=1
DO_DEPS=1
DO_VENDOR=0
DO_SEED=0
DO_TESTS=1
DRY_RUN=0
# Set MINEFOP_SERVICE (e.g. "minefop.service" or "minefop-gunicorn") to have the
# script reload the application server once everything else has succeeded.
SERVICE="${MINEFOP_SERVICE:-}"

REPO_ROOT="$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")/.." && pwd)"
PYTHON="${PYTHON:-python3}"

# ------------------------------------------------------------------ output --
if [[ -t 1 ]]; then
  BOLD=$'\033[1m'; GREEN=$'\033[32m'; YELLOW=$'\033[33m'; RED=$'\033[31m'; RESET=$'\033[0m'
else
  BOLD=""; GREEN=""; YELLOW=""; RED=""; RESET=""
fi

step()  { printf '\n%s==> %s%s\n' "$BOLD" "$1" "$RESET"; }
info()  { printf '    %s\n' "$1"; }
warn()  { printf '%s    ! %s%s\n' "$YELLOW" "$1" "$RESET"; }
ok()    { printf '%s    ✓ %s%s\n' "$GREEN" "$1" "$RESET"; }
die()   { printf '\n%serror: %s%s\n' "$RED" "$1" "$RESET" >&2; exit 1; }
# Confirmation of something that happened — stays quiet during a dry run.
did()   { (( DRY_RUN )) || ok "$1"; }

on_error() {
  local line=$1
  printf '\n%sThe update failed at line %s and stopped there.%s\n' "$RED" "$line" "$RESET" >&2
  printf 'The site is still serving the previous version. Fix the problem above,\n' >&2
  printf 'then run this script again — it will pick up where it left off.\n' >&2
}
trap 'on_error $LINENO' ERR

usage() {
  sed -n '3,17p' "${BASH_SOURCE[0]}" | sed 's/^# \{0,1\}//'
  cat <<'EOF'

Options:
  --branch NAME    Check out and update NAME instead of the current branch.
  --no-pull        Skip the fetch/merge; rebuild from the working copy as it is.
  --no-deps        Skip "pip install -r requirements.txt".
  --no-tests       Skip the test suite (it runs before anything is published).
  --vendor         Also refresh static/vendor/ via npm (needs Node installed).
  --seed           Run "manage.py seed_data" after migrating. First install only:
                   it never overwrites content that already exists.
  --check, -n      Dry run — print each command instead of running it.
  --help, -h       Show this message.

Environment:
  MINEFOP_SERVICE  systemd unit to reload at the end, e.g. "minefop.service".
  MINEFOP_VENV     Path to a virtualenv kept outside the checkout. Otherwise the
                   script uses one already active in your shell, then looks for
                   venv/, .venv/ or env/ inside the repository.
  PYTHON           Python interpreter to use when no virtualenv is found.
EOF
}

# ------------------------------------------------------------------- flags --
while [[ $# -gt 0 ]]; do
  case "$1" in
    --branch)     BRANCH="${2:-}"; [[ -n "$BRANCH" ]] || die "--branch needs a branch name"; shift 2 ;;
    --no-pull)    DO_PULL=0; shift ;;
    --no-deps)    DO_DEPS=0; shift ;;
    --no-tests)   DO_TESTS=0; shift ;;
    --vendor)     DO_VENDOR=1; shift ;;
    --seed)       DO_SEED=1; shift ;;
    --check|-n)   DRY_RUN=1; shift ;;
    --help|-h)    usage; exit 0 ;;
    *)            die "unknown option: $1 (try --help)" ;;
  esac
done

# Run everything through this so --check can print instead of execute.
run() {
  if (( DRY_RUN )); then
    printf '    would run: %s\n' "$*"
  else
    "$@"
  fi
}

cd "$REPO_ROOT"

# ------------------------------------------------------- python environment --
step "Python environment"

# Three ways to find the virtualenv, in order of authority:
#   1. MINEFOP_VENV, for an environment kept outside the checkout;
#   2. VIRTUAL_ENV, when one is already active in the calling shell;
#   3. the usual directory names inside the repository.
VENV=""
VENV_SOURCE=""

if [[ -n "${MINEFOP_VENV:-}" ]]; then
  [[ -x "$MINEFOP_VENV/bin/python" ]] || die "MINEFOP_VENV=$MINEFOP_VENV has no bin/python"
  VENV="$MINEFOP_VENV"
  VENV_SOURCE="MINEFOP_VENV"
elif [[ -n "${VIRTUAL_ENV:-}" && -x "${VIRTUAL_ENV}/bin/python" ]]; then
  VENV="$VIRTUAL_ENV"
  VENV_SOURCE="already active"
else
  for candidate in venv .venv env; do
    if [[ -x "$REPO_ROOT/$candidate/bin/python" ]]; then
      VENV="$REPO_ROOT/$candidate"
      VENV_SOURCE="found in the repository"
      break
    fi
  done
fi

if [[ -n "$VENV" ]]; then
  # Activating puts the venv's python and pip first on PATH for the whole run,
  # which matters when this script runs from cron or a deploy hook with no
  # shell profile behind it.
  # shellcheck disable=SC1091
  source "$VENV/bin/activate"
  PY="$VENV/bin/python"
  ok "virtualenv $VENV ($VENV_SOURCE) — $("$PY" -V 2>&1)"
else
  command -v "$PYTHON" >/dev/null 2>&1 || die "$PYTHON not found — install Python or set PYTHON="
  PY="$PYTHON"
  warn "no virtualenv found — using the system $($PY -V 2>&1)"
  warn "looked at: MINEFOP_VENV, an active VIRTUAL_ENV, then venv/ .venv/ env/ in $REPO_ROOT"
  warn "create one with: $PYTHON -m venv venv && ./venv/bin/pip install -r requirements.txt"
fi

if [[ ! -f "$REPO_ROOT/.env" ]]; then
  warn "no .env file next to manage.py — Django falls back to DEBUG=True and its"
  warn "insecure development SECRET_KEY. On a public server that leaks settings and"
  warn "tracebacks to visitors: create a .env before serving this to the public."
fi

# --------------------------------------------------------------- pull code --
if (( DO_PULL )); then
  step "Pulling from GitHub"
  command -v git >/dev/null 2>&1 || die "git not found"
  git rev-parse --git-dir >/dev/null 2>&1 || die "$REPO_ROOT is not a git repository"

  if [[ -n "$(git status --porcelain --untracked-files=no)" ]]; then
    git status --short --untracked-files=no
    die "the working tree has uncommitted changes — commit, stash or discard them first"
  fi

  target="${BRANCH:-$(git rev-parse --abbrev-ref HEAD)}"
  [[ "$target" != "HEAD" ]] || die "the repository is in a detached HEAD state — pass --branch NAME"

  run git fetch --prune origin
  if [[ -n "$BRANCH" ]]; then
    run git checkout "$BRANCH"
  fi

  before="$(git rev-parse HEAD)"
  # --ff-only: refuse to create a merge commit on a server checkout. If this
  # fails, the local branch has diverged and needs a human decision.
  run git merge --ff-only "origin/$target"
  after="$(git rev-parse HEAD)"

  if (( ! DRY_RUN )); then
    if [[ "$before" == "$after" ]]; then
      ok "already up to date ($target at ${after:0:8})"
    else
      ok "updated $target: ${before:0:8} → ${after:0:8}"
      git --no-pager log --oneline "$before..$after" | sed 's/^/      /'
    fi
  fi
else
  info "skipping the pull (--no-pull)"
fi

# ------------------------------------------------------------ dependencies --
if (( DO_DEPS )); then
  step "Python dependencies"
  # Deliberately no "pip install --upgrade pip": on a distribution-managed
  # Python that fails, and it is not this project's job to move pip anyway.
  run $PY -m pip install --quiet -r requirements.txt
  did "requirements.txt satisfied"
else
  info "skipping dependencies (--no-deps)"
fi

if (( DO_VENDOR )); then
  step "Front-end libraries"
  if command -v npm >/dev/null 2>&1; then
    run npm install --silent
    run npm run vendor
    did "static/vendor/ refreshed"
  else
    warn "npm not found — leaving static/vendor/ as committed"
  fi
fi

# ------------------------------------------------------------------- tests --
# Run before touching the database or the served files: a failure here means the
# checkout is broken, and the previous version keeps serving.
if (( DO_TESTS )); then
  step "Test suite"
  run $PY manage.py test --verbosity 1
  did "tests passed"
else
  info "skipping tests (--no-tests)"
fi

# -------------------------------------------------------------- migrations --
step "Database migrations"
if (( ! DRY_RUN )); then
  # Only worth announcing when there is something to apply — "migrate" reports
  # the no-op case itself.
  pending="$($PY manage.py showmigrations --plan | grep -c '^\[ \]' || true)"
  [[ "$pending" == "0" ]] || info "$pending migration(s) to apply"
fi
run $PY manage.py migrate --noinput
did "database up to date"

if (( DO_SEED )); then
  step "Seed content"
  run $PY manage.py seed_data
  did "seed data present (existing content was left untouched)"
fi

# ------------------------------------------------------------ translations --
step "Translations"
if command -v msgfmt >/dev/null 2>&1; then
  run $PY manage.py compilemessages
  did "locale/en/LC_MESSAGES/django.mo compiled"
else
  warn "msgfmt not found — keeping the committed .mo file"
  warn "install it with: apt-get install gettext"
fi

# ----------------------------------------------------------- static files --
step "Static files"
run $PY manage.py collectstatic --noinput --clear
did "staticfiles/ rebuilt"

# ------------------------------------------------------------------ checks --
step "Deployment checks"
if (( DRY_RUN )); then
  printf '    would run: %s manage.py check --deploy\n' "$PY"
else
  # Advisory only: report the warnings without failing the update.
  $PY manage.py check --deploy || warn "django reported deployment warnings (see above)"
fi

# ----------------------------------------------------------------- reload --
if [[ -n "$SERVICE" ]]; then
  step "Reloading $SERVICE"
  if command -v systemctl >/dev/null 2>&1; then
    run sudo systemctl reload-or-restart "$SERVICE"
    did "$SERVICE reloaded"
  else
    warn "systemctl not found — reload $SERVICE yourself"
  fi
else
  step "Reload"
  info "MINEFOP_SERVICE is not set, so no service was reloaded."
  info "Restart your application server to pick up the new code, or set e.g."
  info "  MINEFOP_SERVICE=minefop.service ./scripts/update.sh"
fi

printf '\n%sUpdate complete.%s\n' "$GREEN$BOLD" "$RESET"
