"""Apply the requested analysis review before storyboard sign-off."""

import calendar
import json

import nbformat as nb

from src.config import ROOT
from src.review_analysis import tables

R = ROOT
t = tables()
m = json.loads((R / "data/processed/analysis_metrics.json").read_text())
md = nb.v4.new_markdown_cell
code = nb.v4.new_code_cell
setup = """from pathlib import Path
import sys
import pandas as pd
from IPython.display import display, Image
ROOT=Path.cwd()
if ROOT.name=='notebooks': ROOT=ROOT.parent
sys.path.insert(0,str(ROOT))
from src.analyse import query
from src.review_analysis import tables
review=tables()
review['decade_sensitivity']=pd.read_csv(ROOT/'data/processed/review_tables/decade_sensitivity.csv')
review['pooling_comparison']=pd.read_csv(ROOT/'data/processed/review_tables/pooling_comparison.csv')
def chart(name): display(Image(filename=str(ROOT/'images'/(name+'.png'))))
"""


def sql(sql, images=()):
    return code(
        "display(query(" + repr(sql) + "))\n" + "".join("chart(" + repr(n) + ")\n" for n in images)
    )


def review(name, images=()):
    return code(
        "display(review["
        + repr(name)
        + "])\n"
        + "".join("chart(" + repr(n) + ")\n" for n in images)
    )


intro = """# Canada's Wildfire Burden: Where It Falls, and Whether the Data Can Be Trusted

Scope: the approved fixed-reporting-agency series, as recorded in data/analysis_scope.json. Counts are reported records, not verified unique incidents. Agency is the reporting dimension, not geographic jurisdiction.

Source: Canadian Forest Service, Natural Resources Canada, Canadian National Fire Database - Agency Fire Data. Contains information licensed under the Open Government Licence - Canada. Source identity and checksum: data/source_versions.csv.

The opening answer is a placeholder and will be written last, after the detail pages are verified. Finding headings remain DRAFT: verify for the reviewer's wording. No Power BI assets are created here. The peak-year reported-area total is pending NFD reconciliation wherever displayed.
"""
heaps = t["heaping"]
top_heaps = heaps.sort_values("near_01_pct", ascending=False).iloc[0]
other = heaps.sort_values("near_01_pct").iloc[0]
quality = [
    md(intro),
    code(setup),
    md(
        "## The answer will be written after the detail is verified\nI leave the opening synthesis pending. This notebook provides the trust checks used by the concentration and burden story."
    ),
    md(
        "## Concentration needs a source-quality check\nI interpret the concentration results in the companion notebook alongside the recording patterns below. A precise calculation does not establish uniform measurement practices."
    ),
    md(
        "## DRAFT: verify: Recorded sizes cluster at different small values across agencies\nI count sizes at exactly zero, one hundredth and one tenth of a hectare by reporting agency. I show separate near-value counts because the source includes legacy numeric approximations; no sizes are rounded or recoded."
    ),
    review("heaping", ["recording_conventions"]),
    md(
        f"### Takeaway\nThe near-one-tenth-hectare share is {top_heaps.near_01_pct:.2f}% for {top_heaps.reporting_agency} and {other.near_01_pct:.2f}% for {other.reporting_agency}. I see different recording patterns across agencies, consistent with different conventions or measurement precision, but I cannot establish each agency's official convention from heaping alone. The strict-equality columns remain distinct from the tolerance diagnostic."
    ),
    md(
        "## DRAFT: verify: Zero inclusion changes the selected median\nI compare the existing median with a positive-size-only sensitivity while leaving the primary calculation unchanged."
    ),
    sql(
        "SELECT COUNT(*) AS records,AVG(CASE WHEN size_ha=0 THEN 1.0 ELSE 0.0 END) AS zero_share FROM vw_analysis"
    ),
    code(
        "sizes=query('SELECT size_ha FROM vw_analysis').size_ha\ndisplay(pd.DataFrame({'scope':['Including zeros','Positive sizes only'],'records':[len(sizes),int(sizes.gt(0).sum())],'median_ha':[sizes.median(),sizes[sizes.gt(0)].median()]}))"
    ),
    md(
        "### Takeaway\nThe selected median is 0.10 hectares including zeros and 0.20 hectares excluding them, as the executed table shows. I keep valid zeros in the primary result and show the positive-size result as sensitivity. Zero is not automatically recoded as missing."
    ),
    md(
        "## DRAFT: verify: A populated coverage cell does not certify complete reporting\nI inspect source counts by agency and year, with missing and outside-coverage states kept explicit."
    ),
    sql(
        "SELECT reporting_agency,year,source_records,selected_records,coverage_status FROM vw_coverage WHERE year BETWEEN 2000 AND 2025 AND (year IN (2000,2018,2025) OR coverage_status<>'Records present; completeness unverified') ORDER BY reporting_agency,year",
        ["coverage"],
    ),
    md(
        "### Takeaway\nThe matrix shows submissions and documented coverage, not a completeness certificate. PE is displayed for context but remains outside the main fixed-agency series. I would verify an unusually small submission before treating it as low fire activity."
    ),
    md(
        "## DRAFT: verify: Missing report dates and unknown causes vary over time\nI track these gaps using source-wide denominators before analytical exclusions, separately from selected-cohort shares."
    ),
    sql(
        "SELECT unknown_cause_share,missing_report_date_share FROM vw_kpi_summary",
        ["quality_trends"],
    ),
    md(
        "### Takeaway\nThe source-wide chart and selected-cohort table have different denominators, so I do not compare their percentages as if they were identical. Changes in recorded gaps can affect comparisons across time. Independent NFD checks remain pending."
    ),
    md(
        "## Date conflicts remain visible and external agreement remains unverified\nI retain the supplied values and their flags rather than invent corrected dates."
    ),
    sql(
        "SELECT SUM(invalid_calendar_date) AS invalid_calendar_dates,SUM(report_calendar_conflict) AS report_calendar_conflicts,SUM(out_before_report) AS out_before_report FROM fact_fire"
    ),
    sql("SELECT COUNT(*) AS verified_nfd_reference_rows FROM fact_nfd_annual"),
    md(
        "### Takeaway\nThe source includes date conflicts, while the NFD reference table is still empty. Internal reconciliation verifies the calculations, not the source coverage. The 2023 reported-area total is pending NFD reconciliation."
    ),
]
cause_sentences = " ".join(
    f"{r.cause_class} represents {r.count_share:.2%} of selected records and {r.area_share:.2%} of reported area."
    for r in t["causes"].itertuples()
)
decade_sentences = " ".join(
    f"The {int(r.decade)}s group covers {int(r.years_observed)} observed years and averages {r.mean_annual_area / 1e6:.2f} million reported hectares per year."
    for r in t["decades"].itertuples()
)
within = t["agency_top3"].loc[t["agency_top3"].reporting_agency.ne("ALL")]
lo = within.loc[within.area_share.idxmin()]
hi = within.loc[within.area_share.idxmax()]
mon = t["nt_response"].set_index("response_classification").loc["MON"]
nt_sentences = (
    "; ".join(
        f"{r.response_classification} represents {r.record_share:.2%} of NT selected records and {r.area_share:.2%} of NT reported area"
        for r in t["nt_response"].itertuples()
    )
    + "."
)
burden = [
    md(intro),
    code(setup),
    md(
        "## The answer will be written after the detail is verified\nI leave the executive synthesis pending and begin with the concentration evidence."
    ),
    md(
        "## DRAFT: verify: A small share of selected records accounts for most reported area\nI compare the largest-record concentration with the mean and median. Cutoff record counts round upward and ties use the source-row key."
    ),
    sql(
        "SELECT reported_records,area_ha,mean_size_ha,median_size_ha FROM vw_kpi_summary",
        ["size_distribution", "concentration"],
    ),
    md(
        f"### Takeaway\nThe largest three percent of selected records account for {m['top_shares']['3']:.2%} of their reported area. The mean is {m['mean_size_ha']:.2f} hectares and the median is {m['median_size_ha']:.2f} hectares. I would not present the mean as the typical recorded size."
    ),
    md(
        "## DRAFT: verify: The pooled concentration share does not hold equally inside agencies\nI recalculate the same cutoff within each reporting agency, using each agency's records and reported area as its denominator."
    ),
    review("agency_top3", ["agency_concentration"]),
    md(
        f"### Takeaway\nWithin-agency top-three-percent area shares range from {lo.area_share:.2%} in {lo.reporting_agency} to {hi.area_share:.2%} in {hi.reporting_agency}, compared with {m['top_shares']['3']:.2%} pooled. Concentration remains substantial, but the pooled percentage does not describe every agency. The table exposes that sensitivity instead of hiding it."
    ),
    md(
        "## DRAFT: verify: Recording differences limit a pooled comparison\nI use the companion data-quality notebook to check exact small-size counts, near-value heaping, duplicate flags and coverage. These checks qualify the burden calculations rather than replacing them."
    ),
    review("heaping"),
    md(
        "### Takeaway\nAgency recording patterns and incomplete coverage affect comparability. I retain zeros in the primary median, flag unresolved identifiers and show small-size representation explicitly. NFD reconciliation remains pending."
    ),
    md(
        "## DRAFT: verify: The largest reported-area year changes the historical average\nI compare annual totals, a full rolling window and a largest-year sensitivity without trend-significance or causal claims."
    ),
    sql(
        "SELECT year,reported_records,area_ha,yoy_area_change,five_year_mean_area,CASE WHEN year=2023 THEN 'pending NFD reconciliation' ELSE 'External reconciliation not completed' END AS nfd_status FROM vw_annual_trend ORDER BY year",
        ["annual_burden", "annual_records"],
    ),
    sql(
        "SELECT scenario,years,reported_records,area_ha,mean_annual_area FROM vw_largest_year_sensitivity"
    ),
    md(
        f"### Takeaway\nThe largest selected total is {m['peak_area_ha'] / 1e6:.2f} million reported hectares in {m['peak_area_year']}, pending NFD reconciliation. Removing that year lowers the annual mean from {m['mean_annual_area_all_years'] / 1e6:.2f} to {m['mean_annual_area_without_largest_year'] / 1e6:.2f} million hectares. I treat that as sensitivity to an extreme year, not proof of a sustained trend."
    ),
    md(
        "## DRAFT: verify: Decade comparisons use unequal observed-year counts\nI compare mean annual reported area and show each group's observed-year count rather than comparing unequal-duration totals."
    ),
    review("decades"),
    md(
        "### Takeaway\n"
        + decade_sentences
        + " The last group is a partial decade and includes the peak year, whose total is pending NFD reconciliation; these descriptive differences do not establish a reporting-adjusted trend."
    ),
    md(
        "## DRAFT: verify: Seasonal reporting patterns differ by agency\nI use valid source months and preserve the unknown-month count separately."
    ),
    sql(
        "SELECT month_num,SUM(reported_records) AS records,SUM(area_ha) AS area_ha FROM vw_seasonality GROUP BY month_num ORDER BY month_num",
        ["seasonality"],
    ),
    md(
        f"### Takeaway\n{calendar.month_name[m['peak_record_month']]} has the highest pooled valid-month count, {m['peak_month_records']:,}. Another {m['invalid_month_records']:,} selected records have no valid source month. Source month does not establish when all reported area burned."
    ),
    md(
        "## DRAFT: verify: Cause count shares differ from reported-area shares\nI keep all cause classes, including Unknown, in both pooled denominators."
    ),
    review("causes", ["causes"]),
    md(
        "### Takeaway\n"
        + cause_sentences.rstrip(".")
        + "; these are recorded classifications, not causal effects."
    ),
    md(
        "## DRAFT: verify: Cause-by-month segments provide a simpler pooled reporting view\nI pool reporting agencies before calculating large-fire shares by cause and source month. I apply the minimum-record rule to the pooled segments, rather than averaging agency-level shares."
    ),
    review("national_segments", ["national_segments"]),
    md(
        "### Takeaway\nThese shares are conditional on selected reported records, not estimates of population risk. Unknown-month and below-minimum segments remain flagged rather than ranked. Agency-specific detail is retained only in the technical notebook section below."
    ),
    md(
        "## DRAFT: verify: Reporting-agency totals are not geographic provincial totals\nI compare the selected agency submissions without geographic allocation or exposure-adjusted rates."
    ),
    sql(
        "SELECT reporting_agency,reported_records,area_ha,large_fire_share,unknown_cause_share FROM vw_agency ORDER BY area_ha DESC",
        ["agency_burden"],
    ),
    md(
        f"### Takeaway\n{m['largest_reporting_agency']} has the largest selected reporting-agency area sum, {m['largest_agency_reported_area_ha'] / 1e6:.2f} million reported hectares. Reporting scope and coverage differ, and Parks Canada remains its own reporting agency. I do not interpret the ordering as performance or public risk."
    ),
    md(
        "## DRAFT: verify: NT response classification has different record and area shares\nI restrict this view to selected NT records and show FUL, MOD, MON and Unknown. Every record-share denominator is all selected NT records; every area-share denominator is all reported area in that same cohort, including Unknown."
    ),
    review("nt_response", ["nt_response_classification"]),
    md("### Takeaway\n" + nt_sentences + " These classes do not establish a suppression effect."),
    md(
        "## Technical notebook detail: full agency-by-cause-by-month segments\nThis full table stays in the notebook only and will not be used as the reporting or dashboard segment view."
    ),
    sql(
        "SELECT reporting_agency,cause_class,month_num,reported_records,large_fire_records,large_fire_share,do_not_rank FROM vw_segments ORDER BY reporting_agency,cause_class,month_num"
    ),
    md(
        "### Takeaway\nThe full table preserves traceability for a technical review. I will use the pooled cause-by-month version for reporting and continue to flag small or unknown-month segments. Neither table is a forecast."
    ),
]
sensitivity = json.loads((R / "data/processed/review_tables/sensitivity_metrics.json").read_text())
for cell in burden:
    if cell.cell_type == "markdown":
        cell.source = cell.source.replace(
            "A small share of selected records accounts for most reported area",
            f"Within-agency top-three-percent area shares range from {sensitivity['within_agency_min']:.2%} to {sensitivity['within_agency_max']:.2%}",
        )
        cell.source = cell.source.replace(
            "The pooled concentration share does not hold equally inside agencies",
            f"Pooling uses a different cutoff from the {sensitivity['within_agency_min']:.2%} to {sensitivity['within_agency_max']:.2%} agency results",
        )
for index in range(len(burden) - 1, -1, -1):
    cell = burden[index]
    if cell.cell_type == "code" and "review['decades']" in cell.source:
        burden[index + 1 : index + 1] = [
            review("decade_sensitivity"),
            md(
                f"### Sensitivity takeaway\nThe 2020–2025 mean annual reported area is {sensitivity['mean_annual_2020s'] / 1e6:.2f} million hectares over six observed years. Excluding 2023, whose reported total is pending NFD reconciliation, leaves {sensitivity['mean_annual_2020s_without_2023'] / 1e6:.2f} million hectares per year over five years. This describes dependence on one year, not evidence of a trend."
            ),
        ]
    if cell.cell_type == "code" and "review['agency_top3']" in cell.source:
        burden[index + 1 : index + 1] = [
            review("pooling_comparison"),
            md(
                f"### Why pooling changes the figure\nPooling does not average agency percentages: it selects the largest records across the entire selected cohort, reallocating slots between agencies whose fire-size distributions and record volumes differ. The area-weighted agency-specific selections capture {sensitivity['area_weighted_within_agency_top3_share']:.2%} of all selected reported area, compared with {sensitivity['pooled_top3_share']:.2%} under the pooled cutoff; the allocation table shows how record fractions change. Pooling does not exceed every agency's share, and the independently rounded cutoffs select {sensitivity['sum_within_agency_cutoff_records']:,} records across agencies versus {sensitivity['pooled_cutoff_records']:,} pooled, so the rules differ slightly in count as well as membership."
            ),
        ]

for cell in burden:
    if cell.cell_type == "code" and "FROM vw_segments ORDER BY reporting_agency" in cell.source:
        cell.source = "full_segments=query('SELECT reporting_agency,cause_class,month_num,reported_records,large_fire_records,large_fire_share,do_not_rank FROM vw_segments ORDER BY reporting_agency,cause_class,month_num')\nwith pd.option_context('display.max_rows',None):\n    display(full_segments)"
for name, cells in [("01_data_quality_and_coverage", quality), ("02_burden_patterns", burden)]:
    book = nb.v4.new_notebook(
        cells=cells,
        metadata={
            "kernelspec": {"display_name": "Python 3", "language": "python", "name": "python3"}
        },
    )
    nb.write(book, R / "notebooks" / f"{name}.ipynb")
print(cause_sentences + "\n" + decade_sentences + "\n" + nt_sentences)
