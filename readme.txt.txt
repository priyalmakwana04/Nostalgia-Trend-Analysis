# Nostalgia Trend Project (Streamlit App)

## What you have
- **data/**: CSV datasets (default app uses `data/final_dataset.csv`)
- **app/**: Streamlit UI (`app/app.py`)
- **powerbi/**: Power BI dashboard file (`.pbix`) + data used for the report
- **report/**: Screenshots for your report

## 1) Setup (Windows)
### A) Install Python
Recommended: **Python 3.11** (best compatibility with scikit-learn).

### B) Create a virtual environment
Open PowerShell in the project folder:

```powershell
python -m venv .venv
.\.venv\Scripts\activate
python -m pip install --upgrade pip
pip install -r requirements.txt
```

## 2) Run the app
From the project folder:

```powershell
streamlit run app\app.py
```

It will open in your browser.  
**Do not run** `python app/app.py` (Streamlit needs the `streamlit run` command).

## 3) If you get errors
- **File not found** for dataset: keep `final_dataset.csv` inside `data/` OR use the Upload option in the sidebar.
- **Module not found**: activate `.venv` and run `pip install -r requirements.txt`.

## 4) Power BI dashboard
Open `powerbi/Nostalgia_Trend_Dashboard.pbix` in **Power BI Desktop**.

## 5) GitHub tip
Do **NOT** upload `.venv/` or `notebooks/.venv/` to GitHub (it makes the repo huge).
