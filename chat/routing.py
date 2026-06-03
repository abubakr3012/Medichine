from django.urls import re_path

from . import consumers
from . import video_consumers
from . import notification_consumers

websocket_urlpatterns = [
    re_path(r"ws/chat/(?P<room_name>\w+)/$", consumers.ChatConsumer.as_asgi()),
    re_path(r"ws/call/(?P<call_id>\w+)/$", video_consumers.VideoCallConsumer.as_asgi()),
    re_path(r"ws/notifications/$", notification_consumers.NotificationConsumer.as_asgi()),
]