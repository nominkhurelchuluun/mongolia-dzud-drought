"""Check every assumption notebook 01 makes about the raw files.

Run this before notebook 01. It opens each raw input, reports what it actually
contains, and tells you whether the detection logic in notebook 01 will succeed.
It writes nothing and takes about a minute, most of it spent opening one SPEI
NetCDF and the temperature GRIB.

Usage
    python scripts/preflight.py

In Colab
    from src import data_loading as dl
    dl.use_colab_drive()
    %run scripts/preflight.py
"""

from __future__ import annotations

import sys
import zipfile
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO_ROOT))

import pandas as pd

from src import data_loading as dl

PASS, FAIL, WARN = "PASS", "FAIL", "WARN"
results = []


def report(status, check, detail=""):
    results.append((status, check))
    print(f"[{status}] {check}")
    if detail:
        for line in str(detail).splitlines():
            print(f"       {line}")


def section(title):
    print(f"\n{'=' * 70}\n{title}\n{'=' * 70}")


section("0. Paths")
dl.describe_paths()

for key, filename in dl.RAW_FILES.items():
    path = dl.RAW_DIR / filename
    if path.exists():
        report(PASS, f"{key}: {filename}",
               f"{path.stat().st_size / 1e6:.1f} MB")
    else:
        report(FAIL, f"{key}: {filename} not found in {dl.RAW_DIR}")

if any(status == FAIL for status, _ in results):
    print("\nPlace the missing files in data/raw/ using the names above, or edit "
          "RAW_FILES in src/data_loading.py to match your filenames.")
    sys.exit(1)


section("1. Mortality workbook")

book = pd.ExcelFile(dl.raw_path("mortality"))
report(PASS, "sheets", ", ".join(book.sheet_names))

mortality = pd.read_excel(dl.raw_path("mortality"))
mortality.columns = [str(c).strip() for c in mortality.columns]
print("\ncolumns in the default sheet:")
for column in mortality.columns:
    print(f"       {column!r}")

detected = {}
for label, predicate in [
        ("DEATH_COL", lambda c: "death" in c.lower()),
        ("PRIOR_COL", lambda c: "prior" in c.lower() and "year" in c.lower()),
        ("RATE_COL", lambda c: "mortality" in c.lower() and "rate" in c.lower())]:
    matches = [c for c in mortality.columns if predicate(c)]
    if len(matches) == 1:
        detected[label] = matches[0]
        report(PASS, f"{label} detected", repr(matches[0]))
    elif not matches:
        report(FAIL, f"{label} matched nothing",
               "notebook 01 cell 3 will raise StopIteration")
    else:
        detected[label] = matches[0]
        report(WARN, f"{label} matched {len(matches)} columns",
               f"will use {matches[0]!r}; others: {matches[1:]}")

for required in ("Aimag", "Year", "Species"):
    if required in mortality.columns:
        report(PASS, f"column {required!r} present")
    else:
        report(FAIL, f"column {required!r} missing")

if "Species" in mortality.columns:
    labels = sorted(mortality["Species"].astype(str).str.strip().unique())
    unmapped = [s for s in labels if s not in dl.SFU_BY_NAME]
    if unmapped:
        report(FAIL, "species labels not in SFU_BY_NAME", unmapped)
    else:
        report(PASS, "all species labels map to an SFU weight", labels)

if "Year" in mortality.columns:
    years = pd.to_numeric(mortality["Year"], errors="coerce").dropna()
    report(PASS, "year range", f"{int(years.min())}-{int(years.max())}")

if "Aimag" in mortality.columns:
    aimags = sorted(mortality["Aimag"].astype(str).str.strip().unique())
    report(PASS if len(aimags) == 21 else WARN,
           f"{len(aimags)} distinct aimags", ", ".join(aimags))

quarter_candidates = [c for c in mortality.columns
                      if any(c.lower().startswith(f"{q} ") or c.lower() == q
                             for q in ("i", "ii", "iii", "iv"))]
if quarter_candidates:
    report(PASS, "cumulative quarterly columns found", quarter_candidates)
else:
    report(WARN, "no cumulative quarterly columns",
           "Figure S2 cannot be rebuilt from this workbook")

if len(detected) == 3:
    sample = mortality.dropna(subset=list(detected.values())).head(3)
    print("\nfirst rows of the detected columns:")
    print(sample[[c for c in ("Aimag", "Year", "Species") if c in mortality.columns]
                 + list(detected.values())].to_string(index=False))


section("2. Population workbook")

population = pd.read_excel(dl.raw_path("population"))
has_unnamed = all(c in population.columns for c in ("Unnamed: 0", "Unnamed: 1"))
report(PASS if has_unnamed else FAIL,
       "first two columns are unnamed",
       "notebook 01 cell 8 expects 'Unnamed: 0' and 'Unnamed: 1'"
       if not has_unnamed else "")

year_columns = [c for c in population.columns if str(c).strip().isdigit()]
report(PASS if year_columns else FAIL,
       f"{len(year_columns)} year columns",
       f"{year_columns[0]} to {year_columns[-1]}" if year_columns else "")

if has_unnamed:
    types = (population["Unnamed: 0"].ffill().astype(str).str.strip()
             .str.lower().unique())
    missing = [k for k in dl.SFU_BY_SPECIES
               if not any(k in t for t in types)]
    report(PASS if not missing else FAIL,
           "all five species present in Livestock_Type",
           f"missing: {missing}" if missing else ", ".join(sorted(types)[:12]))


section("3. Aimag boundaries")

import geopandas as gpd

boundaries = gpd.read_file(dl.raw_path("aimags"))
report(PASS, f"{len(boundaries)} features", ", ".join(boundaries.columns))

name_column = "prefecture" if "prefecture" in boundaries.columns else None
if name_column is None:
    report(FAIL, "no 'prefecture' property",
           "edit load_aimag_boundaries in src/data_loading.py")
else:
    names = sorted(boundaries[name_column].astype(str).str.strip().unique())
    report(PASS, f"{len(names)} names in '{name_column}'", ", ".join(names))
    renamed = {dl.RENAME_GEO.get(n, n) for n in names} - set(dl.NON_AIMAG_UNITS)
    if "Aimag" in mortality.columns:
        mortality_aimags = set(mortality["Aimag"].astype(str).str.strip())
        only_geo = sorted(renamed - mortality_aimags)
        only_mortality = sorted(mortality_aimags - renamed)
        if only_geo or only_mortality:
            report(FAIL, "aimag names do not match after RENAME_GEO",
                   f"only in boundaries: {only_geo}\n"
                   f"only in mortality:  {only_mortality}")
        else:
            report(PASS, "aimag names match the mortality workbook")


section("4. SPEI-3 archive")

with zipfile.ZipFile(dl.raw_path("spei_zip")) as archive:
    members = archive.namelist()

netcdf_members = [m for m in members if m.endswith(".nc")]
spei3_members = [m for m in netcdf_members if "SPEI3" in Path(m).name]
report(PASS if spei3_members else FAIL,
       f"{len(spei3_members)} files matching 'SPEI3' and '.nc'",
       f"of {len(members)} archive members")

if spei3_members:
    print("       example names:")
    for member in spei3_members[:3]:
        print(f"         {Path(member).name}")
    parsed = [dl.parse_yyyymm(m) for m in spei3_members]
    unparsed = [m for m, p in zip(spei3_members, parsed) if p[0] is None]
    if unparsed:
        report(FAIL, f"{len(unparsed)} filenames do not match the _YYYYMM pattern",
               unparsed[:3])
    else:
        years = sorted({p[0] for p in parsed})
        months = sorted({p[1] for p in parsed})
        report(PASS, "filename dates parse",
               f"{min(years)}-{max(years)}, months {min(months)}-{max(months)}, "
               f"{len(spei3_members)} files")
        expected = (max(years) - min(years) + 1) * 12
        if len(spei3_members) < expected:
            report(WARN, f"expected about {expected} monthly files",
                   f"found {len(spei3_members)}")

    files = dl.extract_spei_archive()
    sample = dl.read_spei_months(files[:1])
    report(PASS, "first file reads",
           f"{len(sample)} cells, SPEI range "
           f"{sample['SPEI'].min():.2f} to {sample['SPEI'].max():.2f}")
    latitudes = sorted(sample["latitude"].unique())
    longitudes = sorted(sample["longitude"].unique())
    report(PASS, "grid",
           f"{len(latitudes)} lat x {len(longitudes)} lon, "
           f"resolution {abs(latitudes[1] - latitudes[0]):.3f} deg, "
           f"extent {min(latitudes):.2f}-{max(latitudes):.2f} N, "
           f"{min(longitudes):.2f}-{max(longitudes):.2f} E")


section("5. ERA5 temperature GRIB")

import xarray as xr

with xr.open_dataset(dl.raw_path("t2m_grib"), engine="cfgrib") as dataset:
    variables = list(dataset.data_vars)
    report(PASS, "data variables", ", ".join(variables))

    temperature_variables = [v for v in variables
                             if any(k in v.lower() for k in ("t2m", "temp", "t2"))]
    report(PASS if temperature_variables else FAIL,
           "temperature variable detected",
           temperature_variables[0] if temperature_variables else
           "notebook 01 cell 20 will raise StopIteration")

    time_names = [n for n in ("time", "valid_time") if n in dataset.coords]
    report(PASS if time_names else FAIL, "time coordinate", ", ".join(time_names))

    if temperature_variables and time_names:
        name = temperature_variables[0]
        values = dataset[name]
        report(PASS, "shape", f"{dict(values.sizes)}")
        times = pd.to_datetime(dataset[time_names[0]].values)
        report(PASS, "time range",
               f"{times.min():%Y-%m} to {times.max():%Y-%m}, {len(times)} steps")
        first = float(values.isel({d: 0 for d in values.dims}).values)
        report(PASS if first > 100 else WARN, "units look like kelvin",
               f"first value {first:.1f}; notebook 01 subtracts 273.15")

    grib_latitudes = sorted(dataset.latitude.values.tolist())
    grib_longitudes = sorted(dataset.longitude.values.tolist())
    grib_resolution = abs(grib_latitudes[1] - grib_latitudes[0])
    report(PASS, "grid",
           f"{len(grib_latitudes)} lat x {len(grib_longitudes)} lon, "
           f"resolution {grib_resolution:.3f} deg")

if spei3_members:
    spei_resolution = abs(latitudes[1] - latitudes[0])
    if abs(spei_resolution - grib_resolution) < 1e-6:
        report(PASS, "SPEI and ERA5 grids share a resolution",
               f"{grib_resolution:.3f} deg")
    else:
        report(WARN, "SPEI and ERA5 grids differ",
               f"SPEI {spei_resolution:.3f} deg, ERA5 {grib_resolution:.3f} deg. "
               "This is fine: they are joined to aimags separately, never merged "
               "on coordinates.")


section("Summary")

failures = [check for status, check in results if status == FAIL]
warnings = [check for status, check in results if status == WARN]

print(f"{len(results)} checks, {len(failures)} failed, {len(warnings)} warnings")
if failures:
    print("\nfailed:")
    for check in failures:
        print(f"  {check}")
    print("\nFix these before running notebook 01.")
if warnings:
    print("\nwarnings:")
    for check in warnings:
        print(f"  {check}")
if not failures:
    print("\nNotebook 01 should run. Expect 10 to 30 minutes, most of it in the "
          "SPEI read.")

sys.exit(1 if failures else 0)
