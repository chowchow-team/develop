from channels.routing import ProtocolTypeRouter, URLRouter
from django.urls import path
from chatapp import consumers

websocket_urlpatterns = [
    path('ws/chat/random/', consumers.ChatConsumer.as_asgi()),
    path('ws/chat/dm/', consumers.ChatConsumer.as_asgi()),
    path('ws/count-online/', consumers.CountConsumer.as_asgi()),
]

application = ProtocolTypeRouter({
    'websocket': URLRouter(websocket_urlpatterns)
})
