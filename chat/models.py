from django.db import models
from django.conf import settings

User = settings.AUTH_USER_MODEL

class Message(models.Model):
    user=models.ForeignKey(User,on_delete=models.CASCADE)
    text=models.TextField()
    writed_at=models.DateTimeField(auto_now_add=True)
    likes=models.ManyToManyField(User,related_name='liked_messages',blank=True)
    dizlikes=models.ManyToManyField(User,related_name='dizliked_messages',blank=True)

    def __str__(self):
        return f'{self.user.username}:{self.text[:20]}'
    
class Direct(models.Model):
    sender=models.ForeignKey(User,on_delete=models.CASCADE,related_name='send_messages')
    receiner=models.ForeignKey(User,on_delete=models.CASCADE,related_name='received_messages')
    text=models.TextField()
    created_at=models.DateTimeField(auto_now_add=True)
    is_readed=models.BooleanField(default=False)

    def __str__(self):
        return f'{self.sender.username}:{self.receiner.username}'
    