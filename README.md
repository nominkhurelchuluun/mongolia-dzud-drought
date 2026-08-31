# Climate-associated livestock mortality in Mongolia

Analysis code for *Climate-Associated Livestock Mortality in Mongolia: The
Increasing Role of Summer Drought in Dzud*, submitted to AGU's *Earth's Future*.

Preceding-summer drought (mean June–August SPEI-3 in year *t*−1) and winter cold
(December *t*−1 to February *t* ERA5 temperature Z-score) are related to annual
livestock mortality across Mongolia's 21 aimags and five livestock species,
1992–2024. The analysis panel is 21 aimags × 33 years = 693 aimag-years.

## What a reviewer needs

Nothing but this repository. The raw ERA5 GRIB and SPEI-3 archives are several
gigabytes and are not committed. Every figure and table in the manuscript is
reproduced by notebooks 02–05, which read only the small derived CSVs in
`data/processed/`.

```bash
git clone <repository-url>
cd mongolia-dzud-drought
conda env create -f environment.yml
conda activate mongolia-dzud
jupyter lab
```

Then run `notebooks/02_climate_trends.ipynb` through
`notebooks/05_spatial_analysis.ipynb` in any order. Each runs top to bottom in a
fresh kernel. Figures are written to `figures/` as vector PDF.

If you prefer pip:

```bash
python -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
```

`cfgrib` and `eccodes` are only needed by notebook 01. If pip cannot build
`eccodes` on your platform, install the environment from `environment.yml`
instead, or drop those two lines from `requirements.txt` and skip notebook 01.

## Notebook to output map

| Notebook | Figures | Tables | Reads |
| --- | --- | --- | --- |
| `01_data_preparation.ipynb` | — | — | `data/raw/` only |
| `02_climate_trends.ipynb` | 5, S1 | S6 source values | `data/processed/` |
| `03_mortality_analysis.ipynb` | 2, 3, 4, 6, 7 | S3, S7 | `data/processed/` |
| `04_interaction_models.ipynb` | 8, S2 | S1, S2, S4 | `data/processed/` |
| `05_spatial_analysis.ipynb` | 9 | S5, S6 | `data/processed/` |

Figure 1, the conceptual framework panel, was drawn in BioRender and is not
produced by any code in this repository.

Output filenames:

| File in `figures/` | Manuscript | Notebook |
| --- | --- | --- |
| `figure_02_temporal_alignment.pdf` | Figure 2 | 03 |
| `figure_03_national_livestock_population.pdf` | Figure 3 | 03 |
| `figure_04_species_population_and_mortality.pdf` | Figure 4 | 03 |
| `figure_05_spei3_trends_1992_2024.pdf` | Figure 5 | 02 |
| `figure_06_seasonal_spei_correlations.pdf` | Figure 6 | 03 |
| `figure_07_drought_and_species_mortality.pdf` | Figure 7 | 03 |
| `figure_08_drought_cold_heatmap.pdf` | Figure 8 | 04 |
| `figure_09_drought_sensitivity_map.pdf` | Figure 9 | 05 |
| `figure_S01_spei3_trends_1950_2024.pdf` | Figure S1 | 02 |
| `figure_S02_leave_one_year_out.pdf` | Figure S2 | 04 |

## Reproducing from raw data

Only needed to regenerate `data/processed/`.

1. Create a Copernicus Climate Data Store account and write `~/.cdsapirc`.
2. `python scripts/download_era5.py` for the monthly 2 m temperature GRIB.
3. Obtain the ERA5-Drought SPEI-3 archive (Keune et al., 2025) and the two NSO
   workbooks. See `data/raw/README.md` for the expected filenames.
4. Run `notebooks/01_data_preparation.ipynb`.

### Paths

All paths derive from `DATA_DIR` in `src/data_loading.py`, which defaults to
`./data` relative to the repository root. Override it either way:

```bash
export MONGOLIA_DZUD_DATA=/mnt/big-disk/mongolia-data
export MONGOLIA_DZUD_FIGURES=/mnt/big-disk/figures
```

or, in Colab, at the top of any notebook:

```python
from src import data_loading as dl
dl.use_colab_drive()
```

`use_colab_drive()` mounts Google Drive and repoints `DATA_DIR`, `RAW_DIR`,
`PROCESSED_DIR` and `FIG_DIR` at
`/content/drive/My Drive/mongolia-dzud-drought/`. No `/content/drive/My Drive/`
path is hardcoded anywhere else.

## Figure conventions

`src/data_loading.py` holds the shared matplotlib defaults:

- Okabe-Ito colourblind-safe palette, exposed as `OKABE_ITO` and
  `SPECIES_COLORS`
- `pdf.fonttype = 42` and `ps.fonttype = 42`, so TrueType fonts embed as AGU
  requires
- 8 pt minimum text at final print size
- 170 mm maximum width, 228 mm maximum height

Several figures are drawn supersampled: the canvas is `FIG_SCALE` times the
final size and every font size is multiplied by the same factor. Pass that
factor to `save_figure(fig, name, scale=FIG_SCALE)` so the width and height
checks apply at print size.

`save_figure()` writes **PDF only**. There is no PNG output anywhere in this
repository.

## Known differences from the submitted draft

Restructuring surfaced several inconsistencies. Each is resolved here; the
manuscript text may need to follow.

**SFU-weighted mortality.** The working notebook computed `All_SFU` with a
function called `sfu_weighted_mean` that returned an SFU-weighted *average of the
five species rates*, `Σ(rate_s × SFU_s) / Σ SFU_s`. That is not Equation (2).
Notebook 01 §1 now computes `Σ(deaths_s × SFU_s) / Σ(population_s × SFU_s)` from
the death and prior-year population columns, and prints the difference between
the two definitions.

**Two SPEI archives.** The panel model read one zip and Figures 5 and S3 read
another, and the two used different spatial aggregation. Everything now reads the
single 1950–2024 archive. Aimag and national means are area-weighted by grid
cell–polygon overlap. A point-sampled unweighted variant,
`SPEI_PrevSummer_point`, is carried in the panel so the submitted values can be
recovered.

**Two ERA5 GRIBs.** `T2M_GRIB` and `TP_GRIB` were loaded only by a commented-out
cell and fed no figure. Both are gone. `GRIB_PATH`, the monthly 2 m temperature
file, is the only temperature input.

**Winter Z-score reference period.** DJF temperature is standardised within aimag
over 1992–2024, not over a long-run climatology. Given the warming trend this
shifts the cold-anomaly bins in Figure 8. Both variants are written
(`Temp_Winter_Z_study`, `Temp_Winter_Z_climate`) and notebook 04 refits the
interaction under each. The Methods should state which reference is used.

**Dry-summer threshold.** The code uses strict less-than, `SPEI-3 < −0.5`.
Section 2.3 of the manuscript says "at or below −0.5".

**Panel (c) slope units.** Figure 7c annotated β as "pp/SD", but SPEI-3 is never
z-scored in this analysis. The label now reads "pp per SPEI unit".

**Aggregate used for Figures 7a and 9.** Both used `All`, the unweighted mean of
the five species rates, while the surrounding text describes SFU weighting.
`AGGREGATE_COL` in notebook 03 and `SENSITIVITY_COL` in notebook 05 select the
measure, defaulting to `All` to reproduce the submitted figures. Both notebooks
print the alternative alongside.

## Citation

Archive a release on Zenodo and cite the resulting DOI. `CITATION.cff` holds the
metadata; update the DOI and version there before minting.

## License

MIT, see `LICENSE`. The NSO livestock data, ERA5 reanalysis and ERA5-Drought
SPEI-3 are redistributed under the terms set by their respective providers and
are not covered by this license.
