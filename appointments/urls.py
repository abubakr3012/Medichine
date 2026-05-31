from django.urls import path
from . import views

urlpatterns = [
    path('appoinment/<int:pk>',views.AppointmentCreateView.as_view(),name='create_appointment'),
    path('my_appointments',views.AppointmentListView.as_view(),name='appointments'),
    path('delete_appointment/<int:pk>/',views.AppointmentDeleteView.as_view(),name='delete_appointment'),
    path('update_appointment/<int:pk>/',views.AppointmentUpdateView.as_view(),name='update_appointment'),

]   