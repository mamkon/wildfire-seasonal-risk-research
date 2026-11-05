"""Create small reproducible source samples for preparation tests and later CI."""

import pandas as pd

from src.config import RAW, ROOT, SOURCE_FILE


def main():
    d = pd.read_csv(RAW / SOURCE_FILE, low_memory=False)
    selections = [
        d.groupby("SRC_AGENCY", sort=True).head(3),
        d.loc[d.CAUSE.eq("U")].head(3),
        d.loc[d.RESPONSE.astype(str).str.strip().isin(["FUL", "MOD", "MON"])].head(6),
        d.loc[d.PRESCRIBED.astype(str).str.strip().eq("PB")].head(2),
        d.loc[d.YEAR.lt(1946)].head(2),
    ]
    sample = pd.concat(selections).loc[lambda x: ~x.index.duplicated()].sort_index()
    out = ROOT / "tests/fixtures"
    out.mkdir(parents=True, exist_ok=True)
    sample.to_csv(out / "cnfdb_sample.csv", index=False)
    print(f"Fixture source sample saved: {len(sample)} rows.")


if __name__ == "__main__":
    main()
