from django.conf import settings
from django.db import models
from django.urls import reverse
from django.utils import timezone
from django.utils.crypto import get_random_string
from django.utils.text import slugify
from django.utils.translation import gettext_lazy as _


class TrainingProgram(models.Model):
    """A training with a day-by-day timetable that gates content for candidates."""

    title = models.CharField(_("intitulé"), max_length=250)
    slug = models.SlugField(_("slug"), max_length=270, unique=True, blank=True)
    center = models.ForeignKey(
        "structures.TrainingCenter",
        verbose_name=_("centre de formation"),
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="programs",
    )
    description = models.TextField(_("description"), blank=True)
    start_date = models.DateField(_("date de démarrage"))
    access_code = models.CharField(
        _("code d'accès"),
        max_length=12,
        unique=True,
        blank=True,
        help_text=_("Code communiqué aux candidats pour rejoindre la formation. Généré automatiquement si laissé vide."),
    )
    is_published = models.BooleanField(
        _("publiée"),
        default=True,
        help_text=_("Une formation non publiée n'apparaît pas dans le catalogue et refuse les inscriptions."),
    )
    trainer = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        verbose_name=_("formateur responsable"),
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="training_programs",
    )
    created_at = models.DateTimeField(_("créée le"), auto_now_add=True)

    class Meta:
        verbose_name = _("formation")
        verbose_name_plural = _("formations")
        ordering = ["-start_date", "title"]

    def __str__(self):
        return self.title

    def save(self, *args, **kwargs):
        if not self.slug:
            base_slug = slugify(self.title)[:250] or "formation"
            slug = base_slug
            i = 1
            while TrainingProgram.objects.exclude(pk=self.pk).filter(slug=slug).exists():
                i += 1
                slug = f"{base_slug}-{i}"
            self.slug = slug
        if not self.access_code:
            code = get_random_string(8, allowed_chars="ABCDEFGHJKLMNPQRSTUVWXYZ23456789")
            while TrainingProgram.objects.exclude(pk=self.pk).filter(access_code=code).exists():
                code = get_random_string(8, allowed_chars="ABCDEFGHJKLMNPQRSTUVWXYZ23456789")
            self.access_code = code
        super().save(*args, **kwargs)

    def get_absolute_url(self):
        return reverse("training:program_timetable", kwargs={"slug": self.slug})

    @property
    def total_days(self):
        return self.days.count()

    @property
    def current_day(self):
        """The most recently unlocked day, or None if the program hasn't started."""
        return self.days.filter(date__lte=timezone.localdate()).order_by("-day_number").first()


class TrainingDay(models.Model):
    """One entry of the timetable: the unit of content gating."""

    program = models.ForeignKey(
        TrainingProgram, verbose_name=_("formation"), on_delete=models.CASCADE, related_name="days"
    )
    day_number = models.PositiveIntegerField(_("jour n°"))
    date = models.DateField(_("date"), help_text=_("Date à laquelle ce jour du programme s'ouvre aux candidats."))
    title = models.CharField(_("titre du jour"), max_length=250)
    objectives = models.TextField(_("objectifs pédagogiques"), blank=True)

    class Meta:
        verbose_name = _("jour du programme")
        verbose_name_plural = _("emploi du temps")
        ordering = ["program", "day_number"]
        unique_together = ("program", "day_number")

    def __str__(self):
        return f"{self.program} — {_('Jour')} {self.day_number} : {self.title}"

    def is_unlocked(self, as_of=None):
        as_of = as_of or timezone.localdate()
        return as_of >= self.date

    @property
    def is_today(self):
        return self.date == timezone.localdate()


class Material(models.Model):
    """A course document/resource attached to a timetable day.

    Trainers may upload materials for any future day right away (e.g. on day 1
    they can push everything for the whole program); only the day's own
    ``is_unlocked()`` state controls when candidates may reach it.
    """

    class MaterialType(models.TextChoices):
        DOCUMENT = "document", _("Document")
        VIDEO = "video", _("Vidéo")
        LINK = "link", _("Lien externe")
        OTHER = "other", _("Autre")

    day = models.ForeignKey(TrainingDay, verbose_name=_("jour"), on_delete=models.CASCADE, related_name="materials")
    title = models.CharField(_("titre"), max_length=250)
    material_type = models.CharField(_("type"), max_length=20, choices=MaterialType.choices, default=MaterialType.DOCUMENT)
    file = models.FileField(_("fichier"), upload_to="training/materials/", blank=True)
    external_url = models.URLField(_("lien externe"), blank=True)
    description = models.TextField(_("description"), blank=True)
    order = models.PositiveIntegerField(_("ordre"), default=0)
    uploaded_at = models.DateTimeField(_("mis en ligne le"), auto_now_add=True)

    class Meta:
        verbose_name = _("support de cours")
        verbose_name_plural = _("supports de cours")
        ordering = ["day", "order", "id"]

    def __str__(self):
        return self.title


class Quiz(models.Model):
    """At most one quiz per timetable day, unlocked together with the day."""

    day = models.OneToOneField(TrainingDay, verbose_name=_("jour"), on_delete=models.CASCADE, related_name="quiz")
    title = models.CharField(_("titre"), max_length=250)
    instructions = models.TextField(_("consignes"), blank=True)
    pass_mark = models.PositiveIntegerField(_("note de passage (%)"), default=50)
    time_limit_minutes = models.PositiveIntegerField(_("durée limite (minutes)"), null=True, blank=True)
    max_attempts = models.PositiveIntegerField(
        _("tentatives autorisées"), default=1, help_text=_("0 = tentatives illimitées")
    )

    class Meta:
        verbose_name = _("quiz")
        verbose_name_plural = _("quiz")

    def __str__(self):
        return self.title

    @property
    def total_points(self):
        return sum(self.questions.values_list("points", flat=True)) or 0


class Question(models.Model):
    quiz = models.ForeignKey(Quiz, verbose_name=_("quiz"), on_delete=models.CASCADE, related_name="questions")
    text = models.TextField(_("question"))
    order = models.PositiveIntegerField(_("ordre"), default=0)
    points = models.PositiveIntegerField(_("points"), default=1)
    allow_multiple = models.BooleanField(
        _("plusieurs réponses correctes"),
        default=False,
        help_text=_("Cocher si la question admet plusieurs bonnes réponses (cases à cocher)."),
    )

    class Meta:
        verbose_name = _("question")
        verbose_name_plural = _("questions")
        ordering = ["quiz", "order", "id"]

    def __str__(self):
        return self.text[:80]


class Choice(models.Model):
    question = models.ForeignKey(Question, verbose_name=_("question"), on_delete=models.CASCADE, related_name="choices")
    text = models.CharField(_("texte"), max_length=500)
    is_correct = models.BooleanField(_("bonne réponse"), default=False)

    class Meta:
        verbose_name = _("choix de réponse")
        verbose_name_plural = _("choix de réponse")

    def __str__(self):
        return self.text


class CandidateProfile(models.Model):
    """Extends a Django user with candidate-portal specific fields."""

    user = models.OneToOneField(
        settings.AUTH_USER_MODEL, verbose_name=_("utilisateur"), on_delete=models.CASCADE, related_name="candidate_profile"
    )
    phone = models.CharField(_("téléphone"), max_length=50, blank=True)

    class Meta:
        verbose_name = _("profil candidat")
        verbose_name_plural = _("profils candidats")

    def __str__(self):
        return self.user.get_full_name() or self.user.get_username()


class Enrollment(models.Model):
    candidate = models.ForeignKey(
        CandidateProfile, verbose_name=_("candidat"), on_delete=models.CASCADE, related_name="enrollments"
    )
    program = models.ForeignKey(
        TrainingProgram, verbose_name=_("formation"), on_delete=models.CASCADE, related_name="enrollments"
    )
    enrolled_at = models.DateTimeField(_("inscrit le"), auto_now_add=True)

    class Meta:
        verbose_name = _("inscription")
        verbose_name_plural = _("inscriptions")
        unique_together = ("candidate", "program")
        ordering = ["-enrolled_at"]

    def __str__(self):
        return f"{self.candidate} → {self.program}"

    def attempts_used(self, quiz):
        return self.quiz_attempts.filter(quiz=quiz, submitted_at__isnull=False).count()

    def attempts_remaining(self, quiz):
        if quiz.max_attempts == 0:
            return None  # unlimited
        return max(0, quiz.max_attempts - self.attempts_used(quiz))


class QuizAttempt(models.Model):
    enrollment = models.ForeignKey(
        Enrollment, verbose_name=_("inscription"), on_delete=models.CASCADE, related_name="quiz_attempts"
    )
    quiz = models.ForeignKey(Quiz, verbose_name=_("quiz"), on_delete=models.CASCADE, related_name="attempts")
    started_at = models.DateTimeField(_("commencé le"), auto_now_add=True)
    submitted_at = models.DateTimeField(_("soumis le"), null=True, blank=True)
    score = models.FloatField(_("note (%)"), null=True, blank=True)
    passed = models.BooleanField(_("réussi"), default=False)

    class Meta:
        verbose_name = _("tentative de quiz")
        verbose_name_plural = _("tentatives de quiz")
        ordering = ["-started_at"]

    def __str__(self):
        return f"{self.enrollment.candidate} — {self.quiz} ({self.score})"

    def grade(self):
        """Score this attempt from its recorded answers and persist the result."""
        total_points = self.quiz.total_points or 1
        earned = 0
        for answer in self.answers.select_related("question").prefetch_related("selected_choices", "question__choices"):
            correct_ids = set(answer.question.choices.filter(is_correct=True).values_list("id", flat=True))
            selected_ids = set(answer.selected_choices.values_list("id", flat=True))
            if correct_ids and selected_ids == correct_ids:
                earned += answer.question.points
        self.score = round((earned / total_points) * 100, 1)
        self.passed = self.score >= self.quiz.pass_mark
        self.submitted_at = timezone.now()
        self.save(update_fields=["score", "passed", "submitted_at"])
        return self.score


class QuizAnswer(models.Model):
    attempt = models.ForeignKey(QuizAttempt, verbose_name=_("tentative"), on_delete=models.CASCADE, related_name="answers")
    question = models.ForeignKey(Question, verbose_name=_("question"), on_delete=models.CASCADE, related_name="answers")
    selected_choices = models.ManyToManyField(Choice, verbose_name=_("choix sélectionnés"), blank=True)

    class Meta:
        verbose_name = _("réponse")
        verbose_name_plural = _("réponses")
        unique_together = ("attempt", "question")
