from django.urls import path
from . import views

urlpatterns = [
    path('doctors/',views.show_all_doctors,name='doctors_list')
]
