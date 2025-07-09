from django.urls import path
from . import views

urlpatterns = [
    # ... your existing urls ...
    
    # Add the new URL for downloading the result
    path('session/<int:pk>/download/', views.download_allocation_result, name='download_allocation_result'),
]