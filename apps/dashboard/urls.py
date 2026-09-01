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
    path("messages/", views.message_list, name="message_list"),
    path("messages/<int:pk>/", views.message_detail, name="message_detail"),
]
