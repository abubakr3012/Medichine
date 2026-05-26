from django.contrib import admin
from .models import Message,Direct

admin.site.register([Message,Direct])