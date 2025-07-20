"""PMS URL Configuration

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
from django.urls import path, include
from django.views.generic import RedirectView

from apps.ajax_apis import get_faculty_according_to_level, get_semester_according_to_level
from apps.student.views import enter_priority_in_bulk
from apps.system.views import display_report
from apps.course.views import download_allocation_result

urlpatterns = [
    path('', RedirectView.as_view(url='login/')),
    path('login/', admin.site.urls),
    path('report/', display_report, name='display_result'),
    path('enter-priorities/', enter_priority_in_bulk, name='enter_priorities'),
    path('download-allocation/<int:session_id>/', download_allocation_result, name='download_allocation_result'),
    
    # Include course URLs for Excel downloads
    path('course/', include('apps.course.urls')),
]

urlpatterns += [
    path('ajax/get-faculty-according-to-level/', get_faculty_according_to_level, name='get-faculty-according-to-level'),
    path('ajax/get-semester-according-to-level/', get_semester_according_to_level, name='get-semester-according-to-level'),

]