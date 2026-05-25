from django.db import models
from django.conf import settings

User=settings.AUTH_USER_MODEL

class Appointment(models.Model):
    patient = models.ForeignKey(User,on_delete=models.CASCADE,related_name='appointments')
    doctor=models.ForeignKey('doctors.DoctorProfile',on_delete=models.CASCADE,related_name='appointments')
    date=models.DateTimeField(auto_now_add=True)

    STATUS = (
        ('pending', 'Ожидание'),
        ('approved', 'Подтверждена'),
        ('cancelled', 'Отменена'),
    )

    status=models.CharField(max_length=30,choices=STATUS,default='pending')
    created_at=models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f'{self.patient.username}:{self.doctor.username}'