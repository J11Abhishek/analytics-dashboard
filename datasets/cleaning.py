import pandas as pd


def clean_dataframe(df: pd.DataFrame) -> tuple[pd.DataFrame, list[dict]]:
    """Clean a raw DataFrame and return (cleaned_df, log_entries)."""
    log = []

    # Strip whitespace from string columns
    str_cols = df.select_dtypes(include="object").columns
    df[str_cols] = df[str_cols].apply(lambda col: col.str.strip())

    # Drop exact duplicate rows
    before = len(df)
    df = df.drop_duplicates()
    removed = before - len(df)
    if removed:
        log.append({"action": "Removed duplicates", "detail": f"{removed} rows removed"})

    # Fill missing numeric values with 0, log per column
    numeric_cols = df.select_dtypes(include="number").columns
    for col in numeric_cols:
        missing = df[col].isna().sum()
        if missing:
            df[col] = df[col].fillna(0)
            log.append({"action": f"Filled missing values in '{col}'", "detail": f"{missing} values set to 0"})

    # Attempt to parse any column that looks like a date
    for col in df.columns:
        if "date" in col.lower():
            df[col] = pd.to_datetime(df[col], errors="coerce")

    return df, log

