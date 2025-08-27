from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.utils import timezone
from .models import Note

@login_required
def note_list(request):
    notes = Note.objects.filter(user=request.user).order_by('-updated_at')
    today = timezone.localdate()
    q = request.GET.get("q")
    if q:
        notes = notes.filter(title__icontains=q) | notes.filter(content__icontains=q)
    return render(request, "notes/note_list.html", {"notes": notes, "today": today, "q": q or ""})

# ✅ fehlte dir vermutlich:
@login_required
def add_note(request):
    if request.method == "POST":
        title = (request.POST.get("title") or "").strip()
        content = (request.POST.get("content") or "").strip()
        deadline = request.POST.get("deadline") or None
        Note.objects.create(
            user=request.user,
            title=title,
            content=content,
            deadline=deadline
        )
        return redirect("note_list")
    return render(request, "notes/add_note.html")

# (optional, falls du mein Modal/HTMX verwendest)
@login_required
def edit_note_partial(request, pk):
    note = get_object_or_404(Note, pk=pk, user=request.user)
    return render(request, "notes/_note_form.html", {"note": note})

@login_required
def update_note_partial(request, pk):
    note = get_object_or_404(Note, pk=pk, user=request.user)
    if request.method == "POST":
        note.title = request.POST.get("title")
        note.content = request.POST.get("content")
        note.deadline = request.POST.get("deadline") or None
        note.save()
        today = timezone.localdate()
        return render(request, "notes/_note_card.html", {"note": note, "today": today})
    return redirect("note_list")


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
