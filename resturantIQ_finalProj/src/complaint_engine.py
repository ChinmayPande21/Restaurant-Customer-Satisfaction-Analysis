import re
import pandas as pd

THEMES = {
    "Slow service": {"patterns": [r"wait", r"slow", r"long", r"delay"], "action": "Review peak-hour staffing and track order preparation time."},
    "Staff behavior": {"patterns": [r"staff", r"dismissive", r"rude", r"service"], "action": "Review service coaching, greeting standards, and complaint handling."},
    "Food quality": {"patterns": [r"cold", r"food", r"flavor", r"quality", r"ingredient"], "action": "Audit preparation consistency, holding times, and ingredient quality."},
    "Cleanliness & hygiene": {"patterns": [r"clean", r"hygiene", r"table", r"washroom"], "action": "Increase cleaning checks and log inspections by shift."},
    "Pricing & value": {"patterns": [r"price", r"value", r"portion", r"worth", r"expensive"], "action": "Compare portion size and pricing against local alternatives."},
    "Incorrect order": {"patterns": [r"incorrect", r"wrong", r"order", r"accurate"], "action": "Add order read-back confirmation and pickup accuracy checks."},
}

def detect_complaints(df: pd.DataFrame, min_mentions: int = 2) -> pd.DataFrame:
    rows = []
    for theme, cfg in THEMES.items():
        mask = df.review_text.str.lower().apply(lambda text: any(re.search(p, text) for p in cfg["patterns"]))
        hits = df.loc[mask].copy(); mentions = len(hits)
        if mentions < min_mentions: continue
        neg_pct = (hits.sentiment == "Negative").mean() * 100 if mentions else 0
        score = mentions * (neg_pct / 100)
        priority = "High" if mentions >= max(8, len(df) * .08) and neg_pct >= 55 else "Medium" if mentions >= 3 and neg_pct >= 35 else "Monitor"
        reason = f"{mentions} keyword-matched review(s); {neg_pct:.0f}% are classified negative."
        rows.append({"theme": theme, "mentions": mentions, "negative_pct": neg_pct, "priority": priority, "reason": reason, "action": cfg["action"], "branches": ", ".join(hits.branch.value_counts().head(3).index), "evidence": hits.review_text.head(3).tolist()})
    return pd.DataFrame(rows).sort_values(["priority", "mentions"], key=lambda s: s.map({"High": 0, "Medium": 1, "Monitor": 2}).fillna(9) if s.name == "priority" else -s, ignore_index=True) if rows else pd.DataFrame(columns=["theme", "mentions", "negative_pct", "priority", "reason", "action", "branches", "evidence"])
