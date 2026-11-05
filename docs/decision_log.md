# Decision log

| Choice | Why I made it | Limitation |
|---|---|---|
| One source row remains one master record | I want traceable flags rather than silent deletion. | Candidate counts exclude flagged later exact duplicates. |
| Cause mapping in a seed file | The source codes and decisions can be reviewed separately from code. | Unknown and unmapped codes stay visible. |
| Reporting agency has no derived province | Agency reporting does not establish geographic location. | Provincial spatial allocation remains future work. |
| Keep local response codes unmapped | Only FUL, MOD and MON have a standard definition in the inspected attribute documentation. | I do not compare national active-versus-monitored burden. |
| Explicit prescribed evidence is flagged across source fields | PRESCRIBED alone misses evidence recorded elsewhere. | Missing flags cannot prove wildfire-only scope. |
| Positive source year checked against documented agency coverage | The file contains a sentinel and a positive year outside documented coverage. | A plausible number does not verify its correctness. |
| Invalid coordinates retained, grid cells left missing | Invalid location should not remove a record from nonspatial counts. | Bounding-box checks do not establish a location is on Canadian land. |
| Rounded degree grid, not floor-based cells | This follows the revised specification for a simple display aggregation. | Rounding follows pandas half-to-even; geographic cell areas vary. |
| Size classes use left-closed, right-open bounds | Boundary records fall into one documented class. | The last class has no finite upper bound. |
| Large-fire threshold and sensitivity choices in config | The threshold is an analytical definition, not a discovered physical boundary. | Segment thresholds and rankings still require a decision later. |
| Present candidate windows rather than select silently | History and agency coverage involve a trade-off the reviewer should choose. | No selected-window fact table has been built. |
| No external-reconciliation assertion | I have not acquired the official NFD totals. | Independent agreement remains unknown. |

## Approved window and SQL choices

I use the modern fixed-agency candidate selected by the reviewer. The load batch records its actual start, end and source hash. PE is excluded from this fixed series because its documented coverage starts later. The wider recent candidate remains a sensitivity option, not an unlabelled addition.

I retain all source rows in fact_fire and expose the selected scope explicitly. I do not use fire identifiers as unique incident keys. Every dimension has an Unknown member. Separate source-year and source-month dimensions preserve valid partial dates without inventing calendar days.

I use a provisional minimum segment size recorded in src/load_warehouse.py and the segment view. Below-minimum and unknown-month segments are flagged and must not be ranked. This is a reporting rule, not a statistical guarantee; it can be revised transparently during the analysis review. Exact concentration cutoffs use ceiling record counts and deterministic source-row tie breaking.

The first rolling values remain missing until the full declared window is available. Missing annual area is not filled as zero. Partial decades are labelled with their observed-year count. No significance tests or causal interpretations are introduced.

## Requested checkpoint audit: existing build unchanged

I audited the approved **2000 to 2025, inclusive**, fixed-reporting-agency series. PE is excluded from the main series; reporting agency is not geographic jurisdiction. This audit reads the existing flagged source and database without changing either. The analysis notebooks already exist from the preceding checkpoint; I have not revised them or advanced the build during this audit.

### Exclusions: counts and reported hectares
The first table assigns each source row one reason, using the order shown in the overlapping-rules table below. This provides an additive reconciliation; it is an explanation of the existing filter, not a new exclusion policy. All hectare values are sums of source-reported SIZE_HA, not unique geographic burned land. No size is missing or negative in this pinned source.

| audit_reason | records | total_ha | first_year | last_year |
|---|---|---|---|---|
| Exact duplicate after first | 4 | 4,350.571296 | 1994 | 2021 |
| Invalid source year | 95 | 73,983.440000 | -999 | -999 |
| Known prescribed burn | 379 | 107,495.630470 | 2000 | 2025 |
| Outside approved analysis window | 279808 | 82,653,299.813321 | 1946 | 1999 |
| Outside documented agency years | 1 | 0.009000 | 1930 | 1930 |
| Reporting agency PE excluded | 55 | 73.368542 | 2018 | 2025 |
| Retained | 168276 | 83,988,359.254197 | 2000 | 2025 |


By reporting agency and observed source-year range:

| reporting_agency | audit_reason | records | total_ha | first_year | last_year |
|---|---|---|---|---|---|
| AB | Exact duplicate after first | 1 | 0.100000 | 1995 | 1995 |
| AB | Known prescribed burn | 23 | 792.980000 | 2002 | 2011 |
| AB | Outside approved analysis window | 32247 | 5,369,483.874553 | 1959 | 1999 |
| AB | Retained | 35475 | 8,466,728.940000 | 2000 | 2025 |
| BC | Outside approved analysis window | 112892 | 4,919,787.560000 | 1950 | 1999 |
| BC | Outside documented agency years | 1 | 0.009000 | 1930 | 1930 |
| BC | Retained | 43677 | 10,621,125.814000 | 2000 | 2025 |
| MB | Exact duplicate after first | 2 | 4,349.371296 | 2021 | 2021 |
| MB | Outside approved analysis window | 17967 | 11,795,156.370000 | 1959 | 1999 |
| MB | Retained | 10828 | 8,256,094.998020 | 2000 | 2025 |
| NB | Outside approved analysis window | 5149 | 71,308.400000 | 1980 | 1999 |
| NB | Retained | 7032 | 14,070.300000 | 2000 | 2025 |
| NL | Exact duplicate after first | 1 | 1.100000 | 1994 | 1994 |
| NL | Outside approved analysis window | 2374 | 1,661,716.600000 | 1955 | 1999 |
| NL | Retained | 2540 | 406,752.165460 | 2000 | 2025 |
| NS | Outside approved analysis window | 5262 | 18,034.580000 | 1960 | 1999 |
| NS | Retained | 5825 | 51,419.120475 | 2000 | 2025 |
| NT | Known prescribed burn | 1 | 17.800000 | 2000 | 2000 |
| NT | Outside approved analysis window | 10083 | 20,278,896.300000 | 1959 | 1999 |
| NT | Retained | 5222 | 16,683,860.484011 | 2000 | 2025 |
| ON | Known prescribed burn | 57 | 16,587.700092 | 2000 | 2025 |
| ON | Outside approved analysis window | 42162 | 7,339,472.802566 | 1959 | 1999 |
| ON | Retained | 23662 | 4,342,521.294909 | 2000 | 2025 |
| PC | Known prescribed burn | 291 | 90,087.350378 | 2008 | 2025 |
| PC | Outside approved analysis window | 1382 | 2,297,177.900000 | 1946 | 1999 |
| PC | Retained | 2815 | 3,419,079.888059 | 2000 | 2025 |
| PE | Reporting agency PE excluded | 55 | 73.368542 | 2018 | 2025 |
| QC | Outside approved analysis window | 29727 | 9,290,510.730000 | 1959 | 1999 |
| QC | Retained | 15636 | 9,753,307.625848 | 2000 | 2025 |
| SK | Outside approved analysis window | 14753 | 13,029,981.946202 | 1959 | 1999 |
| SK | Retained | 12570 | 17,101,300.409415 | 2000 | 2025 |
| YT | Invalid source year | 95 | 73,983.440000 | -999 | -999 |
| YT | Known prescribed burn | 7 | 9.800000 | 2022 | 2022 |
| YT | Outside approved analysis window | 5810 | 6,581,772.750000 | 1946 | 1999 |
| YT | Retained | 2994 | 4,872,098.214000 | 2000 | 2025 |


The first_year and last_year columns show the observed range within each group; they do not imply every intervening year has records. A negative year is the unchanged source sentinel, not a calendar year. In addition, the rules overlap as follows, so this next table must not be summed:

| reason | records | total_ha |
|---|---|---|
| Exact duplicate after first | 4 | 4,350.571296 |
| Invalid source year | 95 | 73,983.440000 |
| Outside documented agency years | 96 | 73,983.449000 |
| Outside approved analysis window | 279906 | 82,727,284.462321 |
| Reporting agency PE excluded | 55 | 73.368542 |
| Known prescribed burn | 438 | 166,395.800466 |
| Invalid size | 0 | 0.000000 |
| Unknown reporting agency | 0 | 0.000000 |


Invalid coordinates, missing dates and invalid months are not blanket exclusions from annual size/count totals. They are flagged for analyses that require those fields. Records may therefore be retained for annual totals but unavailable for a map or monthly summary.

### Size heaping
I use strict numeric equality for the exact-count columns. The source contains legacy floating-point values near the requested decimal sizes, so I also show a separately labelled tolerance check. I have not rounded or changed any stored sizes. The tolerance is a diagnostic choice, not an additional exact count.

| reporting_agency | records | exact_0_ha | exact_0.01_ha | within_1e-8_of_0.01_ha | exact_0.1_ha | within_1e-8_of_0.1_ha |
|---|---|---|---|---|---|---|
| ALL SELECTED | 168276 | 8963 | 21256 | 21411 | 20080 | 30410 |
| AB | 35475 | 0 | 16231 | 16231 | 3844 | 3844 |
| BC | 43677 | 255 | 1896 | 1896 | 3930 | 3930 |
| MB | 10828 | 154 | 0 | 0 | 1809 | 1809 |
| NB | 7032 | 66 | 0 | 0 | 3440 | 3440 |
| NL | 2540 | 1115 | 0 | 0 | 361 | 361 |
| NS | 5825 | 929 | 689 | 838 | 623 | 721 |
| NT | 5222 | 70 | 295 | 301 | 285 | 301 |
| ON | 23662 | 2 | 0 | 0 | 490 | 10706 |
| PC | 2815 | 41 | 448 | 448 | 533 | 533 |
| QC | 15636 | 6159 | 0 | 0 | 2222 | 2222 |
| SK | 12570 | 77 | 1254 | 1254 | 2293 | 2293 |
| YT | 2994 | 95 | 443 | 443 | 250 | 250 |


**Zero-size records are included in the existing median.** The SQL median agrees with the including-zero calculation below. Excluding zeros changes the population to positive reported sizes, rather than correcting a known error.

| scope | records | median_ha |
|---|---|---|
| Selected, including zeros | 168276 | 0.100000 |
| Selected, positive sizes only | 159313 | 0.200000 |


I recommend retaining valid zero sizes in the primary descriptive result, reporting the zero share explicitly, and showing the positive-size median as sensitivity. I would not recode zeros as missing without source evidence. The large difference between exact and tolerance counts, if present, should be explained as numeric representation rather than a new physical size class.

### Duplicates using reporting agency + source year + FIRE_ID
I trim surrounding whitespace in the key for this audit. Missing identifiers or invalid source years are counted separately, not collapsed into a shared duplicate key. Repeated composite keys are not necessarily duplicate incidents: the source can reuse identifiers for records with different dates, coordinates or sizes.

| scope | records_with_missing_or_invalid_key | repeated_composite_keys | records_in_repeated_keys | excess_records_beyond_first_key | later_exact_duplicate_rows | later_exact_duplicate_area_ha |
|---|---|---|---|---|---|---|
| All source rows | 260 | 1198 | 2762 | 1564 | 4 | 4,350.571296 |
| Approved agency/year scope before eligibility exclusions | 0 | 574 | 1180 | 606 | 2 | 4,349.371296 |
| Selected analysis records | 0 | 523 | 1078 | 555 | 0 | 0.000000 |


Later occurrences of source-wide exact duplicate rows are:

| reporting_agency | year | FIRE_ID | NFDBFIREID | duplicate_area_ha | selected |
|---|---|---|---|---|---|
| AB | 1995 | DP2-015-95 | AB-1995-DP2-015-95 | 0.100000 | False |
| MB | 2021 | MB2021EA136 | MB-2021-MB2021EA136 | 497.465385 | False |
| MB | 2021 | MB2021NO031 | MB-2021-MB2021NO031 | 3,851.905911 | False |
| NL | 1994 | 1994-302 | NL-1994-302 | 1.100000 | False |


I recommend the current conservative handling: preserve every source row for traceability, exclude only later exact copies from analysis, and retain but flag nonidentical composite-key collisions until their source submissions can be checked. Exact copies would double-count their listed area if both copies entered a sum; the selected cohort already excludes the later exact copies. I do not recommend DISTINCTCOUNT(FIRE_ID) or automatic composite-key deletion as a fix.

### Response category: population and categories
Agency-level summaries for all source years and the selected cohort:

| scope | reporting_agency | records | response_populated_pct | categories |
|---|---|---|---|---|
| All source years | AB | 67746 | 0.00% | None |
| All source years | BC | 156570 | 4.51% | FUL, MOD, MON |
| All source years | MB | 28797 | 19.44% | Actioned, FUL, Limited Action, MOD, MON, No Action |
| All source years | NB | 12181 | 0.00% | None |
| All source years | NL | 4915 | 0.00% | None |
| All source years | NS | 11087 | 11.64% | FUL |
| All source years | NT | 15306 | 56.51% | FUL, MOD, MON |
| All source years | ON | 65881 | 63.12% | FUL, MDP, MNP, MOD, MON, PRO, SUP |
| All source years | PC | 4488 | 40.17% | FUL, MOD, MON |
| All source years | PE | 55 | 100.00% | FUL |
| All source years | QC | 45363 | 1.23% | FUL, MOD, MON |
| All source years | SK | 27323 | 0.00% | None |
| All source years | YT | 8906 | 6.23% | FUL |
| Selected analysis records | AB | 35475 | 0.00% | None |
| Selected analysis records | BC | 43677 | 16.15% | FUL, MOD, MON |
| Selected analysis records | MB | 10828 | 51.68% | Actioned, FUL, Limited Action, MOD, MON, No Action |
| Selected analysis records | NB | 7032 | 0.00% | None |
| Selected analysis records | NL | 2540 | 0.00% | None |
| Selected analysis records | NS | 5825 | 22.15% | FUL |
| Selected analysis records | NT | 5222 | 98.37% | FUL, MOD, MON |
| Selected analysis records | ON | 23662 | 100.00% | FUL, MDP, MNP, MOD, MON, PRO, SUP |
| Selected analysis records | PC | 2815 | 63.27% | FUL, MOD, MON |
| Selected analysis records | QC | 15636 | 3.58% | FUL, MOD, MON |
| Selected analysis records | SK | 12570 | 0.00% | None |
| Selected analysis records | YT | 2994 | 18.54% | FUL |


Every populated agency-year group in the approved period is listed below, including groups whose RESPONSE population is zero. The source-period table includes PE for context; PE does not enter the selected-cohort table. If an agency-year has no source rows, a population percentage is undefined, not zero; those cells are identified in the existing coverage matrix rather than invented here.

| scope | reporting_agency | year | records | response_populated_pct | categories |
|---|---|---|---|---|---|
| Source rows in approved years | AB | 2000 | 783 | 0.00% | None |
| Source rows in approved years | AB | 2001 | 974 | 0.00% | None |
| Source rows in approved years | AB | 2002 | 1445 | 0.00% | None |
| Source rows in approved years | AB | 2003 | 1191 | 0.00% | None |
| Source rows in approved years | AB | 2004 | 1611 | 0.00% | None |
| Source rows in approved years | AB | 2005 | 1374 | 0.00% | None |
| Source rows in approved years | AB | 2006 | 2027 | 0.00% | None |
| Source rows in approved years | AB | 2007 | 1337 | 0.00% | None |
| Source rows in approved years | AB | 2008 | 1722 | 0.00% | None |
| Source rows in approved years | AB | 2009 | 1673 | 0.00% | None |
| Source rows in approved years | AB | 2010 | 1892 | 0.00% | None |
| Source rows in approved years | AB | 2011 | 1173 | 0.00% | None |
| Source rows in approved years | AB | 2012 | 1605 | 0.00% | None |
| Source rows in approved years | AB | 2013 | 1218 | 0.00% | None |
| Source rows in approved years | AB | 2014 | 1451 | 0.00% | None |
| Source rows in approved years | AB | 2015 | 1856 | 0.00% | None |
| Source rows in approved years | AB | 2016 | 1436 | 0.00% | None |
| Source rows in approved years | AB | 2017 | 1244 | 0.00% | None |
| Source rows in approved years | AB | 2018 | 1299 | 0.00% | None |
| Source rows in approved years | AB | 2019 | 1021 | 0.00% | None |
| Source rows in approved years | AB | 2020 | 744 | 0.00% | None |
| Source rows in approved years | AB | 2021 | 1383 | 0.00% | None |
| Source rows in approved years | AB | 2022 | 1297 | 0.00% | None |
| Source rows in approved years | AB | 2023 | 1131 | 0.00% | None |
| Source rows in approved years | AB | 2024 | 1273 | 0.00% | None |
| Source rows in approved years | AB | 2025 | 1338 | 0.00% | None |
| Source rows in approved years | BC | 2000 | 1526 | 0.00% | None |
| Source rows in approved years | BC | 2001 | 1291 | 0.00% | None |
| Source rows in approved years | BC | 2002 | 1772 | 0.00% | None |
| Source rows in approved years | BC | 2003 | 2457 | 0.00% | None |
| Source rows in approved years | BC | 2004 | 2405 | 0.00% | None |
| Source rows in approved years | BC | 2005 | 994 | 0.00% | None |
| Source rows in approved years | BC | 2006 | 2560 | 0.00% | None |
| Source rows in approved years | BC | 2007 | 1607 | 0.00% | None |
| Source rows in approved years | BC | 2008 | 2025 | 0.00% | None |
| Source rows in approved years | BC | 2009 | 3049 | 0.00% | None |
| Source rows in approved years | BC | 2010 | 1689 | 0.00% | None |
| Source rows in approved years | BC | 2011 | 646 | 0.00% | None |
| Source rows in approved years | BC | 2012 | 1640 | 0.00% | None |
| Source rows in approved years | BC | 2013 | 1867 | 0.00% | None |
| Source rows in approved years | BC | 2014 | 1469 | 0.00% | None |
| Source rows in approved years | BC | 2015 | 1863 | 0.00% | None |
| Source rows in approved years | BC | 2016 | 1068 | 0.00% | None |
| Source rows in approved years | BC | 2017 | 1349 | 0.00% | None |
| Source rows in approved years | BC | 2018 | 2089 | 0.00% | None |
| Source rows in approved years | BC | 2019 | 834 | 0.00% | None |
| Source rows in approved years | BC | 2020 | 668 | 0.00% | None |
| Source rows in approved years | BC | 2021 | 1649 | 0.00% | None |
| Source rows in approved years | BC | 2022 | 1783 | 96.75% | FUL, MOD, MON |
| Source rows in approved years | BC | 2023 | 2280 | 98.60% | FUL, MOD, MON |
| Source rows in approved years | BC | 2024 | 1725 | 99.30% | FUL, MOD, MON |
| Source rows in approved years | BC | 2025 | 1372 | 99.85% | FUL, MOD, MON |
| Source rows in approved years | MB | 2000 | 353 | 0.00% | None |
| Source rows in approved years | MB | 2001 | 527 | 0.00% | None |
| Source rows in approved years | MB | 2002 | 755 | 0.00% | None |
| Source rows in approved years | MB | 2003 | 1207 | 0.00% | None |
| Source rows in approved years | MB | 2004 | 55 | 0.00% | None |
| Source rows in approved years | MB | 2005 | 248 | 56.85% | Actioned, FUL, Limited Action, MOD, No Action |
| Source rows in approved years | MB | 2006 | 682 | 64.08% | Actioned, FUL, MOD, No Action |
| Source rows in approved years | MB | 2007 | 382 | 64.66% | Actioned, FUL, Limited Action, MOD |
| Source rows in approved years | MB | 2008 | 397 | 67.76% | Actioned, FUL, MOD, No Action |
| Source rows in approved years | MB | 2009 | 184 | 69.02% | FUL |
| Source rows in approved years | MB | 2010 | 583 | 61.41% | Actioned, FUL, Limited Action, MOD, No Action |
| Source rows in approved years | MB | 2011 | 315 | 64.44% | Actioned, FUL, Limited Action, MOD, No Action |
| Source rows in approved years | MB | 2012 | 497 | 50.50% | FUL, MOD |
| Source rows in approved years | MB | 2013 | 494 | 40.69% | FUL, MOD |
| Source rows in approved years | MB | 2014 | 245 | 49.80% | FUL, MOD |
| Source rows in approved years | MB | 2015 | 459 | 56.86% | FUL, MOD |
| Source rows in approved years | MB | 2016 | 202 | 58.42% | FUL, MOD |
| Source rows in approved years | MB | 2017 | 557 | 42.19% | FUL, MOD |
| Source rows in approved years | MB | 2018 | 476 | 100.00% | FUL, MOD, MON |
| Source rows in approved years | MB | 2019 | 278 | 100.00% | FUL, MOD, MON |
| Source rows in approved years | MB | 2020 | 151 | 98.68% | FUL, MOD, MON |
| Source rows in approved years | MB | 2021 | 494 | 92.91% | FUL, MOD, MON |
| Source rows in approved years | MB | 2022 | 224 | 100.00% | FUL, MOD, MON |
| Source rows in approved years | MB | 2023 | 300 | 100.00% | FUL, MOD, MON |
| Source rows in approved years | MB | 2024 | 321 | 96.57% | FUL, MOD, MON |
| Source rows in approved years | MB | 2025 | 444 | 97.30% | FUL, MOD, MON |
| Source rows in approved years | NB | 2000 | 333 | 0.00% | None |
| Source rows in approved years | NB | 2001 | 490 | 0.00% | None |
| Source rows in approved years | NB | 2002 | 317 | 0.00% | None |
| Source rows in approved years | NB | 2003 | 228 | 0.00% | None |
| Source rows in approved years | NB | 2004 | 253 | 0.00% | None |
| Source rows in approved years | NB | 2005 | 306 | 0.00% | None |
| Source rows in approved years | NB | 2006 | 308 | 0.00% | None |
| Source rows in approved years | NB | 2007 | 316 | 0.00% | None |
| Source rows in approved years | NB | 2008 | 168 | 0.00% | None |
| Source rows in approved years | NB | 2009 | 197 | 0.00% | None |
| Source rows in approved years | NB | 2010 | 179 | 0.00% | None |
| Source rows in approved years | NB | 2011 | 67 | 0.00% | None |
| Source rows in approved years | NB | 2012 | 338 | 0.00% | None |
| Source rows in approved years | NB | 2013 | 353 | 0.00% | None |
| Source rows in approved years | NB | 2014 | 180 | 0.00% | None |
| Source rows in approved years | NB | 2015 | 221 | 0.00% | None |
| Source rows in approved years | NB | 2016 | 285 | 0.00% | None |
| Source rows in approved years | NB | 2017 | 245 | 0.00% | None |
| Source rows in approved years | NB | 2018 | 285 | 0.00% | None |
| Source rows in approved years | NB | 2019 | 182 | 0.00% | None |
| Source rows in approved years | NB | 2020 | 462 | 0.00% | None |
| Source rows in approved years | NB | 2021 | 179 | 0.00% | None |
| Source rows in approved years | NB | 2022 | 214 | 0.00% | None |
| Source rows in approved years | NB | 2023 | 202 | 0.00% | None |
| Source rows in approved years | NB | 2024 | 284 | 0.00% | None |
| Source rows in approved years | NB | 2025 | 440 | 0.00% | None |
| Source rows in approved years | NL | 2000 | 149 | 0.00% | None |
| Source rows in approved years | NL | 2001 | 181 | 0.00% | None |
| Source rows in approved years | NL | 2002 | 99 | 0.00% | None |
| Source rows in approved years | NL | 2003 | 140 | 0.00% | None |
| Source rows in approved years | NL | 2004 | 124 | 0.00% | None |
| Source rows in approved years | NL | 2005 | 121 | 0.00% | None |
| Source rows in approved years | NL | 2006 | 66 | 0.00% | None |
| Source rows in approved years | NL | 2007 | 66 | 0.00% | None |
| Source rows in approved years | NL | 2008 | 72 | 0.00% | None |
| Source rows in approved years | NL | 2009 | 150 | 0.00% | None |
| Source rows in approved years | NL | 2010 | 46 | 0.00% | None |
| Source rows in approved years | NL | 2011 | 41 | 0.00% | None |
| Source rows in approved years | NL | 2012 | 138 | 0.00% | None |
| Source rows in approved years | NL | 2013 | 71 | 0.00% | None |
| Source rows in approved years | NL | 2014 | 1 | 0.00% | None |
| Source rows in approved years | NL | 2015 | 25 | 0.00% | None |
| Source rows in approved years | NL | 2016 | 17 | 0.00% | None |
| Source rows in approved years | NL | 2017 | 80 | 0.00% | None |
| Source rows in approved years | NL | 2018 | 132 | 0.00% | None |
| Source rows in approved years | NL | 2019 | 99 | 0.00% | None |
| Source rows in approved years | NL | 2020 | 94 | 0.00% | None |
| Source rows in approved years | NL | 2021 | 85 | 0.00% | None |
| Source rows in approved years | NL | 2022 | 103 | 0.00% | None |
| Source rows in approved years | NL | 2023 | 101 | 0.00% | None |
| Source rows in approved years | NL | 2024 | 96 | 0.00% | None |
| Source rows in approved years | NL | 2025 | 243 | 0.00% | None |
| Source rows in approved years | NS | 2000 | 212 | 0.00% | None |
| Source rows in approved years | NS | 2001 | 485 | 0.00% | None |
| Source rows in approved years | NS | 2002 | 267 | 0.00% | None |
| Source rows in approved years | NS | 2003 | 272 | 0.00% | None |
| Source rows in approved years | NS | 2004 | 258 | 0.00% | None |
| Source rows in approved years | NS | 2005 | 289 | 0.00% | None |
| Source rows in approved years | NS | 2006 | 214 | 0.00% | None |
| Source rows in approved years | NS | 2007 | 386 | 0.00% | None |
| Source rows in approved years | NS | 2008 | 247 | 0.00% | None |
| Source rows in approved years | NS | 2009 | 190 | 0.00% | None |
| Source rows in approved years | NS | 2010 | 248 | 0.00% | None |
| Source rows in approved years | NS | 2011 | 114 | 0.00% | None |
| Source rows in approved years | NS | 2012 | 352 | 0.00% | None |
| Source rows in approved years | NS | 2013 | 171 | 0.00% | None |
| Source rows in approved years | NS | 2014 | 171 | 0.00% | None |
| Source rows in approved years | NS | 2015 | 247 | 0.00% | None |
| Source rows in approved years | NS | 2016 | 269 | 0.00% | None |
| Source rows in approved years | NS | 2017 | 175 | 100.00% | FUL |
| Source rows in approved years | NS | 2018 | 190 | 100.00% | FUL |
| Source rows in approved years | NS | 2019 | 143 | 0.00% | None |
| Source rows in approved years | NS | 2020 | 176 | 100.00% | FUL |
| Source rows in approved years | NS | 2021 | 113 | 100.00% | FUL |
| Source rows in approved years | NS | 2022 | 152 | 100.00% | FUL |
| Source rows in approved years | NS | 2023 | 220 | 100.00% | FUL |
| Source rows in approved years | NS | 2024 | 85 | 100.00% | FUL |
| Source rows in approved years | NS | 2025 | 179 | 100.00% | FUL |
| Source rows in approved years | NT | 2000 | 275 | 95.64% | FUL, MOD, MON |
| Source rows in approved years | NT | 2001 | 127 | 96.85% | FUL, MOD, MON |
| Source rows in approved years | NT | 2002 | 85 | 96.47% | FUL, MON |
| Source rows in approved years | NT | 2003 | 160 | 98.12% | FUL, MOD, MON |
| Source rows in approved years | NT | 2004 | 297 | 96.63% | FUL, MOD, MON |
| Source rows in approved years | NT | 2005 | 261 | 95.40% | FUL, MOD, MON |
| Source rows in approved years | NT | 2006 | 166 | 98.19% | FUL, MOD, MON |
| Source rows in approved years | NT | 2007 | 184 | 99.46% | FUL, MOD, MON |
| Source rows in approved years | NT | 2008 | 240 | 99.17% | FUL, MOD, MON |
| Source rows in approved years | NT | 2009 | 42 | 100.00% | FUL, MOD, MON |
| Source rows in approved years | NT | 2010 | 224 | 99.11% | FUL, MOD, MON |
| Source rows in approved years | NT | 2011 | 199 | 97.49% | FUL, MOD, MON |
| Source rows in approved years | NT | 2012 | 281 | 98.22% | FUL, MOD, MON |
| Source rows in approved years | NT | 2013 | 248 | 97.18% | FUL, MOD, MON |
| Source rows in approved years | NT | 2014 | 385 | 99.74% | FUL, MOD, MON |
| Source rows in approved years | NT | 2015 | 245 | 99.18% | FUL, MOD, MON |
| Source rows in approved years | NT | 2016 | 188 | 97.87% | FUL, MOD, MON |
| Source rows in approved years | NT | 2017 | 261 | 99.23% | FUL, MOD, MON |
| Source rows in approved years | NT | 2018 | 59 | 96.61% | FUL, MON |
| Source rows in approved years | NT | 2019 | 146 | 97.95% | FUL, MOD, MON |
| Source rows in approved years | NT | 2020 | 70 | 98.57% | FUL, MOD, MON |
| Source rows in approved years | NT | 2021 | 139 | 100.00% | FUL, MOD, MON |
| Source rows in approved years | NT | 2022 | 260 | 100.00% | FUL, MOD, MON |
| Source rows in approved years | NT | 2023 | 305 | 100.00% | FUL, MOD, MON |
| Source rows in approved years | NT | 2024 | 174 | 98.85% | FUL, MOD, MON |
| Source rows in approved years | NT | 2025 | 202 | 100.00% | FUL, MOD, MON |
| Source rows in approved years | ON | 2000 | 659 | 99.39% | MON, PRO, SUP |
| Source rows in approved years | ON | 2001 | 1602 | 99.75% | MON, PRO, SUP |
| Source rows in approved years | ON | 2002 | 1162 | 99.74% | MON, PRO, SUP |
| Source rows in approved years | ON | 2003 | 1040 | 99.90% | MON, PRO, SUP |
| Source rows in approved years | ON | 2004 | 436 | 99.54% | FUL, MON, SUP |
| Source rows in approved years | ON | 2005 | 1962 | 99.85% | FUL, MNP, MOD, MON |
| Source rows in approved years | ON | 2006 | 2284 | 99.96% | FUL, MNP, MOD, MON |
| Source rows in approved years | ON | 2007 | 1127 | 100.00% | FUL, MNP, MON |
| Source rows in approved years | ON | 2008 | 340 | 100.00% | FUL, MDP, MNP, MON |
| Source rows in approved years | ON | 2009 | 388 | 99.74% | FUL, MOD, MON |
| Source rows in approved years | ON | 2010 | 934 | 99.68% | FUL, MNP, MOD, MON |
| Source rows in approved years | ON | 2011 | 1338 | 99.93% | FUL, MDP, MNP, MOD, MON |
| Source rows in approved years | ON | 2012 | 1621 | 99.94% | FUL, MDP, MOD, MON |
| Source rows in approved years | ON | 2013 | 581 | 100.00% | FUL, MOD, MON |
| Source rows in approved years | ON | 2014 | 308 | 98.38% | FUL, MOD, MON |
| Source rows in approved years | ON | 2015 | 671 | 99.70% | FUL, MDP, MOD, MON |
| Source rows in approved years | ON | 2016 | 648 | 99.69% | FUL, MOD, MON |
| Source rows in approved years | ON | 2017 | 779 | 99.61% | FUL, MOD, MON |
| Source rows in approved years | ON | 2018 | 1328 | 99.92% | FUL, MDP, MOD, MON |
| Source rows in approved years | ON | 2019 | 538 | 99.81% | FUL, MDP, MOD, MON |
| Source rows in approved years | ON | 2020 | 609 | 100.00% | FUL, MOD, MON |
| Source rows in approved years | ON | 2021 | 1200 | 99.92% | FUL, MDP, MOD, MON |
| Source rows in approved years | ON | 2022 | 276 | 100.00% | FUL, MOD, MON |
| Source rows in approved years | ON | 2023 | 748 | 99.73% | FUL, MDP, MNP, MOD, MON |
| Source rows in approved years | ON | 2024 | 491 | 99.39% | FUL, MNP, MOD, MON |
| Source rows in approved years | ON | 2025 | 649 | 99.69% | FUL, MOD, MON |
| Source rows in approved years | PC | 2000 | 128 | 0.00% | None |
| Source rows in approved years | PC | 2001 | 128 | 0.00% | None |
| Source rows in approved years | PC | 2002 | 103 | 0.00% | None |
| Source rows in approved years | PC | 2003 | 129 | 0.00% | None |
| Source rows in approved years | PC | 2004 | 101 | 0.00% | None |
| Source rows in approved years | PC | 2005 | 107 | 0.00% | None |
| Source rows in approved years | PC | 2006 | 149 | 0.00% | None |
| Source rows in approved years | PC | 2007 | 95 | 0.00% | None |
| Source rows in approved years | PC | 2008 | 128 | 86.72% | FUL, MOD |
| Source rows in approved years | PC | 2009 | 153 | 88.89% | FUL, MOD |
| Source rows in approved years | PC | 2010 | 124 | 91.13% | FUL, MOD |
| Source rows in approved years | PC | 2011 | 94 | 80.85% | FUL, MOD |
| Source rows in approved years | PC | 2012 | 108 | 0.00% | None |
| Source rows in approved years | PC | 2013 | 122 | 86.89% | FUL, MOD |
| Source rows in approved years | PC | 2014 | 77 | 84.42% | FUL, MOD |
| Source rows in approved years | PC | 2015 | 150 | 81.33% | FUL, MOD |
| Source rows in approved years | PC | 2016 | 89 | 73.03% | FUL, MOD |
| Source rows in approved years | PC | 2017 | 179 | 92.74% | FUL, MOD |
| Source rows in approved years | PC | 2018 | 169 | 89.35% | FUL, MOD |
| Source rows in approved years | PC | 2019 | 87 | 86.21% | FUL, MOD, MON |
| Source rows in approved years | PC | 2020 | 99 | 91.92% | FUL, MOD, MON |
| Source rows in approved years | PC | 2021 | 96 | 82.29% | FUL, MOD, MON |
| Source rows in approved years | PC | 2022 | 160 | 89.38% | FUL, MOD, MON |
| Source rows in approved years | PC | 2023 | 122 | 100.00% | FUL, MOD, MON |
| Source rows in approved years | PC | 2024 | 105 | 88.57% | FUL, MOD, MON |
| Source rows in approved years | PC | 2025 | 104 | 85.58% | FUL, MOD, MON |
| Source rows in approved years | PE | 2018 | 8 | 100.00% | FUL |
| Source rows in approved years | PE | 2019 | 3 | 100.00% | FUL |
| Source rows in approved years | PE | 2020 | 12 | 100.00% | FUL |
| Source rows in approved years | PE | 2021 | 1 | 100.00% | FUL |
| Source rows in approved years | PE | 2022 | 4 | 100.00% | FUL |
| Source rows in approved years | PE | 2023 | 7 | 100.00% | FUL |
| Source rows in approved years | PE | 2024 | 8 | 100.00% | FUL |
| Source rows in approved years | PE | 2025 | 12 | 100.00% | FUL |
| Source rows in approved years | QC | 2000 | 516 | 0.00% | None |
| Source rows in approved years | QC | 2001 | 1003 | 0.00% | None |
| Source rows in approved years | QC | 2002 | 895 | 0.00% | None |
| Source rows in approved years | QC | 2003 | 716 | 0.00% | None |
| Source rows in approved years | QC | 2004 | 319 | 0.00% | None |
| Source rows in approved years | QC | 2005 | 1374 | 0.00% | None |
| Source rows in approved years | QC | 2006 | 683 | 0.00% | None |
| Source rows in approved years | QC | 2007 | 935 | 0.00% | None |
| Source rows in approved years | QC | 2008 | 222 | 0.00% | None |
| Source rows in approved years | QC | 2009 | 483 | 0.00% | None |
| Source rows in approved years | QC | 2010 | 737 | 0.00% | None |
| Source rows in approved years | QC | 2011 | 329 | 0.00% | None |
| Source rows in approved years | QC | 2012 | 795 | 0.00% | None |
| Source rows in approved years | QC | 2013 | 515 | 0.00% | None |
| Source rows in approved years | QC | 2014 | 292 | 0.00% | None |
| Source rows in approved years | QC | 2015 | 384 | 0.00% | None |
| Source rows in approved years | QC | 2016 | 602 | 0.00% | None |
| Source rows in approved years | QC | 2017 | 317 | 0.00% | None |
| Source rows in approved years | QC | 2018 | 592 | 0.00% | None |
| Source rows in approved years | QC | 2019 | 357 | 0.00% | None |
| Source rows in approved years | QC | 2020 | 707 | 0.00% | None |
| Source rows in approved years | QC | 2021 | 624 | 0.00% | None |
| Source rows in approved years | QC | 2022 | 449 | 0.00% | None |
| Source rows in approved years | QC | 2023 | 713 | 0.00% | None |
| Source rows in approved years | QC | 2024 | 518 | 0.00% | None |
| Source rows in approved years | QC | 2025 | 559 | 100.00% | FUL, MOD, MON |
| Source rows in approved years | SK | 2000 | 414 | 0.00% | None |
| Source rows in approved years | SK | 2001 | 856 | 0.00% | None |
| Source rows in approved years | SK | 2002 | 880 | 0.00% | None |
| Source rows in approved years | SK | 2003 | 640 | 0.00% | None |
| Source rows in approved years | SK | 2004 | 329 | 0.00% | None |
| Source rows in approved years | SK | 2005 | 323 | 0.00% | None |
| Source rows in approved years | SK | 2006 | 500 | 0.00% | None |
| Source rows in approved years | SK | 2007 | 366 | 0.00% | None |
| Source rows in approved years | SK | 2008 | 598 | 0.00% | None |
| Source rows in approved years | SK | 2009 | 511 | 0.00% | None |
| Source rows in approved years | SK | 2010 | 571 | 0.00% | None |
| Source rows in approved years | SK | 2011 | 303 | 0.00% | None |
| Source rows in approved years | SK | 2012 | 410 | 0.00% | None |
| Source rows in approved years | SK | 2013 | 429 | 0.00% | None |
| Source rows in approved years | SK | 2014 | 403 | 0.00% | None |
| Source rows in approved years | SK | 2015 | 723 | 0.00% | None |
| Source rows in approved years | SK | 2016 | 402 | 0.00% | None |
| Source rows in approved years | SK | 2017 | 353 | 0.00% | None |
| Source rows in approved years | SK | 2018 | 433 | 0.00% | None |
| Source rows in approved years | SK | 2019 | 257 | 0.00% | None |
| Source rows in approved years | SK | 2020 | 198 | 0.00% | None |
| Source rows in approved years | SK | 2021 | 635 | 0.00% | None |
| Source rows in approved years | SK | 2022 | 447 | 0.00% | None |
| Source rows in approved years | SK | 2023 | 486 | 0.00% | None |
| Source rows in approved years | SK | 2024 | 596 | 0.00% | None |
| Source rows in approved years | SK | 2025 | 507 | 0.00% | None |
| Source rows in approved years | YT | 2000 | 55 | 0.00% | None |
| Source rows in approved years | YT | 2001 | 68 | 0.00% | None |
| Source rows in approved years | YT | 2002 | 69 | 0.00% | None |
| Source rows in approved years | YT | 2003 | 77 | 0.00% | None |
| Source rows in approved years | YT | 2004 | 282 | 18.79% | FUL |
| Source rows in approved years | YT | 2005 | 83 | 45.78% | FUL |
| Source rows in approved years | YT | 2006 | 80 | 40.00% | FUL |
| Source rows in approved years | YT | 2007 | 110 | 23.64% | FUL |
| Source rows in approved years | YT | 2008 | 76 | 31.58% | FUL |
| Source rows in approved years | YT | 2009 | 118 | 26.27% | FUL |
| Source rows in approved years | YT | 2010 | 88 | 46.59% | FUL |
| Source rows in approved years | YT | 2011 | 56 | 33.93% | FUL |
| Source rows in approved years | YT | 2012 | 126 | 31.75% | FUL |
| Source rows in approved years | YT | 2013 | 177 | 19.77% | FUL |
| Source rows in approved years | YT | 2014 | 34 | 73.53% | FUL |
| Source rows in approved years | YT | 2015 | 185 | 23.78% | FUL |
| Source rows in approved years | YT | 2016 | 53 | 52.83% | FUL |
| Source rows in approved years | YT | 2017 | 115 | 26.09% | FUL |
| Source rows in approved years | YT | 2018 | 51 | 37.25% | FUL |
| Source rows in approved years | YT | 2019 | 117 | 35.04% | FUL |
| Source rows in approved years | YT | 2020 | 24 | 41.67% | FUL |
| Source rows in approved years | YT | 2021 | 112 | 16.96% | FUL |
| Source rows in approved years | YT | 2022 | 289 | 0.00% | None |
| Source rows in approved years | YT | 2023 | 222 | 0.00% | None |
| Source rows in approved years | YT | 2024 | 168 | 0.00% | None |
| Source rows in approved years | YT | 2025 | 166 | 0.00% | None |
| Selected analysis records | AB | 2000 | 783 | 0.00% | None |
| Selected analysis records | AB | 2001 | 974 | 0.00% | None |
| Selected analysis records | AB | 2002 | 1444 | 0.00% | None |
| Selected analysis records | AB | 2003 | 1191 | 0.00% | None |
| Selected analysis records | AB | 2004 | 1610 | 0.00% | None |
| Selected analysis records | AB | 2005 | 1372 | 0.00% | None |
| Selected analysis records | AB | 2006 | 2020 | 0.00% | None |
| Selected analysis records | AB | 2007 | 1337 | 0.00% | None |
| Selected analysis records | AB | 2008 | 1719 | 0.00% | None |
| Selected analysis records | AB | 2009 | 1667 | 0.00% | None |
| Selected analysis records | AB | 2010 | 1891 | 0.00% | None |
| Selected analysis records | AB | 2011 | 1171 | 0.00% | None |
| Selected analysis records | AB | 2012 | 1605 | 0.00% | None |
| Selected analysis records | AB | 2013 | 1218 | 0.00% | None |
| Selected analysis records | AB | 2014 | 1451 | 0.00% | None |
| Selected analysis records | AB | 2015 | 1856 | 0.00% | None |
| Selected analysis records | AB | 2016 | 1436 | 0.00% | None |
| Selected analysis records | AB | 2017 | 1244 | 0.00% | None |
| Selected analysis records | AB | 2018 | 1299 | 0.00% | None |
| Selected analysis records | AB | 2019 | 1021 | 0.00% | None |
| Selected analysis records | AB | 2020 | 744 | 0.00% | None |
| Selected analysis records | AB | 2021 | 1383 | 0.00% | None |
| Selected analysis records | AB | 2022 | 1297 | 0.00% | None |
| Selected analysis records | AB | 2023 | 1131 | 0.00% | None |
| Selected analysis records | AB | 2024 | 1273 | 0.00% | None |
| Selected analysis records | AB | 2025 | 1338 | 0.00% | None |
| Selected analysis records | BC | 2000 | 1526 | 0.00% | None |
| Selected analysis records | BC | 2001 | 1291 | 0.00% | None |
| Selected analysis records | BC | 2002 | 1772 | 0.00% | None |
| Selected analysis records | BC | 2003 | 2457 | 0.00% | None |
| Selected analysis records | BC | 2004 | 2405 | 0.00% | None |
| Selected analysis records | BC | 2005 | 994 | 0.00% | None |
| Selected analysis records | BC | 2006 | 2560 | 0.00% | None |
| Selected analysis records | BC | 2007 | 1607 | 0.00% | None |
| Selected analysis records | BC | 2008 | 2025 | 0.00% | None |
| Selected analysis records | BC | 2009 | 3049 | 0.00% | None |
| Selected analysis records | BC | 2010 | 1689 | 0.00% | None |
| Selected analysis records | BC | 2011 | 646 | 0.00% | None |
| Selected analysis records | BC | 2012 | 1640 | 0.00% | None |
| Selected analysis records | BC | 2013 | 1867 | 0.00% | None |
| Selected analysis records | BC | 2014 | 1469 | 0.00% | None |
| Selected analysis records | BC | 2015 | 1863 | 0.00% | None |
| Selected analysis records | BC | 2016 | 1068 | 0.00% | None |
| Selected analysis records | BC | 2017 | 1349 | 0.00% | None |
| Selected analysis records | BC | 2018 | 2089 | 0.00% | None |
| Selected analysis records | BC | 2019 | 834 | 0.00% | None |
| Selected analysis records | BC | 2020 | 668 | 0.00% | None |
| Selected analysis records | BC | 2021 | 1649 | 0.00% | None |
| Selected analysis records | BC | 2022 | 1783 | 96.75% | FUL, MOD, MON |
| Selected analysis records | BC | 2023 | 2280 | 98.60% | FUL, MOD, MON |
| Selected analysis records | BC | 2024 | 1725 | 99.30% | FUL, MOD, MON |
| Selected analysis records | BC | 2025 | 1372 | 99.85% | FUL, MOD, MON |
| Selected analysis records | MB | 2000 | 353 | 0.00% | None |
| Selected analysis records | MB | 2001 | 527 | 0.00% | None |
| Selected analysis records | MB | 2002 | 755 | 0.00% | None |
| Selected analysis records | MB | 2003 | 1207 | 0.00% | None |
| Selected analysis records | MB | 2004 | 55 | 0.00% | None |
| Selected analysis records | MB | 2005 | 248 | 56.85% | Actioned, FUL, Limited Action, MOD, No Action |
| Selected analysis records | MB | 2006 | 682 | 64.08% | Actioned, FUL, MOD, No Action |
| Selected analysis records | MB | 2007 | 382 | 64.66% | Actioned, FUL, Limited Action, MOD |
| Selected analysis records | MB | 2008 | 397 | 67.76% | Actioned, FUL, MOD, No Action |
| Selected analysis records | MB | 2009 | 184 | 69.02% | FUL |
| Selected analysis records | MB | 2010 | 583 | 61.41% | Actioned, FUL, Limited Action, MOD, No Action |
| Selected analysis records | MB | 2011 | 315 | 64.44% | Actioned, FUL, Limited Action, MOD, No Action |
| Selected analysis records | MB | 2012 | 497 | 50.50% | FUL, MOD |
| Selected analysis records | MB | 2013 | 494 | 40.69% | FUL, MOD |
| Selected analysis records | MB | 2014 | 245 | 49.80% | FUL, MOD |
| Selected analysis records | MB | 2015 | 459 | 56.86% | FUL, MOD |
| Selected analysis records | MB | 2016 | 202 | 58.42% | FUL, MOD |
| Selected analysis records | MB | 2017 | 557 | 42.19% | FUL, MOD |
| Selected analysis records | MB | 2018 | 476 | 100.00% | FUL, MOD, MON |
| Selected analysis records | MB | 2019 | 278 | 100.00% | FUL, MOD, MON |
| Selected analysis records | MB | 2020 | 151 | 98.68% | FUL, MOD, MON |
| Selected analysis records | MB | 2021 | 492 | 92.89% | FUL, MOD, MON |
| Selected analysis records | MB | 2022 | 224 | 100.00% | FUL, MOD, MON |
| Selected analysis records | MB | 2023 | 300 | 100.00% | FUL, MOD, MON |
| Selected analysis records | MB | 2024 | 321 | 96.57% | FUL, MOD, MON |
| Selected analysis records | MB | 2025 | 444 | 97.30% | FUL, MOD, MON |
| Selected analysis records | NB | 2000 | 333 | 0.00% | None |
| Selected analysis records | NB | 2001 | 490 | 0.00% | None |
| Selected analysis records | NB | 2002 | 317 | 0.00% | None |
| Selected analysis records | NB | 2003 | 228 | 0.00% | None |
| Selected analysis records | NB | 2004 | 253 | 0.00% | None |
| Selected analysis records | NB | 2005 | 306 | 0.00% | None |
| Selected analysis records | NB | 2006 | 308 | 0.00% | None |
| Selected analysis records | NB | 2007 | 316 | 0.00% | None |
| Selected analysis records | NB | 2008 | 168 | 0.00% | None |
| Selected analysis records | NB | 2009 | 197 | 0.00% | None |
| Selected analysis records | NB | 2010 | 179 | 0.00% | None |
| Selected analysis records | NB | 2011 | 67 | 0.00% | None |
| Selected analysis records | NB | 2012 | 338 | 0.00% | None |
| Selected analysis records | NB | 2013 | 353 | 0.00% | None |
| Selected analysis records | NB | 2014 | 180 | 0.00% | None |
| Selected analysis records | NB | 2015 | 221 | 0.00% | None |
| Selected analysis records | NB | 2016 | 285 | 0.00% | None |
| Selected analysis records | NB | 2017 | 245 | 0.00% | None |
| Selected analysis records | NB | 2018 | 285 | 0.00% | None |
| Selected analysis records | NB | 2019 | 182 | 0.00% | None |
| Selected analysis records | NB | 2020 | 462 | 0.00% | None |
| Selected analysis records | NB | 2021 | 179 | 0.00% | None |
| Selected analysis records | NB | 2022 | 214 | 0.00% | None |
| Selected analysis records | NB | 2023 | 202 | 0.00% | None |
| Selected analysis records | NB | 2024 | 284 | 0.00% | None |
| Selected analysis records | NB | 2025 | 440 | 0.00% | None |
| Selected analysis records | NL | 2000 | 149 | 0.00% | None |
| Selected analysis records | NL | 2001 | 181 | 0.00% | None |
| Selected analysis records | NL | 2002 | 99 | 0.00% | None |
| Selected analysis records | NL | 2003 | 140 | 0.00% | None |
| Selected analysis records | NL | 2004 | 124 | 0.00% | None |
| Selected analysis records | NL | 2005 | 121 | 0.00% | None |
| Selected analysis records | NL | 2006 | 66 | 0.00% | None |
| Selected analysis records | NL | 2007 | 66 | 0.00% | None |
| Selected analysis records | NL | 2008 | 72 | 0.00% | None |
| Selected analysis records | NL | 2009 | 150 | 0.00% | None |
| Selected analysis records | NL | 2010 | 46 | 0.00% | None |
| Selected analysis records | NL | 2011 | 41 | 0.00% | None |
| Selected analysis records | NL | 2012 | 138 | 0.00% | None |
| Selected analysis records | NL | 2013 | 71 | 0.00% | None |
| Selected analysis records | NL | 2014 | 1 | 0.00% | None |
| Selected analysis records | NL | 2015 | 25 | 0.00% | None |
| Selected analysis records | NL | 2016 | 17 | 0.00% | None |
| Selected analysis records | NL | 2017 | 80 | 0.00% | None |
| Selected analysis records | NL | 2018 | 132 | 0.00% | None |
| Selected analysis records | NL | 2019 | 99 | 0.00% | None |
| Selected analysis records | NL | 2020 | 94 | 0.00% | None |
| Selected analysis records | NL | 2021 | 85 | 0.00% | None |
| Selected analysis records | NL | 2022 | 103 | 0.00% | None |
| Selected analysis records | NL | 2023 | 101 | 0.00% | None |
| Selected analysis records | NL | 2024 | 96 | 0.00% | None |
| Selected analysis records | NL | 2025 | 243 | 0.00% | None |
| Selected analysis records | NS | 2000 | 212 | 0.00% | None |
| Selected analysis records | NS | 2001 | 485 | 0.00% | None |
| Selected analysis records | NS | 2002 | 267 | 0.00% | None |
| Selected analysis records | NS | 2003 | 272 | 0.00% | None |
| Selected analysis records | NS | 2004 | 258 | 0.00% | None |
| Selected analysis records | NS | 2005 | 289 | 0.00% | None |
| Selected analysis records | NS | 2006 | 214 | 0.00% | None |
| Selected analysis records | NS | 2007 | 386 | 0.00% | None |
| Selected analysis records | NS | 2008 | 247 | 0.00% | None |
| Selected analysis records | NS | 2009 | 190 | 0.00% | None |
| Selected analysis records | NS | 2010 | 248 | 0.00% | None |
| Selected analysis records | NS | 2011 | 114 | 0.00% | None |
| Selected analysis records | NS | 2012 | 352 | 0.00% | None |
| Selected analysis records | NS | 2013 | 171 | 0.00% | None |
| Selected analysis records | NS | 2014 | 171 | 0.00% | None |
| Selected analysis records | NS | 2015 | 247 | 0.00% | None |
| Selected analysis records | NS | 2016 | 269 | 0.00% | None |
| Selected analysis records | NS | 2017 | 175 | 100.00% | FUL |
| Selected analysis records | NS | 2018 | 190 | 100.00% | FUL |
| Selected analysis records | NS | 2019 | 143 | 0.00% | None |
| Selected analysis records | NS | 2020 | 176 | 100.00% | FUL |
| Selected analysis records | NS | 2021 | 113 | 100.00% | FUL |
| Selected analysis records | NS | 2022 | 152 | 100.00% | FUL |
| Selected analysis records | NS | 2023 | 220 | 100.00% | FUL |
| Selected analysis records | NS | 2024 | 85 | 100.00% | FUL |
| Selected analysis records | NS | 2025 | 179 | 100.00% | FUL |
| Selected analysis records | NT | 2000 | 274 | 95.99% | FUL, MOD, MON |
| Selected analysis records | NT | 2001 | 127 | 96.85% | FUL, MOD, MON |
| Selected analysis records | NT | 2002 | 85 | 96.47% | FUL, MON |
| Selected analysis records | NT | 2003 | 160 | 98.12% | FUL, MOD, MON |
| Selected analysis records | NT | 2004 | 297 | 96.63% | FUL, MOD, MON |
| Selected analysis records | NT | 2005 | 261 | 95.40% | FUL, MOD, MON |
| Selected analysis records | NT | 2006 | 166 | 98.19% | FUL, MOD, MON |
| Selected analysis records | NT | 2007 | 184 | 99.46% | FUL, MOD, MON |
| Selected analysis records | NT | 2008 | 240 | 99.17% | FUL, MOD, MON |
| Selected analysis records | NT | 2009 | 42 | 100.00% | FUL, MOD, MON |
| Selected analysis records | NT | 2010 | 224 | 99.11% | FUL, MOD, MON |
| Selected analysis records | NT | 2011 | 199 | 97.49% | FUL, MOD, MON |
| Selected analysis records | NT | 2012 | 281 | 98.22% | FUL, MOD, MON |
| Selected analysis records | NT | 2013 | 248 | 97.18% | FUL, MOD, MON |
| Selected analysis records | NT | 2014 | 385 | 99.74% | FUL, MOD, MON |
| Selected analysis records | NT | 2015 | 245 | 99.18% | FUL, MOD, MON |
| Selected analysis records | NT | 2016 | 188 | 97.87% | FUL, MOD, MON |
| Selected analysis records | NT | 2017 | 261 | 99.23% | FUL, MOD, MON |
| Selected analysis records | NT | 2018 | 59 | 96.61% | FUL, MON |
| Selected analysis records | NT | 2019 | 146 | 97.95% | FUL, MOD, MON |
| Selected analysis records | NT | 2020 | 70 | 98.57% | FUL, MOD, MON |
| Selected analysis records | NT | 2021 | 139 | 100.00% | FUL, MOD, MON |
| Selected analysis records | NT | 2022 | 260 | 100.00% | FUL, MOD, MON |
| Selected analysis records | NT | 2023 | 305 | 100.00% | FUL, MOD, MON |
| Selected analysis records | NT | 2024 | 174 | 98.85% | FUL, MOD, MON |
| Selected analysis records | NT | 2025 | 202 | 100.00% | FUL, MOD, MON |
| Selected analysis records | ON | 2000 | 655 | 100.00% | MON, PRO, SUP |
| Selected analysis records | ON | 2001 | 1598 | 100.00% | MON, PRO, SUP |
| Selected analysis records | ON | 2002 | 1159 | 100.00% | MON, PRO, SUP |
| Selected analysis records | ON | 2003 | 1039 | 100.00% | MON, PRO, SUP |
| Selected analysis records | ON | 2004 | 434 | 100.00% | FUL, MON, SUP |
| Selected analysis records | ON | 2005 | 1959 | 100.00% | FUL, MNP, MOD, MON |
| Selected analysis records | ON | 2006 | 2283 | 100.00% | FUL, MNP, MOD, MON |
| Selected analysis records | ON | 2007 | 1126 | 100.00% | FUL, MNP, MON |
| Selected analysis records | ON | 2008 | 340 | 100.00% | FUL, MDP, MNP, MON |
| Selected analysis records | ON | 2009 | 387 | 100.00% | FUL, MOD, MON |
| Selected analysis records | ON | 2010 | 931 | 100.00% | FUL, MNP, MOD, MON |
| Selected analysis records | ON | 2011 | 1337 | 100.00% | FUL, MDP, MNP, MOD, MON |
| Selected analysis records | ON | 2012 | 1620 | 100.00% | FUL, MDP, MOD, MON |
| Selected analysis records | ON | 2013 | 581 | 100.00% | FUL, MOD, MON |
| Selected analysis records | ON | 2014 | 303 | 100.00% | FUL, MOD, MON |
| Selected analysis records | ON | 2015 | 669 | 100.00% | FUL, MDP, MOD, MON |
| Selected analysis records | ON | 2016 | 646 | 100.00% | FUL, MOD, MON |
| Selected analysis records | ON | 2017 | 776 | 100.00% | FUL, MOD, MON |
| Selected analysis records | ON | 2018 | 1327 | 100.00% | FUL, MDP, MOD, MON |
| Selected analysis records | ON | 2019 | 537 | 100.00% | FUL, MDP, MOD, MON |
| Selected analysis records | ON | 2020 | 609 | 100.00% | FUL, MOD, MON |
| Selected analysis records | ON | 2021 | 1197 | 100.00% | FUL, MDP, MOD, MON |
| Selected analysis records | ON | 2022 | 275 | 100.00% | FUL, MOD, MON |
| Selected analysis records | ON | 2023 | 743 | 100.00% | FUL, MNP, MOD, MON |
| Selected analysis records | ON | 2024 | 486 | 100.00% | FUL, MOD, MON |
| Selected analysis records | ON | 2025 | 645 | 100.00% | FUL, MOD, MON |
| Selected analysis records | PC | 2000 | 128 | 0.00% | None |
| Selected analysis records | PC | 2001 | 128 | 0.00% | None |
| Selected analysis records | PC | 2002 | 103 | 0.00% | None |
| Selected analysis records | PC | 2003 | 129 | 0.00% | None |
| Selected analysis records | PC | 2004 | 101 | 0.00% | None |
| Selected analysis records | PC | 2005 | 107 | 0.00% | None |
| Selected analysis records | PC | 2006 | 149 | 0.00% | None |
| Selected analysis records | PC | 2007 | 95 | 0.00% | None |
| Selected analysis records | PC | 2008 | 108 | 100.00% | FUL, MOD |
| Selected analysis records | PC | 2009 | 134 | 100.00% | FUL, MOD |
| Selected analysis records | PC | 2010 | 111 | 99.10% | FUL, MOD |
| Selected analysis records | PC | 2011 | 71 | 100.00% | FUL, MOD |
| Selected analysis records | PC | 2012 | 93 | 0.00% | None |
| Selected analysis records | PC | 2013 | 102 | 100.00% | FUL, MOD |
| Selected analysis records | PC | 2014 | 65 | 100.00% | FUL, MOD |
| Selected analysis records | PC | 2015 | 122 | 100.00% | FUL, MOD |
| Selected analysis records | PC | 2016 | 65 | 100.00% | FUL, MOD |
| Selected analysis records | PC | 2017 | 166 | 100.00% | FUL, MOD |
| Selected analysis records | PC | 2018 | 150 | 100.00% | FUL, MOD |
| Selected analysis records | PC | 2019 | 75 | 100.00% | FUL, MOD, MON |
| Selected analysis records | PC | 2020 | 91 | 100.00% | FUL, MOD, MON |
| Selected analysis records | PC | 2021 | 79 | 100.00% | FUL, MOD, MON |
| Selected analysis records | PC | 2022 | 139 | 100.00% | FUL, MOD, MON |
| Selected analysis records | PC | 2023 | 122 | 100.00% | FUL, MOD, MON |
| Selected analysis records | PC | 2024 | 93 | 100.00% | FUL, MOD, MON |
| Selected analysis records | PC | 2025 | 89 | 100.00% | FUL, MOD, MON |
| Selected analysis records | QC | 2000 | 516 | 0.00% | None |
| Selected analysis records | QC | 2001 | 1003 | 0.00% | None |
| Selected analysis records | QC | 2002 | 895 | 0.00% | None |
| Selected analysis records | QC | 2003 | 716 | 0.00% | None |
| Selected analysis records | QC | 2004 | 319 | 0.00% | None |
| Selected analysis records | QC | 2005 | 1374 | 0.00% | None |
| Selected analysis records | QC | 2006 | 683 | 0.00% | None |
| Selected analysis records | QC | 2007 | 935 | 0.00% | None |
| Selected analysis records | QC | 2008 | 222 | 0.00% | None |
| Selected analysis records | QC | 2009 | 483 | 0.00% | None |
| Selected analysis records | QC | 2010 | 737 | 0.00% | None |
| Selected analysis records | QC | 2011 | 329 | 0.00% | None |
| Selected analysis records | QC | 2012 | 795 | 0.00% | None |
| Selected analysis records | QC | 2013 | 515 | 0.00% | None |
| Selected analysis records | QC | 2014 | 292 | 0.00% | None |
| Selected analysis records | QC | 2015 | 384 | 0.00% | None |
| Selected analysis records | QC | 2016 | 602 | 0.00% | None |
| Selected analysis records | QC | 2017 | 317 | 0.00% | None |
| Selected analysis records | QC | 2018 | 592 | 0.00% | None |
| Selected analysis records | QC | 2019 | 357 | 0.00% | None |
| Selected analysis records | QC | 2020 | 707 | 0.00% | None |
| Selected analysis records | QC | 2021 | 624 | 0.00% | None |
| Selected analysis records | QC | 2022 | 449 | 0.00% | None |
| Selected analysis records | QC | 2023 | 713 | 0.00% | None |
| Selected analysis records | QC | 2024 | 518 | 0.00% | None |
| Selected analysis records | QC | 2025 | 559 | 100.00% | FUL, MOD, MON |
| Selected analysis records | SK | 2000 | 414 | 0.00% | None |
| Selected analysis records | SK | 2001 | 856 | 0.00% | None |
| Selected analysis records | SK | 2002 | 880 | 0.00% | None |
| Selected analysis records | SK | 2003 | 640 | 0.00% | None |
| Selected analysis records | SK | 2004 | 329 | 0.00% | None |
| Selected analysis records | SK | 2005 | 323 | 0.00% | None |
| Selected analysis records | SK | 2006 | 500 | 0.00% | None |
| Selected analysis records | SK | 2007 | 366 | 0.00% | None |
| Selected analysis records | SK | 2008 | 598 | 0.00% | None |
| Selected analysis records | SK | 2009 | 511 | 0.00% | None |
| Selected analysis records | SK | 2010 | 571 | 0.00% | None |
| Selected analysis records | SK | 2011 | 303 | 0.00% | None |
| Selected analysis records | SK | 2012 | 410 | 0.00% | None |
| Selected analysis records | SK | 2013 | 429 | 0.00% | None |
| Selected analysis records | SK | 2014 | 403 | 0.00% | None |
| Selected analysis records | SK | 2015 | 723 | 0.00% | None |
| Selected analysis records | SK | 2016 | 402 | 0.00% | None |
| Selected analysis records | SK | 2017 | 353 | 0.00% | None |
| Selected analysis records | SK | 2018 | 433 | 0.00% | None |
| Selected analysis records | SK | 2019 | 257 | 0.00% | None |
| Selected analysis records | SK | 2020 | 198 | 0.00% | None |
| Selected analysis records | SK | 2021 | 635 | 0.00% | None |
| Selected analysis records | SK | 2022 | 447 | 0.00% | None |
| Selected analysis records | SK | 2023 | 486 | 0.00% | None |
| Selected analysis records | SK | 2024 | 596 | 0.00% | None |
| Selected analysis records | SK | 2025 | 507 | 0.00% | None |
| Selected analysis records | YT | 2000 | 55 | 0.00% | None |
| Selected analysis records | YT | 2001 | 68 | 0.00% | None |
| Selected analysis records | YT | 2002 | 69 | 0.00% | None |
| Selected analysis records | YT | 2003 | 77 | 0.00% | None |
| Selected analysis records | YT | 2004 | 282 | 18.79% | FUL |
| Selected analysis records | YT | 2005 | 83 | 45.78% | FUL |
| Selected analysis records | YT | 2006 | 80 | 40.00% | FUL |
| Selected analysis records | YT | 2007 | 110 | 23.64% | FUL |
| Selected analysis records | YT | 2008 | 76 | 31.58% | FUL |
| Selected analysis records | YT | 2009 | 118 | 26.27% | FUL |
| Selected analysis records | YT | 2010 | 88 | 46.59% | FUL |
| Selected analysis records | YT | 2011 | 56 | 33.93% | FUL |
| Selected analysis records | YT | 2012 | 126 | 31.75% | FUL |
| Selected analysis records | YT | 2013 | 177 | 19.77% | FUL |
| Selected analysis records | YT | 2014 | 34 | 73.53% | FUL |
| Selected analysis records | YT | 2015 | 185 | 23.78% | FUL |
| Selected analysis records | YT | 2016 | 53 | 52.83% | FUL |
| Selected analysis records | YT | 2017 | 115 | 26.09% | FUL |
| Selected analysis records | YT | 2018 | 51 | 37.25% | FUL |
| Selected analysis records | YT | 2019 | 117 | 35.04% | FUL |
| Selected analysis records | YT | 2020 | 24 | 41.67% | FUL |
| Selected analysis records | YT | 2021 | 112 | 16.96% | FUL |
| Selected analysis records | YT | 2022 | 282 | 0.00% | None |
| Selected analysis records | YT | 2023 | 222 | 0.00% | None |
| Selected analysis records | YT | 2024 | 168 | 0.00% | None |
| Selected analysis records | YT | 2025 | 166 | 0.00% | None |


The documented standard RESPONSE values are FUL (full response), MOD (modified response) and MON (monitored). Local values such as SUP, PRO and action labels remain unmapped; PROTZONE has no applied national standard. A blank response does not mean monitored or unfought.

**A national fought-versus-monitored comparison is not feasible on this evidence.** Full response, modified response and monitored are response classifications, not validated binary evidence of whether a fire was fought. An agency-specific comparison could be considered only after its code meanings and year-level coverage are verified, with an Unknown category and explicit denominator. I have not added it to the build.

### Power BI dates: planned implementation, not yet executed
**Plain-English reason for the date-related dimensions:** I keep dim_year and dim_month separate so a record with a valid year or month still appears in period totals when its exact day is unknown, while dim_date represents only genuine complete calendar dates.

For the approved main series, year slicers and annual chart axes will use dim_year, with its single-direction relationship to fact_fire.year_key. These annual measures will not use DATEADD, SAMEPERIODLASTYEAR or a fabricated date. The core area measure will explicitly apply in_analysis = 1.

For YoY, I will require a single current year, save that year in a variable, remove filters from dim_year and dim_date, and calculate area at current year minus one while retaining agency, cause and size filters. The result is DIVIDE(current area minus prior area, prior area). A missing, zero-denominator or out-of-scope prior year returns blank, including the first approved year. The previous year is the adjacent calendar year, not the previous nonempty row.

For the rolling measure, I will generate the integer year range from current year minus four through current year, calculate the scoped annual area for each year with year/date filters removed, and average those annual values only when every year in that range is inside the approved period and has a nonblank value. I will not average individual fire sizes or fill missing years with zero. The initial partial windows remain blank, matching vw_annual_trend.five_year_mean_area.

Annual pages will not use an exact-date slicer. If a month slicer is retained, it must be preserved consistently for every compared year and labelled as a same-month comparison. For the initial full-year reference checks, month filters will be cleared as well so the DAX results match the annual SQL view exactly. I will check DAX against both SQL and pandas after implementation; no DAX match or native Power BI validation is claimed yet.

### Audit boundary
I changed only this decision-log document in the project. No warehouse, source, exclusion flag, notebook, model, measure or report was changed. The warehouse SHA-256 before and after this audit is `fd79b03aca1d02d55c1cc93d2bc29fa735360dbde999f765af2942c5b71add68`. NFD external reconciliation remains pending.
