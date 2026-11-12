"""Reproduce the held-out agency-by-month ranking and fixed-review comparison."""
import argparse
import hashlib
import json
import sqlite3
from collections import Counter, defaultdict
from fractions import Fraction
from pathlib import Path

root = Path(__file__).resolve().parents[1]
parser = argparse.ArgumentParser(description=__doc__)
parser.add_argument("--warehouse", required=True, type=Path)
parser.add_argument("--output", type=Path)
args = parser.parse_args()

with sqlite3.connect(args.warehouse.resolve().as_uri() + "?mode=ro", uri=True) as db:
    rows = db.execute("""
        SELECT year_key, fire_key, agency_code,
               CASE WHEN month_key BETWEEN 1 AND 12 THEN month_key END, size_ha >= 200
        FROM fact_fire JOIN dim_agency USING (agency_key)
        WHERE in_analysis = 1 AND repeated_fire_id IS NOT 1 AND exact_duplicate_row IS NOT 1
    """).fetchall()
train = [r for r in rows if r[0] <= 2019]
test = [r for r in rows if r[0] >= 2023]
assert (len(train),len(test),sum(r[-1] for r in test)) == (132037,18814,2027)
pair_n, pair_p, agency_n, agency_p = Counter(),Counter(),Counter(),Counter()
for _, _, agency, month, large in train:
    pair_n[agency,month] += 1
    pair_p[agency,month] += large
    agency_n[agency] += 1
    agency_p[agency] += large
overall = Fraction(sum(r[-1] for r in train),len(train))
groups = defaultdict(list)
for year, key, agency, month, large in test:
    pair = (agency,month)
    if pair in pair_n:
        rate = Fraction(pair_p[pair],pair_n[pair])
    elif agency in agency_n:
        rate = Fraction(agency_p[agency],agency_n[agency])
    else:
        rate = overall
    groups[rate].append((year,key,large))
evaluation = json.loads((root / "modeling/results/evaluation.json").read_text(encoding="utf-8"))
model = evaluation["test_policies"][evaluation["selected_policy"]]
assert (len(test), sum(row[-1] for row in test)) == (
    model["records"], model["true_positives"] + model["false_negatives"]
)
budget = model["true_positives"] + model["false_positives"]
n = positives = 0
ap = 0.0
for rate, group in sorted(groups.items(), reverse=True):
    hits = sum(r[-1] for r in group)
    if n < budget <= n + len(group):
        slots = budget - n
        deterministic = positives + sum(r[-1] for r in sorted(group, key=lambda row: (row[0], row[1]))[:slots])
        expected = positives + slots * hits / len(group)
        result = dict(reviews=budget, test_records=len(test), review_rate=budget/len(test),
                      cutoff_score=float(rate), rows_above_cutoff=n, large_fires_above_cutoff=positives,
                      tied_rows=len(group), tied_large_fires=hits, tied_rows_selected=slots,
                      baseline_large_fires=deterministic, expected_baseline_large_fires_random_tie=expected,
                      model_large_fires=model["true_positives"], tie_break='Ascending reporting year then warehouse row key, without using outcomes.')
    n += len(group)
    positives += hits
    ap += hits / 2027 * positives / n
result['training_years'] = [2000, 2019]
result['evaluation_years'] = [2023, 2025]
result['warehouse_sha256'] = hashlib.sha256(args.warehouse.read_bytes()).hexdigest()
result['baseline_average_precision'] = ap
result['model_average_precision'] = model['average_precision']
if args.output:
    args.output.write_text(json.dumps(result, indent=2) + '\n', encoding='utf-8')
print(json.dumps(result,indent=2))
