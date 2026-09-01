from django.urls import path

from . import views

app_name = "press"

urlpatterns = [
    path("", views.press_list, name="list"),
    path("<slug:slug>/", views.press_detail, name="detail"),
]
