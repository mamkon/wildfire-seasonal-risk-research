.PHONY: data prepare fixtures test warehouse reconcile analysis
data:
	python -m src.download_data
prepare:
	python -m src.prepare_cnfdb
fixtures:
	python -m src.make_fixtures
test:
	python -m pytest tests -q
warehouse:
	python -m src.load_warehouse
reconcile:
	python -m src.reconcile
analysis:
	python -m src.analyse
	python -m src.review_analysis
	python -m src.concentration_sensitivity
	python -m src.review_charts
	python -m src.build_notebooks
	python -m src.execute_notebooks
	python -m src.report_analysis
