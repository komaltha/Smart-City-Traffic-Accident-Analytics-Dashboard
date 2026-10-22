
import streamlit as st
import pandas as pd
import plotly.express as px
import random

from datetime import datetime, timedelta

# ---------------- PAGE CONFIGURATION ----------------
st.set_page_config(
    page_title="Smart City Analytics",
    page_icon="🚦",
    layout="wide"
)

# ---------------- DASHBOARD STYLE ----------------

st.markdown("""
<style>
/* Main dashboard background */
.stApp {
    background-color: #101827;
    color: #FFFFFF;
}

/* Main headings */
h1, h2, h3, h4 {
    color: #58D5FF !important;
}

/* Normal text and descriptions */
.stApp p,
.stApp label,
.stApp [data-testid="stCaptionContainer"] {
    color: #E5E7EB !important;
}

/* KPI cards */
[data-testid="stMetric"] {
    background-color: #1C293B !important;
    padding: 20px !important;
    border-radius: 12px !important;
    border: 1px solid #34465F !important;
}

/* KPI numbers */
[data-testid="stMetricValue"],
[data-testid="stMetricValue"] div {
    color: #FFFFFF !important;
    font-size: 30px !important;
    font-weight: bold !important;
}

/* KPI labels */
[data-testid="stMetricLabel"],
[data-testid="stMetricLabel"] p {
    color: #D1D5DB !important;
    font-size: 15px !important;
}

/* Sidebar */
[data-testid="stSidebar"] {
    background-color: #172235 !important;
}

[data-testid="stSidebar"] * {
    color: #FFFFFF;
}

/* Data table */
[data-testid="stDataFrame"] {
    border: 1px solid #34465F;
    border-radius: 8px;
}

/* Download button */
.stDownloadButton button {
    background-color: #087EA4 !important;
    color: #FFFFFF !important;
    border-radius: 8px;
    font-weight: bold;
}

/* Select boxes and multiselects */
[data-baseweb="select"] * {
    color: #FFFFFF;
}
</style>
""", unsafe_allow_html=True)

# ---------------- GENERATE SAMPLE DATA ----------------
@st.cache_data
def generate_data():
    random.seed(42)

    zones = [
        "Central", "North", "South",
        "East", "West"
    ]

    severities = ["Minor", "Moderate", "Severe"]
    weather_conditions = [
        "Clear", "Rainy", "Foggy", "Cloudy"
    ]
    road_conditions = [
        "Dry", "Wet", "Damaged", "Under Repair"
    ]
    causes = [
        "Overspeeding", "Signal Violation",
        "Poor Road", "Distracted Driving",
        "Heavy Traffic"
    ]

    rows = []

    start_date = datetime(2025, 1, 1)

    for i in range(600):
        date = start_date + timedelta(
            days=random.randint(0, 364)
        )

        rows.append({
            "Date": date,
            "Zone": random.choice(zones),
            "Severity": random.choices(
                severities,
                weights=[55, 30, 15]
            )[0],
            "Traffic Volume": random.randint(100, 2000),
            "Weather": random.choice(weather_conditions),
            "Road Condition": random.choice(road_conditions),
            "Cause": random.choice(causes)
        })

    return pd.DataFrame(rows)


df = generate_data()

# ---------------- TITLE ----------------
st.title("🚦 Smart City Traffic & Accident Analytics")
st.caption(
    "Interactive traffic safety dashboard | Sample data for 2025"
)

# ---------------- SIDEBAR FILTERS ----------------
st.sidebar.title("Dashboard Filters")

zones = st.sidebar.multiselect(
    "Select City Zones",
    options=sorted(df["Zone"].unique()),
    default=sorted(df["Zone"].unique())
)

severity_options = st.sidebar.multiselect(
    "Select Accident Severity",
    options=["Minor", "Moderate", "Severe"],
    default=["Minor", "Moderate", "Severe"]
)

weather_options = st.sidebar.multiselect(
    "Select Weather",
    options=sorted(df["Weather"].unique()),
    default=sorted(df["Weather"].unique())
)

# ---------------- FILTER DATA ----------------
filtered = df[
    df["Zone"].isin(zones)
    & df["Severity"].isin(severity_options)
    & df["Weather"].isin(weather_options)
].copy()

# ---------------- KPI CARDS ----------------
st.subheader("📊 Key Performance Indicators")

total = len(filtered)
severe = (filtered["Severity"] == "Severe").sum()

avg_traffic = (
    round(filtered["Traffic Volume"].mean(), 0)
    if total > 0 else 0
)

zone_counts = filtered["Zone"].value_counts()

highest_zone = (
    zone_counts.idxmax()
    if not zone_counts.empty else "N/A"
)

c1, c2, c3, c4 = st.columns(4)

c1.metric("Total Accidents", f"{total:,}")
c2.metric("Severe Accidents", f"{severe:,}")
c3.metric("Avg. Traffic Volume", f"{avg_traffic:,.0f}")
c4.metric("Highest Accident Zone", highest_zone)

st.divider()

# ---------------- CHARTS: MONTHLY TREND ----------------
st.subheader("📈 Accident Trends")

if not filtered.empty:
    filtered["Month"] = filtered["Date"].dt.month

    monthly = (
        filtered.groupby("Month")
        .size()
        .reset_index(name="Accidents")
    )

    monthly["Month Name"] = monthly["Month"].map(
        lambda m: datetime(2025, m, 1).strftime("%b")
    )

    fig_month = px.line(
        monthly,
        x="Month Name",
        y="Accidents",
        markers=True,
        title="Monthly Accident Trend",
        template="plotly_dark"
    )

    fig_month.update_traces(
        line=dict(color="#58d5ff", width=3)
    )

    fig_month.update_layout(
        paper_bgcolor="#101827",
        plot_bgcolor="#101827"
    )

    st.plotly_chart(fig_month, use_container_width=True)

# ---------------- TWO-COLUMN CHARTS ----------------
left, right = st.columns(2)

with left:
    st.subheader("Accidents by City Zone")

    zone_data = (
        filtered.groupby("Zone")
        .size()
        .reset_index(name="Accidents")
    )

    fig_zone = px.bar(
        zone_data,
        x="Zone",
        y="Accidents",
        color="Zone",
        title="Zone-wise Accident Count",
        template="plotly_dark"
    )

    fig_zone.update_layout(
        showlegend=False,
        paper_bgcolor="#101827",
        plot_bgcolor="#101827"
    )

    st.plotly_chart(fig_zone, use_container_width=True)

with right:
    st.subheader("Accident Severity")

    severity_data = (
        filtered["Severity"]
        .value_counts()
        .rename_axis("Severity")
        .reset_index(name="Count")
    )

    fig_severity = px.pie(
        severity_data,
        names="Severity",
        values="Count",
        hole=0.45,
        title="Severity Distribution",
        template="plotly_dark"
    )

    fig_severity.update_layout(
        paper_bgcolor="#101827"
    )

    st.plotly_chart(
        fig_severity,
        use_container_width=True
    )

# ---------------- WEATHER AND ROAD ANALYSIS ----------------
left, right = st.columns(2)

with left:
    st.subheader("Accidents by Weather")

    weather_data = (
        filtered.groupby("Weather")
        .size()
        .reset_index(name="Accidents")
    )

    fig_weather = px.bar(
        weather_data,
        x="Weather",
        y="Accidents",
        color="Weather",
        template="plotly_dark"
    )

    fig_weather.update_layout(
        showlegend=False,
        paper_bgcolor="#101827",
        plot_bgcolor="#101827"
    )

    st.plotly_chart(fig_weather, use_container_width=True)

with right:
    st.subheader("Accidents by Road Condition")

    road_data = (
        filtered.groupby("Road Condition")
        .size()
        .reset_index(name="Accidents")
    )

    fig_road = px.bar(
        road_data,
        x="Road Condition",
        y="Accidents",
        color="Road Condition",
        template="plotly_dark"
    )

    fig_road.update_layout(
        showlegend=False,
        paper_bgcolor="#101827",
        plot_bgcolor="#101827"
    )

    st.plotly_chart(fig_road, use_container_width=True)

# ---------------- DATA TABLE ----------------
st.subheader("📋 Accident Records")

st.dataframe(
    filtered.sort_values("Date", ascending=False),
    use_container_width=True,
    hide_index=True
)

# ---------------- DOWNLOAD DATA ----------------
csv_data = filtered.to_csv(index=False).encode("utf-8")

st.download_button(
    label="Download Filtered Data as CSV",
    data=csv_data,
    file_name="smart_city_accident_data.csv",
    mime="text/csv"
)

st.caption(
    "Note: This dashboard uses randomly generated sample data. "
    "It does not represent verified real-world accident statistics."
)
