# Analytical Limitations, Caveats, and Confounders

Every credible data analysis must transparently state data constraints, measurement artifacts, and methodological boundaries. Below are the core limitations identified during data inspection and validation.

---

## 1. Instrument Ceiling and Right-Censoring at AQI = 500

- **Observed Phenomenon**: In Delhi-NCR, exactly **53,656 hourly observations** are recorded at the upper saturation limit of **500.0**.
- **Underlying Cause**: The official CPCB National AQI sub-index formula caps the index at 500 when $\text{PM}_{2.5}$ exceeds $250\,\mu\text{g/m}^3$ and $\text{PM}_{10}$ exceeds $430\,\mu\text{g/m}^3$. In severe episodes, true particulate concentrations can reach $700\text{--}1,000\,\mu\text{g/m}^3$, yet the reported AQI remains flat at 500.
- **Analytical Impact**: This ceiling effect causes **right-censoring**. Standard parametric estimators (such as arithmetic mean and variance) systematically underestimate the true severity of peak pollution events. Robust non-parametric metrics (medians, interquartile ranges, survival/censored estimation) are necessary.

---

## 2. Dynamic Monitoring Coverage & Network Expansion (2017–2020)

- **Observed Phenomenon**: Station count in Delhi-NCR expanded substantially between 2017 and 2020:
  - **Early 2017**: Only ~15 continuous monitoring stations were operational (e.g., DTU, ITO, Mandir Marg, Punjabi Bagh, R K Puram, Shadipur, Sirifort, Vikas Sadan Gurugram, Sector-16A Faridabad).
  - **February 2018**: Delhi Pollution Control Committee (DPCC) commissioned 20+ continuous stations (e.g., Ashok Vihar, Jahangirpuri, Sonia Vihar, Okhla Phase-2, Rohini, Wazirpur).
  - **Mid-2018 to 2020**: Peripheral industrial and rural stations (Bawana, Mundka, Loni Ghaziabad, New Industrial Town Faridabad) began transmitting.
- **Analytical Impact**: Comparing simple network-wide annual averages between 2017 and 2023 introduces **spatial selection bias**. Adding high-pollution industrial hotspots (like Mundka and Bawana) pushes network averages upward regardless of baseline trends. Multi-year comparisons must either:
  1. Restrict analysis to the cohort of long-standing "anchor stations" active across all 7 years, or
  2. Implement station-level fixed-effects / normalized trend models.

---

## 3. Station Downtime and Non-Random Missingness

- **Observed Phenomenon**: 8.35% of total station-hours are missing (`<NA>`). Missingness ranges from 3.1% at highly reliable stations (e.g., Mandir Marg, Shadipur) to > 40% at intermittent stations (e.g., Burari Crossing, Chandni Chowk).
- **Analytical Impact**: Sensor dropouts are not strictly missing completely at random (MCAR). Equipment failures frequently occur during peak fog, high moisture, or severe pollution load. Imputing values naively could bias episode severity. Daily aggregations therefore require a minimum threshold of **$\ge 16$ valid hours per day** (67% completeness rule). Days with fewer than 16 valid hours are treated as missing at the daily grain.

---

## 4. Upstream Repository Station ID Duplication

- **Observed Phenomenon**: In the upstream `cpcb-aqi.parquet` file, the `Station ID` column contains identical values for all stations within a city (e.g., all 39 Delhi stations share `site_115`, all Faridabad stations share `site_5341`).
- **Underlying Cause**: Upstream ingestion mapped the parent archive stem to each record rather than extracting unique internal CPCB station IDs.
- **Remediation**: The `Station Name` column is fully distinct across all 56 locations. Our cleaning pipeline derives a slugified unique key (`station_key`, e.g., `delhi_anand_vihar`, `faridabad_sec16a`) to serve as the true relational primary key.

---

## 5. Confounding in Diwali Pollution Episodes

- **Observed Phenomenon**: Elevated AQI is consistently observed in Delhi-NCR during the Diwali festival window across all 7 analyzed years (2017–2023).
- **Confounding Factors**:
  1. **Meteorological Inversion**: Late October to mid-November marks the seasonal onset of calm surface winds (< 1 m/s), low ambient temperatures, and boundary-layer height collapse from ~1,500m to < 400m, trapping all ground emissions.
  2. **Agricultural Stubble Burning**: The post-monsoon harvest window in Punjab and Haryana involves widespread open-field residue burning, generating regional smoke plumes carried by north-westerly winds.
  3. **Firework Emissions**: Episodic pulse of metallic particulates ($\text{Ba}, \text{Sr}, \text{K}$) and sulfur dioxide concentrated within a 12-to-36 hour window.
- **Analytical Stance**: In the absence of high-resolution meteorological wind-trajectory simulations and chemical speciation data, this project **does not make causal claims attributing the entire episode solely to firecrackers**. It evaluates the episode as an observed seasonal pulse with measurable pre-event, peak, and dissipation dynamics.
