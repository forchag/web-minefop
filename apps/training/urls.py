from django.urls import path

from . import views

app_name = "training"

urlpatterns = [
    path("", views.catalog, name="catalog"),
    path("inscription/", views.signup, name="signup"),
    path("connexion/", views.CandidateLoginView.as_view(), name="login"),
    path("deconnexion/", views.CandidateLogoutView.as_view(), name="logout"),
    path("tableau-de-bord/", views.dashboard, name="dashboard"),
    path("rejoindre/", views.join_program, name="join"),
    path("<slug:slug>/", views.program_timetable, name="program_timetable"),
    path("<slug:slug>/jour/<int:day_number>/", views.day_detail, name="day_detail"),
    path(
        "<slug:slug>/jour/<int:day_number>/materiel/<int:material_id>/",
        views.material_download,
        name="material_download",
    ),
    path("<slug:slug>/jour/<int:day_number>/quiz/", views.quiz_take, name="quiz_take"),
    path(
        "<slug:slug>/jour/<int:day_number>/quiz/resultat/<int:attempt_id>/",
        views.quiz_result,
        name="quiz_result",
    ),
]
