from django.db import models
from django.conf import settings

class DoctorProfile(models.Model):
    user=models.OneToOneField(settings.AUTH_USER_MODEL,on_delete=models.CASCADE)
    speciality=models.CharField(max_length=20)
    city=models.CharField(max_length=50)
    clinic=models.CharField(max_length=100)
    bio=models.TextField(blank=True)
    experience=models.PositiveIntegerField(default=0)
    photo=models.ImageField(upload_to='doctors/',null=True,blank=True)

    def __str__(self):
        return f'{self.user.username}:{self.speciality}'
