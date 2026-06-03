from django.db import models
from django.conf import settings
from django.utils.text import slugify
import uuid

User = settings.AUTH_USER_MODEL

class Message(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    text = models.TextField()
    writed_at = models.DateTimeField(auto_now_add=True)
    likes = models.ManyToManyField(User, related_name='liked_messages', blank=True)
    dizlikes = models.ManyToManyField(User, related_name='dizliked_messages', blank=True)
    slug = models.SlugField(unique=True, blank=True, null=True)
    is_delete = models.BooleanField(default=False)
    photo = models.ImageField(upload_to='mesage/', blank=True, null=True)

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(f"{self.text}-{uuid.uuid4().hex[:8]}")
        super().save(*args, **kwargs)

    def delete(self, *args, **kwargs):
        self.is_delete = True
        self.save()

    def __str__(self):
        return f'{self.user.username}:{self.text[:20]}'


class Direct(models.Model):
    sender = models.ForeignKey(User, on_delete=models.CASCADE, related_name='send_messages')
    receiner = models.ForeignKey(User, on_delete=models.CASCADE, related_name='received_messages')
    # blank=True — потому что можно отправить только фото или голос без текста
    text = models.TextField(blank=True, default='')
    created_at = models.DateTimeField(auto_now_add=True)
    is_readed = models.BooleanField(default=False)
    photo = models.ImageField(upload_to='direct/', blank=True, null=True)
    voice = models.FileField(upload_to='voice/', blank=True, null=True)

    def __str__(self):
        return f'{self.sender.username}:{self.receiner.username}'


class Call(models.Model):
    CALL_TYPE_CHOICES = [
        ('video', 'Video Call'),
        ('audio', 'Audio Call'),
    ]
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('accepted', 'Accepted'),
        ('rejected', 'Rejected'),
        ('ended', 'Ended'),
    ]
    
    caller = models.ForeignKey(User, on_delete=models.CASCADE, related_name='initiated_calls')
    receiver = models.ForeignKey(User, on_delete=models.CASCADE, related_name='received_calls')
    call_type = models.CharField(max_length=10, choices=CALL_TYPE_CHOICES, default='video')
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='pending')
    created_at = models.DateTimeField(auto_now_add=True)
    ended_at = models.DateTimeField(blank=True, null=True)

    def __str__(self):
        return f'{self.call_type} call: {self.caller.username} -> {self.receiver.username}'