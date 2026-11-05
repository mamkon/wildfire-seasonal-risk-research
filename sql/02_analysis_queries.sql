-- Can we plan around the average? Even-sized medians use the two middle rows.
SELECT reported_records,area_ha,mean_size_ha,median_size_ha,large_fire_share FROM vw_kpi_summary;
SELECT reporting_agency,top_pct,selected_records,area_share FROM vw_concentration;
SELECT position,cumulative_area_share FROM vw_pareto ORDER BY position;
-- Is the burden changing? Rolling averages require a full calendar-year window.
SELECT year,reported_records,area_ha,yoy_area_change,five_year_mean_area FROM vw_annual_trend ORDER BY year;
SELECT decade,years_observed,mean_annual_area FROM vw_decades ORDER BY decade;
SELECT scenario,years,reported_records,area_ha,mean_annual_area FROM vw_largest_year_sensitivity;
-- When does the season peak? Unknown source months remain visible as -1.
SELECT reporting_agency,month_num,reported_records,area_ha FROM vw_seasonality;
-- What causes reported fires, and which classes account for reported area?
SELECT reporting_agency,cause_class,reported_records,area_ha,count_share,area_share FROM vw_cause;
-- Which observed segments have a high large-fire share? Never rank flagged segments.
SELECT reporting_agency,cause_class,month_num,reported_records,large_fire_share,do_not_rank FROM vw_segments;
-- Can we trust the numbers? Source-wide quality denominators differ from selected facts.
SELECT reporting_agency,year,source_records,selected_records,unknown_cause_share,
 missing_report_date_share,missing_size_share FROM vw_quality_trend;
SELECT threshold_ha,large_fire_records,record_share,area_share FROM vw_threshold_sensitivity;
