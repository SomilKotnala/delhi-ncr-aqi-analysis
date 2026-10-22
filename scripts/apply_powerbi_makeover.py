"""
Power BI Native PBIP Visual & Theme Makeover Script
Transforms D:\\delhi-ncr-aqi-analysis\\delhi_ncr_aqi_analysis_native.pbip into a
premium, interactive, beautiful environmental intelligence report.
"""

import json
import re
from pathlib import Path

PROJECT_ROOT = Path(r"D:\delhi-ncr-aqi-analysis")
PBIP_REPORT = PROJECT_ROOT / "delhi_ncr_aqi_analysis_native.Report"
PBIP_MODEL = PROJECT_ROOT / "delhi_ncr_aqi_analysis_native.SemanticModel"
THEME_PATH = PROJECT_ROOT / "powerbi" / "theme_navy_environmental.json"

print("==================================================================")
print(" Power BI Native PBIP Visual & Theme Makeover Engine")
print("==================================================================")

# -------------------------------------------------------------------------
# Step 1: Update theme_navy_environmental.json with full high-contrast palette
# -------------------------------------------------------------------------
print("\n[Step 1/5] Updating dark navy environmental theme...")
theme_data = {
    "name": "Delhi-NCR Environmental Dark Navy",
    "dataColors": [
        "#2DD4BF",  # Primary Teal
        "#38BDF8",  # Sky Cyan
        "#10B981",  # CPCB Good (Green)
        "#84CC16",  # CPCB Satisfactory (Light Green)
        "#F59E0B",  # CPCB Moderate (Amber)
        "#F97316",  # CPCB Poor (Orange)
        "#EF4444",  # CPCB Very Poor (Red)
        "#991B1B",  # CPCB Severe (Deep Crimson)
        "#A78BFA",  # Purple Accent
        "#60A5FA"   # Blue Accent
    ],
    "background": "#0B1220",
    "foreground": "#111C2E",
    "tableAccent": "#2DD4BF",
    "visualStyles": {
        "*": {
            "*": {
                "outspace": [{"color": {"solid": {"color": "#0B1220"}}}],
                "background": [{"color": {"solid": {"color": "#111C2E"}}, "transparency": 0}],
                "border": [{"show": True, "color": {"solid": {"color": "#1E293B"}}, "radius": 6}],
                "title": [
                    {
                        "show": True,
                        "fontColor": {"solid": {"color": "#F1F5F9"}},
                        "fontSize": 12,
                        "fontFamily": "Segoe UI Semibold"
                    }
                ],
                "labels": [
                    {
                        "color": {"solid": {"color": "#A7B4C7"}},
                        "fontFamily": "Segoe UI",
                        "fontSize": 10
                    }
                ]
            }
        },
        "page": {
            "*": {
                "background": [{"color": {"solid": {"color": "#0B1220"}}, "transparency": 0}]
            }
        },
        "card": {
            "*": {
                "background": [{"color": {"solid": {"color": "#172438"}}, "transparency": 0}],
                "border": [{"show": True, "color": {"solid": {"color": "#1E293B"}}, "radius": 8}],
                "labels": [
                    {
                        "color": {"solid": {"color": "#2DD4BF"}},
                        "fontSize": 28,
                        "fontFamily": "Segoe UI Bold"
                    }
                ],
                "categoryLabels": [
                    {
                        "show": True,
                        "color": {"solid": {"color": "#F1F5F9"}},
                        "fontSize": 10,
                        "fontFamily": "Segoe UI Semibold"
                    }
                ]
            }
        },
        "cardVisual": {
            "*": {
                "background": [{"color": {"solid": {"color": "#172438"}}, "transparency": 0}],
                "border": [{"show": True, "color": {"solid": {"color": "#1E293B"}}, "radius": 8}]
            }
        },
        "tableEx": {
            "*": {
                "grid": [
                    {
                        "gridVertical": True,
                        "gridVerticalColor": {"solid": {"color": "#1E293B"}},
                        "gridHorizontal": True,
                        "gridHorizontalColor": {"solid": {"color": "#1E293B"}},
                        "rowPadding": 4
                    }
                ],
                "columnHeaders": [
                    {
                        "fontColor": {"solid": {"color": "#F1F5F9"}},
                        "backColor": {"solid": {"color": "#1E293B"}},
                        "fontFamily": "Segoe UI Semibold",
                        "fontSize": 10
                    }
                ],
                "values": [
                    {
                        "fontColorPrimary": {"solid": {"color": "#CBD5E1"}},
                        "fontColorSecondary": {"solid": {"color": "#94A3B8"}},
                        "backColorPrimary": {"solid": {"color": "#111C2E"}},
                        "backColorSecondary": {"solid": {"color": "#0F172A"}},
                        "fontFamily": "Segoe UI",
                        "fontSize": 9
                    }
                ]
            }
        },
        "slicer": {
            "*": {
                "header": [
                    {
                        "show": True,
                        "fontColor": {"solid": {"color": "#2DD4BF"}},
                        "fontSize": 10,
                        "fontFamily": "Segoe UI Semibold"
                    }
                ],
                "items": [
                    {
                        "fontColor": {"solid": {"color": "#F1F5F9"}},
                        "background": {"solid": {"color": "#172438"}},
                        "fontFamily": "Segoe UI",
                        "fontSize": 9
                    }
                ]
            }
        }
    }
}

with open(THEME_PATH, "w", encoding="utf-8") as f:
    json.dump(theme_data, f, indent=2)
print("  Theme updated successfully:", THEME_PATH)

# Copy theme to PBIP registered resources
target_theme = PBIP_REPORT / "StaticResources" / "RegisteredResources" / "theme_navy_environmental.json"
target_theme.parent.mkdir(parents=True, exist_ok=True)
with open(target_theme, "w", encoding="utf-8") as f:
    json.dump(theme_data, f, indent=2)
print("  Theme synced to RegisteredResources:", target_theme)

# -------------------------------------------------------------------------
# Step 2: Update Semantic Model (dim_date.tmdl and _Measures.tmdl)
# -------------------------------------------------------------------------
print("\n[Step 2/5] Updating Semantic Model definitions...")

# 2A. Update dim_date.tmdl to add year_month and year_month_key if not present
dim_date_tmdl = PBIP_MODEL / "definition" / "tables" / "dim_date.tmdl"
if dim_date_tmdl.exists():
    content = dim_date_tmdl.read_text(encoding="utf-8")
    if "column year_month" not in content:
        year_month_def = """\n\tcolumn year_month = FORMAT(dim_date[calendar_date], "yyyy-MM")
\t\tdataType: string
\t\tlineageTag: 71b3e782-b43b-4890-a7d1-92b1bca34821
\t\tsummarizeBy: none
\t\tsortByColumn: year_month_key

\t\tannotation SummarizationSetBy = Automatic

\tcolumn year_month_key = dim_date[year] * 100 + dim_date[month]
\t\tdataType: int64
\t\tformatString: 0
\t\tlineageTag: 62c4a914-d83a-4e2b-bb32-8419fdb23187
\t\tsummarizeBy: sum

\t\tannotation SummarizationSetBy = Automatic
"""
        # Insert before partition
        parts = content.split("\tpartition dim_date = m")
        if len(parts) == 2:
            new_content = parts[0] + year_month_def + "\n\tpartition dim_date = m" + parts[1]
            dim_date_tmdl.write_text(new_content, encoding="utf-8")
            print("  Added calculated columns 'year_month' and 'year_month_key' to dim_date.tmdl")
        else:
            print("  Warning: Could not locate partition in dim_date.tmdl")
    else:
        print("  'year_month' already present in dim_date.tmdl")

# 2B. Update _Measures.tmdl to add 'Diurnal Mean AQI'
measures_tmdl = PBIP_MODEL / "definition" / "tables" / "_Measures.tmdl"
if measures_tmdl.exists():
    m_content = measures_tmdl.read_text(encoding="utf-8")
    if "Diurnal Mean AQI" not in m_content:
        diurnal_measure_def = """\n\tmeasure 'Diurnal Mean AQI' = AVERAGE('agg_hourly_diurnal'[mean_aqi])
\t\tlineageTag: e38f9021-d13c-44b2-9a8b-18b321a4f091

\t\tannotation PBI_FormatHint = {"isGeneralNumber":true}
"""
        parts = m_content.split("\tcolumn Placeholder")
        if len(parts) == 2:
            new_m_content = parts[0] + diurnal_measure_def + "\n\tcolumn Placeholder" + parts[1]
            measures_tmdl.write_text(new_m_content, encoding="utf-8")
            print("  Added measure 'Diurnal Mean AQI' to _Measures.tmdl")
        else:
            print("  Warning: Could not locate column Placeholder in _Measures.tmdl")
    else:
        print("  'Diurnal Mean AQI' already present in _Measures.tmdl")

# -------------------------------------------------------------------------
# Step 3: Helper function to build high-contrast Card Visuals
# -------------------------------------------------------------------------
def make_card_visual(name, x, y, width, height, tab_order, measure_name, title_text, callout_color, subtitle=None):
    """Generates a high-contrast KPI Card visual with explicit styling."""
    return {
        "$schema": "https://developer.microsoft.com/json-schemas/fabric/item/report/definition/visualContainer/2.14.0/schema.json",
        "name": name,
        "position": {
            "x": x,
            "y": y,
            "z": tab_order,
            "width": width,
            "height": height,
            "tabOrder": tab_order
        },
        "visual": {
            "visualType": "card",
            "query": {
                "queryState": {
                    "Fields": {
                        "projections": [
                            {
                                "field": {
                                    "Measure": {
                                        "Expression": {"SourceRef": {"Entity": "_Measures"}},
                                        "Property": measure_name
                                    }
                                },
                                "queryRef": f"_Measures.{measure_name}",
                                "nativeQueryRef": measure_name
                            }
                        ]
                    }
                }
            },
            "objects": {
                "labels": [
                    {
                        "properties": {
                            "color": {
                                "solid": {
                                    "color": {
                                        "expr": {
                                            "Literal": {"Value": f"'{callout_color}'"}
                                        }
                                    }
                                }
                            },
                            "fontSize": {
                                "expr": {
                                    "Literal": {"Value": "26D"}
                                }
                            }
                        }
                    }
                ],
                "categoryLabels": [
                    {
                        "properties": {
                            "show": {
                                "expr": {
                                    "Literal": {"Value": "false"}
                                }
                            }
                        }
                    }
                ]
            },
            "visualContainerObjects": {
                "background": [
                    {
                        "properties": {
                            "color": {"solid": {"color": {"expr": {"Literal": {"Value": "'#172438'"}}}}},
                            "transparency": {"expr": {"Literal": {"Value": "0D"}}}
                        }
                    }
                ],
                "border": [
                    {
                        "properties": {
                            "show": {"expr": {"Literal": {"Value": "true"}}},
                            "color": {"solid": {"color": {"expr": {"Literal": {"Value": "'#1E293B'"}}}}},
                            "radius": {"expr": {"Literal": {"Value": "8D"}}}
                        }
                    }
                ],
                "title": [
                    {
                        "properties": {
                            "show": {"expr": {"Literal": {"Value": "true"}}},
                            "text": {"expr": {"Literal": {"Value": f"'{title_text}'"}}},
                            "fontColor": {"solid": {"color": {"expr": {"Literal": {"Value": "'#F1F5F9'"}}}}},
                            "fontSize": {"expr": {"Literal": {"Value": "11D"}}},
                            "fontFamily": {"expr": {"Literal": {"Value": "'Segoe UI Semibold'"}}}
                        }
                    }
                ],
                "subTitle": [
                    {
                        "properties": {
                            "show": {"expr": {"Literal": {"Value": "true" if subtitle else "false"}}},
                            "text": {"expr": {"Literal": {"Value": f"'{subtitle}'" if subtitle else "''"}}},
                            "fontColor": {"solid": {"color": {"expr": {"Literal": {"Value": "'#A7B4C7'"}}}}},
                            "fontSize": {"expr": {"Literal": {"Value": "9D"}}},
                            "fontFamily": {"expr": {"Literal": {"Value": "'Segoe UI'"}}}
                        }
                    }
                ]
            },
            "drillFilterOtherVisuals": True
        }
    }

# -------------------------------------------------------------------------
# Step 4: Transform Page 1 (Regional AQI Overview)
# -------------------------------------------------------------------------
print("\n[Step 4/5] Transforming Page 1 visuals...")
p1_dir = PBIP_REPORT / "definition" / "pages" / "2941a98a6619273cadf8" / "visuals"

# Header
p1_v01 = {
    "$schema": "https://developer.microsoft.com/json-schemas/fabric/item/report/definition/visualContainer/2.14.0/schema.json",
    "name": "p1_v01_header",
    "position": {"x": 20, "y": 15, "z": 1, "width": 1300, "height": 75, "tabOrder": 1},
    "visual": {
        "visualType": "textbox",
        "objects": {
            "general": [{
                "properties": {
                    "paragraphs": [
                        {
                            "textRuns": [{
                                "value": "Delhi-NCR Air Quality | Regional Overview",
                                "textStyle": {"fontFamily": "Segoe UI Semibold", "fontSize": "16pt", "color": "#F1F5F9"}
                            }]
                        },
                        {
                            "textRuns": [{
                                "value": "Monitoring coverage, pollution severity, and long-term AQI patterns | 2017-2023 | Source: CPCB CAAQMS",
                                "textStyle": {"fontFamily": "Segoe UI", "fontSize": "10pt", "color": "#A7B4C7"}
                            }]
                        }
                    ]
                }
            }]
        }
    }
}
(p1_dir / "p1_v01_header" / "visual.json").write_text(json.dumps(p1_v01, indent=2), encoding="utf-8")

# Slicers
p1_v02 = {
    "$schema": "https://developer.microsoft.com/json-schemas/fabric/item/report/definition/visualContainer/2.14.0/schema.json",
    "name": "p1_v02_slicercity",
    "position": {"x": 1340, "y": 15, "z": 2, "height": 75, "width": 270, "tabOrder": 2},
    "visual": {
        "visualType": "slicer",
        "query": {
            "queryState": {
                "Values": {
                    "projections": [{
                        "field": {"Column": {"Expression": {"SourceRef": {"Entity": "dim_station"}}, "Property": "city"}},
                        "queryRef": "dim_station.city", "nativeQueryRef": "city", "active": True
                    }]
                }
            }
        },
        "visualContainerObjects": {
            "title": [{
                "properties": {
                    "show": {"expr": {"Literal": {"Value": "true"}}},
                    "text": {"expr": {"Literal": {"Value": "'Select City'"}}}
                }
            }]
        },
        "drillFilterOtherVisuals": True
    }
}
(p1_dir / "p1_v02_slicercity" / "visual.json").write_text(json.dumps(p1_v02, indent=2), encoding="utf-8")

p1_v03 = {
    "$schema": "https://developer.microsoft.com/json-schemas/fabric/item/report/definition/visualContainer/2.14.0/schema.json",
    "name": "p1_v03_slicerseason",
    "position": {"x": 1630, "y": 15, "z": 3, "height": 75, "width": 270, "tabOrder": 3},
    "visual": {
        "visualType": "slicer",
        "query": {
            "queryState": {
                "Values": {
                    "projections": [{
                        "field": {"Column": {"Expression": {"SourceRef": {"Entity": "dim_date"}}, "Property": "season"}},
                        "queryRef": "dim_date.season", "nativeQueryRef": "season", "active": True
                    }]
                }
            }
        },
        "visualContainerObjects": {
            "title": [{
                "properties": {
                    "show": {"expr": {"Literal": {"Value": "true"}}},
                    "text": {"expr": {"Literal": {"Value": "'Select Season'"}}}
                }
            }]
        },
        "drillFilterOtherVisuals": True
    }
}
(p1_dir / "p1_v03_slicerseason" / "visual.json").write_text(json.dumps(p1_v03, indent=2), encoding="utf-8")

# 4 High-Contrast KPI Cards
c1 = make_card_visual("p1_v04_cardmed", 20, 105, 450, 120, 4, "Median AQI", "Network Median AQI", "#2DD4BF", "Reference Benchmark: 199.29 (Moderate/Poor border)")
c2 = make_card_visual("p1_v05_cardcomp", 490, 105, 450, 120, 5, "Data Completeness %", "Data Completeness Rate", "#38BDF8", "100,794 valid / 111,014 scheduled station-days (90.79%)")
c3 = make_card_visual("p1_v06_cardsev", 960, 105, 450, 120, 6, "Severe AQI Days %", "Severe AQI Episode Share", "#F87171", "6,389 valid days in Severe category (6.34%)")
c4 = make_card_visual("p1_v07_cardcap", 1430, 105, 470, 120, 7, "Sensor Capped Days %", "Sensor-Capped Station-Days (AQI=500)", "#FB923C", "12,536 valid days reaching statutory 500 ceiling (12.44%)")

(p1_dir / "p1_v04_cardmed" / "visual.json").write_text(json.dumps(c1, indent=2), encoding="utf-8")
(p1_dir / "p1_v05_cardcomp" / "visual.json").write_text(json.dumps(c2, indent=2), encoding="utf-8")
(p1_dir / "p1_v06_cardsev" / "visual.json").write_text(json.dumps(c3, indent=2), encoding="utf-8")
(p1_dir / "p1_v07_cardcap" / "visual.json").write_text(json.dumps(c4, indent=2), encoding="utf-8")

# Fixed Monthly AQI Trend Line Chart
p1_v08 = {
    "$schema": "https://developer.microsoft.com/json-schemas/fabric/item/report/definition/visualContainer/2.14.0/schema.json",
    "name": "p1_v08_linetrend",
    "position": {"x": 20, "y": 240, "z": 8, "height": 440, "width": 1250, "tabOrder": 8},
    "visual": {
        "visualType": "lineChart",
        "query": {
            "queryState": {
                "Category": {
                    "projections": [{
                        "field": {"Column": {"Expression": {"SourceRef": {"Entity": "dim_date"}}, "Property": "year_month"}},
                        "queryRef": "dim_date.year_month", "nativeQueryRef": "year_month", "active": True
                    }]
                },
                "Y": {
                    "projections": [
                        {
                            "field": {"Measure": {"Expression": {"SourceRef": {"Entity": "_Measures"}}, "Property": "Median AQI"}},
                            "queryRef": "_Measures.Median AQI", "nativeQueryRef": "Median AQI"
                        },
                        {
                            "field": {"Measure": {"Expression": {"SourceRef": {"Entity": "_Measures"}}, "Property": "Mean AQI"}},
                            "queryRef": "_Measures.Mean AQI", "nativeQueryRef": "Mean AQI"
                        }
                    ]
                }
            },
            "sortDefinition": {
                "sort": [{
                    "field": {"Column": {"Expression": {"SourceRef": {"Entity": "dim_date"}}, "Property": "year_month"}},
                    "direction": "Ascending"
                }],
                "isDefaultSort": False
            }
        },
        "visualContainerObjects": {
            "title": [{
                "properties": {
                    "show": {"expr": {"Literal": {"Value": "true"}}},
                    "text": {"expr": {"Literal": {"Value": "'Long-Term Monthly AQI Trend (2017-2023): Median vs Mean AQI'"}}}
                }
            }],
            "subTitle": [{
                "properties": {
                    "show": {"expr": {"Literal": {"Value": "true"}}},
                    "text": {"expr": {"Literal": {"Value": "'Chronological monthly progression across Delhi-NCR network demonstrating severe annual winter peaks'"}}}
                }
            }]
        },
        "drillFilterOtherVisuals": True
    }
}
(p1_dir / "p1_v08_linetrend" / "visual.json").write_text(json.dumps(p1_v08, indent=2), encoding="utf-8")

# Fixed CPCB AQI Donut Chart (using daily_category)
p1_v09 = {
    "$schema": "https://developer.microsoft.com/json-schemas/fabric/item/report/definition/visualContainer/2.14.0/schema.json",
    "name": "p1_v09_donutcat",
    "position": {"x": 1290, "y": 240, "z": 9, "height": 440, "width": 610, "tabOrder": 9},
    "visual": {
        "visualType": "donutChart",
        "query": {
            "queryState": {
                "Category": {
                    "projections": [{
                        "field": {"Column": {"Expression": {"SourceRef": {"Entity": "fact_daily_aqi"}}, "Property": "daily_category"}},
                        "queryRef": "fact_daily_aqi.daily_category", "nativeQueryRef": "daily_category", "active": True
                    }]
                },
                "Y": {
                    "projections": [{
                        "field": {"Measure": {"Expression": {"SourceRef": {"Entity": "_Measures"}}, "Property": "Valid Station-Days"}},
                        "queryRef": "_Measures.Valid Station-Days", "nativeQueryRef": "Valid Station-Days"
                    }]
                }
            }
        },
        "visualContainerObjects": {
            "title": [{
                "properties": {
                    "show": {"expr": {"Literal": {"Value": "true"}}},
                    "text": {"expr": {"Literal": {"Value": "'CPCB AQI Category Distribution (100,794 Valid Station-Days)'"}}}
                }
            }],
            "subTitle": [{
                "properties": {
                    "show": {"expr": {"Literal": {"Value": "true"}}},
                    "text": {"expr": {"Literal": {"Value": "'Official statutory air quality tiers from Good (0-50) to Severe (401-500)'"}}}
                }
            }]
        },
        "drillFilterOtherVisuals": True
    }
}
(p1_dir / "p1_v09_donutcat" / "visual.json").write_text(json.dumps(p1_v09, indent=2), encoding="utf-8")

# Municipal Median AQI Comparison Bar Chart
p1_v10 = {
    "$schema": "https://developer.microsoft.com/json-schemas/fabric/item/report/definition/visualContainer/2.14.0/schema.json",
    "name": "p1_v10_barcity",
    "position": {"x": 20, "y": 700, "z": 10, "height": 360, "width": 880, "tabOrder": 10},
    "visual": {
        "visualType": "clusteredBarChart",
        "query": {
            "queryState": {
                "Category": {
                    "projections": [{
                        "field": {"Column": {"Expression": {"SourceRef": {"Entity": "dim_station"}}, "Property": "city"}},
                        "queryRef": "dim_station.city", "nativeQueryRef": "city", "active": True
                    }]
                },
                "Y": {
                    "projections": [{
                        "field": {"Measure": {"Expression": {"SourceRef": {"Entity": "_Measures"}}, "Property": "Median AQI"}},
                        "queryRef": "_Measures.Median AQI", "nativeQueryRef": "Median AQI"
                    }]
                }
            },
            "sortDefinition": {
                "sort": [{
                    "field": {"Measure": {"Expression": {"SourceRef": {"Entity": "_Measures"}}, "Property": "Median AQI"}},
                    "direction": "Descending"
                }],
                "isDefaultSort": False
            }
        },
        "visualContainerObjects": {
            "title": [{
                "properties": {
                    "show": {"expr": {"Literal": {"Value": "true"}}},
                    "text": {"expr": {"Literal": {"Value": "'Municipal Median AQI Comparison (5 NCR Cities)'"}}}
                }
            }],
            "subTitle": [{
                "properties": {
                    "show": {"expr": {"Literal": {"Value": "true"}}},
                    "text": {"expr": {"Literal": {"Value": "'Ranked by valid station-day median AQI across 2017-2023'"}}}
                }
            }]
        },
        "drillFilterOtherVisuals": True
    }
}
(p1_dir / "p1_v10_barcity" / "visual.json").write_text(json.dumps(p1_v10, indent=2), encoding="utf-8")

# Fixed 24-Hour Diurnal Rhythm Chart
p1_v11 = {
    "$schema": "https://developer.microsoft.com/json-schemas/fabric/item/report/definition/visualContainer/2.14.0/schema.json",
    "name": "p1_v11_linediurnal",
    "position": {"x": 920, "y": 700, "z": 11, "height": 360, "width": 980, "tabOrder": 11},
    "visual": {
        "visualType": "lineChart",
        "query": {
            "queryState": {
                "Category": {
                    "projections": [{
                        "field": {"Column": {"Expression": {"SourceRef": {"Entity": "agg_hourly_diurnal"}}, "Property": "hour"}},
                        "queryRef": "agg_hourly_diurnal.hour", "nativeQueryRef": "hour", "active": True
                    }]
                },
                "Series": {
                    "projections": [{
                        "field": {"Column": {"Expression": {"SourceRef": {"Entity": "agg_hourly_diurnal"}}, "Property": "is_winter"}},
                        "queryRef": "agg_hourly_diurnal.is_winter", "nativeQueryRef": "is_winter"
                    }]
                },
                "Y": {
                    "projections": [{
                        "field": {"Measure": {"Expression": {"SourceRef": {"Entity": "_Measures"}}, "Property": "Diurnal Mean AQI"}},
                        "queryRef": "_Measures.Diurnal Mean AQI", "nativeQueryRef": "Diurnal Mean AQI"
                    }]
                }
            },
            "sortDefinition": {
                "sort": [{
                    "field": {"Column": {"Expression": {"SourceRef": {"Entity": "agg_hourly_diurnal"}}, "Property": "hour"}},
                    "direction": "Ascending"
                }],
                "isDefaultSort": False
            }
        },
        "visualContainerObjects": {
            "title": [{
                "properties": {
                    "show": {"expr": {"Literal": {"Value": "true"}}},
                    "text": {"expr": {"Literal": {"Value": "'Diurnal 24-Hour Rhythm: Winter Smog Inversion vs Non-Winter Baseline'"}}}
                }
            }],
            "subTitle": [{
                "properties": {
                    "show": {"expr": {"Literal": {"Value": "true"}}},
                    "text": {"expr": {"Literal": {"Value": "'Hourly AQI from 00:00 to 23:00 (Pre-aggregated city-hour-season table)'"}}}
                }
            }]
        },
        "drillFilterOtherVisuals": True
    }
}
(p1_dir / "p1_v11_linediurnal" / "visual.json").write_text(json.dumps(p1_v11, indent=2), encoding="utf-8")
print("  All 11 Page 1 visuals successfully updated and styled!")

# -------------------------------------------------------------------------
# Step 5: Transform Page 2 (Seasonal Dynamics)
# -------------------------------------------------------------------------
print("\n[Step 5/5] Transforming Page 2 visuals...")
p2_dir = PBIP_REPORT / "definition" / "pages" / "b8c347d1e02f4a1a9e31" / "visuals"

# Header
p2_v01 = {
    "$schema": "https://developer.microsoft.com/json-schemas/fabric/item/report/definition/visualContainer/2.14.0/schema.json",
    "name": "p2_v01_header",
    "position": {"x": 20, "y": 15, "z": 1, "width": 1300, "height": 75, "tabOrder": 1},
    "visual": {
        "visualType": "textbox",
        "objects": {
            "general": [{
                "properties": {
                    "paragraphs": [
                        {
                            "textRuns": [{
                                "value": "Seasonal Dynamics | Winter Elevation & Spatial Differences",
                                "textStyle": {"fontFamily": "Segoe UI Semibold", "fontSize": "16pt", "color": "#F1F5F9"}
                            }]
                        },
                        {
                            "textRuns": [{
                                "value": "Comparing seasonal AQI patterns across cities and monitoring stations | 2017-2023",
                                "textStyle": {"fontFamily": "Segoe UI", "fontSize": "10pt", "color": "#A7B4C7"}
                            }]
                        }
                    ]
                }
            }]
        }
    }
}
(p2_dir / "p2_v01_header" / "visual.json").write_text(json.dumps(p2_v01, indent=2), encoding="utf-8")

# Slicers
p2_v02 = {
    "$schema": "https://developer.microsoft.com/json-schemas/fabric/item/report/definition/visualContainer/2.14.0/schema.json",
    "name": "p2_v02_slicercity",
    "position": {"x": 1340, "y": 15, "z": 2, "height": 75, "width": 270, "tabOrder": 2},
    "visual": {
        "visualType": "slicer",
        "query": {
            "queryState": {
                "Values": {
                    "projections": [{
                        "field": {"Column": {"Expression": {"SourceRef": {"Entity": "dim_station"}}, "Property": "city"}},
                        "queryRef": "dim_station.city", "nativeQueryRef": "city", "active": True
                    }]
                }
            }
        },
        "visualContainerObjects": {
            "title": [{
                "properties": {
                    "show": {"expr": {"Literal": {"Value": "true"}}},
                    "text": {"expr": {"Literal": {"Value": "'Select City'"}}}
                }
            }]
        },
        "drillFilterOtherVisuals": True
    }
}
(p2_dir / "p2_v02_slicercity" / "visual.json").write_text(json.dumps(p2_v02, indent=2), encoding="utf-8")

p2_v03 = {
    "$schema": "https://developer.microsoft.com/json-schemas/fabric/item/report/definition/visualContainer/2.14.0/schema.json",
    "name": "p2_v03_sliceryear",
    "position": {"x": 1630, "y": 15, "z": 3, "height": 75, "width": 270, "tabOrder": 3},
    "visual": {
        "visualType": "slicer",
        "query": {
            "queryState": {
                "Values": {
                    "projections": [{
                        "field": {"Column": {"Expression": {"SourceRef": {"Entity": "dim_date"}}, "Property": "year"}},
                        "queryRef": "dim_date.year", "nativeQueryRef": "year", "active": True
                    }]
                }
            }
        },
        "visualContainerObjects": {
            "title": [{
                "properties": {
                    "show": {"expr": {"Literal": {"Value": "true"}}},
                    "text": {"expr": {"Literal": {"Value": "'Select Year'"}}}
                }
            }]
        },
        "drillFilterOtherVisuals": True
    }
}
(p2_dir / "p2_v03_sliceryear" / "visual.json").write_text(json.dumps(p2_v03, indent=2), encoding="utf-8")

# 4 High-Contrast KPI Cards (Page 2)
p2_c1 = make_card_visual("p2_v04_cardwmed", 20, 105, 450, 120, 4, "Winter Median AQI", "Winter Median AQI", "#EF4444", "November to February meteorological winter (Benchmark: 335.61)")
p2_c2 = make_card_visual("p2_v05_cardnwmed", 490, 105, 450, 120, 5, "Non-Winter Median AQI", "Non-Winter Median AQI", "#34D399", "March to October baseline period (Benchmark: 154.00)")
p2_c3 = make_card_visual("p2_v06_carddiff", 960, 105, 450, 120, 6, "Winter Elevation Absolute", "Winter Absolute Elevation", "#FB923C", "Difference: +181.61 AQI points (95% MBB CI: [+156.98, +202.14])")
p2_c4 = make_card_visual("p2_v07_cardratio", 1430, 105, 470, 120, 7, "Winter Elevation Ratio", "Winter Elevation Ratio", "#FBBF24", "Relative amplification: 2.18x over non-winter baseline")

(p2_dir / "p2_v04_cardwmed" / "visual.json").write_text(json.dumps(p2_c1, indent=2), encoding="utf-8")
(p2_dir / "p2_v05_cardnwmed" / "visual.json").write_text(json.dumps(p2_c2, indent=2), encoding="utf-8")
(p2_dir / "p2_v06_carddiff" / "visual.json").write_text(json.dumps(p2_c3, indent=2), encoding="utf-8")
(p2_dir / "p2_v07_cardratio" / "visual.json").write_text(json.dumps(p2_c4, indent=2), encoding="utf-8")

# Clustered Column: City x Season Comparison
p2_v08 = {
    "$schema": "https://developer.microsoft.com/json-schemas/fabric/item/report/definition/visualContainer/2.14.0/schema.json",
    "name": "p2_v08_colcityseason",
    "position": {"x": 20, "y": 240, "z": 8, "height": 440, "width": 1050, "tabOrder": 8},
    "visual": {
        "visualType": "clusteredColumnChart",
        "query": {
            "queryState": {
                "Category": {
                    "projections": [{
                        "field": {"Column": {"Expression": {"SourceRef": {"Entity": "dim_station"}}, "Property": "city"}},
                        "queryRef": "dim_station.city", "nativeQueryRef": "city", "active": True
                    }]
                },
                "Y": {
                    "projections": [
                        {
                            "field": {"Measure": {"Expression": {"SourceRef": {"Entity": "_Measures"}}, "Property": "Winter Median AQI"}},
                            "queryRef": "_Measures.Winter Median AQI", "nativeQueryRef": "Winter Median AQI"
                        },
                        {
                            "field": {"Measure": {"Expression": {"SourceRef": {"Entity": "_Measures"}}, "Property": "Non-Winter Median AQI"}},
                            "queryRef": "_Measures.Non-Winter Median AQI", "nativeQueryRef": "Non-Winter Median AQI"
                        }
                    ]
                }
            }
        },
        "visualContainerObjects": {
            "title": [{
                "properties": {
                    "show": {"expr": {"Literal": {"Value": "true"}}},
                    "text": {"expr": {"Literal": {"Value": "'City-Level Seasonal Contrast: Winter Median vs Non-Winter Median AQI'"}}}
                }
            }],
            "subTitle": [{
                "properties": {
                    "show": {"expr": {"Literal": {"Value": "true"}}},
                    "text": {"expr": {"Literal": {"Value": "'Comparing thermal inversion impact across all 5 municipal jurisdictions'"}}}
                }
            }]
        },
        "drillFilterOtherVisuals": True
    }
}
(p2_dir / "p2_v08_colcityseason" / "visual.json").write_text(json.dumps(p2_v08, indent=2), encoding="utf-8")

# Column Chart: AQI by Meteorological Season
p2_v09 = {
    "$schema": "https://developer.microsoft.com/json-schemas/fabric/item/report/definition/visualContainer/2.14.0/schema.json",
    "name": "p2_v09_colseason",
    "position": {"x": 1090, "y": 240, "z": 9, "height": 440, "width": 810, "tabOrder": 9},
    "visual": {
        "visualType": "clusteredColumnChart",
        "query": {
            "queryState": {
                "Category": {
                    "projections": [{
                        "field": {"Column": {"Expression": {"SourceRef": {"Entity": "dim_date"}}, "Property": "season"}},
                        "queryRef": "dim_date.season", "nativeQueryRef": "season", "active": True
                    }]
                },
                "Y": {
                    "projections": [{
                        "field": {"Measure": {"Expression": {"SourceRef": {"Entity": "_Measures"}}, "Property": "Median AQI"}},
                        "queryRef": "_Measures.Median AQI", "nativeQueryRef": "Median AQI"
                    }]
                }
            },
            "sortDefinition": {
                "sort": [{
                    "field": {"Measure": {"Expression": {"SourceRef": {"Entity": "_Measures"}}, "Property": "Median AQI"}},
                    "direction": "Descending"
                }],
                "isDefaultSort": False
            }
        },
        "visualContainerObjects": {
            "title": [{
                "properties": {
                    "show": {"expr": {"Literal": {"Value": "true"}}},
                    "text": {"expr": {"Literal": {"Value": "'AQI by Meteorological Season (Winter, Summer, Monsoon, Post-Monsoon)'"}}}
                }
            }],
            "subTitle": [{
                "properties": {
                    "show": {"expr": {"Literal": {"Value": "true"}}},
                    "text": {"expr": {"Literal": {"Value": "'Ranked by median valid station-day AQI'"}}}
                }
            }]
        },
        "drillFilterOtherVisuals": True
    }
}
(p2_dir / "p2_v09_colseason" / "visual.json").write_text(json.dumps(p2_v09, indent=2), encoding="utf-8")

# Station Rankings: FIXED Top 10 Most Polluted Stations (Descending Sort)
p2_v10 = {
    "$schema": "https://developer.microsoft.com/json-schemas/fabric/item/report/definition/visualContainer/2.14.0/schema.json",
    "name": "p2_v10_tabletop10",
    "position": {"x": 20, "y": 700, "z": 10, "width": 610, "height": 360, "tabOrder": 10},
    "visual": {
        "visualType": "tableEx",
        "query": {
            "queryState": {
                "Values": {
                    "projections": [
                        {
                            "field": {"Column": {"Expression": {"SourceRef": {"Entity": "dim_station"}}, "Property": "station_name"}},
                            "queryRef": "dim_station.station_name", "nativeQueryRef": "station_name"
                        },
                        {
                            "field": {"Column": {"Expression": {"SourceRef": {"Entity": "dim_station"}}, "Property": "city"}},
                            "queryRef": "dim_station.city", "nativeQueryRef": "city"
                        },
                        {
                            "field": {"Measure": {"Expression": {"SourceRef": {"Entity": "_Measures"}}, "Property": "Valid Station-Days"}},
                            "queryRef": "_Measures.Valid Station-Days", "nativeQueryRef": "Valid Station-Days"
                        },
                        {
                            "field": {"Measure": {"Expression": {"SourceRef": {"Entity": "_Measures"}}, "Property": "Median AQI"}},
                            "queryRef": "_Measures.Median AQI", "nativeQueryRef": "Median AQI"
                        }
                    ]
                }
            },
            "sortDefinition": {
                "sort": [{
                    "field": {"Measure": {"Expression": {"SourceRef": {"Entity": "_Measures"}}, "Property": "Median AQI"}},
                    "direction": "Descending"
                }],
                "isDefaultSort": False
            }
        },
        "filterConfig": {
            "filters": [{
                "name": "Top10PollutedFilter",
                "howCreated": "UserInput",
                "filter": {
                    "$schema": "https://developer.microsoft.com/json-schemas/fabric/item/report/definition/filters/v1.0.0/schema.json",
                    "filterType": "TopN",
                    "operator": "Top",
                    "itemCount": 10,
                    "target": {"table": "dim_station", "column": "station_name"},
                    "orderBy": {"entity": "_Measures", "property": "Median AQI"}
                }
            }]
        },
        "visualContainerObjects": {
            "title": [{
                "properties": {
                    "show": {"expr": {"Literal": {"Value": "true"}}},
                    "text": {"expr": {"Literal": {"Value": "'Top 10 Most Polluted Stations (Highest Median AQI)'"}}}
                }
            }],
            "subTitle": [{
                "properties": {
                    "show": {"expr": {"Literal": {"Value": "true"}}},
                    "text": {"expr": {"Literal": {"Value": "'Ranked descending by valid station-day median AQI'"}}}
                }
            }]
        },
        "drillFilterOtherVisuals": True
    }
}
(p2_dir / "p2_v10_tabletop10" / "visual.json").write_text(json.dumps(p2_v10, indent=2), encoding="utf-8")

# Station Rankings: FIXED Top 10 Cleanest Stations (Ascending Sort)
p2_v11 = {
    "$schema": "https://developer.microsoft.com/json-schemas/fabric/item/report/definition/visualContainer/2.14.0/schema.json",
    "name": "p2_v11_tablebottom10",
    "position": {"x": 650, "y": 700, "z": 11, "width": 610, "height": 360, "tabOrder": 11},
    "visual": {
        "visualType": "tableEx",
        "query": {
            "queryState": {
                "Values": {
                    "projections": [
                        {
                            "field": {"Column": {"Expression": {"SourceRef": {"Entity": "dim_station"}}, "Property": "station_name"}},
                            "queryRef": "dim_station.station_name", "nativeQueryRef": "station_name"
                        },
                        {
                            "field": {"Column": {"Expression": {"SourceRef": {"Entity": "dim_station"}}, "Property": "city"}},
                            "queryRef": "dim_station.city", "nativeQueryRef": "city"
                        },
                        {
                            "field": {"Measure": {"Expression": {"SourceRef": {"Entity": "_Measures"}}, "Property": "Valid Station-Days"}},
                            "queryRef": "_Measures.Valid Station-Days", "nativeQueryRef": "Valid Station-Days"
                        },
                        {
                            "field": {"Measure": {"Expression": {"SourceRef": {"Entity": "_Measures"}}, "Property": "Median AQI"}},
                            "queryRef": "_Measures.Median AQI", "nativeQueryRef": "Median AQI"
                        }
                    ]
                }
            },
            "sortDefinition": {
                "sort": [{
                    "field": {"Measure": {"Expression": {"SourceRef": {"Entity": "_Measures"}}, "Property": "Median AQI"}},
                    "direction": "Ascending"
                }],
                "isDefaultSort": False
            }
        },
        "filterConfig": {
            "filters": [{
                "name": "Bottom10CleanestFilter",
                "howCreated": "UserInput",
                "filter": {
                    "$schema": "https://developer.microsoft.com/json-schemas/fabric/item/report/definition/filters/v1.0.0/schema.json",
                    "filterType": "TopN",
                    "operator": "Bottom",
                    "itemCount": 10,
                    "target": {"table": "dim_station", "column": "station_name"},
                    "orderBy": {"entity": "_Measures", "property": "Median AQI"}
                }
            }]
        },
        "visualContainerObjects": {
            "title": [{
                "properties": {
                    "show": {"expr": {"Literal": {"Value": "true"}}},
                    "text": {"expr": {"Literal": {"Value": "'Top 10 Cleanest Stations (Lowest Median AQI)'"}}}
                }
            }],
            "subTitle": [{
                "properties": {
                    "show": {"expr": {"Literal": {"Value": "true"}}},
                    "text": {"expr": {"Literal": {"Value": "'Ranked ascending by valid station-day median AQI'"}}}
                }
            }]
        },
        "drillFilterOtherVisuals": True
    }
}
(p2_dir / "p2_v11_tablebottom10" / "visual.json").write_text(json.dumps(p2_v11, indent=2), encoding="utf-8")

# Statistical Robustness Panel Textbox
p2_v12 = {
    "$schema": "https://developer.microsoft.com/json-schemas/fabric/item/report/definition/visualContainer/2.14.0/schema.json",
    "name": "p2_v12_textrobustness",
    "position": {"x": 1280, "y": 700, "z": 12, "width": 620, "height": 360, "tabOrder": 12},
    "visual": {
        "visualType": "textbox",
        "objects": {
            "general": [{
                "properties": {
                    "paragraphs": [
                        {
                            "textRuns": [{
                                "value": "Statistical Robustness & Censoring Audit",
                                "textStyle": {"fontFamily": "Segoe UI Semibold", "fontSize": "15pt", "color": "#F1F5F9"}
                            }]
                        },
                        {
                            "textRuns": [{
                                "value": "Econometric & Statistical Verification Highlights:",
                                "textStyle": {"fontFamily": "Segoe UI", "fontSize": "10pt", "color": "#A7B4C7"}
                            }]
                        },
                        {
                            "textRuns": [{
                                "value": "- Temporal Autocorrelation: Daily AR(1) = 0.81 violates naive OLS independence assumptions. Standard error adjustment is mandatory.",
                                "textStyle": {"fontFamily": "Segoe UI", "fontSize": "9pt", "color": "#CBD5E1"}
                            }]
                        },
                        {
                            "textRuns": [{
                                "value": "- Moving Block Bootstrap (L=14 days): 95% Confidence Interval for Winter Elevation is [+156.98, +202.14] AQI points.",
                                "textStyle": {"fontFamily": "Segoe UI", "fontSize": "9pt", "color": "#CBD5E1"}
                            }]
                        },
                        {
                            "textRuns": [{
                                "value": "- Statutory Censoring (Tobit ML): Correcting for the CPCB 500 ceiling estimates true latent elevation at +154.17 AQI points (p < 0.001).",
                                "textStyle": {"fontFamily": "Segoe UI", "fontSize": "9pt", "color": "#CBD5E1"}
                            }]
                        },
                        {
                            "textRuns": [{
                                "value": "- Spatial Invariance: 56 of 56 stations exhibit statistically significant winter elevation (Mann-Whitney U, FDR-adjusted p < 0.001).",
                                "textStyle": {"fontFamily": "Segoe UI", "fontSize": "9pt", "color": "#CBD5E1"}
                            }]
                        }
                    ]
                }
            }]
        }
    }
}
(p2_dir / "p2_v12_textrobustness" / "visual.json").write_text(json.dumps(p2_v12, indent=2), encoding="utf-8")
print("  All 12 Page 2 visuals successfully updated and styled!")

# -------------------------------------------------------------------------
# Step 6: Transform Page 3 (Diwali Episodes)
# -------------------------------------------------------------------------
print("\n[Step 6/5] Transforming Page 3 visuals...")
p3_dir = PBIP_REPORT / "definition" / "pages" / "c5e912f7a43b4d8e8b24" / "visuals"

# Header
p3_v01 = {
    "$schema": "https://developer.microsoft.com/json-schemas/fabric/item/report/definition/visualContainer/2.14.0/schema.json",
    "name": "p3_v01_header",
    "position": {"x": 20, "y": 15, "z": 1, "width": 1300, "height": 75, "tabOrder": 1},
    "visual": {
        "visualType": "textbox",
        "objects": {
            "general": [{
                "properties": {
                    "paragraphs": [
                        {
                            "textRuns": [{
                                "value": "Diwali Episodes | Event Window & Seasonal Context",
                                "textStyle": {"fontFamily": "Segoe UI Semibold", "fontSize": "16pt", "color": "#F1F5F9"}
                            }]
                        },
                        {
                            "textRuns": [{
                                "value": "Station-matched AQI changes around verified festival dates | 2017-2023",
                                "textStyle": {"fontFamily": "Segoe UI", "fontSize": "10pt", "color": "#A7B4C7"}
                            }]
                        }
                    ]
                }
            }]
        }
    }
}
(p3_dir / "p3_v01_header" / "visual.json").write_text(json.dumps(p3_v01, indent=2), encoding="utf-8")

# Slicers: Cohort and Year
p3_v02 = {
    "$schema": "https://developer.microsoft.com/json-schemas/fabric/item/report/definition/visualContainer/2.14.0/schema.json",
    "name": "p3_v02_slicercohort",
    "position": {"x": 1340, "y": 15, "z": 2, "height": 75, "width": 270, "tabOrder": 2},
    "visual": {
        "visualType": "slicer",
        "query": {
            "queryState": {
                "Values": {
                    "projections": [{
                        "field": {"Column": {"Expression": {"SourceRef": {"Entity": "dim_diwali_cohorts"}}, "Property": "timing_cohort"}},
                        "queryRef": "dim_diwali_cohorts.timing_cohort", "nativeQueryRef": "timing_cohort", "active": True
                    }]
                }
            }
        },
        "visualContainerObjects": {
            "title": [{
                "properties": {
                    "show": {"expr": {"Literal": {"Value": "true"}}},
                    "text": {"expr": {"Literal": {"Value": "'Select Cohort'"}}}
                }
            }]
        },
        "drillFilterOtherVisuals": True
    }
}
(p3_dir / "p3_v02_slicercohort" / "visual.json").write_text(json.dumps(p3_v02, indent=2), encoding="utf-8")

# Year Slicer on Page 3: Bound to fact_diwali_pairs.year
p3_v03 = {
    "$schema": "https://developer.microsoft.com/json-schemas/fabric/item/report/definition/visualContainer/2.14.0/schema.json",
    "name": "p3_v03_sliceryear",
    "position": {"x": 1630, "y": 15, "z": 3, "height": 75, "width": 270, "tabOrder": 3},
    "visual": {
        "visualType": "slicer",
        "query": {
            "queryState": {
                "Values": {
                    "projections": [{
                        "field": {"Column": {"Expression": {"SourceRef": {"Entity": "fact_diwali_pairs"}}, "Property": "year"}},
                        "queryRef": "fact_diwali_pairs.year", "nativeQueryRef": "year", "active": True
                    }]
                }
            }
        },
        "visualContainerObjects": {
            "title": [{
                "properties": {
                    "show": {"expr": {"Literal": {"Value": "true"}}},
                    "text": {"expr": {"Literal": {"Value": "'Select Festival Year'"}}}
                }
            }]
        },
        "drillFilterOtherVisuals": True
    }
}
(p3_dir / "p3_v03_sliceryear" / "visual.json").write_text(json.dumps(p3_v03, indent=2), encoding="utf-8")

# 4 High-Contrast KPI Cards (Page 3)
p3_c1 = make_card_visual("p3_v04_cardsurge", 20, 105, 450, 120, 4, "Diwali Pooled Mean Surge", "Diwali Pooled Mean Surge", "#FB923C", "Station-matched pre- vs post-festival surge (+81.57 AQI points)")
p3_c2 = make_card_visual("p3_v05_cardmedsurge", 490, 105, 450, 120, 5, "Diwali Pooled Median Surge", "Diwali Pooled Median Surge", "#FBBF24", "Robust median paired surge: +80.38 AQI points")
p3_c3 = make_card_visual("p3_v06_cardelev", 960, 105, 450, 120, 6, "Diwali Station-Years Elevated %", "Proportion Elevated", "#F87171", "263 of 306 matched station-year pairs elevated (85.95%)")
p3_c4 = make_card_visual("p3_v07_cardpairs", 1430, 105, 470, 120, 7, "Diwali Matched Station-Years", "Matched Station-Year Pairs", "#38BDF8", "306 paired observations across 7 festival years (2017-2023)")

(p3_dir / "p3_v04_cardsurge" / "visual.json").write_text(json.dumps(p3_c1, indent=2), encoding="utf-8")
(p3_dir / "p3_v05_cardmedsurge" / "visual.json").write_text(json.dumps(p3_c2, indent=2), encoding="utf-8")
(p3_dir / "p3_v06_cardelev" / "visual.json").write_text(json.dumps(p3_c3, indent=2), encoding="utf-8")
(p3_dir / "p3_v07_cardpairs" / "visual.json").write_text(json.dumps(p3_c4, indent=2), encoding="utf-8")

# Annual Paired Surge: FIXED Flat Bar Bug (bound to fact_diwali_pairs.year)
p3_v08 = {
    "$schema": "https://developer.microsoft.com/json-schemas/fabric/item/report/definition/visualContainer/2.14.0/schema.json",
    "name": "p3_v08_colannual",
    "position": {"x": 20, "y": 240, "z": 8, "height": 440, "width": 980, "tabOrder": 8},
    "visual": {
        "visualType": "clusteredColumnChart",
        "query": {
            "queryState": {
                "Category": {
                    "projections": [{
                        "field": {"Column": {"Expression": {"SourceRef": {"Entity": "fact_diwali_pairs"}}, "Property": "year"}},
                        "queryRef": "fact_diwali_pairs.year", "nativeQueryRef": "year", "active": True
                    }]
                },
                "Y": {
                    "projections": [{
                        "field": {"Measure": {"Expression": {"SourceRef": {"Entity": "_Measures"}}, "Property": "Diwali Pooled Mean Surge"}},
                        "queryRef": "_Measures.Diwali Pooled Mean Surge", "nativeQueryRef": "Diwali Pooled Mean Surge"
                    }]
                }
            },
            "sortDefinition": {
                "sort": [{
                    "field": {"Column": {"Expression": {"SourceRef": {"Entity": "fact_diwali_pairs"}}, "Property": "year"}},
                    "direction": "Ascending"
                }],
                "isDefaultSort": False
            }
        },
        "visualContainerObjects": {
            "title": [{
                "properties": {
                    "show": {"expr": {"Literal": {"Value": "true"}}},
                    "text": {"expr": {"Literal": {"Value": "'Annual Paired Diwali Surge by Festival Year (2017-2023)'"}}}
                }
            }],
            "subTitle": [{
                "properties": {
                    "show": {"expr": {"Literal": {"Value": "true"}}},
                    "text": {"expr": {"Literal": {"Value": "'Year-specific station-matched mean paired surge: 2020 (+114.3) vs 2023 (+35.2)'"}}}
                }
            }]
        },
        "drillFilterOtherVisuals": True
    }
}
(p3_dir / "p3_v08_colannual" / "visual.json").write_text(json.dumps(p3_v08, indent=2), encoding="utf-8")

# Cohort Contrast Clustered Column
p3_v09 = {
    "$schema": "https://developer.microsoft.com/json-schemas/fabric/item/report/definition/visualContainer/2.14.0/schema.json",
    "name": "p3_v09_colcohort",
    "position": {"x": 1020, "y": 240, "z": 9, "height": 440, "width": 880, "tabOrder": 9},
    "visual": {
        "visualType": "clusteredColumnChart",
        "query": {
            "queryState": {
                "Category": {
                    "projections": [{
                        "field": {"Column": {"Expression": {"SourceRef": {"Entity": "dim_diwali_cohorts"}}, "Property": "timing_cohort"}},
                        "queryRef": "dim_diwali_cohorts.timing_cohort", "nativeQueryRef": "timing_cohort", "active": True
                    }]
                },
                "Y": {
                    "projections": [
                        {
                            "field": {"Measure": {"Expression": {"SourceRef": {"Entity": "_Measures"}}, "Property": "Diwali Pooled Mean Surge"}},
                            "queryRef": "_Measures.Diwali Pooled Mean Surge", "nativeQueryRef": "Diwali Pooled Mean Surge"
                        },
                        {
                            "field": {"Measure": {"Expression": {"SourceRef": {"Entity": "_Measures"}}, "Property": "Diwali Pooled Median Surge"}},
                            "queryRef": "_Measures.Diwali Pooled Median Surge", "nativeQueryRef": "Diwali Pooled Median Surge"
                        }
                    ]
                }
            }
        },
        "visualContainerObjects": {
            "title": [{
                "properties": {
                    "show": {"expr": {"Literal": {"Value": "true"}}},
                    "text": {"expr": {"Literal": {"Value": "'Timing Cohort Contrast: October Diwali vs November Diwali Surge'"}}}
                }
            }],
            "subTitle": [{
                "properties": {
                    "show": {"expr": {"Literal": {"Value": "true"}}},
                    "text": {"expr": {"Literal": {"Value": "'November events average +93.92 surge vs +58.92 for October (+35.00 points seasonal divergence)'"}}}
                }
            }]
        },
        "drillFilterOtherVisuals": True
    }
}
(p3_dir / "p3_v09_colcohort" / "visual.json").write_text(json.dumps(p3_v09, indent=2), encoding="utf-8")

# Cohort Summary Table
p3_v10 = {
    "$schema": "https://developer.microsoft.com/json-schemas/fabric/item/report/definition/visualContainer/2.14.0/schema.json",
    "name": "p3_v10_tablecohort",
    "position": {"x": 20, "y": 700, "z": 10, "width": 980, "height": 360, "tabOrder": 10},
    "visual": {
        "visualType": "tableEx",
        "query": {
            "queryState": {
                "Values": {
                    "projections": [
                        {
                            "field": {"Column": {"Expression": {"SourceRef": {"Entity": "dim_diwali_cohorts"}}, "Property": "timing_cohort"}},
                            "queryRef": "dim_diwali_cohorts.timing_cohort", "nativeQueryRef": "timing_cohort"
                        },
                        {
                            "field": {"Measure": {"Expression": {"SourceRef": {"Entity": "_Measures"}}, "Property": "Diwali Matched Station-Years"}},
                            "queryRef": "_Measures.Diwali Matched Station-Years", "nativeQueryRef": "Diwali Matched Station-Years"
                        },
                        {
                            "field": {"Measure": {"Expression": {"SourceRef": {"Entity": "_Measures"}}, "Property": "Diwali Pooled Mean Surge"}},
                            "queryRef": "_Measures.Diwali Pooled Mean Surge", "nativeQueryRef": "Diwali Pooled Mean Surge"
                        },
                        {
                            "field": {"Measure": {"Expression": {"SourceRef": {"Entity": "_Measures"}}, "Property": "Diwali Pooled Median Surge"}},
                            "queryRef": "_Measures.Diwali Pooled Median Surge", "nativeQueryRef": "Diwali Pooled Median Surge"
                        },
                        {
                            "field": {"Measure": {"Expression": {"SourceRef": {"Entity": "_Measures"}}, "Property": "Diwali Station-Years Elevated %"}},
                            "queryRef": "_Measures.Diwali Station-Years Elevated %", "nativeQueryRef": "Diwali Station-Years Elevated %"
                        }
                    ]
                }
            }
        },
        "visualContainerObjects": {
            "title": [{
                "properties": {
                    "show": {"expr": {"Literal": {"Value": "true"}}},
                    "text": {"expr": {"Literal": {"Value": "'Diwali Timing Cohorts Summary Table (October vs November)'"}}}
                }
            }],
            "subTitle": [{
                "properties": {
                    "show": {"expr": {"Literal": {"Value": "true"}}},
                    "text": {"expr": {"Literal": {"Value": "'Comparing pooled metrics across early-autumn vs late-autumn festival occurrences'"}}}
                }
            }]
        },
        "drillFilterOtherVisuals": True
    }
}
(p3_dir / "p3_v10_tablecohort" / "visual.json").write_text(json.dumps(p3_v10, indent=2), encoding="utf-8")

# Causal Disclaimer Textbox (Exact Required Text)
p3_v11 = {
    "$schema": "https://developer.microsoft.com/json-schemas/fabric/item/report/definition/visualContainer/2.14.0/schema.json",
    "name": "p3_v11_textcausal",
    "position": {"x": 1020, "y": 700, "z": 11, "width": 880, "height": 360, "tabOrder": 11},
    "visual": {
        "visualType": "textbox",
        "objects": {
            "general": [{
                "properties": {
                    "paragraphs": [
                        {
                            "textRuns": [{
                                "value": "Causal Interpretation & Confounding Disclaimer",
                                "textStyle": {"fontFamily": "Segoe UI Semibold", "fontSize": "15pt", "color": "#F1F5F9"}
                            }]
                        },
                        {
                            "textRuns": [{
                                "value": "Mandatory econometric and environmental attribution guidance:",
                                "textStyle": {"fontFamily": "Segoe UI", "fontSize": "10pt", "color": "#A7B4C7"}
                            }]
                        },
                        {
                            "textRuns": [{
                                "value": "- Causal Scope Limitation: These results describe observed AQI patterns around Diwali. They do not independently establish that fireworks caused the observed changes. Seasonal pollution, meteorology, regional emissions, missing observations, and monitoring coverage may also contribute.",
                                "textStyle": {"fontFamily": "Segoe UI", "fontSize": "9pt", "color": "#CBD5E1"}
                            }]
                        },
                        {
                            "textRuns": [{
                                "value": "- The October vs November Natural Experiment: November events average +93.92 AQI points surge vs +58.92 points for October events (+35.00 points difference). This large gap demonstrates substantial seasonal confounding from thermal boundary layer collapse and peak agricultural stubble burning.",
                                "textStyle": {"fontFamily": "Segoe UI", "fontSize": "9pt", "color": "#CBD5E1"}
                            }]
                        },
                        {
                            "textRuns": [{
                                "value": "- Unit of Observation: 306 matched station-year pairs across 7 years, representing paired pre-festival (t-1) vs post-festival (t+1) valid monitoring observations.",
                                "textStyle": {"fontFamily": "Segoe UI", "fontSize": "9pt", "color": "#CBD5E1"}
                            }]
                        }
                    ]
                }
            }]
        }
    }
}
(p3_dir / "p3_v11_textcausal" / "visual.json").write_text(json.dumps(p3_v11, indent=2), encoding="utf-8")
print("  All 11 Page 3 visuals successfully updated and styled!")

# -------------------------------------------------------------------------
# Step 7: Validate All JSON Files
# -------------------------------------------------------------------------
print("\n[Audit] Validating all visual and configuration JSON files...")
json_files = list(PBIP_REPORT.glob("**/*.json"))
error_count = 0
for jf in json_files:
    try:
        with open(jf, "r", encoding="utf-8") as f:
            json.load(f)
    except Exception as e:
        print(f"  ERROR parsing {jf}: {e}")
        error_count += 1

if error_count == 0:
    print(f"  SUCCESS: All {len(json_files)} JSON files validated successfully!")
else:
    print(f"  FAILED: {error_count} JSON files failed validation.")

print("\n==================================================================")
print(" Makeover completed successfully!")
print("==================================================================")
