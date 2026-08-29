from django.urls import path
from . import views

app_name = "datasets"

urlpatterns = [
    path("upload/", views.upload_dataset, name="upload"),
    path("<int:dataset_id>/", views.dataset_detail, name="detail"),
    path("", views.dataset_list, name="list"),
]