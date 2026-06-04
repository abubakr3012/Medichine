import uuid
from django.db import models
from django.conf import settings
from django.utils.text import slugify


class Appointment(models.Model):
    patient = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='appointments')
    doctor = models.ForeignKey('doctors.DoctorProfile', on_delete=models.CASCADE, related_name='appointments')
    date = models.DateTimeField()

    slug = models.SlugField(unique=True, blank=True, null=True)

    is_deleted = models.BooleanField(default=False)

    STATUS = (
        ('pending', 'Ожидание'),
        ('approved', 'Подтверждена'),
        ('cancelled', 'Отменена'),
    )

    status = models.CharField(max_length=30, choices=STATUS, default='pending')
    created_at = models.DateTimeField(auto_now_add=True)
    celery_task_ids = models.JSONField(default=list, blank=True)
    sms_reminder_sent = models.BooleanField(default=False)

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(f"{self.patient_id}-{uuid.uuid4().hex[:8]}")
        super().save(*args, **kwargs)

    def delete(self, *args, **kwargs):
        self.is_deleted = True
        self.save()

    def __str__(self):
        return f'{self.patient.username}:{self.doctor.user.username}'