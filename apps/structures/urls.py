from django.urls import path

from . import views

app_name = "structures"

urlpatterns = [
    path("", views.org_chart, name="org_chart"),
    path("organismes-rattaches/", views.attached_bodies, name="attached_bodies"),
    path("delegations/", views.delegations, name="delegations"),
    path("centres-de-formation/", views.training_center_list, name="training_center_list"),
    path("centres-de-formation/<int:pk>/", views.training_center_detail, name="training_center_detail"),
]
