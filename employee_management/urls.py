"""
URL configuration for employee_management project.

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

from employee.views import *

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', view_index, name='index'),
    path('registration', view_registration, name='registration'),
    path('emp_log', view_login, name='emp_log'),
    path('emp_home', view_homepage, name='emp_home'),
    path('profile', view_profile, name='profile'),
    path('logout', view_logout, name='logout'),
    path('experience', view_experience, name='experience'),
    path('remove_experience/', view_remove_experience, name='remove_experience'),
    path('education', view_education, name='education'),
    path('remove_education/', view_remove_education, name='remove_education'),
    path('password_change/', view_password_change, name='password_change'),
    path('delete_account/', view_delete_account, name='delete_account'),
]
