from django.urls import path

from . import views

app_name = 'encyclopedia'
urlpatterns = [
    path("", views.index, name="index"),
    path("search", views.search, name="search"),
    path("edit/<str:name>", views.edit, name="edit"),
    path("new", views.new, name="new"),
    path("random_page", views.random_page, name="random_page"),
    path("wiki/<str:name>", views.display_page, name="display_page")
]
