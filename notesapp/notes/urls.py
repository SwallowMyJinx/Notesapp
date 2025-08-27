from django.urls import path
from . import views

urlpatterns = [
    path("", views.note_list, name="note_list"),
    path("add/", views.add_note, name="add_note"),
    path("edit/<int:pk>/", views.edit_note, name="edit_note"),                 # <= neu (Seite)
    path("edit/<int:pk>/partial/", views.edit_note_partial, name="edit_note_partial"),
    path("edit/<int:pk>/save/", views.update_note_partial, name="update_note_partial"),
]
