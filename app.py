from __future__ import annotations

from pathlib import Path
import pandas as pd
import streamlit as st
from sklearn.preprocessing import StandardScaler
from sklearn.cluster import KMeans

APP_DIR = Path(__file__).resolve().parent
PROJECT_ROOT = APP_DIR.parent
DEFAULT_DATA_PATH = PROJECT_ROOT / "data" / "final_dataset.csv"

st.set_page_config(page_title="Nostalgia Trend Project", layout="wide")

st.title("📊 Nostalgia Trend Project — Live Demo")
st.caption("Cluster hashtags/posts using engagement and time features. Export clustered data as CSV.")

# ----------------------------
# Sidebar: Data loading
# ----------------------------
st.sidebar.header("1) Dataset")

use_upload = st.sidebar.checkbox("Upload CSV instead of using project /data", value=False)
if use_upload:
    uploaded = st.sidebar.file_uploader("Upload a CSV", type=["csv"])
    if uploaded is None:
        st.info("Upload a CSV to continue.")
        st.stop()
    df = pd.read_csv(uploaded)
    data_source = "Uploaded file"
else:
    if not DEFAULT_DATA_PATH.exists():
        st.error(
            f"Could not find the default dataset at:\n\n{DEFAULT_DATA_PATH}\n\n"
            "Fix: keep final_dataset.csv inside the project's data/ folder OR enable upload."
        )
        st.stop()
    df = pd.read_csv(DEFAULT_DATA_PATH)
    data_source = f"Project file: {DEFAULT_DATA_PATH.relative_to(PROJECT_ROOT)}"

st.sidebar.caption(f"Source: {data_source}")

# ----------------------------
# Validate columns
# ----------------------------
required_cols = {"hashtag", "year", "engagement_score"}
missing = required_cols - set(df.columns)
if missing:
    st.error(
        f"Missing required columns: {sorted(missing)}.\n\n"
        f"Your CSV must contain at least: {sorted(required_cols)}"
    )
    st.stop()

# Ensure numeric
for col in ["year", "engagement_score"]:
    df[col] = pd.to_numeric(df[col], errors="coerce")

df = df.dropna(subset=["year", "engagement_score"]).copy()

# ----------------------------
# Main: Preview + filters
# ----------------------------
st.subheader("Dataset Preview")
c1, c2, c3, c4 = st.columns(4)
with c1:
    st.metric("Rows", f"{len(df):,}")
with c2:
    st.metric("Unique hashtags", f"{df['hashtag'].nunique():,}")
with c3:
    st.metric("Years", f"{int(df['year'].min())}–{int(df['year'].max())}")
with c4:
    st.metric("Platforms", f"{df['platform'].nunique() if 'platform' in df.columns else '—'}")

with st.expander("Show raw data (first 200 rows)"):
    st.dataframe(df.head(200), use_container_width=True)

st.sidebar.header("2) Filters")
years = sorted(df["year"].dropna().astype(int).unique().tolist())
year_min, year_max = (min(years), max(years)) if years else (0, 0)
year_range = st.sidebar.slider("Year range", min_value=year_min, max_value=year_max, value=(year_min, year_max))
filtered = df[(df["year"].astype(int) >= year_range[0]) & (df["year"].astype(int) <= year_range[1])].copy()

if "platform" in filtered.columns:
    platforms = ["All"] + sorted(filtered["platform"].dropna().unique().tolist())
    platform_choice = st.sidebar.selectbox("Platform", platforms, index=0)
    if platform_choice != "All":
        filtered = filtered[filtered["platform"] == platform_choice].copy()

query = st.sidebar.text_input("Hashtag contains", value="")
if query.strip():
    filtered = filtered[filtered["hashtag"].astype(str).str.contains(query.strip(), case=False, na=False)].copy()

st.subheader("Filtered Data")
st.write(f"Showing **{len(filtered):,}** rows after filters.")
st.dataframe(filtered.head(200), use_container_width=True)

if len(filtered) < 10:
    st.warning("Not enough rows after filtering for meaningful clustering. Try widening filters.")
    st.stop()

# ----------------------------
# Sidebar: Clustering settings
# ----------------------------
st.sidebar.header("3) Clustering")

# Feature selection (keep simple + safe)
candidate_features = []
for col in ["engagement_score", "year", "views", "likes", "shares", "comments"]:
    if col in filtered.columns:
        candidate_features.append(col)

default_features = [c for c in ["engagement_score", "year"] if c in candidate_features]
features_selected = st.sidebar.multiselect(
    "Select features",
    options=candidate_features,
    default=default_features,
    help="Selected numeric columns are scaled and used for KMeans clustering.",
)
if len(features_selected) < 2:
    st.error("Select at least 2 features for clustering.")
    st.stop()

k = st.sidebar.slider("Number of clusters (K)", min_value=2, max_value=10, value=3)
random_state = st.sidebar.number_input("Random state", min_value=0, max_value=10_000, value=42, step=1)

# Prepare X
X = filtered[features_selected].apply(pd.to_numeric, errors="coerce")
X = X.dropna()
filtered = filtered.loc[X.index].copy()

scaler = StandardScaler()
X_scaled = scaler.fit_transform(X.values)

kmeans = KMeans(n_clusters=int(k), random_state=int(random_state), n_init="auto")
filtered["cluster"] = kmeans.fit_predict(X_scaled)

# ----------------------------
# Output
# ----------------------------
st.subheader("Clustered Output")
cols_to_show = [c for c in ["post_id", "post_date", "platform", "hashtag", "year", "engagement_score"] if c in filtered.columns]
cols_to_show += ["cluster"]
st.dataframe(filtered[cols_to_show].head(500), use_container_width=True)

st.subheader("Visuals")
col1, col2 = st.columns(2)

with col1:
    st.write("Cluster counts")
    st.bar_chart(filtered["cluster"].value_counts().sort_index())

with col2:
    st.write("Average engagement_score by cluster")
    if "engagement_score" in filtered.columns:
        st.bar_chart(filtered.groupby("cluster")["engagement_score"].mean().sort_index())

st.subheader("Cluster Summary")
summary_cols = ["cluster"] + [c for c in features_selected if c in filtered.columns]
cluster_summary = (
    filtered[summary_cols]
    .groupby("cluster")
    .agg(["count", "mean", "min", "max"])
)
st.dataframe(cluster_summary, use_container_width=True)

# ----------------------------
# Download
# ----------------------------
st.subheader("Download clustered CSV")
csv_bytes = filtered.to_csv(index=False).encode("utf-8")
st.download_button(
    "⬇️ Download clustered_data.csv",
    data=csv_bytes,
    file_name="clustered_data.csv",
    mime="text/csv",
)

st.caption("Tip: Run this with `streamlit run app/app.py` (not `python app.py`).")
