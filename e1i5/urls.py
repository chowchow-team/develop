from django.urls import path
from . import views

urlpatterns = [
    path('upload/', views.upload_video, name='upload_video'),
    path('videos/latest/', views.get_latest_videos, name='get_latest_video'),
]
