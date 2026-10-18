import io
from pathlib import Path
import pandas as pd
import plotly.express as px
import streamlit as st

from src.analysis import branch_summary, kpis
from src.complaint_engine import detect_complaints
from src.data_loader import load_csv_bytes, validate_and_normalize
from src.generate_data import generate_sample
from src.sentiment import add_sentiment

st.set_page_config(page_title="RestaurantIQ", page_icon="RI", layout="wide", initial_sidebar_state="expanded")
st.markdown("""<style>
:root { --ink:#17324d; --teal:#0f766e; --mint:#dff5ef; --amber:#f59e0b; }
.block-container{padding-top:2rem;max-width:1400px}.hero{padding:1.4rem 1.6rem;border-radius:18px;background:linear-gradient(120deg,#17324d,#0f766e);color:white;margin-bottom:1.2rem}.hero h1{font-size:2.3rem;margin:0}.hero p{opacity:.86;margin:.35rem 0 0}.kpi{padding:1rem 1.1rem;border:1px solid #dbe7ee;border-radius:14px;background:#fff}.kpi small{color:#60758a}.kpi strong{display:block;color:#17324d;font-size:1.65rem;margin-top:.3rem}.section{color:#17324d;margin-top:1rem}
</style>""", unsafe_allow_html=True)

@st.cache_data
def sample_data():
    path = Path("data/sample_reviews.csv")
    return generate_sample(path) if not path.exists() else pd.read_csv(path)

if "data" not in st.session_state: st.session_state.data = sample_data()
with st.sidebar:
    st.markdown("## RestaurantIQ")
    st.caption("Evidence-led customer experience intelligence")
    uploaded = st.file_uploader("Upload authorized CSV", type="csv")
    if uploaded:
        try:
            st.session_state.data, warns = load_csv_bytes(uploaded.getvalue())
            for w in warns: st.warning(w)
            st.success(f"Loaded {len(st.session_state.data):,} rows")
        except ValueError as e: st.error(str(e))
    if st.button("Restore sample dataset", use_container_width=True): st.session_state.data = sample_data(); st.rerun()
    st.divider()
    page = st.radio("Navigate", ["Overview", "Sentiment Analysis", "Branch Comparison", "Customer Preferences", "Complaint-to-Action", "Data Explorer"])
    st.divider(); st.caption("Sample dataset is synthetic demo data. Keyword matches are signals, not verified complaints.")

df, warnings = validate_and_normalize(st.session_state.data)
df = add_sentiment(df)
with st.sidebar:
    branches = st.multiselect("Branch", sorted(df.branch.unique()), default=sorted(df.branch.unique()))
    cuisines = st.multiselect("Cuisine", sorted(df.cuisine.unique()), default=sorted(df.cuisine.unique()))
    rating_range = st.slider("Rating range", 1.0, 5.0, (1.0, 5.0), .5)
    sentiments = st.multiselect("Sentiment", ["Positive", "Neutral", "Negative"], default=["Positive", "Neutral", "Negative"])
    if df.date.notna().any():
        dates = pd.to_datetime(df.date, errors="coerce").dropna()
        date_range = st.date_input("Date range", (dates.min().date(), dates.max().date()))
    else: date_range = None

filtered = df[df.branch.isin(branches) & df.cuisine.isin(cuisines) & df.rating.between(*rating_range) & df.sentiment.isin(sentiments)].copy()
if date_range and len(date_range) == 2 and filtered.date.notna().any(): filtered = filtered[filtered.date.between(pd.Timestamp(date_range[0]), pd.Timestamp(date_range[1]) + pd.Timedelta(days=1))]

st.markdown('<div class="hero"><h1>RestaurantIQ</h1><p>Turn customer voice into operational focus — with transparent evidence.</p></div>', unsafe_allow_html=True)
st.caption(f"Showing {len(filtered):,} of {len(df):,} reviews · Filters apply across every page")

def kpi_row(data):
    m = kpis(data); cols = st.columns(4)
    vals = [("Reviews analyzed", f"{m['total']:,}"), ("Average rating", f"{m['avg_rating']:.2f} / 5"), ("Positive reviews", f"{m['positive_pct']:.1f}%"), ("Negative reviews", f"{m['negative_pct']:.1f}%")]
    for c, (label, value) in zip(cols, vals): c.markdown(f'<div class="kpi"><small>{label}</small><strong>{value}</strong></div>', unsafe_allow_html=True)

def charts(data):
    left, right = st.columns(2)
    with left:
        st.plotly_chart(px.histogram(data, x="rating", color_discrete_sequence=["#0f766e"], nbins=5, title="Star-rating distribution"), use_container_width=True)
    with right:
        st.plotly_chart(px.pie(data, names="sentiment", hole=.55, color="sentiment", color_discrete_map={"Positive":"#0f766e","Neutral":"#94a3b8","Negative":"#ef6c5b"}, title="Sentiment mix"), use_container_width=True)

def complaint_cards(data, limit=3):
    issues = detect_complaints(data)
    if issues.empty: st.info("Not enough matching evidence in the current selection."); return issues
    for _, row in issues.head(limit).iterrows():
        icon = "HIGH" if row.priority == "High" else row.priority.upper()
        with st.container(border=True):
            st.markdown(f"**{row.theme}**  ·  `{icon}`")
            st.write(f"{row.mentions} matching reviews · {row.negative_pct:.0f}% negative · Branches: {row.branches}")
            st.caption(f"Why: {row.reason} Action: {row.action}")
    return issues

if page == "Overview":
    st.subheader("Executive overview"); kpi_row(filtered); charts(filtered)
    st.subheader("Top complaint signals"); complaint_cards(filtered)
    st.subheader("Branch performance"); st.dataframe(branch_summary(filtered).style.format({"avg_rating":"{:.2f}","negative_pct":"{:.1f}%"}), use_container_width=True, hide_index=True)
elif page == "Sentiment Analysis":
    st.subheader("Sentiment analysis"); kpi_row(filtered); charts(filtered)
    a, b = st.columns(2)
    with a: st.plotly_chart(px.box(filtered, x="rating", y="sentiment_score", color="sentiment", title="Sentiment score by rating"), use_container_width=True)
    with b:
        if filtered.date.notna().any():
            trend = filtered.dropna(subset=["date"]).assign(month=lambda x: x.date.dt.to_period("M").astype(str)).groupby(["month","sentiment"]).size().reset_index(name="reviews")
            st.plotly_chart(px.line(trend, x="month", y="reviews", color="sentiment", markers=True, title="Sentiment trend"), use_container_width=True)
    st.dataframe(filtered[["review_id","date","branch","rating","sentiment","sentiment_score","review_text"]].sort_values("date", ascending=False), use_container_width=True, hide_index=True)
elif page == "Branch Comparison":
    st.subheader("Branch comparison"); summary = branch_summary(filtered)
    if summary.empty: st.info("No data for these filters.")
    else:
        a,b=st.columns(2); a.plotly_chart(px.bar(summary, x="branch", y="reviews", color="reviews", title="Review volume"), use_container_width=True); b.plotly_chart(px.bar(summary, x="branch", y="avg_rating", color="avg_rating", title="Average rating", range_y=[0,5]), use_container_width=True)
        st.dataframe(summary.style.format({"avg_rating":"{:.2f}","negative_pct":"{:.1f}%"}), use_container_width=True, hide_index=True)
        st.info("Interpret branch results with sample size in mind: a small branch can have a volatile percentage.")
elif page == "Customer Preferences":
    st.subheader("Customer preferences"); a,b=st.columns(2); a.plotly_chart(px.bar(filtered.cuisine.value_counts().rename_axis("cuisine").reset_index(name="reviews"), x="cuisine", y="reviews", title="Most reviewed cuisines"), use_container_width=True); b.plotly_chart(px.pie(filtered, names="dining_type", title="Dining type"), use_container_width=True)
    numeric = [c for c in ["food_quality","service_rating","cleanliness_rating","price_rating"] if c in filtered]
    if numeric: st.plotly_chart(px.box(filtered.melt(id_vars="cuisine", value_vars=numeric), x="variable", y="value", color="variable", title="Experience ratings"), use_container_width=True)
    st.dataframe(filtered.groupby("cuisine").agg(reviews=("review_id","count"), avg_rating=("rating","mean")).reset_index().style.format({"avg_rating":"{:.2f}"}), use_container_width=True, hide_index=True)
elif page == "Complaint-to-Action":
    st.subheader("Complaint-to-Action Engine"); st.write("Transparent keyword signals are paired with sentiment, branches, evidence excerpts, and an operational next step.")
    issues = detect_complaints(filtered)
    if issues.empty: st.info("Insufficient evidence: choose broader filters or add more reviews.")
    for _, row in issues.iterrows():
        with st.expander(f"{row.theme} · {row.priority} priority · {row.mentions} mentions"):
            st.write(f"**Negative-feedback rate:** {row.negative_pct:.1f}%  ·  **Branches:** {row.branches}")
            st.write(f"**Why this priority:** {row.reason}")
            st.write(f"**Recommended action:** {row.action}")
            st.markdown("**Supporting excerpts**")
            for excerpt in row.evidence: st.info(f'“{excerpt}”')
    st.caption("Limitation: keyword matching can miss paraphrases and can match a word without proving a complaint. Validate signals with operational data and human review.")
elif page == "Data Explorer":
    st.subheader("Data explorer"); query = st.text_input("Search review text or branch")
    view = filtered[filtered.review_text.str.contains(query, case=False, na=False) | filtered.branch.str.contains(query, case=False, na=False)] if query else filtered
    st.write(f"Displaying {len(view):,} records")
    st.dataframe(view, use_container_width=True, hide_index=True)
    st.download_button("Download filtered CSV", view.to_csv(index=False).encode("utf-8"), "restaurantiq_filtered_reviews.csv", "text/csv")
