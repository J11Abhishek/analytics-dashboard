import pandas as pd
from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect, get_object_or_404

from .models import Dataset, CleaningLog
from .forms import DatasetUploadForm
from .cleaning import clean_dataframe


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

            cleaned_df, log_entries = clean_dataframe(df)

            dataset = Dataset.objects.create(
                owner=request.user,
                file=uploaded_file,
                original_filename=uploaded_file.name,
                row_count=len(cleaned_df),
                column_count=len(cleaned_df.columns),
                cleaned_data=cleaned_df.to_json(orient="records", date_format="iso"),
            )

            CleaningLog.objects.bulk_create(
                [CleaningLog(dataset=dataset, **entry) for entry in log_entries]
            )

            return redirect("datasets:list")
    else:
        form = DatasetUploadForm()

    return render(request, "datasets/upload.html", {"form": form})


@login_required
def dataset_list(request):
    datasets = Dataset.objects.filter(owner=request.user)
    return render(request, "datasets/list.html", {"datasets": datasets})


@login_required
def dataset_detail(request, dataset_id):
    dataset = get_object_or_404(Dataset, id=dataset_id, owner=request.user)
    logs = dataset.cleaning_logs.all()
    return render(request, "datasets/detail.html", {"dataset": dataset, "logs": logs})

