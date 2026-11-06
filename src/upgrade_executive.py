"""Add the decision views to the local Power BI report project."""

import argparse
import json
import sqlite3
from collections import defaultdict
from pathlib import Path

import numpy as np
from matplotlib.path import Path as PolygonPath

from src import build_desktop_report as pbi

EXECUTIVE = "Executive Summary"
VIEWS = ("Fire Locations", "Fire Hotspots", "Fire Clusters", "Forest Watch", "Carbon Flux")
CREAM = "#F2E6D8"
AMBER = "#FFD291"


def properties(**values):
    return [{"properties": {key: pbi.literal(value) for key, value in values.items()}}]


def color(hex_code):
    return {"solid": {"color": pbi.literal(f"'{hex_code}'")}}


def field(entity, name, kind="Column", aggregate=False):
    expression = {kind: {"Expression": {"SourceRef": {"Entity": entity}}, "Property": name}}
    if aggregate:
        expression = {"Aggregation": {"Expression": expression, "Function": 0}}
    return {
        "field": expression,
        "queryRef": f"{entity}.{name}",
        "nativeQueryRef": name,
        "active": True,
    }


def data_visual(page, title, kind, bounds, roles, objects=None, show_title=True):
    padding = properties(top="6D", bottom="6D", left="8D", right="8D")
    pbi.visual(
        page,
        title,
        kind,
        *bounds,
        query={
            "queryState": {
                role: {"projections": projections} for role, projections in roles.items()
            }
        },
        objects=objects or {},
        visualContainerObjects={
            "padding": padding,
            "title": properties(show=str(show_title).lower(), text=f"'{title}'"),
            "border": properties(show="true", radius="15D"),
        },
    )


def measure(name):
    return field("Executive Metrics", name, "Measure")


def button(page, label, destination, x, width, active=False):
    text = {
        "properties": {
            "text": pbi.literal(f"'{label}'"),
            "fontSize": pbi.literal("10D"),
            "fontColor": color(CREAM),
            "horizontalAlignment": pbi.literal("'center'"),
        },
        "selector": {"id": "default"},
    }
    fill = {
        "properties": {"fillColor": color("#A54028" if active else "#42251E")},
        "selector": {"id": "default"},
    }
    pbi.visual(
        page,
        "Navigate " + label,
        "actionButton",
        x,
        105,
        width,
        43,
        objects={
            "text": [*properties(show="true"), text],
            "fill": [*properties(show="true"), fill],
            "icon": properties(show="false", placement="'left'"),
            "outline": properties(show="false"),
            "shape": properties(tileShape="'rectangleRounded'", roundEdge="8L"),
        },
        visualContainerObjects={
            "background": properties(show="false"),
            "border": properties(show="false"),
            "title": properties(show="false"),
            "visualLink": properties(
                show="true", type="'PageNavigation'", navigationSection=f"'{destination}'"
            ),
        },
    )


def nav(page, current):
    for i, label in enumerate(VIEWS):
        destination = pbi.ident(EXECUTIVE if label == VIEWS[0] else label)
        button(page, label, destination, 14 + 176 * i, 166, label == current)


def map_slicers(page, x):
    for name, width in [("Province or territory", 300), ("Year", 210)]:
        pbi.visual(
            page,
            "Map filter " + name,
            "slicer",
            x,
            158,
            width,
            76,
            query={"queryState": {"Values": {"projections": [field("Map Cells", name)]}}},
            syncGroup={"groupName": "Map " + name, "fieldChanges": True, "filterChanges": True},
            objects={
                "data": properties(mode="'Dropdown'"),
                "header": [
                    {
                        "properties": {
                            "show": pbi.literal("true"),
                            "text": pbi.literal(f"'{name}'"),
                            "fontColor": color(CREAM),
                        }
                    }
                ],
                "items": [{"properties": {"fontColor": color(CREAM), "background": color("#1A1A1E")}}],
            },
            visualContainerObjects={
                "padding": properties(top="6D", bottom="6D", left="8D", right="8D"),
                "title": properties(show="false"),
                "border": properties(show="true", radius="15D"),
            },
        )
        x += width + 12


def azure_map(page, mode, bounds):
    title = {
        "Fire Locations": "Reported area by location",
        "Fire Hotspots": "Historical area hotspots",
        "Fire Clusters": "Nearby location cells",
    }[mode]
    heat = mode == "Fire Hotspots"
    data_visual(
        page,
        title,
        "azureMap",
        bounds,
        {
            "Y": [field("Map Cells", "Latitude")],
            "X": [field("Map Cells", "Longitude")],
            "Size": [field("Map Cells", "Area (ha)", aggregate=True)],
            "Tooltips": [field("Map Cells", "Records", aggregate=True)],
        },
        {
            "bubbleLayer": properties(
                show="false" if heat else "true",
                sizeByValue="true",
                minBubbleRadius="2D",
                maxRadius="8D",
                borderShow="false",
                clusteringEnabled="true" if mode == "Fire Clusters" else "false",
            ),
            "mapControls": properties(defaultStyle="'grayscale_dark'", showStylePicker="true"),
            "heatMapLayer": properties(
                show="true" if heat else "false", heatMapUseSize="true", heatMapRadius="25D"
            ),
        },
    )


def logo(page):
    pbi.visual(
        page,
        "Maple leaf",
        "image",
        25,
        29,
        47,
        47,
        objects={
            "general": [
                {
                    "properties": {
                        "imageUrl": {
                            "expr": {
                                "ResourcePackageItem": {
                                    "PackageName": "RegisteredResources",
                                    "PackageType": 1,
                                    "ItemName": "MapleLeaf.svg",
                                }
                            }
                        }
                    }
                }
            ]
        },
        visualContainerObjects={
            "title": properties(show="false"),
            "background": properties(show="false"),
            "border": properties(show="false"),
            "padding": properties(top="0D", bottom="0D", left="0D", right="0D"),
        },
    )


def header(page, heading, subtitle):
    pbi.note(page, "header band", " ", 14, 9, 1252, 86, fill="#5B2619")
    logo(page)
    pbi.note(page, "header title", heading, 84, 16, 460, 45, 21, bold=True)
    pbi.note(page, "header scope", subtitle, 84, 60, 465, 29, 10)


def executive(page):
    header(page, "Canada Wildfire Dashboard", "2000–2025 · 12 reporting agencies · DRAFT: VERIFY")
    for i, name in enumerate(("Fire records", "Recorded area", "Peak month", "Latest report date")):
        data_visual(
            page,
            name,
            "cardVisual",
            (548 + i * 178, 17, 171, 70),
            {"Data": [measure(name)]},
            {
                "value": [
                    {
                        "properties": {
                            "fontSize": pbi.literal(
                                "12D" if name == "Latest report date" else "15D"
                            ),
                            "fontColor": color(CREAM),
                            "labelDisplayUnits": pbi.literal("1D"),
                        },
                        "selector": {"id": "default"},
                    }
                ],
                "label": [
                    {
                        "properties": {"show": pbi.literal("false")},
                        "selector": {"id": "default"},
                    }
                ],
                "padding": properties(paddingUniform="2D"),
                "layout": properties(paddingUniform="0D"),
                "outline": [
                    {"properties": {"show": pbi.literal("false")}, "selector": {"id": "default"}}
                ],
            },
            show_title=True,
        )
    nav(page, VIEWS[0])
    pbi.chart(
        page,
        "Annual area and five-year mean (million ha)",
        "lineChart",
        "Annual",
        {
            "Category": [("Year", False)],
            "Y": [("Area (million ha)", True), ("Five-year mean (million ha)", True)],
            "Tooltips": [("Records", True)],
        },
        x=14,
        y=158,
        w=714,
        h=202,
        sort=("Year", False, "Ascending"),
    )
    for x, name, bound, target in [
        (14, "July records", "Month scale", "Average known month"),
        (254, "Area in largest 3%", "Share scale", None),
    ]:
        roles = {"Y": [measure(name)], "MaxValue": [measure(bound)]}
        if target:
            roles["TargetValue"] = [measure(target)]
        data_visual(
            page,
            name,
            "gauge",
            (x, 371, 234, 144),
            roles,
            {
                "dataPoint": [{"properties": {"fill": color("#D9622B"), "target": color(AMBER)}}],
                "labels": [{"properties": {"color": color(CREAM)}}],
                "calloutValue": [
                    {"properties": {"color": color(CREAM), "labelDisplayUnits": pbi.literal("1D")}}
                ],
                "target": [{"properties": {"color": color(AMBER)}}],
            },
        )
    data_visual(
        page,
        "Cause coding · 95% known",
        "donutChart",
        (494, 371, 234, 144),
        {
            "Category": [field("Cause Coverage", "Cause coding")],
            "Y": [field("Cause Coverage", "Records", aggregate=True)],
        },
        {
            "legend": properties(show="false"),
            "labels": properties(show="false"),
        },
    )
    pbi.chart(
        page,
        "Records by known month",
        "columnChart",
        "Season",
        {
            "Category": [("Month", False)],
            "Y": [("Records", True)],
        },
        x=14,
        y=525,
        w=714,
        h=129,
        sort=("Month", False, "Ascending"),
    )
    map_slicers(page, 742)
    azure_map(page, VIEWS[0], (742, 242, 524, 250))
    pbi.chart(
        page,
        "Reporting agencies by recorded area",
        "tableEx",
        "Agency",
        {
            "Values": [("Agency", False), ("Area (million ha)", True), ("Records", True)],
        },
        x=742,
        y=502,
        w=524,
        h=152,
        sort=("Area (million ha)", True, "Descending"),
    )
    pbi.note(
        page,
        "decision",
        "Plan for July volume and reserve capacity for large events. The July gauge marker is the average known-month count.",
        15,
        660,
        1250,
        27,
        10,
        AMBER,
        True,
    )
    pbi.note(
        page,
        "scope note",
        "2023 total pending NFD reconciliation. The donut measures cause coding. Map filters apply to rounded cells only.",
        15,
        687,
        1250,
        27,
        10,
        "#C8A99A",
    )


def map_page(label):
    page = pbi.ident(label)
    pbi.item(
        pbi.DEFINITION / "pages" / page / "page.json",
        pbi.REPORT_SCHEMA + "page/2.0.0",
        name=page,
        displayName=label,
        displayOption="FitToPage",
        height=720,
        width=1280,
    )
    header(page, label, "Historical review · 2000–2025 · 12 reporting agencies")
    nav(page, label)
    if label in VIEWS[1:3]:
        map_slicers(page, 14)
        azure_map(page, label, (14, 242, 1252, 398))
        details = {
            "Fire Hotspots": "Colour intensity weights rounded cells by recorded area. Use it to identify where historical area is concentrated.",
            "Fire Clusters": "Zoom to split groups of nearby cells. Cluster counts refer to cells. Use the groups to choose areas for closer review.",
        }
        pbi.note(page, "interpretation", details[label], 15, 650, 1250, 56, 12, AMBER)
    else:
        body = {
            "Forest Watch": "Forest-cover change is unavailable in this model.\n\nUse the historical locations and area views to identify where to request forest-cover data. A forest change layer needs a dated land-cover or forest-loss product with coverage matched to this study.",
            "Carbon Flux": "Spatial carbon flux is unavailable in this model.\n\nA carbon view needs an emissions or flux dataset with documented units, period, and location. Recorded fire size alone cannot estimate emissions or distinguish a carbon source from a sink.",
        }
        pbi.note(page, "data availability", body[label], 24, 185, 1220, 236, 16, fill="#1A1A1E")
        button(page, "Fire Locations", pbi.ident(EXECUTIVE), 14, 166, False)
    return page


def geographic_grid(db):
    records = db.execute("""
        SELECT grid_cell, longitude, latitude, year_key, size_ha
        FROM fact_fire WHERE in_analysis = 1 AND grid_cell IS NOT NULL
        ORDER BY fire_key
    """).fetchall()
    points = np.array([(lon, lat) for _, lon, lat, _, _ in records])
    provinces = np.full(len(records), "Unassigned", dtype=object)
    boundary_path = pbi.ROOT / "data/reference/natural_earth_canada_admin1.json"
    for boundary in json.loads(boundary_path.read_text(encoding="utf-8")):
        geometry = boundary["geometry"]
        polygons = geometry["coordinates"]
        if geometry["type"] == "Polygon":
            polygons = [polygons]
        for exterior, *holes in polygons:
            xs, ys = np.asarray(exterior).T
            candidates = np.flatnonzero(
                (points[:, 0] >= xs.min())
                & (points[:, 0] <= xs.max())
                & (points[:, 1] >= ys.min())
                & (points[:, 1] <= ys.max())
            )
            inside = PolygonPath(exterior).contains_points(points[candidates])
            for hole in holes:
                inside &= ~PolygonPath(hole).contains_points(points[candidates])
            matched = candidates[inside]
            overlap = matched[provinces[matched] != "Unassigned"]
            provinces[matched] = boundary["name"]
            provinces[overlap] = "Unassigned"

    totals = defaultdict(lambda: [0, 0.0])
    for (cell, _, _, year, area), province in zip(records, provinces, strict=True):
        totals[cell, province, year][0] += 1
        totals[cell, province, year][1] += area
    return [
        (cell, *map(int, cell.split("_")), province, year, count, area)
        for (cell, province, year), (count, area) in sorted(totals.items())
    ]


def model_tables(path):
    database = pbi.ROOT / "data/warehouse/wildfire.db"
    with sqlite3.connect(f"{database.resolve().as_uri()}?mode=ro", uri=True) as db:
        count, area, last_date = db.execute("""SELECT COUNT(*), SUM(size_ha),
            MAX(CASE WHEN invalid_calendar_date = 0 THEN report_date END)
            FROM fact_fire WHERE in_analysis = 1""").fetchone()
        known_months = db.execute("""SELECT month_key, COUNT(*) FROM fact_fire
            WHERE in_analysis = 1 AND month_key BETWEEN 1 AND 12 GROUP BY month_key""").fetchall()
        grid = geographic_grid(db)
    assert count == 168276 and round(area, 2) == 83988359.25
    assert dict(known_months)[7] == 42235 and max(known_months, key=lambda row: row[1])[0] == 7
    assert last_date and last_date.startswith("2025-")
    concentration = next(
        float(row["area_share"])
        for row in pbi.rows("review_tables/agency_top3.csv")
        if row["reporting_agency"] == "ALL"
    )
    unknown = next(
        int(row["records"])
        for row in pbi.rows("review_tables/causes.csv")
        if row["cause_class"] == "Unknown"
    )
    assert len({row[0] for row in grid}) == 1121
    assert sum(row[5] for row in grid) == count - 207
    assert {row[4] for row in grid} == set(range(2000, 2026))
    pbi.TABLES.clear()
    pbi.table(
        "Map Cells",
        [
            ("Cell", "string"),
            ("Latitude", "double"),
            ("Longitude", "double"),
            ("Province or territory", "string"),
            ("Year", "int64"),
            ("Records", "int64"),
            ("Area (ha)", "double"),
        ],
        grid,
    )
    for col in pbi.TABLES[-1]["columns"][1:3]:
        col["dataCategory"] = col["name"]
    pbi.table(
        "Cause Coverage",
        [("Cause coding", "string"), ("Records", "int64")],
        [("Known cause", count - unknown), ("Unknown cause", unknown)],
    )
    pbi.table("Executive Metrics", [("Scope", "string")], [("2000–2025 fixed agency scope",)])
    measures = [
        ("Fire records", str(count), "#,0"),
        ("Recorded area", str(area / 1e6), '0.00"M ha"'),
        ("Peak month", '"July"', None),
        ("Latest report date", f'"{last_date}"', None),
        ("July records", "42235", "#,0"),
        ("Average known month", str(sum(row[1] for row in known_months) / 12), "#,0"),
        ("Month scale", "50000", "#,0"),
        ("Area in largest 3%", str(concentration), "0%"),
        ("Share scale", "1", "0%"),
    ]
    pbi.TABLES[-1]["measures"] = [
        {"name": name, "expression": expression, **({"formatString": fmt} if fmt else {})}
        for name, expression, fmt in measures
    ]
    model = json.loads(path.read_text(encoding="utf-8-sig"))
    tables = model["model"]["tables"]
    names = {table["name"] for table in pbi.TABLES}
    tables[:] = [table for table in tables if table["name"] not in names] + pbi.TABLES
    for annotation in model["model"].get("annotations", []):
        if annotation["name"] == "PBI_QueryOrder":
            annotation["value"] = json.dumps([table["name"] for table in tables])
    pbi.write(path, model)
    print(
        f"{count:,} records, {len(grid):,} cells, latest report date {last_date}, {unknown:,} unknown causes."
    )


def main(project):
    pbi.REPORT = project / f"{pbi.NAME}.Report"
    pbi.DEFINITION = pbi.REPORT / "definition"
    model_tables(project / f"{pbi.NAME}.SemanticModel/model.bim")
    resource = pbi.REPORT / "StaticResources/RegisteredResources/MapleLeaf.svg"
    resource.write_text(
        '<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 100 100"><path fill="#F4CFB5" d="M50 4l8 17 8-5-2 23 12-12 3 7 13-2-5 14 7 4-21 17 4 8-24-4 1 24h-8l1-24-24 4 4-8L6 50l7-4-5-14 13 2 3-7 12 12-2-23 8 5z"/></svg>',
        encoding="utf-8",
    )
    report_path = pbi.DEFINITION / "report.json"
    report = json.loads(report_path.read_text(encoding="utf-8-sig"))
    package = next(p for p in report["resourcePackages"] if p["name"] == "RegisteredResources")
    if not any(item["name"] == resource.name for item in package["items"]):
        package["items"].append({"name": resource.name, "path": resource.name, "type": "Image"})
    pbi.write(report_path, report)
    page = pbi.ident(EXECUTIVE)
    for old in (pbi.DEFINITION / "pages" / page / "visuals").glob("*/visual.json"):
        old.unlink()
    executive(page)
    nav_path = pbi.DEFINITION / "pages/pages.json"
    order = json.loads(nav_path.read_text(encoding="utf-8-sig"))
    for label in VIEWS[1:]:
        new_page = map_page(label)
        if new_page not in order["pageOrder"]:
            order["pageOrder"].append(new_page)
    order["activePageName"] = page
    pbi.write(nav_path, order)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("project", type=Path)
    main(parser.parse_args().project)
