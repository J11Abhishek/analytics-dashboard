from django.db import models
from django.contrib.auth.models import User


class Dataset(models.Model):
    owner = models.ForeignKey(User, on_delete=models.CASCADE, related_name="datasets")
    file = models.FileField(upload_to="uploads/%Y/%m/")
    original_filename = models.CharField(max_length=255)
    uploaded_at = models.DateTimeField(auto_now_add=True)
    row_count = models.PositiveIntegerField(default=0)
    column_count = models.PositiveIntegerField(default=0)
    cleaned_data = models.JSONField(null=True, blank=True)

    class Meta:
        ordering = ["-uploaded_at"]

    def __str__(self):
        return f"{self.original_filename} ({self.owner})"