# Derived data

Every file here is written by `notebooks/01_data_preparation.ipynb` and read by
notebooks 02 through 05. These are the files that should be committed to git and
archived on Zenodo, so a reviewer without the raw climate archives can still run
everything.

Run notebook 01 once against a populated `data/raw/` to generate them.

| File | Written by | Read by | Contents |
| --- | --- | --- | --- |
| `mortality_panel.csv` | 01 §7 | 03, 04, 05 | The analysis panel. 21 aimags × 33 years = 693 rows. Species rates, `All`, `All_SFU`, `SPEI_PrevSummer`, `SPEI_PrevSummer_point`, `Temp_Winter`, `Temp_Winter_Z_study`, `Temp_Winter_Z_climate`. |
| `mortality_rates_aimag.csv` | 01 §1 | 01 §7 | Aimag-year mortality rates before the climate merge. |
| `livestock_losses_national_annual.csv` | 01 §2 | 03 | National deaths by species and year, million head. |
| `livestock_population_national_species.csv` | 01 §3 | 03 | National head counts by species, plus `Headcount` and `SFU_units`. |
| `livestock_population_national_total.csv` | 01 §3 | 03 | Reported national total with year-over-year change. |
| `livestock_population_aimag_species.csv` | 01 §3 | — | Aimag-level populations by species. Not used by any manuscript figure; retained because reviewers commonly ask for it. |
| `aimag_boundaries.geojson` | 01 §4 | 02, 05 | Aimag polygons with harmonised names, Ulaanbaatar and the two city districts removed. |
| `spei3_cell_area_weights.csv` | 01 §5 | — | Overlap area between each SPEI grid cell and each aimag polygon. |
| `spei3_jja_aimag_1950_2024.csv` | 01 §5 | 02 | Area-weighted mean June–August SPEI-3 per aimag-year. |
| `spei3_jja_national_1950_2024.csv` | 01 §5 | 02 | Area-weighted national mean June–August SPEI-3. |
| `spei3_jja_aimag_point_1950_2024.csv` | 01 §5 | 01 §7 | Point-sampled unweighted variant, kept to reproduce the submitted panel values. |
| `spei3_seasonal_aimag_1950_2024.csv` | 01 §5 | 03 | Area-weighted seasonal mean SPEI-3 per aimag-year, all four seasons. |
| `spei3_jja_aimag_trends.csv` | 01 §5 | 02, 05 | OLS drying rates per aimag for 1950–2024 and 1992–2024. |
| `era5_seasonal_temperature_aimag.csv` | 01 §6 | — | Seasonal mean 2 m temperature per aimag-year, all four seasons. |
| `era5_djf_temperature_aimag.csv` | 01 §6 | 01 §7 | DJF mean temperature with both Z-score variants. |
