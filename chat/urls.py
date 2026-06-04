from django.urls import path
from . import views

urlpatterns = [
    path('',views.chat_page,name='global_chat'),
    path('like/<int:pk>',views.like,name='like'),
    path('dizlike/<int:pk>',views.dizlike,name='dizlike'),
    path('profile/<str:username>/', views.profile_view, name='profile'),
    path('delete_message/<int:pk>',views.MessageDeleteView.as_view(),name='delete_message'),
    path('send_message/<int:pk>',views.send_message,name='send_message'),
    path('doctor_messages/',views.show_messages,name='show_messages'),
    path('delete_chat/<int:pk>',views.delete_chat,name='delete_chat'),
    path('video_call/<int:user_id>/', views.start_video_call, name='start_video_call'),
    path('call/<int:call_id>/', views.video_call, name='video_call'),
    path('call/<int:call_id>/reject/', views.reject_call, name='reject_call'),
]   