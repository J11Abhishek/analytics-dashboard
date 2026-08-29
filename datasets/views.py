import pandas as pd
from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect

from .models import Dataset
from .forms import DatasetUploadForm


@login_required
def upload_dataset(request):
    if request.method == "POST":
        form = DatasetUploadForm(request.POST, request.FILES)
        if form.is_valid():
            uploaded_file = request.FILES["file"]

            if uploaded_file.name.endswith(".csv"):
                df = pd.read_csv(uploaded_file)
            else:
                df = pd.read_excel(uploaded_file)

            dataset = Dataset.objects.create(
                owner=request.user,
                file=uploaded_file,
                original_filename=uploaded_file.name,
                row_count=len(df),
                column_count=len(df.columns),
                cleaned_data=df.to_json(orient="records", date_format="iso"),
            )

            return redirect("datasets:list")
    else:
        form = DatasetUploadForm()

    return render(request, "datasets/upload.html", {"form": form})


@login_required
def dataset_list(request):
    datasets = Dataset.objects.filter(owner=request.user)
    return render(request, "datasets/list.html", {"datasets": datasets})