"""Source identity and declared analytical choices."""

import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
RAW = ROOT / "data/raw"
PROCESSED = ROOT / "data/processed"
PROFILE = json.loads((ROOT / "verification/source_verification.json").read_text())
SOURCE_FILE = PROFILE["filename"]
SOURCE_VERSION = PROFILE["release_label_in_filename"]
AGENCY_STARTS = PROFILE["documented_agency_start_years"]
END_YEAR = PROFILE["documented_end_year"]
LARGE_FIRE_HA = 200
SENSITIVITY_HA = (100, 200, 1000)
SIZE_BINS = (0, 1, 10, 200, 1000, 10000, float("inf"))
SIZE_LABELS = (
    "Under 1 ha",
    "1 to under 10 ha",
    "10 to under 200 ha",
    "200 to under 1,000 ha",
    "1,000 to under 10,000 ha",
    "10,000+ ha",
)
WINDOW_OPTIONS = {
    "long_fixed_agencies": (1980, False),
    "modern_fixed_agencies": (2000, False),
    "recent_all_agencies": (2018, True),
}
SELECTED_WINDOW = "modern_fixed_agencies"
