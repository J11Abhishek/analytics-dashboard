from django.urls import path
from . import views

app_name = "dashboard"

urlpatterns = [
    path("<int:dataset_id>/", views.view_dashboard, name="view"),
]