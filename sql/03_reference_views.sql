-- Reference answers only. Power BI imports the facts and dimensions, not these views.
CREATE VIEW vw_analysis AS
SELECT f.fire_key,f.fire_id,f.year_key AS year,f.month_key AS month_num,
 a.agency_code AS reporting_agency,c.cause_class,f.size_ha,f.is_large_fire,
 f.missing_report_date,f.grid_cell,f.latitude,f.longitude
FROM fact_fire f JOIN dim_agency a USING(agency_key) JOIN dim_cause c USING(cause_key)
WHERE f.in_analysis=1;

CREATE VIEW vw_kpi_summary AS
WITH ranked AS(SELECT size_ha,ROW_NUMBER() OVER(ORDER BY size_ha) AS rn,
 COUNT(*) OVER() AS n FROM vw_analysis),
med AS(SELECT AVG(size_ha) AS median_size_ha FROM ranked
 WHERE rn IN ((n+1)/2,(n+2)/2))
SELECT COUNT(*) AS reported_records,SUM(size_ha) AS area_ha,AVG(size_ha) AS mean_size_ha,
 (SELECT median_size_ha FROM med) AS median_size_ha,SUM(is_large_fire) AS large_fire_records,
 1.0*SUM(is_large_fire)/COUNT(*) AS large_fire_share,
 1.0*SUM(CASE WHEN cause_class='Unknown' THEN 1 ELSE 0 END)/COUNT(*) AS unknown_cause_share,
 1.0*SUM(missing_report_date)/COUNT(*) AS missing_report_date_share FROM vw_analysis;

CREATE VIEW vw_concentration AS
WITH groups AS(SELECT 'ALL' AS reporting_agency,fire_key,size_ha FROM vw_analysis
 UNION ALL SELECT reporting_agency,fire_key,size_ha FROM vw_analysis),
r AS(SELECT reporting_agency,size_ha,ROW_NUMBER() OVER(PARTITION BY reporting_agency
 ORDER BY size_ha DESC,fire_key) AS rn,COUNT(*) OVER(PARTITION BY reporting_agency) AS n FROM groups),
p AS(SELECT 1 AS top_pct UNION ALL SELECT 3 UNION ALL SELECT 5)
SELECT reporting_agency,top_pct,MAX((n*top_pct+99)/100) AS selected_records,
 SUM(CASE WHEN rn<=(n*top_pct+99)/100 THEN size_ha ELSE 0 END)/NULLIF(SUM(size_ha),0) AS area_share
FROM r CROSS JOIN p GROUP BY reporting_agency,top_pct;

CREATE VIEW vw_pareto AS
SELECT fire_key,size_ha,ROW_NUMBER() OVER(ORDER BY size_ha DESC,fire_key) AS position,
 SUM(size_ha) OVER(ORDER BY size_ha DESC,fire_key ROWS UNBOUNDED PRECEDING)/
 NULLIF(SUM(size_ha) OVER(),0) AS cumulative_area_share FROM vw_analysis;

CREATE VIEW vw_annual_trend AS
WITH grouped AS(SELECT year,COUNT(*) AS reported_records,SUM(size_ha) AS area_ha FROM vw_analysis GROUP BY year),
years AS(SELECT y.year_key AS year,COALESCE(g.reported_records,0) AS reported_records,g.area_ha
 FROM dim_year y CROSS JOIN load_batch b LEFT JOIN grouped g ON g.year=y.year_key
 WHERE y.year_key BETWEEN b.analysis_start AND b.analysis_end)
SELECT year,reported_records,area_ha,area_ha-LAG(area_ha) OVER(ORDER BY year) AS yoy_area_difference,
 (area_ha-LAG(area_ha) OVER(ORDER BY year))/NULLIF(LAG(area_ha) OVER(ORDER BY year),0) AS yoy_area_change,
 CASE WHEN COUNT(area_ha) OVER(ORDER BY year ROWS BETWEEN 4 PRECEDING AND CURRENT ROW)=5
 THEN AVG(area_ha) OVER(ORDER BY year ROWS BETWEEN 4 PRECEDING AND CURRENT ROW) END AS five_year_mean_area
FROM years;

CREATE VIEW vw_decades AS SELECT (year/10)*10 AS decade,COUNT(DISTINCT year) AS years_observed,
 COUNT(*) AS reported_records,SUM(size_ha) AS area_ha,SUM(size_ha)/COUNT(DISTINCT year) AS mean_annual_area
FROM vw_analysis GROUP BY (year/10)*10;

CREATE VIEW vw_largest_year_sensitivity AS
WITH annual AS(SELECT year,COUNT(*) AS records,SUM(size_ha) AS area_ha FROM vw_analysis GROUP BY year),
largest AS(SELECT year FROM annual ORDER BY area_ha DESC,year LIMIT 1)
SELECT 'All selected years' AS scenario,COUNT(*) AS years,SUM(records) AS reported_records,
 SUM(area_ha) AS area_ha,AVG(area_ha) AS mean_annual_area FROM annual
UNION ALL SELECT 'Largest area year removed',COUNT(*),SUM(records),SUM(area_ha),AVG(area_ha)
FROM annual WHERE year<>(SELECT year FROM largest);

CREATE VIEW vw_seasonality AS
SELECT reporting_agency,month_num,COUNT(*) AS reported_records,SUM(size_ha) AS area_ha
FROM vw_analysis GROUP BY reporting_agency,month_num;

CREATE VIEW vw_cause AS
WITH g AS(SELECT reporting_agency,cause_class,COUNT(*) AS reported_records,SUM(size_ha) AS area_ha
 FROM vw_analysis GROUP BY reporting_agency,cause_class)
SELECT reporting_agency,cause_class,reported_records,area_ha,
 1.0*reported_records/SUM(reported_records) OVER(PARTITION BY reporting_agency) AS count_share,
 area_ha/NULLIF(SUM(area_ha) OVER(PARTITION BY reporting_agency),0) AS area_share FROM g;

CREATE VIEW vw_agency AS
WITH r AS(SELECT reporting_agency,size_ha,ROW_NUMBER() OVER(PARTITION BY reporting_agency ORDER BY size_ha) AS rn,
 COUNT(*) OVER(PARTITION BY reporting_agency) AS n FROM vw_analysis),
m AS(SELECT reporting_agency,AVG(size_ha) AS median_size_ha FROM r WHERE rn IN((n+1)/2,(n+2)/2) GROUP BY reporting_agency)
SELECT a.reporting_agency,COUNT(*) AS reported_records,SUM(a.size_ha) AS area_ha,AVG(a.size_ha) AS mean_size_ha,
 m.median_size_ha,1.0*SUM(is_large_fire)/COUNT(*) AS large_fire_share,
 1.0*SUM(CASE WHEN cause_class='Unknown' THEN 1 ELSE 0 END)/COUNT(*) AS unknown_cause_share
FROM vw_analysis a JOIN m USING(reporting_agency) GROUP BY a.reporting_agency;

CREATE VIEW vw_segments AS
SELECT reporting_agency,cause_class,month_num,COUNT(*) AS reported_records,
 SUM(is_large_fire) AS large_fire_records,1.0*SUM(is_large_fire)/COUNT(*) AS large_fire_share,
 CASE WHEN COUNT(*)<30 OR month_num=-1 THEN 1 ELSE 0 END AS do_not_rank
FROM vw_analysis GROUP BY reporting_agency,cause_class,month_num;

CREATE VIEW vw_threshold_sensitivity AS
WITH t AS(SELECT 100 AS threshold_ha UNION ALL SELECT 200 UNION ALL SELECT 1000)
SELECT threshold_ha,SUM(CASE WHEN size_ha>=threshold_ha THEN 1 ELSE 0 END) AS large_fire_records,
 1.0*SUM(CASE WHEN size_ha>=threshold_ha THEN 1 ELSE 0 END)/COUNT(*) AS record_share,
 SUM(CASE WHEN size_ha>=threshold_ha THEN size_ha ELSE 0 END)/NULLIF(SUM(size_ha),0) AS area_share
FROM vw_analysis CROSS JOIN t GROUP BY threshold_ha;

CREATE VIEW vw_quality_trend AS
SELECT a.agency_code AS reporting_agency,f.year_key AS year,COUNT(*) AS source_records,
 SUM(f.in_analysis) AS selected_records,AVG(1.0*f.missing_report_date) AS missing_report_date_share,
 AVG(1.0*f.missing_size) AS missing_size_share,AVG(1.0*f.invalid_size) AS invalid_size_share,
 AVG(CASE WHEN c.cause_class='Unknown' THEN 1.0 ELSE 0.0 END) AS unknown_cause_share,
 SUM(CASE WHEN f.response_key=-1 THEN 1 ELSE 0 END) AS unknown_response_records,
 SUM(CASE WHEN f.date_key=-1 THEN 1 ELSE 0 END) AS unknown_calendar_date_records
FROM fact_fire f JOIN dim_agency a USING(agency_key) JOIN dim_cause c USING(cause_key)
GROUP BY a.agency_code,f.year_key;

CREATE VIEW vw_grid AS SELECT grid_cell,COUNT(*) AS reported_records,SUM(size_ha) AS area_ha,
 AVG(latitude) AS mean_source_latitude,AVG(longitude) AS mean_source_longitude
FROM vw_analysis WHERE grid_cell IS NOT NULL GROUP BY grid_cell;

CREATE VIEW vw_top_fires AS SELECT fire_key,fire_id,reporting_agency,year,month_num,cause_class,size_ha,
 RANK() OVER(ORDER BY size_ha DESC) AS area_rank FROM vw_analysis;

CREATE VIEW vw_coverage AS
SELECT a.agency_code AS reporting_agency,y.year_key AS year,
 COALESCE(q.source_records,0) AS source_records,COALESCE(q.selected_records,0) AS selected_records,
 CASE WHEN y.year_key<a.documented_start_year THEN 'Outside documented coverage'
 WHEN q.source_records IS NULL THEN 'No records; completeness unknown'
 ELSE 'Records present; completeness unverified' END AS coverage_status
FROM dim_agency a CROSS JOIN dim_year y LEFT JOIN vw_quality_trend q
 ON q.reporting_agency=a.agency_code AND q.year=y.year_key
WHERE a.agency_key<>-1 AND y.year_key>=(SELECT MIN(documented_start_year) FROM dim_agency);
