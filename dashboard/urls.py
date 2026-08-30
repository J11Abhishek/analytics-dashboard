from django.urls import path
from . import views

app_name = "dashboard"

urlpatterns = [
    path("<int:dataset_id>/", views.view_dashboard, name="view"),
    path("<int:dataset_id>/export/pdf/", views.export_pdf, name="export_pdf"),
    path("<int:dataset_id>/export/excel/", views.export_excel, name="export_excel"),
]