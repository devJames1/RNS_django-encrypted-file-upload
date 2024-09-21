from django.urls import path, re_path
from . import views

urlpatterns = [
    path("upload/", views.upload_file, name="upload_file"),
    re_path(r'^download/(?P<s3_key>.+)/$', views.download_file, name='download_file'), # modify URL pattern to account for slashes in the s3_key
]
