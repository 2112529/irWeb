"""
URL configuration for irWeb project.

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
from django.urls import path
from App0 import views
# from App0.views import index
from App0 import account
from App0 import gptAPI

urlpatterns = [
    path("admin/", admin.site.urls),
    path('Main/', views.main),
    path('login/',account.login),
    path('logup/',account.logup),
    path('logout/',account.logout),
    path('search/',views.search),
    path('search_word/',views.search_word),
    path('user_information/', account.user_information),
    path('edit_info/',account.edit_user_info),
    path('gptAPI/',gptAPI.ask_question),
    path('search_wildcard/',views.wildcard_search),
    path('p_search/',views.p_search),
    
]
