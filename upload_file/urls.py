from django.urls import path
from .views import file_upload  # Ensure this is correct

urlpatterns = [
    path('', file_upload, name='file_upload'),  # URL pattern for the file upload view
]
