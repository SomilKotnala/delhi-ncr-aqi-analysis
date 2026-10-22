# Analytical Limitations, Caveats, and Confounders

Every credible data analysis must transparently state data constraints, measurement artifacts, and methodological boundaries. Below are the core limitations identified during data inspection and validation.

---

## 1. Regulatory Reporting Ceiling vs. Physical Sensor Detection Limits (AQI = 500.0)

- **Observed Phenomenon**: In Delhi-NCR, exactly **53,656 hourly observations** are recorded at the upper ceiling of **500.0**.
- **Crucial Distinction: Reporting Ceiling vs. Physical Overload**:
  1. **Regulatory / Mathematical Reporting Ceiling**: The official CPCB National Air Quality Index (NAQI) formula mathematically truncates at **500.0**. When 24-hour average $\text{PM}_{2.5}$ exceeds $250\,\mu\text{g/m}^3$ and $\text{PM}_{10}$ exceeds $430\,\mu\text{g/m}^3$, the index equation reaches its defined ceiling. Even if ambient particulate concentrations reach $800\,\mu\text{g/m}^3$ or $1,200\,\mu\text{g/m}^3$, the reported AQI remains flat at 500. This is an **index-level reporting ceiling** (right-censoring of the composite score).
  2. **Physical Sensor Detection Limits**: Continuous CAAQMS beta attenuation monitors (BAM) and optical particle counters (OPC) possess physical optical mass detection limits (typically $1,000\text{--}5,000\,\mu\text{g/m}^3$). Physical detector saturation occurs when particulate density attenuates the optical or beta beam beyond dynamic range, triggering error codes or sensor dropouts (`<NA>`).
  3. **Out-of-Scale Anomalies (> 500)**: Exactly **10 observations** exceeded 500 (e.g., 3,303 and 3,797 at Sector 125 Noida in October 2017). These represent sensor communication glitches or raw calibration voltages that bypassed the NAQI calculation clipping logic.
- **Analytical Impact**: Because the composite index is right-censored at 500, standard Gaussian estimators (arithmetic mean and variance) systematically underestimate the true severity of peak episodic smog. Robust non-parametric metrics (medians, interquartile ranges, Cliff's delta) are strictly mandated.

---

## 2. Source Timezone Convention and Timestamp Normalization

- **Verification**: CPCB continuous stations operate on Indian Standard Time (IST, UTC+05:30). Diurnal analysis of raw columns confirms local time: afternoon solar boundary-layer mixing height dilution produces a diurnal minimum at 15:00–17:00 IST (168.6), while nighttime thermal inversion peaks at 22:00–00:00 IST (242.6).
- **Residual Uncertainty**: Raw CPCB data files do not embed explicit ISO 8601 offset strings (e.g., `+05:30`) in column headers. To resolve ambiguity across international BI tools and databases, our pipeline explicitly derives and stores both `timestamp_ist` (local) and `timestamp_utc` (UTC).

---

## 3. Dynamic Monitoring Coverage & Network Expansion (2017–2020)

- **Observed Phenomenon**: Station count in Delhi-NCR expanded substantially between 2017 and 2020:
  - **Early 2017**: Only ~15 continuous monitoring stations were operational (e.g., DTU, ITO, Mandir Marg, Punjabi Bagh, R K Puram, Shadipur, Sirifort, Vikas Sadan Gurugram, Sector-16A Faridabad).
  - **February 2018**: Delhi Pollution Control Committee (DPCC) commissioned 20+ continuous stations (e.g., Ashok Vihar, Jahangirpuri, Sonia Vihar, Okhla Phase-2, Rohini, Wazirpur).
  - **Mid-2018 to 2020**: Peripheral industrial and rural stations (Bawana, Mundka, Loni Ghaziabad, New Industrial Town Faridabad) began transmitting.
- **Analytical Impact**: Comparing simple network-wide annual averages between 2017 and 2023 introduces **spatial selection bias**. Adding high-pollution industrial hotspots (like Mundka and Bawana) pushes network averages upward regardless of baseline trends. Multi-year comparisons must either:
  1. Restrict analysis to the cohort of long-standing "anchor stations" active across all 7 years, or
  2. Implement station-level fixed-effects / normalized trend models.

---

## 4. Station Downtime and Non-Random Missingness

- **Observed Phenomenon**: 8.35% of total station-hours are missing (`<NA>`). Missingness ranges from 3.1% at highly reliable stations (e.g., Mandir Marg, Shadipur) to > 40% at intermittent stations (e.g., Burari Crossing, Chandni Chowk).
- **Analytical Impact**: Sensor dropouts are not strictly missing completely at random (MCAR). Equipment failures frequently occur during peak fog, high moisture, or severe pollution load. Imputing values naively could bias episode severity. Daily aggregations therefore require a minimum threshold of **$\ge 16$ valid hours per day** (67% completeness rule). Days with fewer than 16 valid hours are treated as missing at the daily grain.

---

## 5. Upstream Repository Station ID Duplication

- **Observed Phenomenon**: In the upstream `cpcb-aqi.parquet` file, the `Station ID` column contains identical values for all stations within a city (e.g., all 39 Delhi stations share `site_115`, all Faridabad stations share `site_5341`).
- **Underlying Cause**: Upstream ingestion mapped the parent archive stem to each record rather than extracting unique internal CPCB station IDs.
- **Remediation**: The `Station Name` column is fully distinct across all 56 locations. Our cleaning pipeline derives a slugified unique key (`station_key`, e.g., `delhi_anand_vihar`, `faridabad_sec16a`) to serve as the true relational primary key.

---

## 6. Confounding in Diwali Pollution Episodes: Observational Seasonal Comparison vs. Causal Counterfactual

- **Observed Phenomenon**: Elevated AQI is consistently observed in Delhi-NCR during the Diwali festival window across all 7 analyzed years (2017–2023), with 263 out of 306 valid station-year pairs (85.95%) exhibiting post-festival elevation.
- **Confounding Factors**:
  1. **Meteorological Inversion**: Late October to mid-November marks the seasonal onset of calm surface winds (< 1 m/s), plunging temperatures, and planetary boundary layer height (PBLH) collapse from ~1,500m to < 300m, trapping all ground emissions.
  2. **Agricultural Stubble Burning**: The post-monsoon paddy harvest in Punjab and Haryana involves open-field residue burning, generating smoke plumes transported south-eastward by prevailing winds.
  3. **Firework Emissions**: Episodic pulse of fine particulates and metallic tracers ($\text{Ba}, \text{Sr}, \text{K}$) concentrated within a 12-to-36 hour window.
- **Observational Comparison vs. Causal Counterfactual**:
  - Comparing **October Diwali** (2017, 2019, 2022: +58.92 pts pooled surge from a moderate baseline of 283 AQI) against **November Diwali** (2018, 2020, 2021, 2023: +93.92 pts pooled surge from an already-severe baseline of 374 AQI) provides a natural **observational seasonal comparison** against differing atmospheric regimes.
  - However, this comparison cannot be treated as a pure randomized causal counterfactual. Year-to-year shifts in festival calendar timing co-vary with meteorological variability and harvest progress.
- **Analytical Stance**: In the absence of high-resolution chemical transport modeling (e.g., WRF-Chem) or isotopic chemical speciation data, this project **does not make causal claims attributing the entire episode solely to firecrackers**. It treats the episode as an observed seasonal pulse with measurable pre-event, peak, and dissipation dynamics.
