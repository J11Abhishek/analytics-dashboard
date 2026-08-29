import io
import pandas as pd
from django.contrib.auth.decorators import login_required
from django.shortcuts import render, get_object_or_404

from datasets.models import Dataset
from .analytics import compute_kpis


@login_required
def view_dashboard(request, dataset_id):
    dataset = get_object_or_404(Dataset, id=dataset_id, owner=request.user)
    df = pd.read_json(io.StringIO(dataset.cleaned_data), orient="records")

    kpis = compute_kpis(df)

    chart_data = {
        "labels": df["product"].value_counts().index.tolist() if "product" in df else [],
        "values": df["product"].value_counts().values.tolist() if "product" in df else [],
    }

    if "date" in df.columns and "revenue" in df.columns:
        d = df.dropna(subset=["date"])
        d["date"] = pd.to_datetime(d["date"])
        monthly = d.set_index("date").resample("ME")["revenue"].sum()
        chart_data["revenue_labels"] = [dt.strftime("%b %Y") for dt in monthly.index]
        chart_data["revenue_values"] = monthly.values.tolist()

    return render(request, "dashboard/view.html", {
        "dataset": dataset,
        "kpis": kpis,
        "chart_data": chart_data,
    })