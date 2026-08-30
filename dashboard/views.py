import io
import pandas as pd
from django.contrib.auth.decorators import login_required
from django.shortcuts import render, get_object_or_404
from django.http import HttpResponse
from django.utils import timezone
from reportlab.lib.pagesizes import letter
from reportlab.lib import colors
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle
from reportlab.lib.styles import getSampleStyleSheet

from datasets.models import Dataset
from .analytics import compute_kpis, generate_insights


@login_required
def view_dashboard(request, dataset_id):
    dataset = get_object_or_404(Dataset, id=dataset_id, owner=request.user)
    df = pd.read_json(io.StringIO(dataset.cleaned_data), orient="records")

    kpis = compute_kpis(df)
    insights = generate_insights(df)

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
        "insights": insights,
        "chart_data": chart_data,
    })


@login_required
def export_pdf(request, dataset_id):
    dataset = get_object_or_404(Dataset, id=dataset_id, owner=request.user)
    df = pd.read_json(io.StringIO(dataset.cleaned_data), orient="records")

    kpis = compute_kpis(df)
    insights = generate_insights(df)

    buffer = io.BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=letter)
    styles = getSampleStyleSheet()
    elements = []

    elements.append(Paragraph(f"{dataset.original_filename} — Summary Report", styles["Title"]))
    elements.append(Paragraph(
        f"Generated {timezone.now().strftime('%b %d, %Y %H:%M')} · {dataset.row_count} rows",
        styles["Normal"]
    ))
    elements.append(Spacer(1, 20))

    kpi_table_data = [
        ["Metric", "Value"],
        ["Total Revenue", f"${kpis['total_revenue']:.0f}" if kpis["total_revenue"] is not None else "—"],
        ["Avg Order Value", f"${kpis['avg_order_value']:.2f}" if kpis["avg_order_value"] is not None else "—"],
        ["Top Product", kpis["top_product"] or "—"],
    ]
    kpi_table = Table(kpi_table_data, hAlign="LEFT")
    kpi_table.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#1f2937")),
        ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
        ("GRID", (0, 0), (-1, -1), 0.5, colors.grey),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 8),
        ("TOPPADDING", (0, 0), (-1, -1), 8),
    ]))
    elements.append(kpi_table)
    elements.append(Spacer(1, 20))

    elements.append(Paragraph("Key Insights", styles["Heading2"]))
    if insights:
        for insight in insights:
            elements.append(Paragraph(f"• {insight}", styles["Normal"]))
    else:
        elements.append(Paragraph("No notable insights for this dataset.", styles["Normal"]))

    doc.build(elements)
    buffer.seek(0)

    response = HttpResponse(buffer.read(), content_type="application/pdf")
    response["Content-Disposition"] = f'attachment; filename="{dataset.original_filename}_report.pdf"'
    return response


@login_required
def export_excel(request, dataset_id):
    dataset = get_object_or_404(Dataset, id=dataset_id, owner=request.user)
    df = pd.read_json(io.StringIO(dataset.cleaned_data), orient="records")

    kpis = compute_kpis(df)
    insights = generate_insights(df)

    summary_df = pd.DataFrame({
        "Metric": ["Total Revenue", "Avg Order Value", "Top Product", "Row Count"],
        "Value": [kpis["total_revenue"], kpis["avg_order_value"], kpis["top_product"], kpis["row_count"]],
    })
    insights_df = pd.DataFrame({"Insight": insights})

    buffer = io.BytesIO()
    with pd.ExcelWriter(buffer, engine="openpyxl") as writer:
        df.to_excel(writer, sheet_name="Cleaned Data", index=False)
        summary_df.to_excel(writer, sheet_name="Summary", index=False)
        insights_df.to_excel(writer, sheet_name="Insights", index=False)
    buffer.seek(0)

    response = HttpResponse(
        buffer.read(),
        content_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
    )
    response["Content-Disposition"] = f'attachment; filename="{dataset.original_filename}_report.xlsx"'
    return response