from django.contrib import messages
from django.contrib.auth import login as auth_login
from django.contrib.auth.decorators import login_required
from django.contrib.auth.views import LoginView, LogoutView
from django.core.exceptions import PermissionDenied
from django.http import FileResponse, Http404
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse_lazy
from django.utils.translation import gettext as _

from .forms import CandidateAuthenticationForm, CandidateSignUpForm, JoinProgramForm
from .models import CandidateProfile, Enrollment, Material, QuizAttempt, TrainingDay, TrainingProgram


def _candidate_profile(user):
    profile, _created = CandidateProfile.objects.get_or_create(user=user)
    return profile


def _get_enrollment(request, program):
    profile = _candidate_profile(request.user)
    return Enrollment.objects.filter(candidate=profile, program=program).first()


def catalog(request):
    programs = TrainingProgram.objects.filter(is_published=True).select_related("center")
    return render(request, "training/catalog.html", {"programs": programs})


def signup(request):
    if request.method == "POST":
        form = CandidateSignUpForm(request.POST)
        if form.is_valid():
            user = form.save()
            auth_login(request, user)
            messages.success(request, _("Bienvenue ! Votre compte candidat a été créé."))
            return redirect("training:join")
    else:
        form = CandidateSignUpForm()
    return render(request, "training/signup.html", {"form": form})


class CandidateLoginView(LoginView):
    template_name = "training/login.html"
    authentication_form = CandidateAuthenticationForm
    redirect_authenticated_user = True

    def get_success_url(self):
        return str(reverse_lazy("training:dashboard"))


class CandidateLogoutView(LogoutView):
    next_page = reverse_lazy("training:catalog")


@login_required(login_url="training:login")
def dashboard(request):
    profile = _candidate_profile(request.user)
    enrollments = (
        Enrollment.objects.filter(candidate=profile)
        .select_related("program", "program__center")
        .prefetch_related("program__days")
    )
    return render(request, "training/dashboard.html", {"enrollments": enrollments})


@login_required(login_url="training:login")
def join_program(request):
    if request.method == "POST":
        form = JoinProgramForm(request.POST)
        if form.is_valid():
            code = form.cleaned_data["access_code"]
            program = TrainingProgram.objects.filter(access_code=code, is_published=True).first()
            if not program:
                form.add_error("access_code", _("Aucune formation publiée ne correspond à ce code."))
            else:
                profile = _candidate_profile(request.user)
                Enrollment.objects.get_or_create(candidate=profile, program=program)
                messages.success(request, _("Vous avez rejoint la formation « %(title)s ».") % {"title": program.title})
                return redirect("training:program_timetable", slug=program.slug)
    else:
        form = JoinProgramForm()
    return render(request, "training/join.html", {"form": form})


@login_required(login_url="training:login")
def program_timetable(request, slug):
    program = get_object_or_404(TrainingProgram, slug=slug)
    enrollment = _get_enrollment(request, program)
    if not enrollment:
        if request.user.is_staff:
            pass  # staff/trainers may preview any program's timetable
        else:
            return render(request, "training/not_enrolled.html", {"program": program}, status=403)
    days = program.days.prefetch_related("materials", "quiz")
    days_with_state = [{"day": day, "unlocked": day.is_unlocked()} for day in days]
    return render(
        request,
        "training/program_timetable.html",
        {"program": program, "days_with_state": days_with_state, "enrollment": enrollment},
    )


def _authorize_day(request, slug, day_number):
    """Shared guard for day-scoped views: enrollment + unlock check.

    Returns (program, day, enrollment). Raises Http404/PermissionDenied when access
    is not allowed so callers don't accidentally leak gated content.
    """
    program = get_object_or_404(TrainingProgram, slug=slug)
    day = get_object_or_404(TrainingDay, program=program, day_number=day_number)
    enrollment = _get_enrollment(request, program)
    if not enrollment and not request.user.is_staff:
        raise PermissionDenied(_("Vous devez rejoindre cette formation pour y accéder."))
    if not day.is_unlocked() and not request.user.is_staff:
        raise PermissionDenied(_("Ce jour du programme n'est pas encore ouvert."))
    return program, day, enrollment


@login_required(login_url="training:login")
def day_detail(request, slug, day_number):
    program, day, enrollment = _authorize_day(request, slug, day_number)
    materials = day.materials.all()
    quiz = getattr(day, "quiz", None)
    attempts_remaining = enrollment.attempts_remaining(quiz) if (quiz and enrollment) else None
    last_attempt = None
    if quiz and enrollment:
        last_attempt = enrollment.quiz_attempts.filter(quiz=quiz, submitted_at__isnull=False).order_by("-started_at").first()
    context = {
        "program": program,
        "day": day,
        "materials": materials,
        "quiz": quiz,
        "attempts_remaining": attempts_remaining,
        "last_attempt": last_attempt,
    }
    return render(request, "training/day_detail.html", context)


@login_required(login_url="training:login")
def material_download(request, slug, day_number, material_id):
    program, day, _enrollment = _authorize_day(request, slug, day_number)
    material = get_object_or_404(Material, pk=material_id, day=day)
    if material.file:
        return FileResponse(material.file.open("rb"), as_attachment=True, filename=material.file.name.rsplit("/", 1)[-1])
    if material.external_url:
        return redirect(material.external_url)
    raise Http404(_("Support indisponible."))


@login_required(login_url="training:login")
def quiz_take(request, slug, day_number):
    program, day, enrollment = _authorize_day(request, slug, day_number)
    quiz = getattr(day, "quiz", None)
    if not quiz:
        raise Http404(_("Aucun quiz pour ce jour."))
    if not enrollment:
        raise PermissionDenied(_("Inscription requise."))

    remaining = enrollment.attempts_remaining(quiz)
    if remaining is not None and remaining <= 0:
        messages.error(request, _("Vous avez épuisé le nombre de tentatives autorisées pour ce quiz."))
        return redirect("training:day_detail", slug=slug, day_number=day_number)

    questions = quiz.questions.prefetch_related("choices")

    if request.method == "POST":
        attempt = QuizAttempt.objects.create(enrollment=enrollment, quiz=quiz)
        for question in questions:
            field_name = f"question_{question.id}"
            selected_ids = request.POST.getlist(field_name)
            answer = attempt.answers.create(question=question)
            if selected_ids:
                answer.selected_choices.set(question.choices.filter(id__in=selected_ids))
        attempt.grade()
        return redirect("training:quiz_result", slug=slug, day_number=day_number, attempt_id=attempt.id)

    context = {
        "program": program,
        "day": day,
        "quiz": quiz,
        "questions": questions,
        "remaining": remaining,
    }
    return render(request, "training/quiz_take.html", context)


@login_required(login_url="training:login")
def quiz_result(request, slug, day_number, attempt_id):
    program, day, enrollment = _authorize_day(request, slug, day_number)
    qs = QuizAttempt.objects.select_related("quiz")
    if not request.user.is_staff:
        qs = qs.filter(enrollment=enrollment)
    attempt = get_object_or_404(qs, pk=attempt_id, quiz__day=day)
    answers = attempt.answers.select_related("question").prefetch_related("selected_choices", "question__choices")
    return render(
        request,
        "training/quiz_result.html",
        {"program": program, "day": day, "attempt": attempt, "answers": answers},
    )
