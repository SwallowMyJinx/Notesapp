from django.shortcuts import render, redirect
from .models import Note
from django.contrib.auth.decorators import login_required
from django.shortcuts import get_object_or_404
from django.http import HttpResponse

@login_required
def note_list(request):
    notes = Note.objects.filter(user=request.user).order_by('-updated_at')
    return render(request, "notes/note_list.html", {"notes": notes})

@login_required
def add_note(request):
    if request.method == "POST":
        title = request.POST.get("title")
        content = request.POST.get("content")
        deadline = request.POST.get("deadline") or None
        Note.objects.create(
            user=request.user,
            title=title,
            content=content,
            deadline=deadline
        )
        return redirect("note_list")
    return render(request, "notes/add_note.html")

@login_required
def edit_note(request, pk):
    note = get_object_or_404(Note, pk=pk, user=request.user)

    if request.method == "POST":
        note.title = request.POST.get("title")
        note.content = request.POST.get("content")
        note.deadline = request.POST.get("deadline") or None
        note.save()
        return redirect("note_list")

    return render(request, "notes/edit_note.html", {"note": note})


@login_required
def delete_note(request, pk):
    note = get_object_or_404(Note, pk=pk, user=request.user)
    if request.method == "POST":
        note.delete()
        return redirect("note_list")
    
    return render(request, "notes/confirm_delete.html", {"note": note})