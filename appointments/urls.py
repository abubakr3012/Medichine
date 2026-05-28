from django.urls import path
from . import views

urlpatterns = [
    path('appoinment/<int:pk>',views.create_appointment,name='create_appointment'),
    path('my_appointments/',views.show_appointment,name='appointments'),
    path('delete_appointment/<int:pk>/',views.delete_appointment,name='delete_appointment')
]   