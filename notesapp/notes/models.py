from django.db import models
from django.contrib.auth.models import User

class Note(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    title = models.CharField(max_length=200)
    content = models.TextField()
    deadline = models.DateField(null=True, blank=True)
    color = models.CharField(max_length=20, default="yellow")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.title


class ColorLabel(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    color = models.CharField(max_length=20)  
    label = models.CharField(max_length=50, blank=True, default="")

    class Meta:
        unique_together = ("user", "color")

    def __str__(self):
        return f"{self.user} – {self.color}: {self.label}"
