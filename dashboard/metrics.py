"""
dashboard/metrics.py
====================
Pure analytical functions and KPI computations for the Delhi-NCR Air Quality Dashboard.

Design Principles:
- Pure functions: inputs are DataFrames/parameters, outputs are structured dicts/DataFrames.
- Testable in isolation without Streamlit dependencies.
- Defensive: handles empty filter results, missing columns, and nulls gracefully.
- Grounded in official CPCB categories and audited Stage 2C statistical benchmarks.
"""

from typing import Dict, List, Optional, Tuple, Any
import numpy as np
import pandas as pd

# CPCB Statutory AQI Categories, Breakpoints, and Palette
CPCB_CATEGORIES = [
    "Good",
    "Satisfactory",
    "Moderate",
    "Poor",
    "Very Poor",
    "Severe"
]

CPCB_BREAKPOINTS = [
    (0, 50, "Good", "#00B050"),
    (51, 100, "Satisfactory", "#92D050"),
    (101, 200, "Moderate", "#FFFF00"),
    (201, 300, "Poor", "#FF9900"),
    (301, 400, "Very Poor", "#FF0000"),
    (401, 500, "Severe", "#800000"),
]

CPCB_COLOR_MAP = {
    "Good": "#00B050",          # Bright Green
    "Satisfactory": "#92D050",  # Light Green
    "Moderate": "#E6B800",      # Deep Gold/Yellow (accessible on white)
    "Poor": "#FF8C00",          # Dark Orange
    "Very Poor": "#E60000",      # Crimson Red
    "Severe": "#7A0019",         # Deep Maroon
}

# Pre-registered Diwali Dates for Context
DIWALI_DATES = {
    2017: "2017-10-19",
    2018: "2018-11-07",
    2019: "2019-10-27",
    2020: "2020-11-14",
    2021: "2021-11-04",
    2022: "2022-10-24",
    2023: "2023-11-12",
}


def filter_data(
    df: pd.DataFrame,
    cities: Optional[List[str]] = None,
    stations: Optional[List[str]] = None,
    date_range: Optional[Tuple[pd.Timestamp, pd.Timestamp]] = None,
    seasons: Optional[List[str]] = None,
    valid_only: bool = True,
) -> pd.DataFrame:
    """
    Filter daily AQI dataset defensively based on UI widget selections.

    Parameters
    ----------
    df : pd.DataFrame
        Fact daily AQI DataFrame.
    cities : list of str, optional
        Target cities to include. If None or empty, all cities retained.
    stations : list of str, optional
        Target station keys or names to include. If None or empty, all retained.
    date_range : tuple of (start_date, end_date), optional
        Inclusive date window.
    seasons : list of str, optional
        Target seasons to include.
    valid_only : bool, default True
        If True, filters to is_day_valid == True (completeness >= 16 hrs/day).

    Returns
    -------
    pd.DataFrame
        Filtered subset view.
    """
    if df.empty:
        return df.copy()

    filtered = df

    if valid_only and "is_day_valid" in filtered.columns:
        filtered = filtered[filtered["is_day_valid"] == True]

    if cities:
        filtered = filtered[filtered["city"].isin(cities)]

    if stations:
        # Match against station_name or station_key
        station_mask = (filtered["station_name"].isin(stations)) | (
            filtered["station_key"].isin(stations)
        )
        filtered = filtered[station_mask]

    if date_range is not None and len(date_range) == 2:
        start_date, end_date = pd.to_datetime(date_range[0]), pd.to_datetime(date_range[1])
        if "date" in filtered.columns:
            filtered = filtered[(filtered["date"] >= start_date) & (filtered["date"] <= end_date)]

    if seasons:
        if "season" in filtered.columns:
            filtered = filtered[filtered["season"].isin(seasons)]

    return filtered


def compute_kpis(df: pd.DataFrame, total_scheduled_days: Optional[int] = None) -> Dict[str, Any]:
    """
    Compute core headline KPIs for the active dataset filter.

    Parameters
    ----------
    df : pd.DataFrame
        Daily fact records (already filtered for active scope or valid subset).
    total_scheduled_days : int, optional
        Total scheduled/monitored station-days in active filter scope prior to
        validity filtering. When provided, preserves the true data completeness
        ratio: valid_days / total_scheduled_days * 100.

    Returns
    -------
    dict
        Dictionary containing headline values, formatted strings, and counts.
    """
    if df.empty:
        return {
            "median_aqi": np.nan,
            "mean_aqi": np.nan,
            "total_station_days": 0,
            "valid_station_days": 0,
            "completeness_pct": 0.0,
            "severe_days_count": 0,
            "severe_days_pct": 0.0,
            "capped_days_count": 0,
            "capped_days_pct": 0.0,
            "min_aqi": np.nan,
            "max_aqi": np.nan,
            "iqr_aqi": np.nan,
            "active_stations_count": 0,
        }

    # Identify valid records
    if "is_day_valid" in df.columns:
        valid_df = df[df["is_day_valid"] == True]
        valid_days = len(valid_df)
    else:
        valid_df = df[df["daily_mean_aqi"].notna()]
        valid_days = len(valid_df)

    # Use total_scheduled_days if provided, else length of input DataFrame
    total_days = total_scheduled_days if (total_scheduled_days is not None and total_scheduled_days > 0) else len(df)

    if valid_df.empty:
        return {
            "median_aqi": np.nan,
            "mean_aqi": np.nan,
            "total_station_days": total_days,
            "valid_station_days": 0,
            "completeness_pct": 0.0,
            "severe_days_count": 0,
            "severe_days_pct": 0.0,
            "capped_days_count": 0,
            "capped_days_pct": 0.0,
            "min_aqi": np.nan,
            "max_aqi": np.nan,
            "iqr_aqi": np.nan,
            "active_stations_count": df["station_key"].nunique() if "station_key" in df.columns else 0,
        }

    aqi_series = valid_df["daily_mean_aqi"].dropna()
    median_val = float(aqi_series.median())
    mean_val = float(aqi_series.mean())
    min_val = float(aqi_series.min())
    max_val = float(aqi_series.max())
    p25 = float(np.percentile(aqi_series, 25))
    p75 = float(np.percentile(aqi_series, 75))
    iqr_val = p75 - p25

    # Completeness rate
    completeness_pct = (valid_days / total_days * 100.0) if total_days > 0 else 0.0

    # Severe days (> 400 AQI)
    severe_mask = valid_df["daily_mean_aqi"] > 400.0
    severe_count = int(severe_mask.sum())
    severe_pct = (severe_count / valid_days * 100.0) if valid_days > 0 else 0.0

    # Capped days (capped_hours_count > 0)
    if "capped_hours_count" in valid_df.columns:
        capped_mask = valid_df["capped_hours_count"] > 0
        capped_count = int(capped_mask.sum())
        capped_pct = (capped_count / valid_days * 100.0) if valid_days > 0 else 0.0
    else:
        capped_count = 0
        capped_pct = 0.0

    active_stations = valid_df["station_key"].nunique() if "station_key" in valid_df.columns else 0

    return {
        "median_aqi": round(median_val, 2),
        "mean_aqi": round(mean_val, 2),
        "total_station_days": total_days,
        "valid_station_days": valid_days,
        "completeness_pct": round(completeness_pct, 2),
        "severe_days_count": severe_count,
        "severe_days_pct": round(severe_pct, 2),
        "capped_days_count": capped_count,
        "capped_days_pct": round(capped_pct, 2),
        "min_aqi": round(min_val, 2),
        "max_aqi": round(max_val, 2),
        "p25_aqi": round(p25, 2),
        "p75_aqi": round(p75, 2),
        "iqr_aqi": round(iqr_val, 2),
        "active_stations_count": active_stations,
    }


def compute_monthly_trend(df: pd.DataFrame) -> pd.DataFrame:
    """
    Compute monthly aggregated median, mean, and IQR AQI time-series.

    Parameters
    ----------
    df : pd.DataFrame
        Daily fact records.

    Returns
    -------
    pd.DataFrame
        Sorted monthly records with year_month, median, mean, p25, p75.
    """
    if df.empty or "date" not in df.columns:
        return pd.DataFrame(
            columns=["year_month", "year", "month", "median_aqi", "mean_aqi", "p25_aqi", "p75_aqi", "count"]
        )

    valid_df = df[df["is_day_valid"] == True] if "is_day_valid" in df.columns else df
    if valid_df.empty:
        return pd.DataFrame(
            columns=["year_month", "year", "month", "median_aqi", "mean_aqi", "p25_aqi", "p75_aqi", "count"]
        )

    # Work on a copy with date as period/timestamp
    vdf = valid_df.copy()
    vdf["year_month"] = pd.to_datetime(vdf["date"]).dt.to_period("M").dt.to_timestamp()

    grouped = vdf.groupby("year_month")["daily_mean_aqi"].agg(
        median_aqi="median",
        mean_aqi="mean",
        p25_aqi=lambda x: np.percentile(x.dropna(), 25) if len(x.dropna()) > 0 else np.nan,
        p75_aqi=lambda x: np.percentile(x.dropna(), 75) if len(x.dropna()) > 0 else np.nan,
        count="count",
    ).reset_index()

    grouped["year"] = grouped["year_month"].dt.year
    grouped["month"] = grouped["year_month"].dt.month
    grouped = grouped.sort_values("year_month").reset_index(drop=True)

    # Round numeric values
    for col in ["median_aqi", "mean_aqi", "p25_aqi", "p75_aqi"]:
        grouped[col] = grouped[col].round(2)

    return grouped


def compute_city_summary(df: pd.DataFrame) -> pd.DataFrame:
    """
    Compute city-by-city analytical rankings and summary statistics.

    Parameters
    ----------
    df : pd.DataFrame
        Daily fact records.

    Returns
    -------
    pd.DataFrame
        Sorted summary table by median AQI descending.
    """
    cols = ["city", "valid_station_days", "median_aqi", "mean_aqi", "severe_days_pct", "capped_days_pct", "stations_count"]
    if df.empty or "city" not in df.columns:
        return pd.DataFrame(columns=cols)

    valid_df = df[df["is_day_valid"] == True] if "is_day_valid" in df.columns else df
    if valid_df.empty:
        return pd.DataFrame(columns=cols)

    records = []
    for city, grp in valid_df.groupby("city"):
        aqi = grp["daily_mean_aqi"].dropna()
        n_days = len(aqi)
        if n_days == 0:
            continue
        med = float(aqi.median())
        mean_val = float(aqi.mean())
        sev_pct = float((aqi > 400).sum() / n_days * 100.0)
        capped_pct = float((grp["capped_hours_count"] > 0).sum() / n_days * 100.0) if "capped_hours_count" in grp.columns else 0.0
        n_stations = grp["station_key"].nunique() if "station_key" in grp.columns else 0

        records.append({
            "city": city,
            "valid_station_days": n_days,
            "median_aqi": round(med, 2),
            "mean_aqi": round(mean_val, 2),
            "severe_days_pct": round(sev_pct, 2),
            "capped_days_pct": round(capped_pct, 2),
            "stations_count": n_stations,
        })

    res = pd.DataFrame(records)
    if not res.empty:
        res = res.sort_values("median_aqi", ascending=False).reset_index(drop=True)
    return res


def compute_category_distribution(df: pd.DataFrame) -> pd.DataFrame:
    """
    Compute distribution of records across the 6 statutory CPCB AQI categories.

    Parameters
    ----------
    df : pd.DataFrame
        Daily fact records.

    Returns
    -------
    pd.DataFrame
        Table with category, count, percentage, and hex color code.
    """
    cols = ["category", "count", "percentage", "color"]
    if df.empty:
        return pd.DataFrame([
            {"category": cat, "count": 0, "percentage": 0.0, "color": CPCB_COLOR_MAP[cat]}
            for cat in CPCB_CATEGORIES
        ])

    valid_df = df[df["is_day_valid"] == True] if "is_day_valid" in df.columns else df
    total_valid = len(valid_df)

    if total_valid == 0:
        return pd.DataFrame([
            {"category": cat, "count": 0, "percentage": 0.0, "color": CPCB_COLOR_MAP[cat]}
            for cat in CPCB_CATEGORIES
        ])

    # If daily_category is already computed, use it; else derive from daily_mean_aqi
    if "daily_category" in valid_df.columns:
        counts = valid_df["daily_category"].value_counts().to_dict()
    else:
        # Bin on the fly
        def assign_cpcb(val):
            if pd.isna(val):
                return np.nan
            if val <= 50:
                return "Good"
            elif val <= 100:
                return "Satisfactory"
            elif val <= 200:
                return "Moderate"
            elif val <= 300:
                return "Poor"
            elif val <= 400:
                return "Very Poor"
            else:
                return "Severe"
        cats = valid_df["daily_mean_aqi"].apply(assign_cpcb)
        counts = cats.value_counts().to_dict()

    rows = []
    for cat in CPCB_CATEGORIES:
        cnt = int(counts.get(cat, 0))
        pct = round(cnt / total_valid * 100.0, 2)
        rows.append({
            "category": cat,
            "count": cnt,
            "percentage": pct,
            "color": CPCB_COLOR_MAP[cat],
        })

    return pd.DataFrame(rows)


def compute_seasonal_comparison(df: pd.DataFrame) -> Dict[str, Any]:
    """
    Compute rigorous seasonal statistics comparing Winter vs Non-Winter.

    Parameters
    ----------
    df : pd.DataFrame
        Daily fact records.

    Returns
    -------
    dict
        Detailed comparison metrics, ratios, IQRs, and seasonal table.
    """
    if df.empty or "is_winter" not in df.columns:
        return {
            "winter_median": np.nan,
            "non_winter_median": np.nan,
            "winter_mean": np.nan,
            "non_winter_mean": np.nan,
            "absolute_diff": np.nan,
            "ratio": np.nan,
            "winter_iqr": np.nan,
            "non_winter_iqr": np.nan,
            "winter_days": 0,
            "non_winter_days": 0,
            "by_season": pd.DataFrame(),
        }

    valid_df = df[df["is_day_valid"] == True] if "is_day_valid" in df.columns else df
    w_df = valid_df[valid_df["is_winter"] == True]["daily_mean_aqi"].dropna()
    nw_df = valid_df[valid_df["is_winter"] == False]["daily_mean_aqi"].dropna()

    w_med = float(w_df.median()) if len(w_df) > 0 else np.nan
    nw_med = float(nw_df.median()) if len(nw_df) > 0 else np.nan
    w_mean = float(w_df.mean()) if len(w_df) > 0 else np.nan
    nw_mean = float(nw_df.mean()) if len(nw_df) > 0 else np.nan

    diff = w_med - nw_med if not np.isnan(w_med) and not np.isnan(nw_med) else np.nan
    ratio = w_med / nw_med if nw_med and nw_med > 0 else np.nan

    w_iqr = float(np.percentile(w_df, 75) - np.percentile(w_df, 25)) if len(w_df) > 0 else np.nan
    nw_iqr = float(np.percentile(nw_df, 75) - np.percentile(nw_df, 25)) if len(nw_df) > 0 else np.nan

    # Breakdown across all meteorological seasons if season column exists
    season_records = []
    if "season" in valid_df.columns:
        season_order = ["Winter", "Summer / Pre-Monsoon", "Monsoon", "Post-Monsoon", "Transition (Feb)"]
        for s in season_order:
            sub = valid_df[valid_df["season"] == s]["daily_mean_aqi"].dropna()
            if len(sub) > 0:
                season_records.append({
                    "season": s,
                    "count": len(sub),
                    "median_aqi": round(float(sub.median()), 2),
                    "mean_aqi": round(float(sub.mean()), 2),
                    "p25_aqi": round(float(np.percentile(sub, 25)), 2),
                    "p75_aqi": round(float(np.percentile(sub, 75)), 2),
                    "severe_pct": round(float((sub > 400).sum() / len(sub) * 100.0), 2),
                })
    by_season_df = pd.DataFrame(season_records)

    return {
        "winter_median": round(w_med, 2) if not np.isnan(w_med) else np.nan,
        "non_winter_median": round(nw_med, 2) if not np.isnan(nw_med) else np.nan,
        "winter_mean": round(w_mean, 2) if not np.isnan(w_mean) else np.nan,
        "non_winter_mean": round(nw_mean, 2) if not np.isnan(nw_mean) else np.nan,
        "absolute_diff": round(diff, 2) if not np.isnan(diff) else np.nan,
        "ratio": round(ratio, 2) if not np.isnan(ratio) else np.nan,
        "winter_iqr": round(w_iqr, 2) if not np.isnan(w_iqr) else np.nan,
        "non_winter_iqr": round(nw_iqr, 2) if not np.isnan(nw_iqr) else np.nan,
        "winter_days": len(w_df),
        "non_winter_days": len(nw_df),
        "by_season": by_season_df,
    }


def compute_station_rankings(
    df: pd.DataFrame, top_n: int = 10, min_records: int = 100
) -> Dict[str, pd.DataFrame]:
    """
    Compute top N most polluted and top N cleanest monitoring stations.

    Parameters
    ----------
    df : pd.DataFrame
        Daily fact records.
    top_n : int, default 10
        Number of stations to rank.
    min_records : int, default 100
        Minimum valid recorded days to qualify for ranking (prevents artifactual outlier rankings).

    Returns
    -------
    dict
        {"top_polluted": DataFrame, "cleanest": DataFrame}
    """
    cols = ["rank", "station_name", "city", "valid_days", "median_aqi", "mean_aqi", "severe_days_pct", "capped_hours_pct"]
    if df.empty or "station_name" not in df.columns:
        return {"top_polluted": pd.DataFrame(columns=cols), "cleanest": pd.DataFrame(columns=cols)}

    valid_df = df[df["is_day_valid"] == True] if "is_day_valid" in df.columns else df
    if valid_df.empty:
        return {"top_polluted": pd.DataFrame(columns=cols), "cleanest": pd.DataFrame(columns=cols)}

    station_records = []
    for st_name, grp in valid_df.groupby("station_name"):
        aqi = grp["daily_mean_aqi"].dropna()
        n = len(aqi)
        if n < min_records:
            continue
        med = float(aqi.median())
        mean_val = float(aqi.mean())
        sev_pct = float((aqi > 400).sum() / n * 100.0)
        capped_pct = float((grp["capped_hours_count"] > 0).sum() / n * 100.0) if "capped_hours_count" in grp.columns else 0.0
        city = grp["city"].iloc[0] if "city" in grp.columns else "Unknown"

        station_records.append({
            "station_name": st_name,
            "city": city,
            "valid_days": n,
            "median_aqi": round(med, 2),
            "mean_aqi": round(mean_val, 2),
            "severe_days_pct": round(sev_pct, 2),
            "capped_hours_pct": round(capped_pct, 2),
        })

    rank_df = pd.DataFrame(station_records)
    if rank_df.empty:
        return {"top_polluted": pd.DataFrame(columns=cols), "cleanest": pd.DataFrame(columns=cols)}

    # Top polluted: highest median AQI
    top_polluted = rank_df.sort_values("median_aqi", ascending=False).head(top_n).reset_index(drop=True)
    top_polluted.insert(0, "rank", range(1, len(top_polluted) + 1))

    # Cleanest: lowest median AQI
    cleanest = rank_df.sort_values("median_aqi", ascending=True).head(top_n).reset_index(drop=True)
    cleanest.insert(0, "rank", range(1, len(cleanest) + 1))

    return {
        "top_polluted": top_polluted,
        "cleanest": cleanest,
    }


def compute_diwali_event_analysis(df: pd.DataFrame) -> Dict[str, Any]:
    """
    Perform event-study analysis for Diwali pollution shocks (t-7 to t+7).

    Evaluates:
    1. Daily median AQI trajectory across relative event days (-7 to +7).
    2. Station-matched paired differences: AQI(t+1) - AQI(t-1) for stations active on both days.
    3. Yearly event summary contrasting Late October vs Mid November Diwali timing.

    Parameters
    ----------
    df : pd.DataFrame
        Daily fact records.

    Returns
    -------
    dict
        Timeline DataFrame, paired differences summary, and yearly breakdown table.
    """
    if df.empty or "diwali_relative_day" not in df.columns:
        return {
            "timeline": pd.DataFrame(),
            "yearly_paired_diff": pd.DataFrame(),
            "overall_paired_diff": {},
            "timing_cohort_summary": pd.DataFrame(),
        }

    # Filter to valid days in the Diwali event window
    valid_mask = (df["is_day_valid"] == True) if "is_day_valid" in df.columns else df["daily_mean_aqi"].notna()
    event_df = df[valid_mask & (df["diwali_relative_day"].between(-7, 7))].copy()

    if event_df.empty:
        return {
            "timeline": pd.DataFrame(),
            "yearly_paired_diff": pd.DataFrame(),
            "overall_paired_diff": {},
            "timing_cohort_summary": pd.DataFrame(),
        }

    # 1. Timeline: Median AQI per relative day by year & overall
    timeline_grp = event_df.groupby(["year", "diwali_relative_day"])["daily_mean_aqi"].agg(
        median_aqi="median",
        mean_aqi="mean",
        count="count"
    ).reset_index()

    overall_timeline = event_df.groupby("diwali_relative_day")["daily_mean_aqi"].agg(
        median_aqi="median",
        mean_aqi="mean",
        count="count"
    ).reset_index()
    overall_timeline["year"] = "All Years Combined"

    comb_timeline = pd.concat([timeline_grp, overall_timeline], ignore_index=True)
    comb_timeline["median_aqi"] = comb_timeline["median_aqi"].round(2)
    comb_timeline["mean_aqi"] = comb_timeline["mean_aqi"].round(2)

    # 2. Station-Matched Paired Differences (t+1 vs t-1)
    years = sorted(event_df["year"].unique())
    yearly_diff_records = []
    all_paired_changes = []

    for yr in years:
        yr_data = event_df[event_df["year"] == yr]
        pre = yr_data[yr_data["diwali_relative_day"] == -1].set_index("station_key")["daily_mean_aqi"]
        post = yr_data[yr_data["diwali_relative_day"] == 1].set_index("station_key")["daily_mean_aqi"]
        
        common_stations = pre.index.intersection(post.index)
        if len(common_stations) == 0:
            continue

        paired_pre = pre.loc[common_stations]
        paired_post = post.loc[common_stations]
        diffs = paired_post - paired_pre

        mean_diff = float(diffs.mean())
        med_diff = float(diffs.median())
        pct_elevated = float((diffs > 0).sum() / len(diffs) * 100.0)
        baseline_med = float(paired_pre.median())
        post_med = float(paired_post.median())

        # Determine timing cohort: Late October vs Mid November
        diwali_date = DIWALI_DATES.get(yr, "Unknown")
        month = int(diwali_date.split("-")[1]) if "-" in diwali_date else 11
        timing_cohort = "Late October" if month == 10 else "Mid November"

        yearly_diff_records.append({
            "year": yr,
            "diwali_date": diwali_date,
            "timing_cohort": timing_cohort,
            "matched_stations": len(common_stations),
            "pre_diwali_median": round(baseline_med, 2),
            "post_diwali_median": round(post_med, 2),
            "mean_paired_change": round(mean_diff, 2),
            "median_paired_change": round(med_diff, 2),
            "pct_stations_elevated": round(pct_elevated, 2),
        })
        all_paired_changes.extend(diffs.tolist())

    yearly_diff_df = pd.DataFrame(yearly_diff_records)

    # Cohort comparison: Late Oct vs Mid Nov
    cohort_summary = pd.DataFrame()
    if not yearly_diff_df.empty and "timing_cohort" in yearly_diff_df.columns:
        cohort_summary = yearly_diff_df.groupby("timing_cohort").agg(
            years_count=("year", "count"),
            avg_pre_median=("pre_diwali_median", "mean"),
            avg_post_median=("post_diwali_median", "mean"),
            avg_mean_change=("mean_paired_change", "mean"),
            avg_median_change=("median_paired_change", "mean"),
            avg_pct_elevated=("pct_stations_elevated", "mean"),
        ).reset_index().round(2)

    overall_stats = {}
    if len(all_paired_changes) > 0:
        overall_stats = {
            "total_pairs": len(all_paired_changes),
            "mean_change": round(float(np.mean(all_paired_changes)), 2),
            "median_change": round(float(np.median(all_paired_changes)), 2),
            "pct_elevated": round(float(np.sum(np.array(all_paired_changes) > 0) / len(all_paired_changes) * 100.0), 2),
        }

    return {
        "timeline": comb_timeline,
        "yearly_paired_diff": yearly_diff_df,
        "overall_paired_diff": overall_stats,
        "timing_cohort_summary": cohort_summary,
    }
