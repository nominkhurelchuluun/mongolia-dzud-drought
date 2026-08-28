# Raw inputs

No file in this directory is committed. The two climate archives are several
gigabytes and the NSO workbooks are redistributed under the terms set by the
National Statistics Office of Mongolia.

**Only `notebooks/01_data_preparation.ipynb` reads anything here.** Notebooks 02
through 05 read the derived CSVs in `data/processed/`, which are committed, so a
reviewer can reproduce every figure and table without obtaining these files.

Place files in this directory using exactly the names in the first column. The
names are defined in `src/data_loading.RAW_FILES`; change them there if you keep
the originals under their download hashes.

| Expected filename | Source | Notes |
| --- | --- | --- |
| `era5_monthly_t2m_mongolia_1950_2024.grib` | Copernicus Climate Data Store, `reanalysis-era5-single-levels-monthly-means`, 2 m temperature | Run `python scripts/download_era5.py`. Subset to 41.5–52.0°N, 87.5–119.9°E, 1950–2024, monthly means, GRIB. |
| `era5_drought_spei3_mongolia_1950_2024.zip` | ERA5-Drought SPEI-3, Keune et al. (2025) | One NetCDF per month, filenames ending `_YYYYMM.nc` and containing `SPEI3`. Subset to the same bounding box. |
| `mongolia_mortality_rates.xlsx` | National Statistics Office of Mongolia | One row per aimag, year and species. Must contain columns for deaths, prior-year livestock and mortality rate, plus `Aimag`, `Year`, `Species`. |
| `types_livestock_aimag.xlsm` | National Statistics Office of Mongolia | Wide sheet: livestock type in the first unnamed column, aimag in the second, one column per year, values in thousands of head. |
| `mongolia.prefectures.geojson` | Mongolia first-level administrative boundaries | Feature property `prefecture` holds the aimag name. A harmonised copy is written to `data/processed/aimag_boundaries.geojson` by notebook 01 and is committed. |

## Version history of the climate inputs

Two ERA5 temperature GRIBs at different resolutions existed in the original
working notebook. Only the coarser monthly file, referenced there as
`GRIB_PATH`, fed any published figure. The second file (`T2M_GRIB`) and a total
precipitation GRIB (`TP_GRIB`) were loaded by a cell that was commented out and
produced nothing; both have been removed.

Two SPEI-3 zip archives also existed. The panel model drew from one and Figures 5
and S3 from the other. This repository uses the 1950–2024 archive for everything.
See the "Known differences from the submitted draft" section of the top-level
README.

## Checksums

Record the SHA-256 of each file you place here before archiving on Zenodo:

```bash
shasum -a 256 data/raw/* > data/raw/CHECKSUMS.txt
```
