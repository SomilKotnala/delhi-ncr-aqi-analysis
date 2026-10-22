"""
dashboard/app.py
================
Delhi-NCR Air Quality Intelligence & Episode Analysis Dashboard (2017–2023)

An interactive, production-grade portfolio application showcasing:
1. Star-schema database integration (PostgreSQL with local Parquet fallback)
2. Interactive time-series exploration with CPCB health risk categorization
3. Rigorous seasonal and spatial dynamics with block bootstrap robustness metrics
4. Station-matched Diwali episode causal decomposition & confounding audit

Stack: Streamlit, Plotly, Pandas, NumPy, PostgreSQL / Parquet
"""

import sys
from pathlib import Path
import numpy as np
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import streamlit as st

# Add project root to sys.path
PROJECT_ROOT = Path(__file__).resolve().parent.parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from dashboard.data_access import load_all_dashboard_data
from dashboard.metrics import (
    CPCB_CATEGORIES,
    CPCB_COLOR_MAP,
    CPCB_BREAKPOINTS,
    filter_data,
    compute_kpis,
    compute_monthly_trend,
    compute_city_summary,
    compute_category_distribution,
    compute_seasonal_comparison,
    compute_station_rankings,
    compute_diwali_event_analysis,
)

# -----------------------------------------------------------------------------
# 1. PAGE CONFIGURATION & STYLING
# -----------------------------------------------------------------------------
st.set_page_config(
    page_title="Delhi-NCR Air Quality Intelligence",
    page_icon="🌫️",
    layout="wide",
    initial_sidebar_state="expanded",
)

# Custom CSS for high-polish analytics presentation
st.markdown("""
<style>
    /* Metric Card Styling */
    .metric-container {
        background-color: #ffffff;
        border: 1px solid #e0e0e0;
        border-radius: 8px;
        padding: 16px 20px;
        box-shadow: 0 2px 4px rgba(0,0,0,0.04);
        margin-bottom: 12px;
    }
    .metric-title {
        font-size: 0.85rem;
        font-weight: 600;
        color: #555555;
        text-transform: uppercase;
        letter-spacing: 0.5px;
    }
    .metric-value {
        font-size: 1.9rem;
        font-weight: 700;
        color: #1a1a1a;
        margin: 4px 0;
    }
    .metric-caption {
        font-size: 0.8rem;
        color: #777777;
    }
    .provenance-badge {
        display: inline-block;
        background-color: #f0f7ff;
        border: 1px solid #cce5ff;
        color: #004085;
        padding: 4px 10px;
        border-radius: 12px;
        font-size: 0.78rem;
        font-weight: 500;
        margin-bottom: 8px;
    }
    .methodology-box {
        background-color: #f8f9fa;
        border-left: 4px solid #17a2b8;
        padding: 12px 16px;
        border-radius: 4px;
        font-size: 0.86rem;
        color: #333333;
        margin-top: 10px;
        margin-bottom: 15px;
    }
    .audit-box {
        background-color: #fff9e6;
        border-left: 4px solid #ffc107;
        padding: 12px 16px;
        border-radius: 4px;
        font-size: 0.86rem;
        color: #493800;
        margin-top: 10px;
        margin-bottom: 15px;
    }
</style>
""", unsafe_allow_html=True)


# -----------------------------------------------------------------------------
# 2. DATA INGESTION & FILTER SIDEBAR
# -----------------------------------------------------------------------------
st.sidebar.title("🌫️ Delhi-NCR AQI Explorer")
st.sidebar.markdown("**Portfolio Project by Beginner Data Analyst**")

# Data connection source toggle
source_option = st.sidebar.selectbox(
    "Data Source Layer",
    options=["auto", "postgres", "parquet"],
    format_func=lambda x: {
        "auto": "Auto-detect (PostgreSQL with Parquet Fallback)",
        "postgres": "PostgreSQL Database (localhost:5432)",
        "parquet": "Local Parquet Storage (data/processed/)",
    }[x],
    index=0,
    help="Dual-mode pipeline: loads live from PostgreSQL star schema if available, else high-speed Parquet.",
)

# Load data
with st.spinner("Loading air quality datasets..."):
    datasets = load_all_dashboard_data(preferred_source=source_option)

df_daily_raw = datasets["daily"]
df_stations = datasets["stations"]
df_diurnal = datasets["diurnal"]
source_info = datasets["source_info"]

st.sidebar.markdown(f"""
<div class="provenance-badge">
    📡 {source_info['source']}<br>
    📊 {source_info['daily_rows']:,} records ({source_info['min_date']} to {source_info['max_date']})
</div>
""", unsafe_allow_html=True)

st.sidebar.markdown("---")
st.sidebar.subheader("🔍 Analytical Filters")

# Filter: Cities
all_cities = sorted(df_daily_raw["city"].unique().tolist())
selected_cities = st.sidebar.multiselect(
    "Filter Cities",
    options=all_cities,
    default=all_cities,
    help="Select one or more NCR cities. Defaults to all 5 cities.",
)

# Filter: Stations (dynamically conditioned on cities)
stations_in_cities = sorted(
    df_daily_raw[df_daily_raw["city"].isin(selected_cities)]["station_name"].unique().tolist()
)
selected_stations = st.sidebar.multiselect(
    "Filter Stations",
    options=stations_in_cities,
    default=[],
    help="Leave empty to analyze all stations in selected cities.",
)

# Filter: Date Range
min_cal_date = df_daily_raw["date"].min().date()
max_cal_date = df_daily_raw["date"].max().date()
selected_date_range = st.sidebar.date_input(
    "Date Range",
    value=(min_cal_date, max_cal_date),
    min_value=min_cal_date,
    max_value=max_cal_date,
)

# Filter: Season
season_options = ["Winter", "Summer / Pre-Monsoon", "Monsoon", "Post-Monsoon", "Transition (Feb)"]
selected_seasons = st.sidebar.multiselect(
    "Meteorological Seasons",
    options=season_options,
    default=season_options,
)

# Filter: Completeness threshold
valid_only = st.sidebar.checkbox(
    "Valid Records Only (≥ 16 hrs/day)",
    value=True,
    help="CPCB completeness criterion: requires at least 16 hourly readings for daily statistical validity.",
)

# Apply filters: demographic and temporal scope first (retaining both valid and invalid records)
df_scope = filter_data(
    df_daily_raw,
    cities=selected_cities if selected_cities else all_cities,
    stations=selected_stations if selected_stations else None,
    date_range=selected_date_range if isinstance(selected_date_range, (tuple, list)) and len(selected_date_range) == 2 else None,
    seasons=selected_seasons if selected_seasons else None,
    valid_only=False,
)
total_scope_scheduled_days = len(df_scope)

# Apply CPCB validity filter if enabled
if valid_only and "is_day_valid" in df_scope.columns:
    df_filtered = df_scope[df_scope["is_day_valid"] == True]
else:
    df_filtered = df_scope

# Quick CSV Download
st.sidebar.markdown("---")
st.sidebar.subheader("💾 Export Filtered Data")
csv_data = df_filtered.head(10000).to_csv(index=False).encode("utf-8")
st.sidebar.download_button(
    label="Download Sample CSV (10k rows)",
    data=csv_data,
    file_name="delhi_ncr_aqi_filtered.csv",
    mime="text/csv",
    help="Exports the active filtered subset (capped at 10,000 rows for rapid client download).",
)


# -----------------------------------------------------------------------------
# 3. HEADER & PROVENANCE BANNER
# -----------------------------------------------------------------------------
st.title("🌫️ Delhi-NCR Air Quality Intelligence & Episode Analysis")
st.markdown("""
**An Audited Empirical Investigation of Seasonal Inversion Dynamics, Spatial Inequality, and Diwali Episodic Shocks (2017–2023)**  
*CPCB Statutory Data | Star-Schema Architecture | Block-Bootstrap Inference*
""")

# Top Navigation Tabs
tab1, tab2, tab3 = st.tabs([
    "🌐 1. Regional Overview & Health Risk",
    "❄️ 2. Seasonal Inversion & Spatial Dynamics",
    "🎆 3. Diwali Pollution Episodes & Confounding",
])


# =============================================================================
# TAB 1: REGIONAL OVERVIEW & HEALTH RISK
# =============================================================================
with tab1:
    kpis = compute_kpis(df_filtered, total_scheduled_days=total_scope_scheduled_days)

    # Dynamic card title depending on whether all 5 cities are selected or a subset
    is_full_network = (set(selected_cities) == set(all_cities)) and not selected_stations
    scope_title = "Network Median AQI" if is_full_network else f"{', '.join(selected_cities)} Median AQI"

    # Row 1: KPI Metric Cards
    c1, c2, c3, c4 = st.columns(4)
    with c1:
        st.markdown(f"""
        <div class="metric-container" style="border-left: 5px solid #FF8C00;">
            <div class="metric-title">{scope_title}</div>
            <div class="metric-value">{kpis['median_aqi']}</div>
            <div class="metric-caption">Mean: <strong>{kpis['mean_aqi']}</strong> | IQR: <strong>{kpis['iqr_aqi']}</strong></div>
        </div>
        """, unsafe_allow_html=True)

    with c2:
        st.markdown(f"""
        <div class="metric-container" style="border-left: 5px solid #00B050;">
            <div class="metric-title">Valid Station-Days</div>
            <div class="metric-value">{kpis['valid_station_days']:,}</div>
            <div class="metric-caption">Completeness: <strong>{kpis['completeness_pct']}%</strong> (≥16 hrs/day)</div>
        </div>
        """, unsafe_allow_html=True)

    with c3:
        st.markdown(f"""
        <div class="metric-container" style="border-left: 5px solid #E60000;">
            <div class="metric-title">Severe Days (>400 AQI)</div>
            <div class="metric-value">{kpis['severe_days_pct']}%</div>
            <div class="metric-caption">Count: <strong>{kpis['severe_days_count']:,}</strong> station-days</div>
        </div>
        """, unsafe_allow_html=True)

    with c4:
        st.markdown(f"""
        <div class="metric-container" style="border-left: 5px solid #7A0019;">
            <div class="metric-title">Sensor Ceiling Capped</div>
            <div class="metric-value">{kpis['capped_days_pct']}%</div>
            <div class="metric-caption">Station-days with ≥1 capped hour (500.0)</div>
        </div>
        """, unsafe_allow_html=True)

    # Row 2: Monthly Time-Series Trend & CPCB Severity Distribution
    col_trend, col_dist = st.columns([7, 3])

    with col_trend:
        st.subheader("📈 Monthly AQI Trajectory (2017–2023)")
        monthly_df = compute_monthly_trend(df_filtered)

        if not monthly_df.empty:
            fig_trend = go.Figure()

            # Shaded CPCB category bands
            bands = [
                (0, 50, "Good", "rgba(0, 176, 80, 0.08)"),
                (51, 100, "Satisfactory", "rgba(146, 208, 80, 0.08)"),
                (101, 200, "Moderate", "rgba(255, 255, 0, 0.08)"),
                (201, 300, "Poor", "rgba(255, 153, 0, 0.08)"),
                (301, 400, "Very Poor", "rgba(255, 0, 0, 0.08)"),
                (401, 500, "Severe", "rgba(128, 0, 0, 0.12)"),
            ]
            for y0, y1, label, color in bands:
                fig_trend.add_hrect(
                    y0=y0, y1=y1, fillcolor=color, layer="below", line_width=0,
                    annotation_text=label, annotation_position="top left",
                    annotation_font_size=9, annotation_font_color="#777777"
                )

            # IQR Ribbon (p25 to p75)
            fig_trend.add_trace(go.Scatter(
                x=pd.concat([monthly_df["year_month"], monthly_df["year_month"][::-1]]),
                y=pd.concat([monthly_df["p75_aqi"], monthly_df["p25_aqi"][::-1]]),
                fill="toself",
                fillcolor="rgba(31, 119, 180, 0.15)",
                line=dict(color="rgba(255,255,255,0)"),
                hoverinfo="skip",
                showlegend=True,
                name="Interquartile Range (IQR)",
            ))

            # Monthly Median line
            fig_trend.add_trace(go.Scatter(
                x=monthly_df["year_month"],
                y=monthly_df["median_aqi"],
                mode="lines+markers",
                name="Monthly Median AQI",
                line=dict(color="#1f77b4", width=2.5),
                marker=dict(size=5),
                hovertemplate="<b>%{x|%b %Y}</b><br>Median AQI: <b>%{y:.1f}</b><extra></extra>",
            ))

            # Monthly Mean line
            fig_trend.add_trace(go.Scatter(
                x=monthly_df["year_month"],
                y=monthly_df["mean_aqi"],
                mode="lines",
                name="Monthly Mean AQI",
                line=dict(color="#ff7f0e", width=1.8, dash="dot"),
                hovertemplate="<b>%{x|%b %Y}</b><br>Mean AQI: <b>%{y:.1f}</b><extra></extra>",
            ))

            fig_trend.update_layout(
                height=380,
                margin=dict(l=40, r=20, t=20, b=30),
                legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1),
                yaxis=dict(title="AQI Value", range=[0, 480]),
                xaxis=dict(title=None),
                hovermode="x unified",
            )
            st.plotly_chart(fig_trend, use_container_width=True)
        else:
            st.warning("No data available for the selected filters.")

    with col_dist:
        st.subheader("🎯 CPCB Severity Share")
        cat_df = compute_category_distribution(df_filtered)

        fig_pie = px.pie(
            cat_df,
            names="category",
            values="count",
            color="category",
            color_discrete_map=CPCB_COLOR_MAP,
            hole=0.45,
        )
        fig_pie.update_traces(
            textposition="inside",
            textinfo="percent+label",
            hovertemplate="<b>%{label}</b><br>Station-Days: %{value:,} (%{percent})<extra></extra>",
        )
        fig_pie.update_layout(
            height=380,
            margin=dict(l=10, r=10, t=20, b=20),
            showlegend=False,
        )
        st.plotly_chart(fig_pie, use_container_width=True)

    # Row 3: City Breakdown & Diurnal Profiles
    col_city, col_diurnal = st.columns([5, 5])

    with col_city:
        st.subheader("🏙️ City Comparison (Median AQI & Severe Risk)")
        city_summary = compute_city_summary(df_filtered)

        if not city_summary.empty:
            fig_city = px.bar(
                city_summary,
                x="city",
                y="median_aqi",
                color="median_aqi",
                color_continuous_scale="Reds",
                text="median_aqi",
                labels={"city": "NCR City", "median_aqi": "Median AQI"},
            )
            fig_city.update_traces(
                texttemplate="<b>%{text:.1f}</b>",
                textposition="outside",
                hovertemplate="<b>%{x}</b><br>Median AQI: %{y:.1f}<br>Severe Days: %{customdata[0]:.1f}%<extra></extra>",
                customdata=city_summary[["severe_days_pct"]],
            )
            fig_city.update_layout(
                height=320,
                margin=dict(l=30, r=20, t=20, b=30),
                coloraxis_showscale=False,
                yaxis=dict(range=[0, max(city_summary["median_aqi"]) * 1.2]),
            )
            st.plotly_chart(fig_city, use_container_width=True)
        else:
            st.info("No city data matches criteria.")

    with col_diurnal:
        st.subheader("⏰ 24-Hour Diurnal Dynamics (Winter vs Non-Winter)")
        if not df_diurnal.empty:
            diurnal_plot = df_diurnal[df_diurnal["city"] == "All Cities (Network)"].copy()
            if diurnal_plot.empty:
                diurnal_plot = df_diurnal.groupby(["hour", "is_winter"])["median_aqi"].mean().reset_index()

            diurnal_plot["Season Group"] = diurnal_plot["is_winter"].map({True: "Winter (Nov–Feb)", False: "Non-Winter (Mar–Oct)"})

            fig_diurnal = px.line(
                diurnal_plot,
                x="hour",
                y="median_aqi",
                color="Season Group",
                color_discrete_map={"Winter (Nov–Feb)": "#E60000", "Non-Winter (Mar–Oct)": "#1f77b4"},
                markers=True,
                labels={"hour": "Hour of Day (IST)", "median_aqi": "Median Hourly AQI"},
            )
            fig_diurnal.update_layout(
                height=320,
                margin=dict(l=30, r=20, t=20, b=30),
                xaxis=dict(tickmode="linear", tick0=0, dtick=2),
                legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1),
            )
            st.plotly_chart(fig_diurnal, use_container_width=True)
        else:
            st.info("Diurnal profiles unavailable.")

    # Analytical Context Footnote
    st.markdown("""
    <div class="methodology-box">
        💡 <strong>Analytical Context:</strong> Over <strong>56.0%</strong> of recorded station-days in Delhi-NCR fall into the 
        <strong>Poor, Very Poor, or Severe</strong> categories (AQI &gt; 200). Note the striking diurnal inversion curve: in winter, 
        nighttime surface cooling creates shallow thermal inversions, trapping vehicular emissions and biomass smoke near ground level, 
        peaking between 22:00 and 08:00 IST.
    </div>
    """, unsafe_allow_html=True)


# =============================================================================
# TAB 2: SEASONAL & SPATIAL DYNAMICS
# =============================================================================
with tab2:
    st.subheader("❄️ Seasonal Disparity: Winter Inversion Shock")
    sc = compute_seasonal_comparison(df_filtered)

    # Seasonal KPI Cards
    s1, s2, s3, s4 = st.columns(4)
    with s1:
        st.markdown(f"""
        <div class="metric-container" style="border-left: 5px solid #004085;">
            <div class="metric-title">Winter Median AQI</div>
            <div class="metric-value">{sc['winter_median']}</div>
            <div class="metric-caption">Mean: <strong>{sc['winter_mean']}</strong> | Days: <strong>{sc['winter_days']:,}</strong></div>
        </div>
        """, unsafe_allow_html=True)

    with s2:
        st.markdown(f"""
        <div class="metric-container" style="border-left: 5px solid #28a745;">
            <div class="metric-title">Non-Winter Median AQI</div>
            <div class="metric-value">{sc['non_winter_median']}</div>
            <div class="metric-caption">Mean: <strong>{sc['non_winter_mean']}</strong> | Days: <strong>{sc['non_winter_days']:,}</strong></div>
        </div>
        """, unsafe_allow_html=True)

    with s3:
        st.markdown(f"""
        <div class="metric-container" style="border-left: 5px solid #dc3545;">
            <div class="metric-title">Winter Excess Elevation</div>
            <div class="metric-value">+{sc['absolute_diff']}</div>
            <div class="metric-caption">Winter / Non-Winter Ratio: <strong>{sc['ratio']}x</strong></div>
        </div>
        """, unsafe_allow_html=True)

    with s4:
        st.markdown(f"""
        <div class="metric-container" style="border-left: 5px solid #6f42c1;">
            <div class="metric-title">Stations Elevated</div>
            <div class="metric-value">100.0%</div>
            <div class="metric-caption">56 of 56 stations record higher winter median</div>
        </div>
        """, unsafe_allow_html=True)

    # Visuals: Box Distribution by Season & City Seasonal Comparison
    col_season_box, col_season_city = st.columns([6, 4])

    with col_season_box:
        st.subheader("📊 AQI Distribution Across Meteorological Seasons")
        if not df_filtered.empty and "season" in df_filtered.columns:
            fig_box = px.box(
                df_filtered,
                x="season",
                y="daily_mean_aqi",
                color="season",
                category_orders={"season": ["Winter", "Post-Monsoon", "Transition (Feb)", "Summer / Pre-Monsoon", "Monsoon"]},
                color_discrete_map={
                    "Winter": "#7A0019",
                    "Post-Monsoon": "#FF8C00",
                    "Transition (Feb)": "#A0522D",
                    "Summer / Pre-Monsoon": "#E6B800",
                    "Monsoon": "#00B050",
                },
                points=False,
                labels={"season": "Season", "daily_mean_aqi": "Daily Mean AQI"},
            )
            fig_box.update_layout(
                height=350,
                margin=dict(l=30, r=20, t=20, b=30),
                showlegend=False,
                yaxis=dict(range=[0, 510]),
            )
            st.plotly_chart(fig_box, use_container_width=True)
        else:
            st.warning("No seasonal data available.")

    with col_season_city:
        st.subheader("🏙️ City-by-City Seasonal Elevation")
        if not df_filtered.empty and "city" in df_filtered.columns:
            city_season_df = df_filtered.groupby(["city", "is_winter"])["daily_mean_aqi"].median().reset_index()
            city_season_df["Season"] = city_season_df["is_winter"].map({True: "Winter", False: "Non-Winter"})

            fig_city_season = px.bar(
                city_season_df,
                x="city",
                y="daily_mean_aqi",
                color="Season",
                barmode="group",
                color_discrete_map={"Winter": "#7A0019", "Non-Winter": "#1f77b4"},
                labels={"city": "City", "daily_mean_aqi": "Median AQI"},
            )
            fig_city_season.update_layout(
                height=350,
                margin=dict(l=30, r=20, t=20, b=30),
                legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1),
                yaxis=dict(range=[0, 420]),
            )
            st.plotly_chart(fig_city_season, use_container_width=True)

    # Spatial Inequality: Top 10 Polluted vs Cleanest
    st.markdown("---")
    st.subheader("📍 Station-Level Inequality Rankings (Min. 100 Recorded Days)")
    rankings = compute_station_rankings(df_filtered, top_n=10, min_records=100)

    col_hot, col_clean = st.columns(2)
    with col_hot:
        st.markdown("**🔥 Top 10 Most Polluted Monitoring Stations**")
        if not rankings["top_polluted"].empty:
            st.dataframe(
                rankings["top_polluted"][["rank", "station_name", "city", "median_aqi", "severe_days_pct", "valid_days"]],
                column_config={
                    "rank": "Rank",
                    "station_name": "Station Name",
                    "city": "City",
                    "median_aqi": st.column_config.NumberColumn("Median AQI", format="%.1f"),
                    "severe_days_pct": st.column_config.NumberColumn("Severe Days %", format="%.1f%%"),
                    "valid_days": st.column_config.NumberColumn("Valid Days", format="%d"),
                },
                hide_index=True,
                use_container_width=True,
            )
        else:
            st.info("No station rankings available.")

    with col_clean:
        st.markdown("**🌿 Top 10 Cleanest / Lowest-AQI Stations**")
        if not rankings["cleanest"].empty:
            st.dataframe(
                rankings["cleanest"][["rank", "station_name", "city", "median_aqi", "severe_days_pct", "valid_days"]],
                column_config={
                    "rank": "Rank",
                    "station_name": "Station Name",
                    "city": "City",
                    "median_aqi": st.column_config.NumberColumn("Median AQI", format="%.1f"),
                    "severe_days_pct": st.column_config.NumberColumn("Severe Days %", format="%.1f%%"),
                    "valid_days": st.column_config.NumberColumn("Valid Days", format="%d"),
                },
                hide_index=True,
                use_container_width=True,
            )
        else:
            st.info("No station rankings available.")

    # Statistical Robustness Callout Card
    st.markdown("""
    <div class="audit-box">
        🔬 <strong>Statistical Robustness Audit (Addressing Autocorrelation & Station Clustering):</strong><br>
        Standard pooled two-sample tests assume independent observations, yet Delhi-NCR monitoring stations exhibit strong 
        spatial co-dependence and temporal autocorrelation. In our formal Stage 2C statistical audit:
        <ul>
            <li><strong>Moving Block Bootstrap (L = 14 Days, B = 2,000):</strong> Preserves 2-week meteorological memory. 
            Estimated calendar-day regional median winter elevation is <strong>+181.90 AQI points</strong> (95% CI: <strong>[156.98, 202.14]</strong>).</li>
            <li><strong>Station-Balanced Wilcoxon Signed-Rank Test:</strong> Eliminates spatial imbalance by computing station-level medians. 
            Paired median difference = <strong>+181.84 AQI points</strong> (W = 0.0, p = 2.45 × 10⁻¹¹, 100% of stations higher).</li>
            <li><strong>Right-Censored Tobit Model (Addressing Sensor Ceiling at 500.0):</strong> Winter coefficient = 
            <strong>+154.17 AQI points</strong> (Robust SE = 0.81, p &lt; 10⁻¹⁵).</li>
        </ul>
    </div>
    """, unsafe_allow_html=True)


# =============================================================================
# TAB 3: DIWALI POLLUTION EPISODE ANALYSIS
# =============================================================================
with tab3:
    st.subheader("🎆 Diwali Episodic Shock & Causal Deconfounding (2017–2023)")
    diwali_res = compute_diwali_event_analysis(df_filtered)

    # Top KPI metrics
    overall_p = diwali_res["overall_paired_diff"]
    d1, d2, d3, d4 = st.columns(4)
    with d1:
        st.markdown(f"""
        <div class="metric-container" style="border-left: 5px solid #FF8C00;">
            <div class="metric-title">Mean Paired Surge</div>
            <div class="metric-value">+{overall_p.get('mean_change', 0.0)}</div>
            <div class="metric-caption">Post-Diwali (t+1) vs Pre-Diwali (t-1)</div>
        </div>
        """, unsafe_allow_html=True)

    with d2:
        st.markdown(f"""
        <div class="metric-container" style="border-left: 5px solid #E60000;">
            <div class="metric-title">Median Paired Surge</div>
            <div class="metric-value">+{overall_p.get('median_change', 0.0)}</div>
            <div class="metric-caption">Station-matched difference</div>
        </div>
        """, unsafe_allow_html=True)

    with d3:
        st.markdown(f"""
        <div class="metric-container" style="border-left: 5px solid #28a745;">
            <div class="metric-title">Station-Years Elevated</div>
            <div class="metric-value">{overall_p.get('pct_elevated', 0.0)}%</div>
            <div class="metric-caption">Proportion showing higher AQI at t+1</div>
        </div>
        """, unsafe_allow_html=True)

    with d4:
        st.markdown(f"""
        <div class="metric-container" style="border-left: 5px solid #17a2b8;">
            <div class="metric-title">Matched Station-Year Pairs</div>
            <div class="metric-value">{overall_p.get('total_pairs', 0):,}</div>
            <div class="metric-caption">Valid (t-1, t+1) pairs across 7 years</div>
        </div>
        """, unsafe_allow_html=True)

    # Visual: Event Study Timeline (-7 to +7)
    timeline_df = diwali_res["timeline"]
    if not timeline_df.empty:
        st.subheader("📅 Event Study Window Trajectory (t - 7 to t + 7 Days)")
        
        # Plotly multi-line chart
        fig_event = go.Figure()

        # Add trace for each individual year
        years = sorted([y for y in timeline_df["year"].unique() if y != "All Years Combined"])
        for yr in years:
            sub = timeline_df[timeline_df["year"] == yr]
            fig_event.add_trace(go.Scatter(
                x=sub["diwali_relative_day"],
                y=sub["median_aqi"],
                mode="lines+markers",
                name=f"Diwali {yr}",
                opacity=0.65,
                line=dict(width=1.8),
                hovertemplate=f"<b>Diwali {yr}</b><br>Day %{{x}}: Median AQI <b>%{{y:.1f}}</b><extra></extra>",
            ))

        # Add heavy bold line for Combined Overall Average
        comb_sub = timeline_df[timeline_df["year"] == "All Years Combined"]
        if not comb_sub.empty:
            fig_event.add_trace(go.Scatter(
                x=comb_sub["diwali_relative_day"],
                y=comb_sub["median_aqi"],
                mode="lines+markers",
                name="★ 7-Year Multi-Year Average",
                line=dict(color="#111111", width=3.5),
                marker=dict(size=7, color="#111111"),
                hovertemplate="<b>Multi-Year Average</b><br>Day %{x}: Median AQI <b>%{y:.1f}</b><extra></extra>",
            ))

        # Vertical line at t=0 (Diwali Day)
        fig_event.add_vline(x=0, line_width=2, line_dash="dash", line_color="#E60000")
        fig_event.add_annotation(
            x=0, y=470, text="Diwali Night (t=0)", showarrow=True, arrowhead=1,
            font=dict(size=11, color="#E60000"), bgcolor="#ffffff", bordercolor="#E60000"
        )

        fig_event.update_layout(
            height=380,
            margin=dict(l=40, r=20, t=30, b=30),
            xaxis=dict(
                title="Days Relative to Diwali (t = 0 is Diwali Day)",
                tickmode="linear",
                tick0=-7,
                dtick=1,
            ),
            yaxis=dict(title="Median Daily AQI", range=[100, 510]),
            legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1),
            hovermode="x unified",
        )
        st.plotly_chart(fig_event, use_container_width=True)

    # Paired Changes & Timing Cohort Table
    col_paired, col_timing = st.columns([6, 4])

    with col_paired:
        st.subheader("📊 Station-Matched Paired Changes by Year (t+1 vs t-1)")
        yearly_df = diwali_res["yearly_paired_diff"]
        if not yearly_df.empty:
            fig_bar_yr = px.bar(
                yearly_df,
                x="year",
                y="mean_paired_change",
                color="timing_cohort",
                color_discrete_map={"Late October": "#FF8C00", "Mid November": "#7A0019"},
                text="mean_paired_change",
                labels={"year": "Year", "mean_paired_change": "Mean Paired Change (AQI)", "timing_cohort": "Timing"},
            )
            fig_bar_yr.update_traces(
                texttemplate="<b>%{text:+.1f}</b>",
                textposition="outside",
            )
            fig_bar_yr.update_layout(
                height=320,
                margin=dict(l=30, r=20, t=20, b=30),
                legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1),
                yaxis=dict(title="Change in AQI (t+1 vs t-1)"),
            )
            st.plotly_chart(fig_bar_yr, use_container_width=True)

    with col_timing:
        st.subheader("🌓 Timing Cohort Breakdown")
        cohort_df = diwali_res["timing_cohort_summary"]
        if not cohort_df.empty:
            st.dataframe(
                cohort_df,
                column_config={
                    "timing_cohort": "Cohort",
                    "years_count": "Years",
                    "avg_pre_median": st.column_config.NumberColumn("Pre Median", format="%.1f"),
                    "avg_post_median": st.column_config.NumberColumn("Post Median", format="%.1f"),
                    "avg_mean_change": st.column_config.NumberColumn("Mean Surge", format="%+.1f"),
                    "avg_pct_elevated": st.column_config.NumberColumn("Elevated %", format="%.1f%%"),
                },
                hide_index=True,
                use_container_width=True,
            )
        st.markdown("""
        **Key Empirical Finding:**  
        - **Late October Diwali (2017, 2019, 2022):** Occurs before full winter boundary layer collapse (baseline ~230–280). Firecracker pulses generate acute, conspicuous surges (+82.3 pts mean).
        - **Mid November Diwali (2018, 2020, 2021, 2023):** Coincides with peak agricultural stubble burning and pre-existing severe winter inversion baselines (>350).
        """)

    # Causal Confounding Disclaimer Callout
    st.markdown("""
    <div class="audit-box">
        ⚠️ <strong>Causal Attribution & Meteorological Confounding Disclaimer:</strong><br>
        A naive interpretation attributes the entirety of the post-Diwali AQI surge to firecracker emissions. 
        However, rigorous observational data analysis reveals two major confounders:
        <ol>
            <li><strong>Regional Agricultural Burning:</strong> Post-monsoon paddy stubble burning in Punjab and Haryana 
            peaks annually between October 25 and November 15, directly overlapping the Diwali calendar window.</li>
            <li><strong>Planetary Boundary Layer Height (PBLH) Collapse:</strong> As ambient temperatures plunge in late autumn, 
            the atmospheric mixing depth drops from &gt;1,500m to &lt;300m, concentrating all ground-level emissions regardless of source.</li>
            <li><strong>Sensor Ceiling Compression:</strong> When baseline pollution is already near 400 AQI, sensor capping at 500.0 compresses 
            the observable surge, artificially dampening measured effect sizes in mid-November years.</li>
        </ol>
        <em>Conclusion: True source apportionment requires chemical speciation (e.g. potassium/strontium tracers for pyrotechnics vs levoglucosan for biomass) or counterfactual chemical transport modeling (WRF-Chem).</em>
    </div>
    """, unsafe_allow_html=True)


# -----------------------------------------------------------------------------
# 4. GLOSSARY & REPRODUCIBILITY EXPANDER
# -----------------------------------------------------------------------------
with st.expander("📚 Metric Definitions, Denominators & Reproducibility Audit"):
    st.markdown("""
    | Metric | Formula / Calculation | Denominator | Handling of Missing / Ceiling |
    | :--- | :--- | :--- | :--- |
    | **Network Median AQI** | $\\text{Median}(AQI_{valid})$ across all active records | Valid station-days | Excludes missing; includes capped at 500.0 |
    | **Data Completeness Rate** | $\\frac{N_{valid}}{N_{total}} \\times 100$ | Total scheduled station-days (111,014) | Requires $\\ge 16$ valid hourly readings |
    | **Severe AQI Days %** | $\\frac{N(AQI > 400)}{N_{valid}} \\times 100$ | Valid station-days (100,794) | Excludes incomplete days |
    | **Sensor Capped Days %** | $\\frac{N(capped\\_hours > 0)}{N_{valid}} \\times 100$ | Valid station-days | Counts station-days with $\\ge 1$ capped hour |
    | **Winter Excess Elevation** | $\\text{Median}_{winter} - \\text{Median}_{non\\_winter}$ | Subsets by meteorological season | Audited via 14-day Moving Block Bootstrap |
    | **Station-Matched Diwali Surge** | $AQI_i(t+1) - AQI_i(t-1)$ | Matched station-year pairs active on both $t-1$ and $t+1$ (306 pooled pairs) | Discards unobserved station-days (no imputation) |
    """)
    st.caption("Delhi-NCR Air Quality Analysis Portfolio Project | Built with Python, PostgreSQL, Streamlit, and Power BI.")
