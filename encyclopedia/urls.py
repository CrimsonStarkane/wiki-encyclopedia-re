from django.urls import path, re_path

from . import views

urlpatterns = [
    path("", views.index, name="index"),
    path("search/", views.init_search, name="isearch"),
    path("random/", views.random, name="random"),
    path("wiki/add/input/", views.add, name="add"),
    path("wiki/edit/<entry>", views.edit, name="edit"),
    path("wiki/<entry>/", views.entry, name="entry"),
    re_path(r"wiki/search/?$", views.search, name="search")
]
