# NFD reference acquisition

The current source entry point is https://national-forestry-database.ca/en/data/fires.php. The older nfdp.ccfm.org address is retained only in historical source records. Checked November 5, 2026: the new home page, about page and indexed download instructions confirm the NFD identity, but the fire table could not be accessed through the research tool. This access failure alone does not establish that all automated access is prohibited.

Download annual number-of-fires and area-burned tables by jurisdiction for 2000–2025, where available. Use the table's filters and retain both the original exports and their settings. Preserve table titles, reporting-category labels, units, revisions, accessed date, source URLs and footnotes. Store unchanged files under data/reference/ and footnotes beside them in nfd_footnotes.txt. No NFD exports were found in that folder during this review. Do not claim they were downloaded manually until the files exist.

The official instructions at https://national-forestry-database.ca/en/howto.php say to click inside the data table, choose the bottom toolbar's download icon, then choose Data. Data opens in a new tab for CSV download. Crosstab is another CSV option, with a different layout. Download the comments separately by selecting the comments section. Check that the export includes all intended years and jurisdictions rather than only a highlighted mark.

Before importing, identify whether Parks Canada is included in provincial totals, whether prescribed burns are included, the minimum fire size and any unreported jurisdiction-years. Keep missing entries distinct from zero.

The reference import must preserve jurisdiction, year, reporting_category, source_version, fire_count, area_ha, source_url, accessed_date and footnotes or a traceable footnote reference. Inspect the existing database schema before adding metadata fields. Retain source units and document conversion to hectares. Do not mix subtotal and total rows. Verify whether CNFDB reporting scope can actually be matched to these figures; an agency code alone is not proof of geographic agreement. Preserve response categories as classification labels, not evidence of suppression actions or outcomes.

No reference figures are supplied until these checks can be performed. The resulting comparison belongs in reconciliation_report.md and is a report of differences, not a test requiring the government sources to agree.
