from django.urls import path

from . import views

app_name = "media"

urlpatterns = [
    path("evenements/", views.event_list, name="event_list"),
    path("evenements/<slug:slug>/", views.event_detail, name="event_detail"),
    path("galerie/", views.gallery_list, name="gallery_list"),
]
