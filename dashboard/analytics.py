import pandas as pd


def compute_kpis(df: pd.DataFrame) -> dict:
    return {
        "total_revenue": float(df["revenue"].sum()) if "revenue" in df else None,
        "avg_order_value": float(df["revenue"].mean()) if "revenue" in df else None,
        "top_product": df["product"].value_counts().idxmax() if "product" in df and len(df) else None,
        "row_count": len(df),
    }


def generate_insights(df: pd.DataFrame) -> list[str]:
    insights = []

    # Month-over-month revenue trend
    if "date" in df.columns and "revenue" in df.columns:
        d = df.dropna(subset=["date"]).copy()
        d["date"] = pd.to_datetime(d["date"])
        monthly = d.set_index("date").resample("ME")["revenue"].sum()
        if len(monthly) >= 2:
            last, prev = monthly.iloc[-1], monthly.iloc[-2]
            if prev:
                pct = (last - prev) / prev * 100
                direction = "up" if pct > 0 else "down"
                insights.append(f"Revenue is {direction} {abs(pct):.1f}% vs. the previous month.")

    # Top and bottom performing region
    if "region" in df.columns and "revenue" in df.columns:
        by_region = df.groupby("region")["revenue"].sum().sort_values(ascending=False)
        if len(by_region) > 1:
            top, bottom = by_region.index[0], by_region.index[-1]
            insights.append(f"{top} is the top-performing region by revenue.")
            gap = (by_region.iloc[0] - by_region.iloc[-1]) / by_region.iloc[0] * 100
            if gap > 30:
                insights.append(f"{bottom} lags {top} by {gap:.0f}% in revenue — worth investigating.")

    # Best-selling product
    if "product" in df.columns and len(df):
        top_product = df["product"].value_counts().idxmax()
        share = df["product"].value_counts(normalize=True).iloc[0] * 100
        insights.append(f"'{top_product}' accounts for {share:.0f}% of all orders.")

    # Outlier detection on revenue
    if "revenue" in df.columns and df["revenue"].std() > 0:
        mean, std = df["revenue"].mean(), df["revenue"].std()
        outliers = df[(df["revenue"] - mean).abs() > 3 * std]
        if len(outliers):
            insights.append(f"Found {len(outliers)} unusually large or small revenue entries — may be worth reviewing.")

    return insights[:6]