from django.db import models
from django.conf import settings

class Message(models.Model):
    user=models.ForeignKey(settings.AUTH_USER_MODEL,on_delete=models.CASCADE)
    text=models.TextField()
    writed_at=models.DateTimeField(auto_now_add=True)
    likes=models.IntegerField(default=0)

    def __str__(self):
        return f'{self.user.username}:{self.text[:20]}'