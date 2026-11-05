PRAGMA foreign_keys = ON;
-- SQLite enables foreign keys per connection. Use BOOLEAN/BIT and generated
-- identity syntax appropriate to PostgreSQL/SQL Server when porting.
-- Grain: one ingestion of a pinned source snapshot.
CREATE TABLE load_batch(batch_key INTEGER PRIMARY KEY,source_version TEXT NOT NULL,
 source_sha256 TEXT NOT NULL,analysis_start INTEGER NOT NULL,analysis_end INTEGER NOT NULL);
-- Grain: one reporting agency, not geographic jurisdiction.
CREATE TABLE dim_agency(agency_key INTEGER PRIMARY KEY,agency_code TEXT UNIQUE NOT NULL,
 reporting_agency TEXT NOT NULL,documented_start_year INTEGER);
-- Grain: one normalized source cause code.
CREATE TABLE dim_cause(cause_key INTEGER PRIMARY KEY,cause_code TEXT UNIQUE NOT NULL,cause_class TEXT NOT NULL);
-- Grain: one size interval; upper bound is exclusive, NULL means unbounded.
CREATE TABLE dim_size_class(size_class_key INTEGER PRIMARY KEY,size_class TEXT NOT NULL,
 sort_order INTEGER,min_ha REAL,max_ha REAL);
-- Grain: one source response code, including unmapped local codes.
CREATE TABLE dim_response(response_key INTEGER PRIMARY KEY,response_code TEXT UNIQUE NOT NULL,response_class TEXT NOT NULL);
-- Grain: one actual valid source calendar date; -1 is Unknown, never imputed.
CREATE TABLE dim_date(date_key INTEGER PRIMARY KEY,date TEXT UNIQUE,year INTEGER,
 month_num INTEGER,month_name TEXT,season TEXT,decade INTEGER);
-- Separate year/month dimensions keep valid partial dates in period totals.
CREATE TABLE dim_year(year_key INTEGER PRIMARY KEY,year_label TEXT NOT NULL);
CREATE TABLE dim_month(month_key INTEGER PRIMARY KEY,month_name TEXT NOT NULL,season TEXT NOT NULL);
-- Grain: one source row, including flagged/excluded records. in_analysis defines
-- the approved eligible cohort. Keep excluded evidence available for auditing.
CREATE TABLE fact_fire(fire_key INTEGER PRIMARY KEY,fire_id TEXT,batch_key INTEGER NOT NULL,
 date_key INTEGER NOT NULL,year_key INTEGER NOT NULL,month_key INTEGER NOT NULL,
 agency_key INTEGER NOT NULL,cause_key INTEGER NOT NULL,size_class_key INTEGER NOT NULL,
 response_key INTEGER NOT NULL,latitude REAL CHECK(latitude BETWEEN 41 AND 84),
 longitude REAL CHECK(longitude BETWEEN -141 AND -52),size_ha REAL CHECK(size_ha>=0),
 is_large_fire INTEGER CHECK(is_large_fire IN(0,1)),in_analysis INTEGER NOT NULL CHECK(in_analysis IN(0,1)),
 missing_report_date INTEGER NOT NULL,missing_size INTEGER NOT NULL,invalid_size INTEGER NOT NULL,
 invalid_coordinates INTEGER NOT NULL,invalid_calendar_date INTEGER NOT NULL,
 report_calendar_conflict INTEGER NOT NULL,exact_duplicate_row INTEGER NOT NULL,
 known_prescribed INTEGER NOT NULL,repeated_fire_id INTEGER NOT NULL,
 grid_cell TEXT,report_date TEXT,out_date TEXT,out_before_report INTEGER NOT NULL,
 FOREIGN KEY(batch_key) REFERENCES load_batch,FOREIGN KEY(date_key) REFERENCES dim_date,
 FOREIGN KEY(year_key) REFERENCES dim_year,FOREIGN KEY(month_key) REFERENCES dim_month,
 FOREIGN KEY(agency_key) REFERENCES dim_agency,FOREIGN KEY(cause_key) REFERENCES dim_cause,
 FOREIGN KEY(size_class_key) REFERENCES dim_size_class,FOREIGN KEY(response_key) REFERENCES dim_response);
-- Grain: one geographic jurisdiction, year, reporting category and source release.
-- Empty until official NFD exports and scope footnotes are verified.
CREATE TABLE fact_nfd_annual(jurisdiction TEXT NOT NULL,year INTEGER NOT NULL,
 reporting_category TEXT NOT NULL,source_version TEXT NOT NULL,fire_count INTEGER CHECK(fire_count>=0),
 area_ha REAL CHECK(area_ha>=0),source_url TEXT NOT NULL,scope_note TEXT NOT NULL,
 PRIMARY KEY(jurisdiction,year,reporting_category,source_version));
CREATE INDEX fire_scope ON fact_fire(in_analysis,year_key,agency_key);
