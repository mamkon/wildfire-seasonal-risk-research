"""Requested review tables, using the existing approved scope without changing SQL."""

import json

from src.analyse import query
from src.config import PROCESSED

HEAP_SQL = """SELECT reporting_agency,COUNT(*) AS records,
 SUM(CASE WHEN size_ha=0 THEN 1 ELSE 0 END) AS exactly_zero,
 SUM(CASE WHEN size_ha=0.01 THEN 1 ELSE 0 END) AS exactly_001,
 SUM(CASE WHEN size_ha=0.1 THEN 1 ELSE 0 END) AS exactly_01,
 SUM(CASE WHEN ABS(size_ha-0.01)<=0.00000001 THEN 1 ELSE 0 END) AS near_001,
 SUM(CASE WHEN ABS(size_ha-0.1)<=0.00000001 THEN 1 ELSE 0 END) AS near_01
 FROM vw_analysis GROUP BY reporting_agency ORDER BY reporting_agency"""
NT_SQL = """SELECT CASE WHEN r.response_code IN ('FUL','MOD','MON') THEN r.response_code
 ELSE 'Unknown' END AS response_classification,COUNT(*) AS records,SUM(f.size_ha) AS area_ha
 FROM fact_fire f JOIN dim_agency a USING(agency_key) JOIN dim_response r USING(response_key)
 WHERE f.in_analysis=1 AND a.agency_code='NT'
 GROUP BY CASE WHEN r.response_code IN ('FUL','MOD','MON') THEN r.response_code ELSE 'Unknown' END"""
CAUSE_SQL = """SELECT cause_class,SUM(reported_records) AS records,SUM(area_ha) AS area_ha
 FROM vw_cause GROUP BY cause_class ORDER BY cause_class"""
NATIONAL_SEGMENTS_SQL = """SELECT cause_class,month_num,SUM(reported_records) AS records,
 SUM(large_fire_records) AS large_fire_records,
 1.0*SUM(large_fire_records)/SUM(reported_records) AS large_fire_share,
 CASE WHEN SUM(reported_records)<30 OR month_num=-1 THEN 1 ELSE 0 END AS do_not_rank
 FROM vw_segments GROUP BY cause_class,month_num ORDER BY cause_class,month_num"""


def tables():
    heaps = query(HEAP_SQL)
    for label in ["exactly_zero", "exactly_001", "exactly_01", "near_001", "near_01"]:
        heaps[label + "_pct"] = heaps[label] / heaps.records * 100
    nt = (
        query(NT_SQL)
        .set_index("response_classification")
        .reindex(["FUL", "MOD", "MON", "Unknown"], fill_value=0)
        .reset_index()
    )
    nt["record_share"] = nt.records / nt.records.sum()
    nt["area_share"] = nt.area_ha / nt.area_ha.sum()
    nt["record_denominator"] = int(nt.records.sum())
    nt["area_denominator_ha"] = float(nt.area_ha.sum())
    causes = query(CAUSE_SQL)
    causes["count_share"] = causes.records / causes.records.sum()
    causes["area_share"] = causes.area_ha / causes.area_ha.sum()
    decades = query(
        "SELECT decade,years_observed,reported_records,area_ha,mean_annual_area FROM vw_decades ORDER BY decade"
    )
    concentration = query(
        "SELECT reporting_agency,selected_records,area_share FROM vw_concentration WHERE top_pct=3 ORDER BY reporting_agency"
    )
    segments = query(NATIONAL_SEGMENTS_SQL)
    return dict(
        heaping=heaps,
        nt_response=nt,
        causes=causes,
        decades=decades,
        agency_top3=concentration,
        national_segments=segments,
    )


def main():
    out = PROCESSED / "review_tables"
    out.mkdir(exist_ok=True)
    data = tables()
    for name, t in data.items():
        t.to_csv(out / f"{name}.csv", index=False)
    status = {
        "year": 2023,
        "status": "pending NFD reconciliation",
        "applies_to": "Every displayed CNFDB reported-area total for this year; numeric SQL reference values remain unchanged.",
    }
    (PROCESSED / "reconciliation_status.json").write_text(
        json.dumps(status, indent=2), encoding="utf-8"
    )
    for name in ["nt_response", "causes", "decades", "agency_top3"]:
        print(name + "\n" + data[name].to_string(index=False))


if __name__ == "__main__":
    main()
