-- External comparison remains gated: no geographic assignment of PC fires exists.
-- Only like-for-like, verified jurisdiction/category reference data may be joined.
-- Empty output means pending evidence, never agreement or zero discrepancy.
SELECT jurisdiction,year,reporting_category,source_version,fire_count,area_ha,scope_note
FROM fact_nfd_annual ORDER BY jurisdiction,year,reporting_category;
