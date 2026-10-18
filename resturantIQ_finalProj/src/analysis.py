import pandas as pd

def kpis(df):
    total = len(df); pos = (df.sentiment == "Positive").mean() * 100 if total else 0; neg = (df.sentiment == "Negative").mean() * 100 if total else 0
    return {"total": total, "avg_rating": df.rating.mean() if total else 0, "positive_pct": pos, "negative_pct": neg}

def branch_summary(df):
    if df.empty: return pd.DataFrame(columns=["branch", "reviews", "avg_rating", "negative_pct"])
    return df.groupby("branch").agg(reviews=("review_id", "count"), avg_rating=("rating", "mean"), negative_pct=("sentiment", lambda s: (s == "Negative").mean() * 100)).reset_index().sort_values("avg_rating", ascending=False)
