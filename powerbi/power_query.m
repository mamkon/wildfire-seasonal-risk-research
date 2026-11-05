// Separate queries: create pDataFolder, then fxLoadCsv, then each named table.
// Parameter value is deliberately blank. Enter your private folder in Desktop;
// do not commit a populated local path.
// QUERY: pDataFolder
"" meta [IsParameterQuery=true, Type="Text", IsParameterQueryRequired=true]

// QUERY: fxLoadCsv
(TableName as text, ColumnTypes as list) as table =>
let
    Folder = if Text.Length(pDataFolder)=0 then error "Choose the exported data folder in pDataFolder." else Text.TrimEnd(pDataFolder,{"/",Character.FromNumber(92)}),
    Source = Csv.Document(File.Contents(Folder & "/" & TableName & ".csv"),[Delimiter=",",Encoding=65001,QuoteStyle=QuoteStyle.Csv]),
    Headers = Table.PromoteHeaders(Source,[PromoteAllScalars=true]),
    Blanks = Table.ReplaceValue(Headers,"",null,Replacer.ReplaceValue,Table.ColumnNames(Headers)),
    Typed = Table.TransformColumnTypes(Blanks,ColumnTypes,"en-US")
in Typed

// QUERY: load_batch
fxLoadCsv("load_batch",{{"batch_key",Int64.Type},{"source_version",type text},{"source_sha256",type text},{"analysis_start",Int64.Type},{"analysis_end",Int64.Type}})

// QUERY: fact_fire
fxLoadCsv("fact_fire",{{"fire_key",Int64.Type},{"fire_id",type text},{"batch_key",Int64.Type},{"date_key",Int64.Type},{"year_key",Int64.Type},{"month_key",Int64.Type},{"agency_key",Int64.Type},{"cause_key",Int64.Type},{"size_class_key",Int64.Type},{"response_key",Int64.Type},{"latitude",type number},{"longitude",type number},{"size_ha",type number},{"is_large_fire",Int64.Type},{"in_analysis",Int64.Type},{"missing_report_date",Int64.Type},{"missing_size",Int64.Type},{"invalid_size",Int64.Type},{"invalid_coordinates",Int64.Type},{"invalid_calendar_date",Int64.Type},{"report_calendar_conflict",Int64.Type},{"exact_duplicate_row",Int64.Type},{"known_prescribed",Int64.Type},{"repeated_fire_id",Int64.Type},{"grid_cell",type text},{"report_date",type date},{"out_date",type date},{"out_before_report",Int64.Type}})

// QUERY: fact_nfd_annual
fxLoadCsv("fact_nfd_annual",{{"jurisdiction",type text},{"year",Int64.Type},{"reporting_category",type text},{"source_version",type text},{"fire_count",Int64.Type},{"area_ha",type number},{"source_url",type text},{"scope_note",type text}})

// QUERY: dim_agency
fxLoadCsv("dim_agency",{{"agency_key",Int64.Type},{"agency_code",type text},{"reporting_agency",type text},{"documented_start_year",Int64.Type},{"reporting_agency_name",type text}})

// QUERY: dim_cause
fxLoadCsv("dim_cause",{{"cause_key",Int64.Type},{"cause_code",type text},{"cause_class",type text}})

// QUERY: dim_size_class
fxLoadCsv("dim_size_class",{{"size_class_key",Int64.Type},{"size_class",type text},{"sort_order",Int64.Type},{"min_ha",type number},{"max_ha",type number}})

// QUERY: dim_response
fxLoadCsv("dim_response",{{"response_key",Int64.Type},{"response_code",type text},{"response_class",type text}})

// QUERY: dim_date
fxLoadCsv("dim_date",{{"date_key",Int64.Type},{"date",type date},{"year",Int64.Type},{"month_num",Int64.Type},{"month_name",type text},{"season",type text},{"decade",Int64.Type}})

// QUERY: dim_year
fxLoadCsv("dim_year",{{"year_key",Int64.Type},{"year_label",type text},{"decade_start",Int64.Type},{"decade_label",type text}})

// QUERY: dim_month
fxLoadCsv("dim_month",{{"month_key",Int64.Type},{"month_name",type text},{"season",type text}})

// QUERY: dim_grid
fxLoadCsv("dim_grid",{{"grid_cell",type text},{"latitude",type number},{"longitude",type number}})

// QUERY: size_points
fxLoadCsv("size_points",{{"size_value",type number},{"size_label",type text}})

// OPTIONAL ODBC alternative, only if a local SQLite ODBC driver and DSN exist.
// Not needed for the CSV route. Import base facts and dimensions, not views.
// Odbc.Query("dsn=WildfireResearch", "SELECT fire_key, size_ha, in_analysis FROM fact_fire")
