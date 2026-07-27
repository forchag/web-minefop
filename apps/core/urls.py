from django.urls import path

from . import views

app_name = "core"

urlpatterns = [
    path("", views.home, name="home"),
    path("missions/", views.mission, name="mission"),
    path("historique/", views.history, name="history"),
    path("mot-du-ministre/", views.minister_message, name="minister"),
    path("formation-professionnelle/", views.vocational_training, name="vocational_training"),
]
