from django.urls import path
from . import views

urlpatterns = [
    path('',views.register,name='register'),
    path('login/',views.login_user,name='login'),
    path('logout/',views.logout_user,name='logout'),
    path('confirm/',views.confirm_email,name='confirm'),
    path('forget_password',views.forget_password,name='forget_password'),
    path('reset_confirm',views.reset_confirm,name='reset_confirm'),
    path("dashboard/",views.redirect_dashboard,name="redirect_dashboard"),    
    path('dashboard/',    views.redirect_dashboard,name='redirect_dashboard'),
    path('patient/dashboard/',views.patient_dashboard,name='patient_dashboard'),
    path('doctor/dashboard/',views.doctor_dashboard,name='doctor_dashboard'),
    path('admin/dashboard/',views.admin_dashboard,name='admin_dashboard'),
    path("my_profile/",views.profile,name='my_profile'),
    path('update_profile/<int:pk>',views.update_profile,name='update_profile')
]
