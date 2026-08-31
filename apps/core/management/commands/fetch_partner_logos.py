"""Mirror the portal's partner logos onto the Ministry's own domain.

Each tile on the entry portal can name the logo address supplied by the
structure it links to. Serving the image straight from that address works most
of the time, but two things commonly break it, and both look identical to a
visitor — the tile just shows its acronym instead of the logo:

* the source server is down, slow, or has moved the file;
* the source server runs a hotlink-protection plugin (very common on the
  WordPress sites several of these structures use) that silently refuses any
  image request whose Referer header names a foreign site. The request never
  errors in a way a visitor would notice — the image simply never loads.
  `referrerpolicy="no-referrer"` on the `<img>` tag already defeats that for
  the browser-side embed, but the surest fix is to stop depending on that
  server at all.

This command downloads each address once and stores the file against the
partner, after which `PartnerSite.logo_src` serves the local copy and the
portal stops reaching outside this domain. It is safe to re-run: a partner that
already has an uploaded file is skipped unless --force is given.

    python manage.py fetch_partner_logos
    python manage.py fetch_partner_logos --force        # re-download everything
    python manage.py fetch_partner_logos --dry-run      # check reachability only

Run this from an environment with real internet access to the structures'
sites — a sandboxed one may have some of those hosts blocked by its own
network policy, which is not the same as the address being broken.
"""

import mimetypes
from urllib.error import HTTPError, URLError
from urllib.parse import urlparse
from urllib.request import Request, urlopen

from django.core.files.base import ContentFile
from django.core.management.base import BaseCommand
from django.utils.text import slugify

from apps.core.models import PartnerSite

TIMEOUT = 30
MAX_BYTES = 5 * 1024 * 1024
ALLOWED_TYPES = {
    "image/png": ".png",
    "image/jpeg": ".jpg",
    "image/gif": ".gif",
    "image/webp": ".webp",
    "image/svg+xml": ".svg",
}
# A plain browser UA. Some of the sites we fetch from block requests that
# identify themselves as a script or bot; sending no Referer (the default —
# never set one below) is what actually defeats referer-based hotlink checks.
USER_AGENT = (
    "Mozilla/5.0 (compatible; MINEFOP-portal-logo-sync/1.0; "
    "+https://minefop.cm)"
)


class Command(BaseCommand):
    help = "Download each partner's supplied logo and serve it from this domain."

    def add_arguments(self, parser):
        parser.add_argument(
            "--force",
            action="store_true",
            help="Re-download even for partners that already have an uploaded logo.",
        )
        parser.add_argument(
            "--dry-run",
            action="store_true",
            help="Check that each supplied address answers, without downloading or saving anything.",
        )

    def handle(self, *args, **options):
        force = options["force"]
        dry_run = options["dry_run"]

        partners = PartnerSite.objects.exclude(logo_url="").order_by("column", "order")
        if not partners:
            self.stdout.write("No partner carries a logo address — nothing to fetch.")
            return

        if dry_run:
            self._check(partners)
            return

        fetched = skipped = failed = 0
        for partner in partners:
            label = partner.acronym or partner.name

            if partner.logo and not force:
                self.stdout.write(f"  {label}: already hosted here, skipping")
                skipped += 1
                continue

            try:
                content, extension = self._download(partner.logo_url)
            except Exception as error:  # noqa: BLE001 — report and carry on
                self.stderr.write(self.style.WARNING(f"  {label}: {error}"))
                failed += 1
                continue

            name = f"{slugify(label) or 'partenaire'}{extension}"
            partner.logo.save(name, ContentFile(content), save=True)
            self.stdout.write(self.style.SUCCESS(f"  {label}: saved as {partner.logo.name}"))
            fetched += 1

        self.stdout.write("")
        self.stdout.write(f"Downloaded {fetched}, skipped {skipped}, failed {failed}.")
        if failed:
            self.stdout.write(
                "The tiles that failed keep using their supplied address; upload a "
                "file through Sites partenaires to host them here instead."
            )

    def _check(self, partners):
        """--dry-run: actually reach each address and report what came back.

        This is the closest thing to "does the logo really load" that can be
        run without touching the database — point it at a machine with normal
        internet access rather than treating a sandboxed check as conclusive.
        """
        ok = already_hosted = broken = 0
        for partner in partners:
            label = partner.acronym or partner.name
            if partner.logo:
                self.stdout.write(f"  {label}: already hosted here — {partner.logo.url}")
                already_hosted += 1
                continue

            try:
                content_type, size = self._probe(partner.logo_url)
            except Exception as error:  # noqa: BLE001 — report and carry on
                self.stderr.write(self.style.WARNING(f"  {label}: UNREACHABLE — {error}"))
                self.stderr.write(f"           {partner.logo_url}")
                broken += 1
                continue

            size_note = f", {size:,} bytes" if size is not None else ""
            self.stdout.write(
                self.style.SUCCESS(f"  {label}: reachable — {content_type or 'unknown type'}{size_note}")
            )
            ok += 1

        self.stdout.write("")
        self.stdout.write(f"Reachable: {ok}, already hosted here: {already_hosted}, broken: {broken}.")
        if broken:
            self.stdout.write(
                "Run without --dry-run to mirror the reachable ones onto this domain; "
                "a broken address needs a new one from the structure, or a logo "
                "uploaded directly through Sites partenaires."
            )

    def _probe(self, url):
        """HEAD the address; some servers reject HEAD, so fall back to a GET."""
        parsed = urlparse(url)
        if parsed.scheme not in ("http", "https"):
            raise ValueError(f"unsupported address ({parsed.scheme or 'no scheme'})")

        for method in ("HEAD", "GET"):
            request = Request(url, method=method, headers={"User-Agent": USER_AGENT})
            try:
                with urlopen(request, timeout=TIMEOUT) as response:  # noqa: S310
                    content_type = (response.headers.get_content_type() or "").lower()
                    length = response.headers.get("Content-Length")
                    return content_type, int(length) if length else None
            except HTTPError as error:
                if method == "HEAD" and error.code in (405, 501):
                    continue  # the server doesn't support HEAD — try GET
                raise ValueError(f"HTTP {error.code} {error.reason}") from error
            except URLError as error:
                raise ValueError(str(error.reason)) from error
        raise AssertionError("unreachable")  # both methods raised or returned above

    def _download(self, url):
        parsed = urlparse(url)
        if parsed.scheme not in ("http", "https"):
            raise ValueError(f"unsupported address ({parsed.scheme or 'no scheme'})")

        request = Request(url, headers={"User-Agent": USER_AGENT})
        try:
            with urlopen(request, timeout=TIMEOUT) as response:  # noqa: S310
                content_type = (response.headers.get_content_type() or "").lower()
                # Read one byte past the cap so an oversized file is detected
                # rather than silently truncated.
                content = response.read(MAX_BYTES + 1)
        except HTTPError as error:
            raise ValueError(f"HTTP {error.code} {error.reason}") from error
        except URLError as error:
            raise ValueError(str(error.reason)) from error

        if len(content) > MAX_BYTES:
            raise ValueError(f"larger than {MAX_BYTES // (1024 * 1024)} MB")
        if not content:
            raise ValueError("empty response")

        extension = ALLOWED_TYPES.get(content_type)
        if extension is None:
            guessed = mimetypes.guess_type(parsed.path)[0]
            extension = ALLOWED_TYPES.get(guessed or "")
        if extension is None:
            raise ValueError(f"not an image we store ({content_type or 'unknown type'})")

        return content, extension
