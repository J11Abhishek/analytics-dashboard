import pandas as pd


def compute_kpis(df: pd.DataFrame) -> dict:
    return {
        "total_revenue": float(df["revenue"].sum()) if "revenue" in df else None,
        "avg_order_value": float(df["revenue"].mean()) if "revenue" in df else None,
        "top_product": df["product"].value_counts().idxmax() if "product" in df and len(df) else None,
        "row_count": len(df),
    }