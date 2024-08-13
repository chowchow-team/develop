"""
URL configuration for backend project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/4.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/', include('accountapp.urls')),
    path('api/friend/', include('friendapp.urls')),
    path('api/chat/', include('chatapp.urls')),
    path('api/notification/', include('notificationapp.urls')),
    path('api/main/',include('mainapp.urls')),
    path('api/llm/', include('llmapp.urls'))
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
