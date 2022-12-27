"""csb_project URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/4.1/topics/http/urls/
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
import sqlite3
from django.urls import path
from .views import View
view=View()

urlpatterns = [
    path('admin/', admin.site.urls),
    path("", view.home),
    path("register", view.register),
    path("login", view.login),
    path("app",view.app),
    path("logout/", view.logout),
    path("send_message",view.send_message),
    path("app/?<str:keyword>",view.send_message)
]
