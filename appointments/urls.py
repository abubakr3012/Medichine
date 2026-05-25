from django.urls import path
from . import views

urlpatterns = [
    path('appoinment/<int:pk>',views.create_appointment,name='create_appointment'),
]
