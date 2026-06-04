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
        choices=ROLE_CHOICES,
        default='patient'
    )

    phone = models.CharField(
        max_length=20, unique=True, null=True, blank=True
    )
    age=models.PositiveIntegerField(null=True,blank=True)

    city = models.CharField(max_length=50, blank=True)

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
    

class Profile(models.Model):

    ROLE_CHOICES = (
        ('patient', 'Patient'),
        ('doctor', 'Doctor'),
        ('admin', 'Admin'),
    )

    user=models.OneToOneField(settings.AUTH_USER_MODEL,on_delete=models.CASCADE,related_name='profile')
    age=models.PositiveIntegerField(null=True,blank=True)
    role = models.CharField(max_length=20, choices=ROLE_CHOICES, default='patient')
    phone=models.CharField(max_length=14,blank=True)
    city = models.CharField(max_length=50, blank=True)
    photo=models.ImageField(upload_to='users/',blank=True,null=True)


    def __str__(self):
        return f'{self.user}:{self.phone}'

