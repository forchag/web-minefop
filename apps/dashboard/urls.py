from django.urls import path

from . import views

app_name = "dashboard"

urlpatterns = [
    path("connexion/", views.dashboard_login, name="login"),
    path("deconnexion/", views.dashboard_logout, name="logout"),
    path("", views.dashboard_home, name="home"),

    path("blog/", views.blog_list, name="blog_list"),
    path("blog/nouveau/", views.blog_form_view, name="blog_create"),
    path("blog/<int:pk>/modifier/", views.blog_form_view, name="blog_edit"),
    path("blog/<int:pk>/publier/", views.blog_toggle_publish, name="blog_toggle_publish"),
    path("blog/<int:pk>/supprimer/", views.blog_delete, name="blog_delete"),

    path("actualites/", views.news_list, name="news_list"),
    path("actualites/nouveau/", views.news_form_view, name="news_create"),
    path("actualites/<int:pk>/modifier/", views.news_form_view, name="news_edit"),
    path("actualites/<int:pk>/publier/", views.news_toggle_publish, name="news_toggle_publish"),
    path("actualites/<int:pk>/supprimer/", views.news_delete, name="news_delete"),

    path("opportunites/", views.opportunity_list, name="opportunity_list"),
    path("opportunites/nouveau/", views.opportunity_form_view, name="opportunity_create"),
    path("opportunites/<int:pk>/modifier/", views.opportunity_form_view, name="opportunity_edit"),
    path(
        "opportunites/<int:pk>/publier/",
        views.opportunity_toggle_publish,
        name="opportunity_toggle_publish",
    ),
    path("opportunites/<int:pk>/supprimer/", views.opportunity_delete, name="opportunity_delete"),

    path("documents/", views.document_list, name="document_list"),
    path("documents/nouveau/", views.document_form_view, name="document_create"),
    path("documents/<int:pk>/modifier/", views.document_form_view, name="document_edit"),
    path("documents/<int:pk>/supprimer/", views.document_delete, name="document_delete"),

    path("evenements/", views.event_list, name="event_list"),
    path("evenements/nouveau/", views.event_form_view, name="event_create"),
    path("evenements/<int:pk>/modifier/", views.event_form_view, name="event_edit"),
    path("evenements/<int:pk>/publier/", views.event_toggle_publish, name="event_toggle_publish"),
    path("evenements/<int:pk>/supprimer/", views.event_delete, name="event_delete"),

    path("galerie/", views.photo_list, name="photo_list"),
    path("galerie/nouveau/", views.photo_form_view, name="photo_create"),
    path("galerie/<int:pk>/modifier/", views.photo_form_view, name="photo_edit"),
    path("galerie/<int:pk>/supprimer/", views.photo_delete, name="photo_delete"),

    path("directions/", views.directorate_list, name="directorate_list"),
    path("directions/nouveau/", views.directorate_create, name="directorate_create"),
    path("directions/<int:pk>/modifier/", views.directorate_edit, name="directorate_edit"),
    path(
        "directions/<int:pk>/sous-directions/nouveau/",
        views.sous_direction_create,
        name="sous_direction_create",
    ),
    path(
        "sous-directions/<int:pk>/modifier/",
        views.sous_direction_edit,
        name="sous_direction_edit",
    ),

    path("messages/", views.message_list, name="message_list"),
    path("messages/<int:pk>/", views.message_detail, name="message_detail"),
]
