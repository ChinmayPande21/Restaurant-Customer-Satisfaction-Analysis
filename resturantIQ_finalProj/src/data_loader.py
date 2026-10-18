from io import BytesIO
import pandas as pd

REQUIRED = {"rating", "review_text"}
OPTIONAL = ["review_id", "date", "branch", "cuisine", "food_quality", "service_rating", "cleanliness_rating", "price_rating", "dining_type"]

def validate_and_normalize(data: pd.DataFrame) -> tuple[pd.DataFrame, list[str]]:
    if data is None or data.empty: raise ValueError("The CSV is empty.")
    df = data.copy(); df.columns = [str(c).strip().lower() for c in df.columns]
    missing = REQUIRED - set(df.columns)
    if missing: raise ValueError(f"Missing required column(s): {', '.join(sorted(missing))}")
    warnings = []
    df["rating"] = pd.to_numeric(df["rating"], errors="coerce")
    bad = df["rating"].isna() | ~df["rating"].between(1, 5)
    if bad.any(): warnings.append(f"Removed {int(bad.sum())} rows with invalid ratings (expected 1–5)."); df = df.loc[~bad].copy()
    df["review_text"] = df["review_text"].fillna("").astype(str).str.strip()
    empty = df["review_text"].eq("")
    if empty.any(): warnings.append(f"Removed {int(empty.sum())} rows with empty review text."); df = df.loc[~empty].copy()
    defaults = {"review_id": [f"UPL{i:04d}" for i in range(len(df))], "branch": "Unknown", "cuisine": "Unknown", "dining_type": "Unknown"}
    for col, default in defaults.items():
        if col not in df: df[col] = default
        df[col] = df[col].fillna(default if isinstance(default, str) else "Unknown")
    if "date" in df: df["date"] = pd.to_datetime(df["date"], errors="coerce")
    else: df["date"] = pd.NaT
    for col in ["food_quality", "service_rating", "cleanliness_rating", "price_rating"]:
        if col in df: df[col] = pd.to_numeric(df[col], errors="coerce")
    return df.reset_index(drop=True), warnings

def load_csv_bytes(file_bytes: bytes) -> tuple[pd.DataFrame, list[str]]:
    return validate_and_normalize(pd.read_csv(BytesIO(file_bytes)))
