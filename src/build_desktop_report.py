"""Build a portable PBIR report from the reviewed analytical summaries."""

import base64
import calendar
import csv
import hashlib
import json
from collections import Counter
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
PROJECT = ROOT.parent / "Canada Wildfire Report"
NAME = "Canada Wildfire"
REPORT = PROJECT / f"{NAME}.Report"
MODEL = PROJECT / f"{NAME}.SemanticModel"
DEFINITION = REPORT / "definition"
SCHEMA = "https://developer.microsoft.com/json-schemas/fabric/"
REPORT_SCHEMA = "item/report/definition/"
TABLES = []


def write(path, data):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(data, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def item(path, schema, **data):
    write(path, {"$schema": SCHEMA + schema + "/schema.json", **data})


def rows(path):
    with (ROOT / "data/processed" / path).open(encoding="utf-8-sig", newline="") as f:
        return list(csv.DictReader(f))


def table(name, fields, data):
    types = {"string": "type text", "int64": "Int64.Type", "double": "type number"}
    columns = [
        {"name": field, "sourceColumn": field, "dataType": kind, "summarizeBy": "none"}
        for field, kind in fields
    ]
    names = ", ".join(json.dumps(field) for field, _ in fields)
    conversions = ", ".join(
        "{" + json.dumps(field) + ", " + types[kind] + "}" for field, kind in fields
    )
    payload = base64.b64encode(json.dumps(data, ensure_ascii=False).encode()).decode()
    TABLES.append(
        {
            "name": name,
            "columns": columns,
            "annotations": [
                {"name": "PBI_ResultType", "value": "Table"},
                {"name": "PBI_NavigationStepName", "value": "Navigation"},
            ],
            "partitions": [
                {
                    "name": name,
                    "mode": "import",
                    "source": {
                        "type": "m",
                        "expression": [
                            "let",
                            f'    Source = Table.FromRows(Json.Document(Binary.FromText("{payload}", BinaryEncoding.Base64)), {{{names}}}),',
                            f'    Typed = Table.TransformColumnTypes(Source, {{{conversions}}}, "en-CA")',
                            "in",
                            "    Typed",
                        ],
                    },
                }
            ],
        }
    )


def ident(label):
    return hashlib.sha1(label.encode()).hexdigest()[:20]


def literal(value):
    return {"expr": {"Literal": {"Value": value}}}


def visual(page, label, kind, x, y, w, h, **properties):
    name = ident(page + label)
    item(
        DEFINITION / "pages" / page / "visuals" / name / "visual.json",
        REPORT_SCHEMA + "visualContainer/2.0.0",
        name=name,
        position={"x": x, "y": y, "width": w, "height": h, "z": y * 10 + x, "tabOrder": y * 10 + x},
        visual={"visualType": kind, **properties},
    )


def note(page, label, content, x, y, w, h, size=12, color="#F2E6D8", bold=False):
    paragraphs = [
        {
            "textRuns": [
                {
                    "value": line,
                    "textStyle": {
                        "fontFamily": "Segoe UI",
                        "fontSize": f"{size}pt",
                        "color": color,
                        **({"fontWeight": "bold"} if bold else {}),
                    },
                }
            ]
        }
        for line in content.splitlines()
    ]
    visual(
        page,
        label,
        "textbox",
        x,
        y,
        w,
        h,
        objects={"general": [{"properties": {"paragraphs": paragraphs}}]},
        visualContainerObjects={
            "padding": [
                {"properties": {edge: literal("4D") for edge in ("top", "bottom", "left", "right")}}
            ],
            "background": [{"properties": {"show": literal("true" if h == 100 else "false")}}],
            "border": [
                {
                    "properties": {
                        "show": literal("true" if h == 100 else "false"),
                        "radius": literal("15D"),
                    }
                }
            ],
        },
    )


def chart(page, title, kind, entity, roles, x=24, y=160, w=1232, h=435, sort=None):
    def projection(field, aggregate):
        column = {"Column": {"Expression": {"SourceRef": {"Entity": entity}}, "Property": field}}
        expression = {"Aggregation": {"Expression": column, "Function": 0}} if aggregate else column
        return {
            "field": expression,
            "queryRef": f"{entity}.{field}",
            "nativeQueryRef": field,
            "active": True,
        }

    query = {
        "queryState": {
            role: {"projections": [projection(f, a) for f, a in fields]}
            for role, fields in roles.items()
        }
    }
    if sort:
        query["sortDefinition"] = {
            "sort": [{"field": projection(*sort[:2])["field"], "direction": sort[2]}]
        }
    objects = {} if kind == "tableEx" else axis_objects()
    visual(
        page,
        title,
        kind,
        x,
        y,
        w,
        h,
        query=query,
        drillFilterOtherVisuals=True,
        objects=objects,
        visualContainerObjects={
            "title": [
                {
                    "properties": {
                        "show": literal("true"),
                        "text": literal("'" + title.replace("'", "''") + "'"),
                    }
                }
            ],
            "border": [{"properties": {"show": literal("true"), "radius": literal("15D")}}],
        },
    )


def axis_objects():
    label_color = {"solid": {"color": literal("'#C8A99A'")}}
    return {
        axis: [{"properties": {"labelColor": label_color, "showAxisTitle": literal("false")}}]
        for axis in ("categoryAxis", "valueAxis")
    } | {"legend": [{"properties": {"labelColor": label_color}}]}


CARDS = [
    ("Concentration", "59% to over 99%\nArea from the largest 3%"),
    ("Trust", "Recording varies\nExact small sizes differ"),
    ("Cause", "87% of area\nNatural/lightning class"),
    ("NT response", "90% of area\nModified + monitored"),
]


def fields(*pairs):
    return [(field, aggregate) for field, aggregate in pairs]


def percent_label(p):
    if 0 < p < 0.01:
        return "under 1%"
    if 0.99 < p < 1:
        return "over 99%"
    return f"{p:.0%}"


def main():
    annual = rows("warehouse_exports/vw_annual_trend.csv")
    assert sum(int(r["reported_records"]) for r in annual) == 168276
    assert round(sum(float(r["area_ha"]) for r in annual), 2) == 83988359.25
    table(
        "Annual",
        [
            ("Year", "string"),
            ("Area (million ha)", "double"),
            ("Five-year mean (million ha)", "double"),
            ("Records", "int64"),
        ],
        [
            (
                r["year"],
                float(r["area_ha"]) / 1e6,
                float(r["five_year_mean_area"]) / 1e6 if r["five_year_mean_area"] else None,
                int(r["reported_records"]),
            )
            for r in annual
        ],
    )
    conc = rows("review_tables/agency_top3.csv")
    table(
        "Concentration",
        [
            ("Agency", "string"),
            ("Area share (%)", "double"),
            ("Display share", "string"),
            ("Top records", "int64"),
        ],
        [
            (
                r["reporting_agency"],
                100 * float(r["area_share"]),
                percent_label(float(r["area_share"])),
                int(r["selected_records"]),
            )
            for r in conc
            if r["reporting_agency"] != "ALL"
        ],
    )
    table(
        "Recording",
        [
            ("Agency", "string"),
            ("Exact size", "string"),
            ("Record share (%)", "double"),
            ("Records", "int64"),
            ("Agency records", "int64"),
        ],
        [
            (r["reporting_agency"], label, float(r[key + "_pct"]), int(r[key]), int(r["records"]))
            for r in rows("review_tables/heaping.csv")
            for label, key in [
                ("0 ha", "exactly_zero"),
                ("0.01 ha", "exactly_001"),
                ("0.1 ha", "exactly_01"),
            ]
        ],
    )
    table(
        "Cause",
        [
            ("Cause", "string"),
            ("Record share (%)", "double"),
            ("Area share (%)", "double"),
            ("Records", "int64"),
        ],
        [
            (
                r["cause_class"],
                100 * float(r["count_share"]),
                100 * float(r["area_share"]),
                int(r["records"]),
            )
            for r in rows("review_tables/causes.csv")
        ],
    )
    nt = rows("review_tables/nt_response.csv")
    response = {"FUL": "Full", "MOD": "Modified", "MON": "Monitored", "Unknown": "Unknown"}
    table(
        "NT Response",
        [
            ("Response classification", "string"),
            ("Record share (%)", "double"),
            ("Area share (%)", "double"),
            ("Records", "int64"),
        ],
        [
            (
                response[r["response_classification"]],
                100 * float(r["record_share"]),
                100 * float(r["area_share"]),
                int(r["records"]),
            )
            for r in nt
        ],
    )
    month_counts = Counter()
    for r in rows("warehouse_exports/vw_seasonality.csv"):
        month_counts[int(r["month_num"])] += int(r["reported_records"])
    assert month_counts[7] == 42235 and sum(month_counts.values()) == 168276
    table(
        "Season",
        [("Month", "string"), ("Records", "int64")],
        [(f"{i:02} {calendar.month_abbr[i]}", month_counts[i]) for i in range(1, 13)],
    )
    table(
        "Agency",
        [
            ("Agency", "string"),
            ("Records", "int64"),
            ("Area (million ha)", "double"),
            ("Median size (ha)", "double"),
        ],
        [
            (
                r["reporting_agency"],
                int(r["reported_records"]),
                float(r["area_ha"]) / 1e6,
                float(r["median_size_ha"]),
            )
            for r in rows("warehouse_exports/vw_agency.csv")
        ],
    )
    grid = sorted(
        rows("warehouse_exports/vw_grid.csv"), key=lambda r: float(r["area_ha"]), reverse=True
    )
    table(
        "Grid",
        [
            ("Rounded coordinate cell", "string"),
            ("Area (million ha)", "double"),
            ("Records", "int64"),
        ],
        [
            (r["grid_cell"], float(r["area_ha"]) / 1e6, int(r["reported_records"]))
            for r in grid[:20]
        ],
    )

    item(
        PROJECT / f"{NAME}.pbip",
        "pbip/pbipProperties/1.0.0",
        version="1.0",
        artifacts=[{"report": {"path": REPORT.name}}],
        settings={"enableAutoRecovery": True},
    )
    item(
        REPORT / "definition.pbir",
        "item/report/definitionProperties/2.0.0",
        version="4.0",
        datasetReference={"byPath": {"path": "../" + MODEL.name}},
    )
    item(
        MODEL / "definition.pbism",
        "item/semanticModel/definitionProperties/1.0.0",
        version="1.0",
        settings={},
    )
    write(
        MODEL / "model.bim",
        {
            "name": NAME,
            "compatibilityLevel": 1601,
            "model": {
                "culture": "en-CA",
                "sourceQueryCulture": "en-CA",
                "defaultPowerBIDataSourceVersion": "powerBI_V3",
                "tables": TABLES,
                "annotations": [
                    {"name": "PBI_QueryOrder", "value": json.dumps([t["name"] for t in TABLES])}
                ],
            },
        },
    )
    item(DEFINITION / "version.json", REPORT_SCHEMA + "versionMetadata/1.0.0", version="2.0.0")
    theme = json.loads((ROOT / "powerbi/theme.json").read_text(encoding="utf-8"))
    write(REPORT / "StaticResources/RegisteredResources/Ember.json", theme)
    version = {"visual": "2.5.0", "report": "3.1.0", "page": "2.3.0"}
    item(
        DEFINITION / "report.json",
        REPORT_SCHEMA + "report/3.1.0",
        themeCollection={
            "baseTheme": {
                "name": "CY25SU12",
                "reportVersionAtImport": version,
                "type": "SharedResources",
            },
            "customTheme": {
                "name": "Ember.json",
                "reportVersionAtImport": version,
                "type": "RegisteredResources",
            },
        },
        resourcePackages=[
            {
                "name": "RegisteredResources",
                "type": "RegisteredResources",
                "items": [{"name": "Ember.json", "path": "Ember.json", "type": "CustomTheme"}],
            }
        ],
    )

    pages = json.loads((ROOT / "powerbi/pages.json").read_text(encoding="utf-8"))
    order = [ident(p["navigation"]) for p in pages]
    item(
        DEFINITION / "pages/pages.json",
        REPORT_SCHEMA + "pagesMetadata/1.0.0",
        pageOrder=order,
        activePageName=order[0],
    )
    for p in sorted(pages, key=lambda p: p["build_order"]):
        nav = p["navigation"]
        page = ident(nav)
        item(
            DEFINITION / "pages" / page / "page.json",
            REPORT_SCHEMA + "page/2.0.0",
            name=page,
            displayName=nav,
            displayOption="FitToPage",
            height=720,
            width=1280,
        )
        note(
            page,
            "kicker",
            f"CANADA WILDFIRE RESEARCH  /  {nav.upper()}  /  DRAFT: VERIFY",
            24,
            12,
            1232,
            32,
            11,
            "#E8A33D",
            True,
        )
        note(
            page,
            "headline",
            p["headline"].removeprefix("DRAFT: verify: "),
            24,
            48,
            1232,
            56,
            21,
            bold=True,
        )
        scope = "2000–2025  •  12 reporting agencies  •  Counts are database records. Area sums recorded fire sizes."
        if nav == "NT Response":
            scope = "2000–2025  •  Northwest Territories reporting agency only  •  Unknown stays in both denominators."
        note(page, "scope", scope, 24, 108, 1232, 38, 12, "#C8A99A")
        if nav in ("Executive Summary", "Change"):
            top = 260 if nav == "Executive Summary" else 160
            chart(
                page,
                "Annual area and five-year mean (million ha)",
                "lineChart",
                "Annual",
                {
                    "Category": fields(("Year", False)),
                    "Y": fields(("Area (million ha)", True), ("Five-year mean (million ha)", True)),
                    "Tooltips": fields(("Records", True)),
                },
                y=top,
                h=595 - top,
                sort=("Year", False, "Ascending"),
            )
            note(
                page,
                "peak",
                "2023  •  17.61 million ha  •  pending NFD reconciliation",
                24,
                603,
                1232,
                34,
                13,
                "#E8A33D",
                True,
            )
            if nav == "Change":
                note(
                    page,
                    "sensitivity",
                    "2020–2025 mean: 6.26M ha per year. Excluding 2023: 3.99M ha. 2000s: 1.74M ha. 2010s: 2.91M ha. Reporting changes and unequal periods limit comparisons.",
                    24,
                    643,
                    1232,
                    60,
                )
            else:
                for i, (label, answer) in enumerate(CARDS):
                    note(
                        page,
                        label,
                        label.upper() + "\n" + answer,
                        24 + i * 312,
                        155,
                        296,
                        100,
                        12,
                        "#F2E6D8",
                        True,
                    )
                note(
                    page,
                    "context",
                    "168,276 records  •  83.99 million ha  •  Natural Resources Canada, Canadian National Fire Database",
                    24,
                    647,
                    1232,
                    40,
                )
        elif nav == "Concentration":
            chart(
                page,
                "Area in the largest 3% of records within each agency",
                "barChart",
                "Concentration",
                {
                    "Category": fields(("Agency", False)),
                    "Y": fields(("Area share (%)", True)),
                    "Tooltips": fields(("Display share", False), ("Top records", True)),
                },
                sort=("Area share (%)", True, "Descending"),
            )
            note(
                page,
                "callout",
                "Yukon: 59%. Alberta: over 99%. The pooled national share is 96%, using one cutoff across agencies.",
                24,
                610,
                1232,
                60,
            )
        elif nav == "Trust":
            chart(
                page,
                "Share of agency records at each exact size",
                "clusteredBarChart",
                "Recording",
                {
                    "Category": fields(("Agency", False)),
                    "Series": fields(("Exact size", False)),
                    "Y": fields(("Record share (%)", True)),
                    "Tooltips": fields(("Records", True), ("Agency records", True)),
                },
                h=395,
            )
            note(
                page,
                "recording",
                "Alberta records cluster at exactly 0.01 ha. Quebec has a higher share at exactly zero.",
                24,
                566,
                1232,
                38,
            )
            note(
                page,
                "evidence",
                "The full 2023 source count and rounded area match the 2025 annual report. Jurisdiction-by-year NFD reconciliation is pending.",
                24,
                609,
                1232,
                64,
                12,
                "#C8A99A",
            )
        elif nav in ("Cause", "NT Response"):
            nt_page = nav == "NT Response"
            category = "Response classification" if nt_page else "Cause"
            chart(
                page,
                "Record share compared with area share",
                "clusteredBarChart",
                nav,
                {
                    "Category": fields((category, False)),
                    "Y": fields(("Record share (%)", True), ("Area share (%)", True)),
                    "Tooltips": fields(("Records", True)),
                },
            )
            line = (
                "Modified and monitored together account for 90% of area. Denominators: 5,222 records and 16.68 million ha."
                if nt_page
                else "Natural/lightning: 46% of records and 87% of area. Human: 49% of records and 8% of area."
            )
            note(page, "callout", line, 24, 610, 1232, 60)
        elif nav == "Season":
            chart(
                page,
                "Records by known report month",
                "columnChart",
                "Season",
                {"Category": fields(("Month", False)), "Y": fields(("Records", True))},
                sort=("Month", False, "Ascending"),
            )
            note(
                page,
                "callout",
                "July has 42,235 records, the highest pooled count. The chart omits 3,418 records with unknown month.",
                24,
                610,
                1232,
                60,
            )
        elif nav == "Agency Scorecard":
            chart(
                page,
                "Area, counts and median size by reporting agency",
                "tableEx",
                "Agency",
                {
                    "Values": fields(
                        ("Agency", False),
                        ("Area (million ha)", True),
                        ("Records", True),
                        ("Median size (ha)", True),
                    )
                },
            )
            note(
                page,
                "callout",
                "Compare recording conventions before interpreting differences in median sizes.",
                24,
                610,
                1232,
                60,
            )
        else:
            chart(
                page,
                "Top 20 rounded coordinate cells by area",
                "barChart",
                "Grid",
                {
                    "Category": fields(("Rounded coordinate cell", False)),
                    "Y": fields(("Area (million ha)", True)),
                    "Tooltips": fields(("Records", True)),
                },
                sort=("Area (million ha)", True, "Descending"),
            )
            note(
                page,
                "callout",
                "Cells group rounded coordinates. The values sum recorded sizes and do not trace fire perimeters.",
                24,
                610,
                1232,
                60,
            )
    print(f"Built {len(pages)} pages and {len(TABLES)} embedded tables.")


if __name__ == "__main__":
    main()
