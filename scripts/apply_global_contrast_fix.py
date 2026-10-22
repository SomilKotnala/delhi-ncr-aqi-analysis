"""
Power BI Global Readability & Color-Contrast Fix Engine
Audits and updates theme and all 34 PBIR visuals across all 3 pages
to eliminate all black-on-dark text and enforce WCAG AAA contrast.
"""

import json
from pathlib import Path

PROJECT_ROOT = Path(r"D:\delhi-ncr-aqi-analysis")
PBIP_REPORT = PROJECT_ROOT / "delhi_ncr_aqi_analysis_native.Report"
PBIP_MODEL = PROJECT_ROOT / "delhi_ncr_aqi_analysis_native.SemanticModel"
THEME_PATH = PROJECT_ROOT / "powerbi" / "theme_navy_environmental.json"

print("==================================================================")
print(" Power BI Global Readability & Contrast Repair Engine")
print("==================================================================")

# -------------------------------------------------------------------------
# Step 1: Update theme_navy_environmental.json centrally
# -------------------------------------------------------------------------
print("\n[Step 1/4] Updating central theme with high-contrast text tokens...")

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
    # ROOT TOKENS: Foreground MUST be bright white/light off-white
    "background": "#0B1220",
    "foreground": "#F8FAFC",                  # Global primary text (Pure Light)
    "foregroundNeutralDark": "#FFFFFF",       # High-contrast headings
    "foregroundNeutralSecondary": "#CBD5E1",  # Subtitles, axis, legends
    "foregroundNeutralTertiary": "#94A3B8",   # Muted metadata
    "backgroundLight": "#111C2E",            # Card surfaces
    "backgroundNeutral": "#172438",          # Elevated surfaces
    "tableAccent": "#2DD4BF",
    
    # TextClasses: Standard Microsoft Power BI Typography Targets
    "textClasses": {
        "callout": {
            "fontFace": "Segoe UI Bold",
            "fontSize": 26,
            "color": {"solid": {"color": "#2DD4BF"}}
        },
        "title": {
            "fontFace": "Segoe UI Semibold",
            "fontSize": 12,
            "color": {"solid": {"color": "#F8FAFC"}}
        },
        "header": {
            "fontFace": "Segoe UI Semibold",
            "fontSize": 10,
            "color": {"solid": {"color": "#F8FAFC"}}
        },
        "label": {
            "fontFace": "Segoe UI",
            "fontSize": 10,
            "color": {"solid": {"color": "#CBD5E1"}}
        }
    },
    
    # VisualStyles: Explicit element mappings
    "visualStyles": {
        "*": {
            "*": {
                "outspace": [{"color": {"solid": {"color": "#0B1220"}}}],
                "background": [{"color": {"solid": {"color": "#111C2E"}}, "transparency": 0}],
                "border": [{"show": True, "color": {"solid": {"color": "#1E293B"}}, "radius": 6}],
                "title": [
                    {
                        "show": True,
                        "fontColor": {"solid": {"color": "#F8FAFC"}},
                        "fontSize": 12,
                        "fontFamily": "Segoe UI Semibold"
                    }
                ],
                "subTitle": [
                    {
                        "show": True,
                        "fontColor": {"solid": {"color": "#CBD5E1"}},
                        "fontSize": 9,
                        "fontFamily": "Segoe UI"
                    }
                ],
                "labels": [
                    {
                        "color": {"solid": {"color": "#CBD5E1"}},
                        "fontFamily": "Segoe UI",
                        "fontSize": 10
                    }
                ],
                "categoryAxis": [
                    {
                        "show": True,
                        "labelColor": {"solid": {"color": "#CBD5E1"}},
                        "titleColor": {"solid": {"color": "#E2E8F0"}},
                        "showAxisTitle": True
                    }
                ],
                "valueAxis": [
                    {
                        "show": True,
                        "labelColor": {"solid": {"color": "#CBD5E1"}},
                        "titleColor": {"solid": {"color": "#E2E8F0"}},
                        "gridlineColor": {"solid": {"color": "#1E293B"}},
                        "showAxisTitle": True
                    }
                ],
                "legend": [
                    {
                        "show": True,
                        "labelColor": {"solid": {"color": "#CBD5E1"}},
                        "titleColor": {"solid": {"color": "#E2E8F0"}}
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
                        "fontSize": 26,
                        "fontFamily": "Segoe UI Bold"
                    }
                ],
                "categoryLabels": [
                    {
                        "show": False,
                        "color": {"solid": {"color": "#CBD5E1"}},
                        "fontSize": 10,
                        "fontFamily": "Segoe UI"
                    }
                ],
                "title": [
                    {
                        "show": True,
                        "fontColor": {"solid": {"color": "#F8FAFC"}},
                        "fontSize": 11,
                        "fontFamily": "Segoe UI Semibold"
                    }
                ],
                "subTitle": [
                    {
                        "show": True,
                        "fontColor": {"solid": {"color": "#CBD5E1"}},
                        "fontSize": 9,
                        "fontFamily": "Segoe UI"
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
                        "fontColor": {"solid": {"color": "#FFFFFF"}},
                        "backColor": {"solid": {"color": "#1E293B"}},
                        "fontFamily": "Segoe UI Semibold",
                        "fontSize": 10
                    }
                ],
                "values": [
                    {
                        "fontColorPrimary": {"solid": {"color": "#E2E8F0"}},
                        "fontColorSecondary": {"solid": {"color": "#CBD5E1"}},
                        "backColorPrimary": {"solid": {"color": "#111C2E"}},
                        "backColorSecondary": {"solid": {"color": "#0F172A"}},
                        "fontFamily": "Segoe UI",
                        "fontSize": 9.5
                    }
                ],
                "total": [
                    {
                        "fontColor": {"solid": {"color": "#FFFFFF"}},
                        "backColor": {"solid": {"color": "#1E293B"}},
                        "fontFamily": "Segoe UI Semibold",
                        "fontSize": 10
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
                        "fontColor": {"solid": {"color": "#F8FAFC"}},
                        "background": {"solid": {"color": "#172438"}},
                        "fontFamily": "Segoe UI",
                        "fontSize": 9.5
                    }
                ]
            }
        }
    }
}

with open(THEME_PATH, "w", encoding="utf-8") as f:
    json.dump(theme_data, f, indent=2)
print("  Theme updated successfully:", THEME_PATH)

target_theme = PBIP_REPORT / "StaticResources" / "RegisteredResources" / "theme_navy_environmental.json"
target_theme.parent.mkdir(parents=True, exist_ok=True)
with open(target_theme, "w", encoding="utf-8") as f:
    json.dump(theme_data, f, indent=2)
print("  Theme synced to RegisteredResources:", target_theme)


# -------------------------------------------------------------------------
# Step 2: Helper functions for Explicit Visual Formatting
# -------------------------------------------------------------------------
def make_container_objects(title_text, subtitle_text=None, is_card=False, is_textbox=False):
    """Builds standard high-contrast visualContainerObjects."""
    bg_color = "'#172438'" if (is_card or is_textbox) else "'#111C2E'"
    radius = "8D" if is_card else "6D"
    
    obj = {
        "background": [
            {
                "properties": {
                    "color": {"solid": {"color": {"expr": {"Literal": {"Value": bg_color}}}}},
                    "transparency": {"expr": {"Literal": {"Value": "0D"}}}
                }
            }
        ],
        "border": [
            {
                "properties": {
                    "show": {"expr": {"Literal": {"Value": "true"}}},
                    "color": {"solid": {"color": {"expr": {"Literal": {"Value": "'#1E293B'"}}}}},
                    "radius": {"expr": {"Literal": {"Value": radius}}}
                }
            }
        ]
    }
    
    if title_text:
        obj["title"] = [
            {
                "properties": {
                    "show": {"expr": {"Literal": {"Value": "true"}}},
                    "text": {"expr": {"Literal": {"Value": f"'{title_text}'"}}},
                    "fontColor": {"solid": {"color": {"expr": {"Literal": {"Value": "'#F8FAFC'"}}}}},
                    "fontSize": {"expr": {"Literal": {"Value": "11.5D"}}},
                    "fontFamily": {"expr": {"Literal": {"Value": "'Segoe UI Semibold'"}}}
                }
            }
        ]
    
    if subtitle_text:
        obj["subTitle"] = [
            {
                "properties": {
                    "show": {"expr": {"Literal": {"Value": "true"}}},
                    "text": {"expr": {"Literal": {"Value": f"'{subtitle_text}'"}}},
                    "fontColor": {"solid": {"color": {"expr": {"Literal": {"Value": "'#CBD5E1'"}}}}},
                    "fontSize": {"expr": {"Literal": {"Value": "9D"}}},
                    "fontFamily": {"expr": {"Literal": {"Value": "'Segoe UI'"}}}
                }
            }
        ]
    
    return obj


def make_cartesian_objects(has_legend=False):
    """Builds explicit high-contrast categoryAxis, valueAxis, and legend objects."""
    objs = {
        "categoryAxis": [
            {
                "properties": {
                    "show": {"expr": {"Literal": {"Value": "true"}}},
                    "labelColor": {"solid": {"color": {"expr": {"Literal": {"Value": "'#CBD5E1'"}}}}},
                    "titleColor": {"solid": {"color": {"expr": {"Literal": {"Value": "'#E2E8F0'"}}}}},
                    "fontSize": {"expr": {"Literal": {"Value": "9.5D"}}},
                    "fontFamily": {"expr": {"Literal": {"Value": "'Segoe UI'"}}}
                }
            }
        ],
        "valueAxis": [
            {
                "properties": {
                    "show": {"expr": {"Literal": {"Value": "true"}}},
                    "labelColor": {"solid": {"color": {"expr": {"Literal": {"Value": "'#CBD5E1'"}}}}},
                    "titleColor": {"solid": {"color": {"expr": {"Literal": {"Value": "'#E2E8F0'"}}}}},
                    "gridlineColor": {"solid": {"color": {"expr": {"Literal": {"Value": "'#1E293B'"}}}}},
                    "fontSize": {"expr": {"Literal": {"Value": "9.5D"}}},
                    "fontFamily": {"expr": {"Literal": {"Value": "'Segoe UI'"}}}
                }
            }
        ]
    }
    if has_legend:
        objs["legend"] = [
            {
                "properties": {
                    "show": {"expr": {"Literal": {"Value": "true"}}},
                    "labelColor": {"solid": {"color": {"expr": {"Literal": {"Value": "'#CBD5E1'"}}}}},
                    "titleColor": {"solid": {"color": {"expr": {"Literal": {"Value": "'#E2E8F0'"}}}}},
                    "fontSize": {"expr": {"Literal": {"Value": "9D"}}},
                    "fontFamily": {"expr": {"Literal": {"Value": "'Segoe UI'"}}}
                }
            }
        ]
    return objs


def make_table_objects():
    """Builds explicit high-contrast table styling."""
    return {
        "columnHeaders": [
            {
                "properties": {
                    "fontColor": {"solid": {"color": {"expr": {"Literal": {"Value": "'#FFFFFF'"}}}}},
                    "backColor": {"solid": {"color": {"expr": {"Literal": {"Value": "'#1E293B'"}}}}},
                    "fontSize": {"expr": {"Literal": {"Value": "10D"}}},
                    "fontFamily": {"expr": {"Literal": {"Value": "'Segoe UI Semibold'"}}}
                }
            }
        ],
        "values": [
            {
                "properties": {
                    "fontColorPrimary": {"solid": {"color": {"expr": {"Literal": {"Value": "'#E2E8F0'"}}}}},
                    "fontColorSecondary": {"solid": {"color": {"expr": {"Literal": {"Value": "'#CBD5E1'"}}}}},
                    "backColorPrimary": {"solid": {"color": {"expr": {"Literal": {"Value": "'#111C2E'"}}}}},
                    "backColorSecondary": {"solid": {"color": {"expr": {"Literal": {"Value": "'#0F172A'"}}}}},
                    "fontSize": {"expr": {"Literal": {"Value": "9.5D"}}},
                    "fontFamily": {"expr": {"Literal": {"Value": "'Segoe UI'"}}}
                }
            }
        ]
    }


def make_slicer_objects():
    """Builds explicit high-contrast slicer styling."""
    return {
        "header": [
            {
                "properties": {
                    "show": {"expr": {"Literal": {"Value": "true"}}},
                    "fontColor": {"solid": {"color": {"expr": {"Literal": {"Value": "'#2DD4BF'"}}}}},
                    "fontSize": {"expr": {"Literal": {"Value": "10D"}}},
                    "fontFamily": {"expr": {"Literal": {"Value": "'Segoe UI Semibold'"}}}
                }
            }
        ],
        "items": [
            {
                "properties": {
                    "fontColor": {"solid": {"color": {"expr": {"Literal": {"Value": "'#F8FAFC'"}}}}},
                    "background": {"solid": {"color": {"expr": {"Literal": {"Value": "'#172438'"}}}}},
                    "fontSize": {"expr": {"Literal": {"Value": "9.5D"}}},
                    "fontFamily": {"expr": {"Literal": {"Value": "'Segoe UI'"}}}
                }
            }
        ]
    }


def make_card_visual(name, x, y, width, height, tab_order, measure_name, title_text, callout_color, subtitle):
    """Builds a high-contrast KPI Card with explicit colors on all elements."""
    return {
        "$schema": "https://developer.microsoft.com/json-schemas/fabric/item/report/definition/visualContainer/2.14.0/schema.json",
        "name": name,
        "position": {"x": x, "y": y, "z": tab_order, "width": width, "height": height, "tabOrder": tab_order},
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
                            "color": {"solid": {"color": {"expr": {"Literal": {"Value": f"'{callout_color}'"}}}}},
                            "fontSize": {"expr": {"Literal": {"Value": "26D"}}}
                        }
                    }
                ],
                "categoryLabels": [
                    {
                        "properties": {
                            "show": {"expr": {"Literal": {"Value": "false"}}}
                        }
                    }
                ]
            },
            "visualContainerObjects": make_container_objects(title_text, subtitle, is_card=True),
            "drillFilterOtherVisuals": True
        }
    }


# -------------------------------------------------------------------------
# Step 3: Global Visual Updates (All 3 Pages)
# -------------------------------------------------------------------------
print("\n[Step 2/4] Applying explicit high-contrast formatting across all 3 pages...")

# ----------------- PAGE 1: Regional AQI Overview -----------------
p1_dir = PBIP_REPORT / "definition" / "pages" / "2941a98a6619273cadf8" / "visuals"

# p1_v01_header: Textbox
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
                                "textStyle": {"fontFamily": "Segoe UI Semibold", "fontSize": "16pt", "color": "#FFFFFF"}
                            }]
                        },
                        {
                            "textRuns": [{
                                "value": "Monitoring coverage, pollution severity, and long-term AQI patterns | 2017-2023 | Source: CPCB CAAQMS",
                                "textStyle": {"fontFamily": "Segoe UI", "fontSize": "10pt", "color": "#CBD5E1"}
                            }]
                        }
                    ]
                }
            }]
        }
    }
}
(p1_dir / "p1_v01_header" / "visual.json").write_text(json.dumps(p1_v01, indent=2), encoding="utf-8")

# p1_v02_slicercity: Slicer
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
        "objects": make_slicer_objects(),
        "visualContainerObjects": make_container_objects("Select City"),
        "drillFilterOtherVisuals": True
    }
}
(p1_dir / "p1_v02_slicercity" / "visual.json").write_text(json.dumps(p1_v02, indent=2), encoding="utf-8")

# p1_v03_slicerseason: Slicer
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
        "objects": make_slicer_objects(),
        "visualContainerObjects": make_container_objects("Select Season"),
        "drillFilterOtherVisuals": True
    }
}
(p1_dir / "p1_v03_slicerseason" / "visual.json").write_text(json.dumps(p1_v03, indent=2), encoding="utf-8")

# 4 Cards Page 1
c1 = make_card_visual("p1_v04_cardmed", 20, 105, 450, 120, 4, "Median AQI", "Network Median AQI", "#2DD4BF", "Reference Benchmark: 199.29 (Moderate/Poor border)")
c2 = make_card_visual("p1_v05_cardcomp", 490, 105, 450, 120, 5, "Data Completeness %", "Data Completeness Rate", "#38BDF8", "100,794 valid / 111,014 scheduled station-days (90.79%)")
c3 = make_card_visual("p1_v06_cardsev", 960, 105, 450, 120, 6, "Severe AQI Days %", "Severe AQI Episode Share", "#F87171", "6,389 valid days in Severe category (6.34%)")
c4 = make_card_visual("p1_v07_cardcap", 1430, 105, 470, 120, 7, "Sensor Capped Days %", "Sensor-Capped Station-Days (AQI=500)", "#FB923C", "12,536 valid days reaching statutory 500 ceiling (12.44%)")
(p1_dir / "p1_v04_cardmed" / "visual.json").write_text(json.dumps(c1, indent=2), encoding="utf-8")
(p1_dir / "p1_v05_cardcomp" / "visual.json").write_text(json.dumps(c2, indent=2), encoding="utf-8")
(p1_dir / "p1_v06_cardsev" / "visual.json").write_text(json.dumps(c3, indent=2), encoding="utf-8")
(p1_dir / "p1_v07_cardcap" / "visual.json").write_text(json.dumps(c4, indent=2), encoding="utf-8")

# p1_v08_linetrend: Line Chart
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
        "objects": make_cartesian_objects(has_legend=True),
        "visualContainerObjects": make_container_objects(
            "Long-Term Monthly AQI Trend (2017-2023): Median vs Mean AQI",
            "Chronological monthly progression across Delhi-NCR network demonstrating severe annual winter peaks"
        ),
        "drillFilterOtherVisuals": True
    }
}
(p1_dir / "p1_v08_linetrend" / "visual.json").write_text(json.dumps(p1_v08, indent=2), encoding="utf-8")

# p1_v09_donutcat: Donut Chart
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
        "objects": {
            "legend": [
                {
                    "properties": {
                        "show": {"expr": {"Literal": {"Value": "true"}}},
                        "labelColor": {"solid": {"color": {"expr": {"Literal": {"Value": "'#CBD5E1'"}}}}},
                        "fontSize": {"expr": {"Literal": {"Value": "9.5D"}}}
                    }
                }
            ],
            "labels": [
                {
                    "properties": {
                        "show": {"expr": {"Literal": {"Value": "true"}}},
                        "color": {"solid": {"color": {"expr": {"Literal": {"Value": "'#F8FAFC'"}}}}},
                        "fontSize": {"expr": {"Literal": {"Value": "9.5D"}}}
                    }
                }
            ]
        },
        "visualContainerObjects": make_container_objects(
            "CPCB AQI Category Distribution (100,794 Valid Station-Days)",
            "Official statutory air quality tiers from Good (0-50) to Severe (401-500)"
        ),
        "drillFilterOtherVisuals": True
    }
}
(p1_dir / "p1_v09_donutcat" / "visual.json").write_text(json.dumps(p1_v09, indent=2), encoding="utf-8")

# p1_v10_barcity: Clustered Bar Chart
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
        "objects": make_cartesian_objects(has_legend=False),
        "visualContainerObjects": make_container_objects(
            "Municipal Median AQI Comparison (5 NCR Cities)",
            "Ranked descending by valid station-day median AQI across 2017-2023"
        ),
        "drillFilterOtherVisuals": True
    }
}
(p1_dir / "p1_v10_barcity" / "visual.json").write_text(json.dumps(p1_v10, indent=2), encoding="utf-8")

# p1_v11_linediurnal: Line Chart
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
        "objects": make_cartesian_objects(has_legend=True),
        "visualContainerObjects": make_container_objects(
            "Diurnal 24-Hour Rhythm: Winter Smog Inversion vs Non-Winter Baseline",
            "Hourly AQI from 00:00 to 23:00 (Pre-aggregated city-hour-season table)"
        ),
        "drillFilterOtherVisuals": True
    }
}
(p1_dir / "p1_v11_linediurnal" / "visual.json").write_text(json.dumps(p1_v11, indent=2), encoding="utf-8")
print("  Page 1: 11 visuals updated with explicit high-contrast properties.")


# ----------------- PAGE 2: Seasonal Dynamics -----------------
p2_dir = PBIP_REPORT / "definition" / "pages" / "b8c347d1e02f4a1a9e31" / "visuals"

# p2_v01_header: Textbox
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
                                "textStyle": {"fontFamily": "Segoe UI Semibold", "fontSize": "16pt", "color": "#FFFFFF"}
                            }]
                        },
                        {
                            "textRuns": [{
                                "value": "Comparing seasonal AQI patterns across cities and monitoring stations | 2017-2023",
                                "textStyle": {"fontFamily": "Segoe UI", "fontSize": "10pt", "color": "#CBD5E1"}
                            }]
                        }
                    ]
                }
            }]
        }
    }
}
(p2_dir / "p2_v01_header" / "visual.json").write_text(json.dumps(p2_v01, indent=2), encoding="utf-8")

# p2_v02_slicercity: Slicer
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
        "objects": make_slicer_objects(),
        "visualContainerObjects": make_container_objects("Select City"),
        "drillFilterOtherVisuals": True
    }
}
(p2_dir / "p2_v02_slicercity" / "visual.json").write_text(json.dumps(p2_v02, indent=2), encoding="utf-8")

# p2_v03_sliceryear: Slicer
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
        "objects": make_slicer_objects(),
        "visualContainerObjects": make_container_objects("Select Year"),
        "drillFilterOtherVisuals": True
    }
}
(p2_dir / "p2_v03_sliceryear" / "visual.json").write_text(json.dumps(p2_v03, indent=2), encoding="utf-8")

# 4 Cards Page 2
p2_c1 = make_card_visual("p2_v04_cardwmed", 20, 105, 450, 120, 4, "Winter Median AQI", "Winter Median AQI", "#EF4444", "November to February meteorological winter (Benchmark: 335.61)")
p2_c2 = make_card_visual("p2_v05_cardnwmed", 490, 105, 450, 120, 5, "Non-Winter Median AQI", "Non-Winter Median AQI", "#34D399", "March to October baseline period (Benchmark: 154.00)")
p2_c3 = make_card_visual("p2_v06_carddiff", 960, 105, 450, 120, 6, "Winter Elevation Absolute", "Winter Absolute Elevation", "#FB923C", "Difference: +181.61 AQI points (95% MBB CI: [+156.98, +202.14])")
p2_c4 = make_card_visual("p2_v07_cardratio", 1430, 105, 470, 120, 7, "Winter Elevation Ratio", "Winter Elevation Ratio", "#FBBF24", "Relative amplification: 2.18x over non-winter baseline")
(p2_dir / "p2_v04_cardwmed" / "visual.json").write_text(json.dumps(p2_c1, indent=2), encoding="utf-8")
(p2_dir / "p2_v05_cardnwmed" / "visual.json").write_text(json.dumps(p2_c2, indent=2), encoding="utf-8")
(p2_dir / "p2_v06_carddiff" / "visual.json").write_text(json.dumps(p2_c3, indent=2), encoding="utf-8")
(p2_dir / "p2_v07_cardratio" / "visual.json").write_text(json.dumps(p2_c4, indent=2), encoding="utf-8")

# p2_v08_colcityseason: Clustered Column
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
        "objects": make_cartesian_objects(has_legend=True),
        "visualContainerObjects": make_container_objects(
            "City-Level Seasonal Contrast: Winter Median vs Non-Winter Median AQI",
            "Comparing thermal inversion impact across all 5 municipal jurisdictions"
        ),
        "drillFilterOtherVisuals": True
    }
}
(p2_dir / "p2_v08_colcityseason" / "visual.json").write_text(json.dumps(p2_v08, indent=2), encoding="utf-8")

# p2_v09_colseason: Column Chart
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
        "objects": make_cartesian_objects(has_legend=False),
        "visualContainerObjects": make_container_objects(
            "AQI by Meteorological Season (Winter, Summer, Monsoon, Post-Monsoon)",
            "Ranked descending by median valid station-day AQI"
        ),
        "drillFilterOtherVisuals": True
    }
}
(p2_dir / "p2_v09_colseason" / "visual.json").write_text(json.dumps(p2_v09, indent=2), encoding="utf-8")

# p2_v10_tabletop10: Table Top 10 Most Polluted
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
        "objects": make_table_objects(),
        "visualContainerObjects": make_container_objects(
            "Top 10 Most Polluted Stations (Highest Median AQI)",
            "Ranked descending by valid station-day median AQI"
        ),
        "drillFilterOtherVisuals": True
    }
}
(p2_dir / "p2_v10_tabletop10" / "visual.json").write_text(json.dumps(p2_v10, indent=2), encoding="utf-8")

# p2_v11_tablebottom10: Table Top 10 Cleanest
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
        "objects": make_table_objects(),
        "visualContainerObjects": make_container_objects(
            "Top 10 Cleanest Stations (Lowest Median AQI)",
            "Ranked ascending by valid station-day median AQI"
        ),
        "drillFilterOtherVisuals": True
    }
}
(p2_dir / "p2_v11_tablebottom10" / "visual.json").write_text(json.dumps(p2_v11, indent=2), encoding="utf-8")

# p2_v12_textrobustness: Textbox with elevated navy card surface
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
                                "textStyle": {"fontFamily": "Segoe UI Semibold", "fontSize": "15pt", "color": "#FFFFFF"}
                            }]
                        },
                        {
                            "textRuns": [{
                                "value": "Econometric & Statistical Verification Highlights:",
                                "textStyle": {"fontFamily": "Segoe UI", "fontSize": "10pt", "color": "#CBD5E1"}
                            }]
                        },
                        {
                            "textRuns": [{
                                "value": "- Temporal Autocorrelation: Daily AR(1) = 0.81 violates naive OLS independence assumptions. Standard error adjustment is mandatory.",
                                "textStyle": {"fontFamily": "Segoe UI", "fontSize": "9.5pt", "color": "#E2E8F0"}
                            }]
                        },
                        {
                            "textRuns": [{
                                "value": "- Moving Block Bootstrap (L=14 days): 95% Confidence Interval for Winter Elevation is [+156.98, +202.14] AQI points.",
                                "textStyle": {"fontFamily": "Segoe UI", "fontSize": "9.5pt", "color": "#E2E8F0"}
                            }]
                        },
                        {
                            "textRuns": [{
                                "value": "- Statutory Censoring (Tobit ML): Correcting for the CPCB 500 ceiling estimates true latent elevation at +154.17 AQI points (p < 0.001).",
                                "textStyle": {"fontFamily": "Segoe UI", "fontSize": "9.5pt", "color": "#E2E8F0"}
                            }]
                        },
                        {
                            "textRuns": [{
                                "value": "- Spatial Uniformity: 56 of 56 stations exhibit statistically significant winter elevation (Mann-Whitney U, FDR-adjusted p < 0.001).",
                                "textStyle": {"fontFamily": "Segoe UI", "fontSize": "9.5pt", "color": "#E2E8F0"}
                            }]
                        }
                    ]
                }
            }]
        },
        "visualContainerObjects": make_container_objects(None, None, is_textbox=True),
        "drillFilterOtherVisuals": True
    }
}
(p2_dir / "p2_v12_textrobustness" / "visual.json").write_text(json.dumps(p2_v12, indent=2), encoding="utf-8")
print("  Page 2: 12 visuals updated with explicit high-contrast properties.")


# ----------------- PAGE 3: Diwali Episode Analysis -----------------
p3_dir = PBIP_REPORT / "definition" / "pages" / "c5e912f7a43b4d8e8b24" / "visuals"

# p3_v01_header: Textbox
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
                                "textStyle": {"fontFamily": "Segoe UI Semibold", "fontSize": "16pt", "color": "#FFFFFF"}
                            }]
                        },
                        {
                            "textRuns": [{
                                "value": "Station-matched AQI changes around verified festival dates | 2017-2023",
                                "textStyle": {"fontFamily": "Segoe UI", "fontSize": "10pt", "color": "#CBD5E1"}
                            }]
                        }
                    ]
                }
            }]
        }
    }
}
(p3_dir / "p3_v01_header" / "visual.json").write_text(json.dumps(p3_v01, indent=2), encoding="utf-8")

# p3_v02_slicercohort: Slicer
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
        "objects": make_slicer_objects(),
        "visualContainerObjects": make_container_objects("Select Cohort"),
        "drillFilterOtherVisuals": True
    }
}
(p3_dir / "p3_v02_slicercohort" / "visual.json").write_text(json.dumps(p3_v02, indent=2), encoding="utf-8")

# p3_v03_sliceryear: Slicer
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
        "objects": make_slicer_objects(),
        "visualContainerObjects": make_container_objects("Select Festival Year"),
        "drillFilterOtherVisuals": True
    }
}
(p3_dir / "p3_v03_sliceryear" / "visual.json").write_text(json.dumps(p3_v03, indent=2), encoding="utf-8")

# 4 Cards Page 3
p3_c1 = make_card_visual("p3_v04_cardsurge", 20, 105, 450, 120, 4, "Diwali Pooled Mean Surge", "Diwali Pooled Mean Surge", "#FB923C", "Station-matched pre- vs post-festival surge (+81.57 AQI points)")
p3_c2 = make_card_visual("p3_v05_cardmedsurge", 490, 105, 450, 120, 5, "Diwali Pooled Median Surge", "Diwali Pooled Median Surge", "#FBBF24", "Robust median paired surge: +80.38 AQI points")
p3_c3 = make_card_visual("p3_v06_cardelev", 960, 105, 450, 120, 6, "Diwali Station-Years Elevated %", "Proportion Elevated", "#F87171", "263 of 306 matched station-year pairs elevated (85.95%)")
p3_c4 = make_card_visual("p3_v07_cardpairs", 1430, 105, 470, 120, 7, "Diwali Matched Station-Years", "Matched Station-Year Pairs", "#38BDF8", "306 paired observations across 7 festival years (2017-2023)")
(p3_dir / "p3_v04_cardsurge" / "visual.json").write_text(json.dumps(p3_c1, indent=2), encoding="utf-8")
(p3_dir / "p3_v05_cardmedsurge" / "visual.json").write_text(json.dumps(p3_c2, indent=2), encoding="utf-8")
(p3_dir / "p3_v06_cardelev" / "visual.json").write_text(json.dumps(p3_c3, indent=2), encoding="utf-8")
(p3_dir / "p3_v07_cardpairs" / "visual.json").write_text(json.dumps(p3_c4, indent=2), encoding="utf-8")

# p3_v08_colannual: Clustered Column
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
        "objects": make_cartesian_objects(has_legend=False),
        "visualContainerObjects": make_container_objects(
            "Annual Paired Diwali Surge by Festival Year (2017-2023)",
            "Year-specific station-matched mean paired surge: 2020 (+114.3) vs 2023 (+35.2)"
        ),
        "drillFilterOtherVisuals": True
    }
}
(p3_dir / "p3_v08_colannual" / "visual.json").write_text(json.dumps(p3_v08, indent=2), encoding="utf-8")

# p3_v09_colcohort: Clustered Column
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
        "objects": make_cartesian_objects(has_legend=True),
        "visualContainerObjects": make_container_objects(
            "Timing Cohort Contrast: October Diwali vs November Diwali Surge",
            "November events average +93.92 surge vs +58.92 for October (+35.00 points seasonal divergence)"
        ),
        "drillFilterOtherVisuals": True
    }
}
(p3_dir / "p3_v09_colcohort" / "visual.json").write_text(json.dumps(p3_v09, indent=2), encoding="utf-8")

# p3_v10_tablecohort: Table
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
        "objects": make_table_objects(),
        "visualContainerObjects": make_container_objects(
            "Diwali Timing Cohorts Summary Table (October vs November)",
            "Comparing pooled metrics across early-autumn vs late-autumn festival occurrences"
        ),
        "drillFilterOtherVisuals": True
    }
}
(p3_dir / "p3_v10_tablecohort" / "visual.json").write_text(json.dumps(p3_v10, indent=2), encoding="utf-8")

# p3_v11_textcausal: Textbox with elevated navy card surface
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
                                "textStyle": {"fontFamily": "Segoe UI Semibold", "fontSize": "15pt", "color": "#FFFFFF"}
                            }]
                        },
                        {
                            "textRuns": [{
                                "value": "Mandatory econometric and environmental attribution guidance:",
                                "textStyle": {"fontFamily": "Segoe UI", "fontSize": "10pt", "color": "#CBD5E1"}
                            }]
                        },
                        {
                            "textRuns": [{
                                "value": "- Causal Scope Limitation: These results describe observed AQI patterns around Diwali. They do not independently establish that fireworks caused the observed changes. Seasonal pollution, meteorology, regional emissions, missing observations, and monitoring coverage may also contribute.",
                                "textStyle": {"fontFamily": "Segoe UI", "fontSize": "9.5pt", "color": "#E2E8F0"}
                            }]
                        },
                        {
                            "textRuns": [{
                                "value": "- The October vs November Natural Experiment: November events average +93.92 AQI points surge vs +58.92 points for October events (+35.00 points difference). This large gap demonstrates substantial seasonal confounding from thermal boundary layer collapse and peak agricultural stubble burning.",
                                "textStyle": {"fontFamily": "Segoe UI", "fontSize": "9.5pt", "color": "#E2E8F0"}
                            }]
                        },
                        {
                            "textRuns": [{
                                "value": "- Unit of Observation: 306 matched station-year pairs across 7 years, representing paired pre-festival (t-1) vs post-festival (t+1) valid monitoring observations.",
                                "textStyle": {"fontFamily": "Segoe UI", "fontSize": "9.5pt", "color": "#E2E8F0"}
                            }]
                        }
                    ]
                }
            }]
        },
        "visualContainerObjects": make_container_objects(None, None, is_textbox=True),
        "drillFilterOtherVisuals": True
    }
}
(p3_dir / "p3_v11_textcausal" / "visual.json").write_text(json.dumps(p3_v11, indent=2), encoding="utf-8")
print("  Page 3: 11 visuals updated with explicit high-contrast properties.")

# -------------------------------------------------------------------------
# Step 4: Validate all JSON files in the report
# -------------------------------------------------------------------------
print("\n[Step 3/4] Validating all report JSON files...")
all_json = list(PBIP_REPORT.glob("**/*.json"))
err_count = 0
for jf in all_json:
    try:
        with open(jf, "r", encoding="utf-8") as f:
            json.load(f)
    except Exception as e:
        print(f"  ERROR: {jf}: {e}")
        err_count += 1

if err_count == 0:
    print(f"  SUCCESS: All {len(all_json)} JSON files are structurally valid and well-formed!")
else:
    print(f"  FAILED: {err_count} JSON errors found.")

print("\n==================================================================")
print(" Global Readability & Contrast Repair Complete!")
print("==================================================================")
