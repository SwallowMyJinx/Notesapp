from django.urls import path
from . import views

urlpatterns = [
    path("", views.note_list, name="note_list"),
    path("add/", views.add_note, name="add_note"),
    path("edit/<int:pk>/", views.edit_note, name="edit_note"),
    path("delete/<int:pk>/", views.delete_note, name="delete_note"),
    path("color/", views.update_color, name="update_color"),  # post request 
    path("color-labels/", views.update_color_labels, name="update_color_labels"), 
    path("search/", views.search, name="search"),
    path("search/suggest/", views.search_suggest, name="search_suggest"),
]