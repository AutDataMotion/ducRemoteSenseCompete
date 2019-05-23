"""RSCompete URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/2.1/topics/http/urls/
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
from django.urls import path
from RSCompeteAPI.views import *

urlpatterns = [
    path('admin/', admin.site.urls),
    path('competition', competitionList),
    path('user/login', login),
    path("user/info", users),
    path("user/register", register),
    path("test", test),
    path("user/logout", logout),
    path("theme/count", count),
    path("results", results),
    path("results/upload", results_upload),
    path("results/leaderboard", leaderboard),
    path("statistics/all", statistics_all),
    path("statistics/country", statistics_country),
    path("statistics/city", statistics_city),
    path("statistics/city/detail", statistics_detail),
]
