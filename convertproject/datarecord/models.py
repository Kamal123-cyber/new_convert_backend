from django.db import models
from django.contrib.auth import get_user_model

User = get_user_model()

class Record(models.Model):
    STATUS_CHOICES = (
        ('pending', 'Pending'),
        ('processing', 'Processing'),
        ('completed', 'Completed'),
        ('failed', 'Failed'),
    )

    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='records')
    original_file = models.FileField(upload_to='original_files/')
    original_format = models.CharField(max_length=10)
    original_size = models.PositiveIntegerField(help_text="File size in bytes")
    converted_file = models.FileField(upload_to='converted_files/', null=True, blank=True)
    converted_format = models.CharField(max_length=10)
    converted_size = models.PositiveIntegerField(null=True, blank=True, help_text="File size in bytes")
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.user.username}'s conversion: {self.original_format} to {self.converted_format} ({self.status})"

    class Meta:
        ordering = ['-created_at']