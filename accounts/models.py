from django.db import models
from django.contrib.auth.models import User

class EmailConfirm(models.Model):
    user=models.OneToOneField(User,on_delete=models.CASCADE)
    code=models.CharField(max_length=5)

    def __str__(self):
        return self.user
    
class ResetPassword(models.Model):
    user=models.OneToOneField(User,on_delete=models.CASCADE)
    code=models.CharField(max_length=5)
    created_at=models.DateField(auto_now_add=True)