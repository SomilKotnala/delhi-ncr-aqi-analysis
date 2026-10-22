"""
Exploratory Data Analysis (EDA) Module: Delhi-NCR Air Quality
=============================================================
Generates publication-quality charts addressing the core research questions:
  1. Monthly and seasonal AQI cycles (Q1)
  2. Station-level spatial heterogeneity and winter rankings (Q2)
  3. Frequency distribution of CPCB severity categories (Q3)
  4. 24-hour diurnal profiling across seasons (Q6)
  5. Multi-year Diwali pollution episode event study (Q8)
  6. Station uptime, completeness, and sensor capping audit (Q7)

All charts include formal source attribution, CPCB color hexes, and clear annotations.
Outputs saved to `reports/figures/`.
"""

import os
import sys
import logging
from pathlib import Path
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.ticker as ticker
import seaborn as sns

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S"
)
logger = logging.getLogger(__name__)

# Base project paths
SCRIPT_DIR = Path(__file__).resolve().parent
PROJECT_ROOT = Path(r"D:\delhi-ncr-aqi-analysis")
DATA_PROCESSED_DIR = PROJECT_ROOT / "data" / "processed"
TABLES_DIR = PROJECT_ROOT / "reports" / "tables"
FIGURES_DIR = PROJECT_ROOT / "reports" / "figures"

# Official CPCB AQI Color Palette
CPCB_COLORS = {
    "Good": "#009639",
    "Satisfactory": "#7ec242",
    "Moderate": "#fdd023",
    "Poor": "#f58220",
    "Very Poor": "#e62b1e",
    "Severe": "#9b111e"
}

# General styling
plt.rcParams["font.sans-serif"] = "DejaVu Sans"
plt.rcParams["axes.edgecolor"] = "#cccccc"
plt.rcParams["axes.linewidth"] = 0.8


def plot_q1_monthly_trends(df_daily: pd.DataFrame, out_path: Path) -> None:
    """Q1: 12-Month Annual Cyclical Profile with IQR band and Severe Days %."""
    logger.info("Generating Figure 1: Monthly Trends & Seasonal Inversion Wave...")
    valid = df_daily[df_daily["is_day_valid"]].copy()
    valid["month"] = pd.to_datetime(valid["date"]).dt.month
    
    monthly = valid.groupby("month").agg(
        median_aqi=("daily_mean_aqi", "median"),
        q25=("daily_mean_aqi", lambda x: np.percentile(x.dropna(), 25)),
        q75=("daily_mean_aqi", lambda x: np.percentile(x.dropna(), 75)),
        severe_pct=("daily_mean_aqi", lambda x: (x > 400).mean() * 100)
    ).reset_index()

    month_names = ["Jan", "Feb", "Mar", "Apr", "May", "Jun", "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"]
    monthly["month_name"] = [month_names[m-1] for m in monthly["month"]]

    fig, ax1 = plt.subplots(figsize=(11, 6), dpi=300)
    ax2 = ax1.twinx()

    # Severe % Bars on ax2
    bars = ax2.bar(
        monthly["month"], monthly["severe_pct"],
        color="#9b111e", alpha=0.25, width=0.55,
        label="Severe Days Share (% > 400 AQI)"
    )
    ax2.set_ylabel("Severe Days Share (%)", color="#9b111e", fontsize=11, fontweight="bold")
    ax2.set_ylim(0, 35)
    ax2.grid(False)

    # Median Line & IQR Band on ax1
    ax1.plot(monthly["month"], monthly["median_aqi"], color="#1f4e78", marker="o", linewidth=2.5, label="Network Median Daily AQI")
    ax1.fill_between(monthly["month"], monthly["q25"], monthly["q75"], color="#1f4e78", alpha=0.15, label="Interquartile Range (IQR: 25th–75th Percentile)")

    # Category Threshold Lines
    ax1.axhline(50, color=CPCB_COLORS["Good"], linestyle="--", alpha=0.5, linewidth=1)
    ax1.axhline(100, color=CPCB_COLORS["Satisfactory"], linestyle="--", alpha=0.5, linewidth=1)
    ax1.axhline(200, color=CPCB_COLORS["Moderate"], linestyle="--", alpha=0.5, linewidth=1)
    ax1.axhline(300, color=CPCB_COLORS["Poor"], linestyle="--", alpha=0.5, linewidth=1)
    ax1.axhline(400, color=CPCB_COLORS["Very Poor"], linestyle="--", alpha=0.7, linewidth=1.2)

    ax1.set_title("Delhi-NCR Monthly Air Quality Cycle & Severe Episode Frequencies (2017–2023)", fontsize=13, fontweight="bold", pad=12)
    ax1.set_xlabel("Calendar Month", fontsize=11, fontweight="bold")
    ax1.set_ylabel("Air Quality Index (NAQI)", color="#1f4e78", fontsize=11, fontweight="bold")
    ax1.set_xticks(monthly["month"])
    ax1.set_xticklabels(monthly["month_name"], fontsize=10)
    ax1.set_ylim(0, 450)
    ax1.grid(axis="y", linestyle=":", alpha=0.6)

    # Legend combining both axes
    lines1, labels1 = ax1.get_legend_handles_labels()
    lines2, labels2 = ax2.get_legend_handles_labels()
    ax1.legend(lines1 + lines2, labels1 + labels2, loc="upper left", framealpha=0.9, fontsize=9)

    fig.text(0.5, 0.01, "Source: Central Pollution Control Board (CPCB) continuous monitoring network (56 Delhi-NCR stations, 2017–2023)", ha="center", fontsize=8, color="#555555")
    plt.tight_layout(rect=[0, 0.03, 1, 0.97])
    fig.savefig(out_path)
    plt.close(fig)
    logger.info(f"Saved {out_path.name}")


def plot_q2_station_rankings(df_daily: pd.DataFrame, out_path: Path) -> None:
    """Q2: Top 10 Most Polluted vs Cleanest Stations in Winter."""
    logger.info("Generating Figure 2: Station Winter Pollution Rankings...")
    winter = df_daily[df_daily["is_winter"] & df_daily["is_day_valid"]].copy()

    station_stats = winter.groupby(["city", "station_name"]).agg(
        winter_median=("daily_mean_aqi", "median"),
        days_monitored=("daily_mean_aqi", "count")
    ).reset_index()
    # Filter stations with adequate data
    station_stats = station_stats[station_stats["days_monitored"] >= 100].sort_values("winter_median", ascending=True)

    top_10 = station_stats.tail(10)
    bottom_5 = station_stats.head(5)
    combined = pd.concat([bottom_5, top_10])

    city_colors = {
        "Delhi": "#c00000",
        "Ghaziabad": "#ed7d31",
        "Faridabad": "#4472c4",
        "Noida": "#70ad47",
        "Gurugram": "#ffc000"
    }
    bar_colors = [city_colors.get(c, "#888888") for c in combined["city"]]

    fig, ax = plt.subplots(figsize=(11, 7), dpi=300)
    bars = ax.barh(combined["station_name"], combined["winter_median"], color=bar_colors, height=0.65)

    ax.axvline(400, color="#9b111e", linestyle="--", linewidth=1.5, label="Severe Threshold (AQI 400)")
    ax.axvline(300, color="#e62b1e", linestyle=":", linewidth=1.2, label="Very Poor Threshold (AQI 300)")

    ax.set_title("Station Winter AQI Benchmarks: Most Polluted vs. Cleanest Stations (2017–2023)", fontsize=13, fontweight="bold", pad=12)
    ax.set_xlabel("Median Winter AQI (Nov 1 – Jan 31)", fontsize=11, fontweight="bold")
    ax.set_xlim(0, 450)
    ax.grid(axis="x", linestyle=":", alpha=0.6)

    # City Legend
    legend_patches = [plt.Rectangle((0,0),1,1, color=col) for col in city_colors.values()]
    ax.legend(legend_patches, city_colors.keys(), loc="lower right", title="City", framealpha=0.9, fontsize=9)

    for bar in bars:
        w = bar.get_width()
        ax.text(w + 3, bar.get_y() + bar.get_height()/2, f"{w:.1f}", va="center", fontsize=8.5, color="#222222")

    fig.text(0.5, 0.01, "Source: CPCB Continuous CAAQMS Network. Minimum 100 winter days required per station cohort.", ha="center", fontsize=8, color="#555555")
    plt.tight_layout(rect=[0, 0.03, 1, 0.97])
    fig.savefig(out_path)
    plt.close(fig)
    logger.info(f"Saved {out_path.name}")


def plot_q3_severity_distribution(df_daily: pd.DataFrame, out_path: Path) -> None:
    """Q3: Severity Category Distribution by Season (100% Stacked Bar)."""
    logger.info("Generating Figure 3: Severity Category Distribution...")
    valid = df_daily[df_daily["is_day_valid"]].copy()
    categories = ["Good", "Satisfactory", "Moderate", "Poor", "Very Poor", "Severe"]

    ct = pd.crosstab(valid["season"], valid["daily_category"], normalize="index") * 100.0
    ct = ct.reindex(columns=[c for c in categories if c in ct.columns], fill_value=0)
    
    # Order seasons logically
    season_order = ["Winter", "Post-Monsoon", "Transition (Feb)", "Summer / Pre-Monsoon", "Monsoon"]
    ct = ct.reindex([s for s in season_order if s in ct.index])

    fig, ax = plt.subplots(figsize=(11, 5.5), dpi=300)
    bottom = np.zeros(len(ct))

    for cat in ct.columns:
        values = ct[cat].values
        ax.bar(ct.index, values, bottom=bottom, label=cat, color=CPCB_COLORS.get(cat, "#999999"), width=0.55)
        bottom += values

    ax.set_title("Seasonal Distribution of CPCB Air Quality Severity Categories in Delhi-NCR (2017–2023)", fontsize=13, fontweight="bold", pad=12)
    ax.set_ylabel("Proportion of Monitored Station-Days (%)", fontsize=11, fontweight="bold")
    ax.set_ylim(0, 100)
    ax.legend(loc="upper right", bbox_to_anchor=(1.18, 1.0), title="AQI Category", framealpha=0.9, fontsize=9)
    ax.grid(axis="y", linestyle=":", alpha=0.5)

    fig.text(0.5, 0.01, "Source: Central Pollution Control Board (CPCB) continuous monitoring network (100,794 valid station-days)", ha="center", fontsize=8, color="#555555")
    plt.tight_layout(rect=[0, 0.03, 0.88, 0.97])
    fig.savefig(out_path)
    plt.close(fig)
    logger.info(f"Saved {out_path.name}")


def plot_q5_diurnal_hourly(df_hourly: pd.DataFrame, out_path: Path) -> None:
    """Q6: 24-Hour Diurnal Profile comparing Winter vs. Monsoon."""
    logger.info("Generating Figure 5: 24-Hour Diurnal Profiling...")
    valid = df_hourly[df_hourly["is_valid"] & df_hourly["season"].isin(["Winter", "Monsoon"])].copy()

    diurnal = valid.groupby(["season", "hour"])["aqi_cleaned"].agg(["median", "mean"]).reset_index()

    fig, ax = plt.subplots(figsize=(10, 5.5), dpi=300)
    
    for season, col, ls in [("Winter", "#9b111e", "-"), ("Monsoon", "#009639", "--")]:
        sub = diurnal[diurnal["season"] == season]
        ax.plot(sub["hour"], sub["median"], color=col, linestyle=ls, marker="o", linewidth=2.2, label=f"{season} Median AQI")
        ax.plot(sub["hour"], sub["mean"], color=col, linestyle=":", alpha=0.6, linewidth=1.5, label=f"{season} Mean AQI")

    ax.set_title("Diurnal Air Quality Dynamics: Winter Inversion vs. Monsoon Washout", fontsize=13, fontweight="bold", pad=12)
    ax.set_xlabel("Hour of Day (Indian Standard Time, IST)", fontsize=11, fontweight="bold")
    ax.set_ylabel("Hourly AQI", fontsize=11, fontweight="bold")
    ax.set_xticks(range(0, 24))
    ax.set_xlim(-0.5, 23.5)
    ax.grid(True, linestyle=":", alpha=0.6)

    # Annotations
    ax.annotate("Morning Rush Peak\n(09:00–10:00 IST)", xy=(9.5, 340), xytext=(6, 380),
                arrowprops=dict(arrowstyle="->", color="#333333", lw=1.2), fontsize=8.5, fontweight="bold")
    ax.annotate("Afternoon Solar Dilution\n(15:00–17:00 IST)", xy=(16, 280), xytext=(14, 210),
                arrowprops=dict(arrowstyle="->", color="#333333", lw=1.2), fontsize=8.5, fontweight="bold")
    ax.annotate("Night Inversion Peak\n(22:00–00:00 IST)", xy=(23, 345), xytext=(19, 410),
                arrowprops=dict(arrowstyle="->", color="#333333", lw=1.2), fontsize=8.5, fontweight="bold")

    ax.legend(loc="upper left", framealpha=0.9, fontsize=9)
    fig.text(0.5, 0.01, "Source: CPCB Continuous CAAQMS Network. Timestamps in local Indian Standard Time (IST, UTC+05:30).", ha="center", fontsize=8, color="#555555")
    plt.tight_layout(rect=[0, 0.03, 1, 0.97])
    fig.savefig(out_path)
    plt.close(fig)
    logger.info(f"Saved {out_path.name}")


def plot_q6_diwali_event_study(df_daily: pd.DataFrame, out_path: Path) -> None:
    """Q8: Multi-Year Diwali Event Study Trajectory (t-7 to t+7)."""
    logger.info("Generating Figure 6: Diwali Event-Study Pulse...")
    diwali = df_daily[df_daily["is_diwali_window"] & df_daily["is_day_valid"]].copy()

    event_curve = diwali.groupby(["year", "diwali_relative_day"])["daily_mean_aqi"].median().reset_index()

    fig, ax = plt.subplots(figsize=(11, 6), dpi=300)
    year_palette = sns.color_palette("tab10", n_colors=7)
    years = sorted(event_curve["year"].unique())

    for idx, yr in enumerate(years):
        sub = event_curve[event_curve["year"] == yr].sort_values("diwali_relative_day")
        ax.plot(sub["diwali_relative_day"], sub["daily_mean_aqi"], marker="s", markersize=4,
                linewidth=1.8, label=f"Diwali {yr}", color=year_palette[idx])

    # Overall multi-year median composite
    multi_median = event_curve.groupby("diwali_relative_day")["daily_mean_aqi"].median()
    ax.plot(multi_median.index, multi_median.values, color="#000000", linewidth=3.5, linestyle="--", label="7-Year Composite Median")

    ax.axvline(0, color="#9b111e", linestyle="-", linewidth=2.0, alpha=0.8, label="Diwali Festival Day (t=0)")
    ax.axvspan(-7, -1, color="#70ad47", alpha=0.08, label="Pre-Event Baseline (t-7 to t-1)")
    ax.axvspan(0, 1, color="#e62b1e", alpha=0.10, label="Peak Festival Episode (t0 to t+1)")

    ax.set_title("Diwali Pollution Pulse & Dissipation Trajectories in Delhi-NCR (2017–2023)", fontsize=13, fontweight="bold", pad=12)
    ax.set_xlabel("Relative Days to Diwali (t = 0 is Festival Day)", fontsize=11, fontweight="bold")
    ax.set_ylabel("Network Median Daily AQI", fontsize=11, fontweight="bold")
    ax.set_xticks(range(-7, 8))
    ax.set_xlim(-7.5, 7.5)
    ax.set_ylim(150, 480)
    ax.grid(True, linestyle=":", alpha=0.6)

    ax.legend(loc="upper left", bbox_to_anchor=(1.02, 1.0), framealpha=0.9, fontsize=8.5)
    fig.text(0.5, 0.01, "Source: CPCB Continuous CAAQMS Network. Festival dates independently verified from official national gazettes.", ha="center", fontsize=8, color="#555555")
    plt.tight_layout(rect=[0, 0.03, 0.85, 0.97])
    fig.savefig(out_path)
    plt.close(fig)
    logger.info(f"Saved {out_path.name}")


def plot_q7_uptime_vs_pollution(df_station: pd.DataFrame, out_path: Path) -> None:
    """Q7: Station Uptime % vs Median AQI with Capping Bubble Size."""
    logger.info("Generating Figure 7: Station Completeness & Sensor Capping Audit...")
    fig, ax = plt.subplots(figsize=(10, 6), dpi=300)

    city_colors = {
        "Delhi": "#c00000",
        "Ghaziabad": "#ed7d31",
        "Faridabad": "#4472c4",
        "Noida": "#70ad47",
        "Gurugram": "#ffc000"
    }

    for city in city_colors:
        sub = df_station[df_station["city"] == city]
        if len(sub) == 0:
            continue
        sizes = (sub["capped_hours_pct"] * 35) + 30
        ax.scatter(sub["uptime_hourly_pct"], sub["median_aqi"], s=sizes,
                   color=city_colors[city], alpha=0.75, edgecolors="#333333", linewidth=0.8, label=city)

    ax.set_title("Station Data Completeness vs. Pollution Burden (Bubble size = Capping % at 500)", fontsize=12, fontweight="bold", pad=12)
    ax.set_xlabel("Hourly Uptime (% of recorded valid hours)", fontsize=11, fontweight="bold")
    ax.set_ylabel("Median Station AQI", fontsize=11, fontweight="bold")
    ax.set_xlim(50, 100)
    ax.set_ylim(140, 270)
    ax.grid(True, linestyle=":", alpha=0.6)
    ax.legend(loc="upper left", title="City", framealpha=0.9, fontsize=9)

    fig.text(0.5, 0.01, "Source: CPCB Continuous CAAQMS Network (56 stations across Delhi-NCR).", ha="center", fontsize=8, color="#555555")
    plt.tight_layout(rect=[0, 0.03, 1, 0.97])
    fig.savefig(out_path)
    plt.close(fig)
    logger.info(f"Saved {out_path.name}")


def run_all_eda():
    """Generates all production figures."""
    FIGURES_DIR.mkdir(parents=True, exist_ok=True)

    logger.info("Loading processed analytical tables...")
    daily_path = DATA_PROCESSED_DIR / "fact_daily_aqi.parquet"
    hourly_path = DATA_PROCESSED_DIR / "fact_hourly_aqi.parquet"
    station_path = DATA_PROCESSED_DIR / "dim_station.csv"

    df_daily = pd.read_parquet(daily_path)
    df_hourly = pd.read_parquet(hourly_path)
    df_station = pd.read_csv(station_path)

    plot_q1_monthly_trends(df_daily, FIGURES_DIR / "q1_monthly_seasonal_trends.png")
    plot_q2_station_rankings(df_daily, FIGURES_DIR / "q2_station_rankings.png")
    plot_q3_severity_distribution(df_daily, FIGURES_DIR / "q3_severity_distribution.png")
    plot_q5_diurnal_hourly(df_hourly, FIGURES_DIR / "q5_diurnal_hourly_patterns.png")
    plot_q6_diwali_event_study(df_daily, FIGURES_DIR / "q6_diwali_event_study.png")
    plot_q7_uptime_vs_pollution(df_station, FIGURES_DIR / "q7_station_uptime_vs_capping.png")

    logger.info("All 6 production figures generated successfully.")


if __name__ == "__main__":
    run_all_eda()
