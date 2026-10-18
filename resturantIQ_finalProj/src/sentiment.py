import pandas as pd
from vaderSentiment.vaderSentiment import SentimentIntensityAnalyzer

_analyzer = SentimentIntensityAnalyzer()

def classify_sentiment(text: str) -> tuple[str, float]:
    score = _analyzer.polarity_scores(str(text))["compound"]
    label = "Positive" if score >= 0.05 else "Negative" if score <= -0.05 else "Neutral"
    return label, score

def add_sentiment(df: pd.DataFrame) -> pd.DataFrame:
    out = df.copy(); values = out["review_text"].map(classify_sentiment)
    out["sentiment"] = values.map(lambda x: x[0]); out["sentiment_score"] = values.map(lambda x: x[1]); return out
