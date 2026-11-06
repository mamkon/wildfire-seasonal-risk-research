# Canada Wildfire Intelligence (2000–2025)

**Geospatial reporting, data lineage, and large-fire triage**

**Situation.** Fire records from different agencies can reflect different recording practices. For seasonal planning, I wanted to see when the workload was highest, where recorded fire area was concentrated, and which comparisons needed more caution.

**Task.** I built an auditable Power BI project using 26 reporting years from the Canadian National Fire Database (CNFDB). The fixed study scope covers 168,276 records from 12 reporting agencies and sums 83.99 million hectares of recorded fire sizes.

**Action.** I traced the source records through the SQLite warehouse to the dashboard, grouped locations into rounded coordinate cells, and kept the executive indicators at the full study scope. The Trust page shows how agencies record small fire sizes and separates the published national comparison from pending jurisdiction-level reconciliation.

**Result.** The report lets readers compare July's historical record volume with the monthly benchmark and explore recorded area by province or territory and year. The concentration page shows how much of each agency's area came from its largest events, which helps frame where large-event capacity merits closer review.

![Annual recorded fire area and the five-year mean](images/annual_burden.png)

**Companion modeling case study** · [Can we flag recorded Canadian wildfires that reach 200 hectares?](modeling/README.md)

## What I found

| Finding | How I would use it |
| --- | --- |
| The largest 3% of records account for **59% to over 99%** of recorded area within individual agencies. | Review large-event capacity by agency. A pooled national threshold can hide substantial differences in local workload. |
| **July** has the most records with a known report month, at **42,235**. | Use July as a starting point for national seasonal planning, then check individual agency calendars before setting staffing or outreach dates. |
| Natural/lightning causes account for **46% of records and 87% of area**. Human causes account for **49% of records and 8% of area**. | Track the frequency of recorded incidents and the scale of large events separately. They answer different planning questions. |
| Mean annual area for 2020–2025 falls from **6.26 million ha** to **3.99 million ha** when 2023 is removed. | Compare ordinary-year and extreme-year capacity needs. The periods are unequal and reporting changes limit the comparison. |

Agencies record small fires differently. I checked how often each agency records exactly 0, 0.01, and 0.1 ha before comparing typical sizes. Counts refer to database records. Area sums reported sizes and can include overlapping land. The analysis describes historical reporting and provides no forecast of seasonal fire probability.

## How I built it

| Tool | Role in the project |
| --- | --- |
| **Python** | Profiled the source data, preserved exclusion flags, independently checked the SQL results, and produced the notebooks and charts. |
| **Structured Query Language (SQL) / SQLite** | Built the fact and dimension tables and calculated annual totals, seasonal counts, cause shares, and recording checks. |
| **Power BI Desktop** | Built 13 report pages, including Executive Summary, Concentration, Trust, Change, Cause, and Northwest Territories response classification. |
| **Excel** | Packaged summary tables and denominator checks for spreadsheet review. |

Open the [Power BI project](dashboard/Canada_Wildfire.pbip) in Desktop after cloning or downloading the repository. Keep the two project folders beside the project shortcut. Select **Refresh now** if Desktop prompts you to load the embedded summaries. [Build guide](powerbi/BUILD_GUIDE.md)

## Geospatial and semantic model architecture

```text
dashboard/
├── Canada_Wildfire.pbip
├── Canada_Wildfire.Report/
│   ├── definition.pbir
│   ├── definition/
│   └── StaticResources/
└── Canada_Wildfire.SemanticModel/
    ├── definition.pbism
    └── model.bim
```

The Power BI project shortcut (`.pbip`) opens the report. The report's `definition.pbir` links to the local semantic model using `byPath`. The report's `definition/` folder holds page and visual definitions. The GitHub model stores its Data Analysis Expressions (DAX) measures and Power Query M queries in `model.bim`.

| Report control | What it shows |
| --- | --- |
| **Azure Maps** | 168,069 records contribute to 1,121 rounded coordinate cells. Locations, heat and clusters show historical records at cell level. The province or territory and year dropdowns filter those views while the executive indicators retain the full study scope. |
| **Geographic assignment** | Original coordinates are matched to Natural Earth province and territory boundaries before rounding. The 2,275 plottable records without a boundary match appear as **Unassigned**. A separate 207 records have no plottable coordinates and are omitted from the maps. |
| **July benchmark** | The gauge compares 42,235 July records with the average of 13,738 records per calendar month, pooled across the study years and calculated from records with a known month. |
| **Area concentration** | The largest 3% of records account for about 96% of pooled recorded area. The agency-by-agency comparison ranges from 59% to over 99%. |
| **Cause coding** | The donut shows 160,515 records with a known cause and 7,761 with an unknown cause. The source provides no detection confidence score. |
| **Trust and reconciliation** | The full 2023 source-year count and rounded area match the national table in the 2025 annual report. The narrower analytical total remains **pending National Forestry Database reconciliation**. |
| **Forest Watch and Carbon Flux** | These pages describe the external forest-change and carbon datasets needed to support those views. |

[Dashboard opening instructions and proposed palette](dashboard/README.md) · [Natural Earth boundary data](https://www.naturalearthdata.com/downloads/50m-cultural-vectors/50m-admin-1-states-provinces/) · [Reconciliation notes](docs/reconciliation_report.md)

The Executive Summary layout draws on the [SAS Visual Analytics wildfire dashboard](https://communities.sas.com/t5/SAS-Visual-Analytics-Gallery/Fighting-the-Amazon-forest-fires-with-advanced-analytics/ta-p/784221). The Canadian boundary layer comes from [Natural Earth](https://www.naturalearthdata.com/about/terms-of-use/).

Start with the [data quality notebook](notebooks/01_data_quality_and_coverage.ipynb), then read the [burden analysis](notebooks/02_burden_patterns.ipynb). The [Excel workbook](Canada_Wildfire_Review.xlsx) provides the main figures in tables.

## Scope and validation

I used a fixed reporting-agency scope and excluded Prince Edward Island from the main window because its documented coverage starts later. Reporting agencies and geographic jurisdictions are distinct. The Northwest Territories view reports response classifications and includes unknown classifications in its denominators.

The full 2023 source-year count and area rounded to whole hectares match the 2025 annual report's published national table. The project's narrower scope excludes seven Prince Edward Island records and five Ontario records flagged as prescribed fires for that year. **Jurisdiction-by-year National Forestry Database reconciliation is pending.** [Reconciliation notes](docs/reconciliation_report.md)

## Reproduce the analysis

Set up Python with `python -m pip install -r requirements.txt`. From the repository root, run these commands in order:

```text
python -m src.download_data
python -m src.prepare_cnfdb
python -m src.load_warehouse
python -m src.reconcile
make analysis
python -m src.export_powerbi
python -m pytest tests -q
```

On Windows without `make`, run the Python commands under `analysis` in the [Makefile](Makefile). The downloader expects the pinned release in [source_versions.csv](data/source_versions.csv) and verifies its SHA-256. If the provider replaces the current archive, place the matching pinned extract in `data/raw/` before running preparation. Raw inputs, generated row-level exports and the local database are excluded from Git.

The combined [Colab notebook](notebooks/03_colab_research_review.ipynb) contains saved outputs. Its interactive runtime path requires the separate review bundle with the built database and figures.

## Source and attribution

Canadian Forest Service. *Canadian National Fire Database: Agency Fire Data*. Natural Resources Canada, Canadian Forest Service, Northern Forestry Centre. Contains information licensed under the [Open Government Licence – Canada](https://open.canada.ca/en/open-government-licence-canada). [Source directory](https://cwfis.cfs.nrcan.gc.ca/downloads/nfdb/fire_pnt/current_version/) · [Data and reuse notes](docs/data_sources_and_licences.md)
