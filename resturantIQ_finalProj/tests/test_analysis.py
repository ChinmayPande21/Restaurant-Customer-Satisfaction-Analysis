import pandas as pd
from src.analysis import kpis
from src.complaint_engine import detect_complaints
from src.data_loader import validate_and_normalize
from src.sentiment import classify_sentiment

def frame():
    return pd.DataFrame({"review_id":["1","2","3"],"rating":[5,1,2],"review_text":["Amazing friendly service", "We waited too long and food was cold", "Slow service and wrong order"],"branch":["A","A","B"],"cuisine":["Thai"]*3,"sentiment":["Positive","Negative","Negative"]})

def test_validation_requires_columns():
    try: validate_and_normalize(pd.DataFrame({"rating":[4]})); assert False
    except ValueError as e: assert "review_text" in str(e)

def test_kpis():
    result = kpis(frame()); assert result["total"] == 3; assert round(result["negative_pct"], 1) == 66.7

def test_sentiment_classification():
    assert classify_sentiment("Excellent, delicious and friendly")[0] == "Positive"; assert classify_sentiment("Awful, slow and cold")[0] == "Negative"

def test_complaint_engine_uses_evidence():
    issues = detect_complaints(frame(), min_mentions=1); assert "Slow service" in issues.theme.tolist(); assert issues.iloc[0].evidence
