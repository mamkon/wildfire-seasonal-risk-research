"""Fetch the pinned CNFDB input and verify its recorded checksum."""

import hashlib
import urllib.request
import zipfile

import pandas as pd

from src.config import RAW, ROOT


def main():
    RAW.mkdir(parents=True, exist_ok=True)
    source = pd.read_csv(ROOT / "data/source_versions.csv", dtype=str).iloc[0]
    target = RAW / source.filename
    if target.exists() and hashlib.sha256(target.read_bytes()).hexdigest() == source.sha256:
        print("Cached CNFDB source matches the recorded checksum.")
        return
    archive = RAW / "cnfdb_download.zip"
    urllib.request.urlretrieve(source.url, archive)
    with zipfile.ZipFile(archive) as z:
        names = [n for n in z.namelist() if n.rsplit("/", 1)[-1] == source.filename]
        if len(names) != 1:
            raise RuntimeError(
                "The official current release changed. Review a new version before replacing the pinned source."
            )
        content = z.read(names[0])
    if hashlib.sha256(content).hexdigest() != source.sha256:
        raise RuntimeError("The source checksum changed. The existing input was not overwritten.")
    target.write_bytes(content)
    print("Downloaded CNFDB and verified the recorded checksum.")


if __name__ == "__main__":
    main()
