from django.contrib import admin
from .models import *

admin.site.register([EmailConfirm,ResetPassword,Profile,User])