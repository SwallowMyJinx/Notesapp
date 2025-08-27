from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.utils import timezone
from django.http import HttpResponseBadRequest
from .models import Note, ColorLabel
from django.db.models import Q
from django.http import JsonResponse
from django.shortcuts import render
from django.urls import reverse
from .models import Note 

# Zentrale Farbdefinition
ALLOWED_COLORS = [
    ("yellow", "bg-yellow-400"),
    ("green",  "bg-green-500"),
    ("blue",   "bg-blue-500"),
    ("purple", "bg-purple-500"),
    ("pink",   "bg-pink-500"),
    ("gray",   "bg-gray-500"),
    ("red",    "bg-red-500"),
    ("orange", "bg-orange-500"),
]
ALLOWED_COLOR_NAMES = {name for name, _ in ALLOWED_COLORS}


def _get_color_labels_map(user):
    """
    Liefert ein Dict {farbe: label_text} für den aktuellen User.
    Nicht gesetzte Labels werden als "" zurückgegeben.
    """
    labels = ColorLabel.objects.filter(user=user)
    result = {c: "" for c, _ in ALLOWED_COLORS}
    for cl in labels:
        result[cl.color] = cl.label
    return result


@login_required
def note_list(request):
    """
    Übersichtsliste der Notizen.
    Optionaler GET-Parameter ?color=<name> filtert nach Farbe.
    """
    notes = Note.objects.filter(user=request.user).order_by("-updated_at")

    color_filter = (request.GET.get("color") or "").strip().lower()
    if color_filter in ALLOWED_COLOR_NAMES:
        notes = notes.filter(color=color_filter)

    labels_map = _get_color_labels_map(request.user)
    # Liste für Templates: (color, tailwind_bg_class, label_text)
    labels = [(c, bg, labels_map.get(c, "")) for c, bg in ALLOWED_COLORS]

    for n in notes:
        n.label_text = labels_map.get(n.color, "").strip()

    context = {
        "notes": notes,
        "colors": ALLOWED_COLORS,     # für Farb-Buttons im Drawer
        "labels": labels,             # für Label-Form & Filter-Chips
        "labels_map": labels_map,     # falls du es direkt brauchst
        "active_color": color_filter, # aktiver Filter
        "today": timezone.localdate(),
    }
    return render(request, "notes/note_list.html", context)


@login_required
def add_note(request):
    """
    Neue Notiz anlegen.
    """
    if request.method == "POST":
        title = (request.POST.get("title") or "").strip()
        content = (request.POST.get("content") or "").strip()
        deadline = request.POST.get("deadline") or None
        Note.objects.create(
            user=request.user,
            title=title,
            content=content,
            deadline=deadline,
        )
        return redirect("note_list")
    return render(request, "notes/add_note.html")


@login_required
def edit_note(request, pk):
    """
    Notiz bearbeiten.
    """
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
    """
    Notiz löschen (mit Confirm-GET).
    """
    note = get_object_or_404(Note, pk=pk, user=request.user)
    if request.method == "POST":
        note.delete()
        return redirect("note_list")
    return render(request, "notes/confirm_delete.html", {"note": note})


@login_required
def update_color(request):
    """
    Farbe einer Notiz setzen (POST).
    Erwartet: note_id, color
    """
    if request.method != "POST":
        return HttpResponseBadRequest("POST required")

    note_id = request.POST.get("note_id")
    if not note_id:
        return HttpResponseBadRequest("note_id required")

    color = (request.POST.get("color") or "").strip().lower()
    if color not in ALLOWED_COLOR_NAMES:
        return HttpResponseBadRequest("invalid color")

    note = get_object_or_404(Note, pk=note_id, user=request.user)
    note.color = color
    note.save()
    return redirect("note_list")


@login_required
def update_color_labels(request):
    """
    Labels (Bedeutung) für alle Farben eines Users speichern (POST).
    Erwartet Felder: label_<color> für jede erlaubte Farbe.
    """
    if request.method != "POST":
        return HttpResponseBadRequest("POST required")

    for color in ALLOWED_COLOR_NAMES:
        key = f"label_{color}"
        value = (request.POST.get(key) or "").strip()
        obj, _ = ColorLabel.objects.get_or_create(user=request.user, color=color)
        obj.label = value
        obj.save()

    return redirect("note_list")


def search(request):
    q = (request.GET.get("q") or "").strip()
    notes = Note.objects.none()
    if q:
        notes = Note.objects.filter(
            Q(title__icontains=q) | Q(content__icontains=q)
        ).order_by("-updated_at")
    return render(request, "./notes/search_results.html", {"q": q, "notes": notes})

def search_suggest(request):
    q = (request.GET.get("q") or "").strip()
    out = []
    if q:
        qs = (Note.objects
              .filter(Q(title__icontains=q) | Q(content__icontains=q))
              .order_by("-updated_at")[:8])
        for n in qs:
            # Ziel-URL für Klick auf Vorschlag:
            if hasattr(n, "get_absolute_url"):
                url = n.get_absolute_url()
            else:
                # Fallback: öffnet Suchseite mit dem aktuellen Query
                url = reverse("search") + f"?q={q}"
            snippet = (n.content or "").replace("\n", " ")
            if len(snippet) > 90:
                snippet = snippet[:90].rstrip() + "…"
            out.append({
                "id": n.pk,
                "title": n.title or "(ohne Titel)",
                "url": url,
                "snippet": snippet,
            })
    return JsonResponse({"results": out})