# Climate-associated livestock mortality in Mongolia

Analysis code for *Climate-Associated Livestock Mortality in Mongolia: The
Increasing Role of Summer Drought in Dzud*, submitted to AGU's *Earth's Future*.

The study asks whether a dry summer leaves Mongolian herds more likely to die
the following year, and whether that effect gets worse when a severe winter
follows. Mean June–August SPEI-3 in year *t*−1 and the December *t*−1 to
February *t* ERA5 temperature Z-score are related to annual livestock mortality
across 21 aimags and five species, 1992–2024. The panel is 693 aimag-years.

## Running it

Notebooks 02 through 05 read only the derived CSVs in `data/processed/`, which
are committed here. The ERA5 GRIB and the SPEI-3 archive run to several
gigabytes and are not, but nothing except notebook 01 touches them.

```bash
git clone https://github.com/nominkhurelchuluun/mongolia-dzud-drought.git
cd mongolia-dzud-drought
conda env create -f environment.yml
conda activate mongolia-dzud
jupyter lab
```

Run notebooks 02 through 05 in any order. Each is self-contained and runs top to
bottom in a fresh kernel. Figures land in `figures/` as vector PDF.

Pip works too:

```bash
python -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
```

Only notebook 01 needs `cfgrib` and `eccodes`. If pip cannot build `eccodes` on
your platform, use `environment.yml`, or drop those lines and skip notebook 01.

## Which notebook makes what

| Notebook | Figures | Tables | Reads |
| --- | --- | --- | --- |
| `01_data_preparation.ipynb` | — | — | `data/raw/` |
| `02_climate_trends.ipynb` | 5, S1 | S1, S3 | `data/processed/` |
| `03_mortality_analysis.ipynb` | 2, 3, 4, 6, 7 | S5 | `data/processed/` |
| `04_interaction_models.ipynb` | 8, S2 | 1, S2, S4 | `data/processed/` |
| `05_spatial_analysis.ipynb` | 9 | S1, S6 | `data/processed/` |

Figure 1, the conceptual panel, was drawn in BioRender and has no code here.

| File in `figures/` | Manuscript |
| --- | --- |
| `figure_02_temporal_alignment.pdf` | Figure 2 |
| `figure_03_national_livestock_population.pdf` | Figure 3 |
| `figure_04_species_population_and_mortality.pdf` | Figure 4 |
| `figure_05_spei3_trends_1992_2024.pdf` | Figure 5 |
| `figure_06_seasonal_spei_correlations.pdf` | Figure 6 |
| `figure_07_drought_and_species_mortality.pdf` | Figure 7 |
| `figure_08_drought_cold_heatmap.pdf` | Figure 8 |
| `figure_09_drought_sensitivity_map.pdf` | Figure 9 |
| `figure_S01_spei3_trends_1950_2024.pdf` | Figure S1 |
| `figure_S02_leave_one_year_out.pdf` | Figure S2 |

## Starting from the raw archives

Only needed if you want to rebuild `data/processed/` yourself.

1. Get a Copernicus Climate Data Store account and write `~/.cdsapirc`.
2. Run `python scripts/download_era5.py` for the monthly 2 m temperature GRIB.
3. Obtain the ERA5-Drought SPEI-3 archive (Keune et al., 2025) and the two NSO
   workbooks. `data/raw/README.md` lists the filenames each one needs.
4. Run `python scripts/preflight.py`, which checks that every file is readable
   and that the column names match what notebook 01 expects.
5. Run `notebooks/01_data_preparation.ipynb`. Budget 20 to 30 minutes, most of
   it reading 913 monthly NetCDF files.

### Paths

Everything derives from `DATA_DIR` in `src/data_loading.py`, which defaults to
`./data`. Point it elsewhere with environment variables:

```bash
export MONGOLIA_DZUD_DATA=/mnt/big-disk/mongolia-data
export MONGOLIA_DZUD_FIGURES=/mnt/big-disk/figures
```

In Colab, `dl.use_colab_drive()` mounts Drive and repoints all four directories
at `/content/drive/My Drive/mongolia-dzud-drought/`. No Drive path is hardcoded
anywhere else.

## Figure conventions

The shared matplotlib defaults live in `src/data_loading.py`: the Okabe-Ito
colourblind-safe palette, `pdf.fonttype = 42` so fonts embed as TrueType rather
than Type 3, 8 pt minimum text at print size, and a 170 by 228 mm bounding box.

Several figures are drawn oversized. The canvas is `FIG_SCALE` times the final
size with every font scaled to match, which keeps hairlines and small text
clean. Pass the same factor to `save_figure(fig, name, scale=FIG_SCALE)` so the
size check runs against the printed dimensions rather than the canvas.

`save_figure()` writes PDF and nothing else. Every figure in the repository is
vector; none contains a raster image.

## Where this differs from the submitted draft

Rebuilding the analysis turned up several things that need to change in the
manuscript text.

**The SFU-weighted rate was computed wrongly.** A function called
`sfu_weighted_mean` returned `Σ(rate × SFU) / Σ SFU`, an SFU-weighted average of
the five species rates. Equation 2 is `Σ(deaths × SFU) / Σ(population × SFU)`, a
ratio of weighted totals. The two agree in quiet years and diverge sharply in
dzud years: the national mean moves from 4.13% to 4.48%, and individual
aimag-years move by up to 18.8 percentage points. Notebook 01 prints the
comparison, and cross-checks the corrected values against the population
workbook, which is a different NSO file from the one they were built from.

**Two SPEI archives were in use.** The panel model read one zip and Figures 5
and S1 read another, with different spatial aggregation. Everything now reads
the 1950–2024 archive, area-weighted by grid cell to polygon overlap. The
difference turned out to be small (mean 0.004, maximum 0.15 SPEI units), but a
point-sampled variant is kept in the panel as `SPEI_PrevSummer_point`.

**Two ERA5 temperature files were present.** Only the monthly 2 m file fed any
figure. The second GRIB and a precipitation file were loaded by a commented-out
cell and produced nothing. Both are gone.

**Winter Z-scores use the study period.** DJF temperature is standardised within
aimag over 1992–2024 rather than a long-run climatology, which matters because
Mongolian winters warmed over the ERA5 record. Notebook 04 refits the
interaction under both references; the estimate barely moves (1.283 versus
1.276), though the severe-cold count shifts from 122 to 109 aimag-years. The
Methods should say which one is used.

**The dry-summer threshold is strict.** The code uses `SPEI-3 < −0.5`. Section
2.3 of the manuscript says "at or below".

**Figure 7c annotated β as "pp/SD".** SPEI-3 is never z-scored here, and
averaging three overlapping monthly windows gives the predictor a standard
deviation below one, so "per SD" overstates the effect. The units now sit on the
axis label instead.

**Figures 7a and 9 use a different aggregate from the rest of the paper.** They
average the five species rates with equal weight, which is not Equation 2 and
was not defined in the Methods. `AGGREGATE_COL` in notebook 03 and
`SENSITIVITY_COL` in notebook 05 select the measure. Both notebooks print the
alternative next to the default so the two can be compared.

## Citation

Khurelchuluun, N., Leland, C., Davi, N. K., Andreu-Hayles, L., & Rao, M. P.
(2026). Analysis code for Climate-Associated Livestock Mortality in Mongolia
(v1.0.0) [Software]. Zenodo. https://doi.org/10.5281/zenodo.XXXXXXX

Cite the archived release rather than the repository, so the version you used
stays resolvable. `CITATION.cff` carries the same metadata in machine-readable
form.

## License

The code is under the MIT license; see `LICENSE` for the terms. The NSO
livestock records, ERA5 reanalysis and ERA5-Drought SPEI-3 come from their own
providers under their own conditions, and redistributing the derived tables here
does not extend the MIT license to them.
