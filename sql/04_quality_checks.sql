PRAGMA foreign_key_check;
PRAGMA integrity_check;
SELECT COUNT(*) AS source_records,SUM(in_analysis) AS analysis_records FROM fact_fire;
SELECT SUM(CASE WHEN date_key=-1 THEN 1 ELSE 0 END) AS unknown_date,
 SUM(CASE WHEN agency_key=-1 THEN 1 ELSE 0 END) AS unknown_agency,
 SUM(CASE WHEN response_key=-1 THEN 1 ELSE 0 END) AS unknown_response FROM fact_fire;
SELECT COUNT(*) AS invalid_sizes FROM fact_fire WHERE size_ha<0;
SELECT COUNT(*) AS invalid_coordinates FROM fact_fire
WHERE latitude NOT BETWEEN 41 AND 84 OR longitude NOT BETWEEN -141 AND -52;
SELECT fire_id,COUNT(*) AS source_rows FROM fact_fire GROUP BY fire_id HAVING COUNT(*)>1;
-- Unknown is required in each dimension even if unused in this snapshot.
SELECT 'dim_date' AS dimension_name,COUNT(*) AS unknown_rows FROM dim_date WHERE date_key=-1
UNION ALL SELECT 'dim_agency',COUNT(*) FROM dim_agency WHERE agency_key=-1
UNION ALL SELECT 'dim_cause',COUNT(*) FROM dim_cause WHERE cause_key=-1
UNION ALL SELECT 'dim_size_class',COUNT(*) FROM dim_size_class WHERE size_class_key=-1
UNION ALL SELECT 'dim_response',COUNT(*) FROM dim_response WHERE response_key=-1;
