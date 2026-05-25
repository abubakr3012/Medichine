from django.urls import path
from . import views

urlpatterns = [
    path('',views.chat_page,name='global_chat'),
    path('like/<int:pk>',views.like,name='like'),
    path('dizlike/<int:pk>',views.dizlike,name='dizlike'),
    path('profile/<str:username>/', views.profile_view, name='profile'),
    path('delete_message/<int:pk>',views.delete_message,name='delete_message')
]   
