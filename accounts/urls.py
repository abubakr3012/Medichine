from django.urls import path
from . import views

urlpatterns = [
    path('',views.register,name='register'),
    path('login/',views.login_user,name='login'),
    path('logout/',views.logout_user,name='logout'),
    path('confirm/',views.confirm_email,name='confirm'),
    path('forget_password',views.forget_password,name='forget_password'),
    path('reset_confirm',views.reset_confirm,name='reset_confirm'),
]
