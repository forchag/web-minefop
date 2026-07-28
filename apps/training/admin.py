from django.contrib import admin

from .models import (
    CandidateProfile,
    Choice,
    Enrollment,
    Material,
    Question,
    Quiz,
    QuizAnswer,
    QuizAttempt,
    TrainingDay,
    TrainingProgram,
)


class TrainingDayInline(admin.TabularInline):
    model = TrainingDay
    extra = 1
    fields = ("day_number", "date", "title")
    ordering = ("day_number",)
    show_change_link = True


@admin.register(TrainingProgram)
class TrainingProgramAdmin(admin.ModelAdmin):
    list_display = ("title", "center", "start_date", "total_days", "access_code", "is_published")
    list_filter = ("is_published", "center")
    search_fields = ("title", "access_code")
    prepopulated_fields = {"slug": ("title",)}
    autocomplete_fields = ("center", "trainer")
    readonly_fields = ("access_code",)
    inlines = [TrainingDayInline]


class MaterialInline(admin.TabularInline):
    model = Material
    extra = 1
    fields = ("title", "material_type", "file", "external_url", "order")


@admin.register(TrainingDay)
class TrainingDayAdmin(admin.ModelAdmin):
    list_display = ("program", "day_number", "date", "title", "is_unlocked_now")
    list_filter = ("program",)
    search_fields = ("title", "program__title")
    ordering = ("program", "day_number")
    autocomplete_fields = ("program",)
    inlines = [MaterialInline]

    @admin.display(boolean=True, description="Ouvert aujourd'hui")
    def is_unlocked_now(self, obj):
        return obj.is_unlocked()


class QuestionInline(admin.TabularInline):
    model = Question
    extra = 1
    fields = ("text", "points", "allow_multiple", "order")
    show_change_link = True


@admin.register(Quiz)
class QuizAdmin(admin.ModelAdmin):
    list_display = ("title", "day", "pass_mark", "max_attempts")
    autocomplete_fields = ("day",)
    inlines = [QuestionInline]


class ChoiceInline(admin.TabularInline):
    model = Choice
    extra = 2
    fields = ("text", "is_correct")


@admin.register(Question)
class QuestionAdmin(admin.ModelAdmin):
    list_display = ("__str__", "quiz", "points", "allow_multiple")
    list_filter = ("quiz",)
    inlines = [ChoiceInline]


@admin.register(CandidateProfile)
class CandidateProfileAdmin(admin.ModelAdmin):
    list_display = ("user", "phone")
    search_fields = ("user__username", "user__email", "user__first_name", "user__last_name", "phone")
    autocomplete_fields = ("user",)


@admin.register(Enrollment)
class EnrollmentAdmin(admin.ModelAdmin):
    list_display = ("candidate", "program", "enrolled_at")
    list_filter = ("program",)
    autocomplete_fields = ("candidate", "program")


@admin.register(QuizAttempt)
class QuizAttemptAdmin(admin.ModelAdmin):
    list_display = ("enrollment", "quiz", "started_at", "submitted_at", "score", "passed")
    list_filter = ("quiz__day__program", "passed")
    readonly_fields = ("started_at",)


admin.site.register(QuizAnswer)
