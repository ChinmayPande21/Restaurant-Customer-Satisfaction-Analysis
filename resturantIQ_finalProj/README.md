# RestaurantIQ

RestaurantIQ is a Python + Streamlit customer-experience intelligence dashboard. Its signature feature, the **Complaint-to-Action Engine**, combines transparent keyword signals with VADER sentiment, branch context, real review excerpts, priority rules, and practical operational actions.

## Features
- Reproducible synthetic demo data (500 rows) and CSV upload.
- Consistent branch, cuisine, rating, sentiment, and date filters.
- Overview, sentiment, branch comparison, preferences, complaint engine, and data explorer pages.
- Plotly charts, filtered CSV export, validation messages, and automated tests.

## Run on Windows PowerShell
```powershell
py -m venv .venv
.\\.venv\\Scripts\\Activate.ps1
pip install -r requirements.txt
python -m src.generate_data
streamlit run app.py
```
If activation is blocked, run `.venv\\Scripts\\python.exe -m pip install -r requirements.txt` and `.venv\\Scripts\\python.exe -m streamlit run app.py`.

Run tests with `python -m pytest`.

## CSV format
Required: `rating`, `review_text`. Optional: `review_id`, `date`, `branch`, `cuisine`, `food_quality`, `service_rating`, `cleanliness_rating`, `price_rating`, `dining_type`. Ratings must be 1–5. Uploaded data should be authorized and should not contain unnecessary personal information.

## Architecture
`app.py` owns the Streamlit UI. `src/data_loader.py` validates input, `sentiment.py` classifies text with VADER, `analysis.py` calculates KPIs, `complaint_engine.py` detects themes, and `generate_data.py` creates the fixed-seed demo dataset. `tests/` covers core behavior.

## How the USP works
Each issue has explicit regex keywords. A review is counted once per theme, even when it matches multiple themes. Priority is based on mention volume and negative percentage: High requires substantial volume and at least 55% negative feedback; Medium and Monitor are lower-confidence tiers. Excerpts are taken from matching rows, never fabricated. Keyword detection can miss paraphrases or over-match context, so findings are signals for investigation rather than verified root causes.

## College abstract and viva notes
**Abstract:** RestaurantIQ turns unstructured restaurant reviews into understandable evidence for managers. It demonstrates data validation, NLP sentiment classification, exploratory analysis, and a transparent action recommendation layer.

**Workflow:** CSV/sample data → validation and normalization → VADER sentiment → filters → KPIs/charts → complaint themes → priority and action.

**Existing vs proposed:** A spreadsheet can show averages but often hides recurring text complaints. RestaurantIQ links text evidence to branches and recommended next steps while keeping the rules explainable.

**Advantages:** low cost, reproducible, easy to demonstrate, no API key, exportable. **Limitations:** synthetic data is not real customer research; VADER and keywords are English-oriented; correlations are not causation; small samples can mislead.

**Presentation script:** “I will start with the filters, show how the selected data changes the KPIs, compare branches, then open the Complaint-to-Action Engine. For one theme, I will demonstrate its count, negative rate, branches, real excerpts, priority reason, and recommended action.”

**Demo sequence:** restore sample → Overview → filter one branch → Sentiment Analysis → Branch Comparison → Complaint-to-Action → download filtered CSV.

### Likely viva questions
1. Why Streamlit? It provides a Python-first interactive UI quickly.
2. Why VADER? It is lightweight, explainable, and needs no paid API.
3. What is sentiment score? A compound polarity score from -1 to +1.
4. Why validate CSVs? To prevent crashes and misleading calculations.
5. How are themes detected? Explicit regex keyword groups.
6. Can one review match two themes? Yes, once within each theme; it is not double-counted inside a theme.
7. What makes priority transparent? Volume and negative-rate thresholds are shown.
8. Is a keyword match a confirmed complaint? No; it is an investigation signal.
9. Why show sample size? Percentages from small groups are unstable.
10. How is the data reproducible? The generator uses a fixed random seed.
11. Can this use real data? Yes, through the validated CSV upload.
12. What would you improve? Multilingual models, human review labels, root-cause tracking, and a database.
13. Why not an LLM? Core functionality should not depend on cost or credentials.
14. How are secrets handled? No secrets are required or stored.
15. How can it deploy? Push to GitHub and select the repository in Streamlit Community Cloud.

## GitHub / deployment
Commit the project without `.venv`, credentials, or private data. On Streamlit Community Cloud, choose `app.py` as the entrypoint and `requirements.txt` for dependencies.
