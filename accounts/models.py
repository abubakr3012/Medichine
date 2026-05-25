from django.db import models
from django.contrib.auth.models import AbstractUser
from django.conf import settings

class User(AbstractUser):

    ROLE_CHOICES = (
        ('patient', 'Patient'),
        ('doctor', 'Doctor'),
        ('admin', 'Admin'),
    )

    role = models.CharField(
        max_length=20,
        choices=ROLE_CHOICES
    )

    phone = models.CharField(
        max_length=20,
        unique=True
    )

    def __str__(self):
        return self.username

class EmailConfirm(models.Model):
    user=models.OneToOneField(settings.AUTH_USER_MODEL,on_delete=models.CASCADE)
    code=models.CharField(max_length=5)

    def __str__(self):
        return self.user
    
class ResetPassword(models.Model):
    user=models.ForeignKey(settings.AUTH_USER_MODEL,on_delete=models.CASCADE)
    code=models.CharField(max_length=5)
    created_at=models.DateField(auto_now_add=True)

    def __str__(self):
        return self.user.username