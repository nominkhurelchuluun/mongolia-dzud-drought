"""Download the ERA5 monthly 2 m temperature GRIB used by notebook 01.

Requires a Copernicus Climate Data Store account and a ``~/.cdsapirc`` file
containing the API key. See https://cds.climate.copernicus.eu/how-to-api

Usage
    python scripts/download_era5.py
    python scripts/download_era5.py --start 1950 --end 2024 --out data/raw

The SPEI-3 archive is not downloadable through this script. ERA5-Drought
(Keune et al., 2025) is distributed as a separate dataset; see
``data/raw/README.md``.
"""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO_ROOT))

from src import data_loading as dl

DATASET = "reanalysis-era5-single-levels-monthly-means"

AREA = [dl.LAT_MAX, dl.LON_MIN, dl.LAT_MIN, dl.LON_MAX]


def build_request(start_year, end_year):
    return {
        "product_type": ["monthly_averaged_reanalysis"],
        "variable": ["2m_temperature"],
        "year": [str(y) for y in range(start_year, end_year + 1)],
        "month": [f"{m:02d}" for m in range(1, 13)],
        "time": ["00:00"],
        "data_format": "grib",
        "download_format": "unarchived",
        "area": AREA,
    }


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--start", type=int, default=dl.SPEI_START)
    parser.add_argument("--end", type=int, default=dl.SPEI_END)
    parser.add_argument("--out", type=Path, default=None)
    parser.add_argument("--dry-run", action="store_true")
    arguments = parser.parse_args()

    destination_dir = arguments.out or dl.RAW_DIR
    destination_dir.mkdir(parents=True, exist_ok=True)
    destination = destination_dir / dl.RAW_FILES["t2m_grib"]

    request = build_request(arguments.start, arguments.end)

    print(f"dataset     {DATASET}")
    print(f"area        N {AREA[0]}, W {AREA[1]}, S {AREA[2]}, E {AREA[3]}")
    print(f"years       {arguments.start}-{arguments.end}")
    print(f"destination {destination}")

    if arguments.dry_run:
        print("\ndry run, nothing downloaded")
        return

    if destination.exists():
        print("\nfile already exists, nothing to do")
        return

    import cdsapi

    client = cdsapi.Client()
    client.retrieve(DATASET, request, str(destination))
    print(f"\nwrote {destination} "
          f"({destination.stat().st_size / 1e6:.1f} MB)")


if __name__ == "__main__":
    main()
