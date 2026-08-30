"""Shared paths, constants, loaders and plotting defaults.

Two families of functions live here.

``build_*`` functions read the large raw archives (ERA5 GRIB, SPEI-3 NetCDF zip,
NSO Excel workbooks, aimag GeoJSON). Only ``notebooks/01_data_preparation.ipynb``
calls them, and only that notebook needs ``data/raw`` to be populated.

``load_*`` functions read the small derived CSVs in ``data/processed``, which are
committed to the repository. Notebooks 02-05 use these exclusively and therefore
run without any raw file present.

Set the ``MONGOLIA_DZUD_DATA`` environment variable, or call
``use_colab_drive()``, to move ``DATA_DIR`` away from the repository default.
"""

from __future__ import annotations

import os
import re
import zipfile
from pathlib import Path

import numpy as np
import pandas as pd

REPO_ROOT = Path(__file__).resolve().parents[1]

DATA_DIR = Path(os.environ.get("MONGOLIA_DZUD_DATA", REPO_ROOT / "data"))
RAW_DIR = DATA_DIR / "raw"
PROCESSED_DIR = DATA_DIR / "processed"
FIG_DIR = Path(os.environ.get("MONGOLIA_DZUD_FIGURES", REPO_ROOT / "figures"))
SCRATCH_DIR = Path(os.environ.get("MONGOLIA_DZUD_SCRATCH", REPO_ROOT / ".scratch"))

RAW_FILES = {
    "mortality": "mongolia_mortality_rates.xlsx",
    "population": "types_livestock_aimag.xlsm",
    "aimags": "mongolia.prefectures.geojson",
    "t2m_grib": "era5_monthly_t2m_mongolia_1950_2024.grib",
    "spei_zip": "era5_drought_spei3_mongolia_1950_2024.zip",
}

SPECIES_COLS = ["Mort_hor", "Mort_cat", "Mort_cam", "Mort_sheep", "Mort_goat"]

SPECIES_LABELS = {
    "Mort_hor": "Horse",
    "Mort_cat": "Cattle",
    "Mort_cam": "Camel",
    "Mort_sheep": "Sheep",
    "Mort_goat": "Goat",
}

SPECIES_MAP = {v: k for k, v in SPECIES_LABELS.items()}

SFU_WEIGHTS = {
    "Mort_hor": 7.0,
    "Mort_cat": 6.0,
    "Mort_cam": 5.0,
    "Mort_sheep": 1.0,
    "Mort_goat": 0.9,
}

SFU_BY_NAME = {SPECIES_LABELS[k]: v for k, v in SFU_WEIGHTS.items()}

SFU_BY_SPECIES = {k.lower(): v for k, v in SFU_BY_NAME.items()}

RENAME_GEO = {"GoviAltai": "Govi-Altai", "uvs": "Uvs"}

NON_AIMAG_UNITS = ["Baganuur", "Bagakhangai", "Ulaanbaatar"]

MORT_START, MORT_END = 1992, 2024
SPEI_START, SPEI_END = 1950, 2024

DRY_THRESHOLD = -0.5
SEVERE_DROUGHT_THRESHOLD = -1.0
COLD_THRESHOLD = 0.0
SEVERE_COLD_THRESHOLD = -1.0

SPEI_EDGES = [-np.inf, SEVERE_DROUGHT_THRESHOLD, DRY_THRESHOLD, np.inf]
TEMP_EDGES = [-np.inf, SEVERE_COLD_THRESHOLD, COLD_THRESHOLD, np.inf]

ZSCORE_REFERENCE = (MORT_START, MORT_END)

LAT_MIN, LAT_MAX = 41.5, 52.0
LON_MIN, LON_MAX = 87.5, 119.9

JJA_MONTHS = (6, 7, 8)

SEASON_MAP = {
    12: "DJF", 1: "DJF", 2: "DJF",
    3: "MAM", 4: "MAM", 5: "MAM",
    6: "JJA", 7: "JJA", 8: "JJA",
    9: "SON", 10: "SON", 11: "SON",
}

EQUAL_AREA_CRS = "EPSG:6933"

OKABE_ITO = {
    "orange": "#E69F00",
    "sky_blue": "#56B4E9",
    "bluish_green": "#009E73",
    "yellow": "#F0E442",
    "blue": "#0072B2",
    "vermillion": "#D55E00",
    "reddish_purple": "#CC79A7",
    "black": "#000000",
    "brown": "#8C6D31",
}

SPECIES_COLORS = {
    "Mort_cat": OKABE_ITO["vermillion"],
    "Mort_hor": OKABE_ITO["blue"],
    "Mort_goat": OKABE_ITO["reddish_purple"],
    "Mort_sheep": OKABE_ITO["bluish_green"],
    "Mort_cam": OKABE_ITO["brown"],
}

DRY_COLOR = OKABE_ITO["vermillion"]
NORMAL_COLOR = OKABE_ITO["sky_blue"]
WET_COLOR = OKABE_ITO["blue"]

MM_PER_INCH = 25.4
AGU_MAX_WIDTH_MM = 170.0
AGU_MAX_HEIGHT_MM = 228.0
AGU_MIN_FONT_PT = 8.0


def mm_to_in(value_mm):
    """Convert millimetres to inches."""
    return value_mm / MM_PER_INCH


AGU_MAX_WIDTH_IN = mm_to_in(AGU_MAX_WIDTH_MM)
AGU_MAX_HEIGHT_IN = mm_to_in(AGU_MAX_HEIGHT_MM)


def use_colab_drive(subdir="mongolia-dzud-drought"):
    """Mount Google Drive and repoint DATA_DIR and FIG_DIR at it.

    Returns the resolved data directory. Safe to call outside Colab, where it
    raises ImportError and leaves the module-level paths untouched.
    """
    global DATA_DIR, RAW_DIR, PROCESSED_DIR, FIG_DIR, SCRATCH_DIR
    from google.colab import drive

    drive.mount("/content/drive", force_remount=False)
    root = Path("/content/drive/My Drive") / subdir
    DATA_DIR = root / "data"
    RAW_DIR = DATA_DIR / "raw"
    PROCESSED_DIR = DATA_DIR / "processed"
    FIG_DIR = root / "figures"
    SCRATCH_DIR = Path("/content/scratch")
    for path in (RAW_DIR, PROCESSED_DIR, FIG_DIR, SCRATCH_DIR):
        path.mkdir(parents=True, exist_ok=True)
    return DATA_DIR


def raw_path(key):
    """Return the path to a raw input file and fail loudly if it is absent."""
    path = RAW_DIR / RAW_FILES[key]
    if not path.exists():
        raise FileNotFoundError(
            f"{path} not found. See data/raw/README.md for provenance and "
            "download instructions. Notebooks 02-05 do not need this file."
        )
    return path


def processed_path(name):
    """Return the path to a derived CSV in data/processed."""
    return PROCESSED_DIR / name


def set_plot_style():
    """Apply the manuscript-wide matplotlib defaults."""
    import matplotlib as mpl

    mpl.rcParams.update({
        "font.family": "sans-serif",
        "font.sans-serif": ["Arial", "Helvetica", "Liberation Sans", "DejaVu Sans"],
        "mathtext.fontset": "dejavusans",
        "font.size": AGU_MIN_FONT_PT,
        "axes.labelsize": AGU_MIN_FONT_PT + 1,
        "axes.titlesize": AGU_MIN_FONT_PT + 1,
        "xtick.labelsize": AGU_MIN_FONT_PT,
        "ytick.labelsize": AGU_MIN_FONT_PT,
        "legend.fontsize": AGU_MIN_FONT_PT,
        "legend.title_fontsize": AGU_MIN_FONT_PT,
        "axes.linewidth": 0.6,
        "axes.spines.top": False,
        "axes.spines.right": False,
        "axes.grid": True,
        "axes.axisbelow": True,
        "grid.alpha": 0.30,
        "grid.linestyle": "--",
        "grid.linewidth": 0.5,
        "lines.linewidth": 1.0,
        "xtick.direction": "out",
        "ytick.direction": "out",
        "figure.dpi": 130,
        "figure.facecolor": "white",
        "savefig.facecolor": "white",
        "savefig.transparent": False,
        "pdf.fonttype": 42,
        "ps.fonttype": 42,
    })


def figure_size(width_fraction=1.0, height_mm=None, aspect=0.62):
    """Return a (width, height) tuple in inches within the AGU width limit."""
    width_in = AGU_MAX_WIDTH_IN * float(width_fraction)
    height_in = mm_to_in(height_mm) if height_mm is not None else width_in * aspect
    return (width_in, min(height_in, AGU_MAX_HEIGHT_IN))


def save_figure(fig, name, subdir=None, scale=1.0):
    """Write a figure to FIG_DIR as vector PDF and return the path.

    PDF only. No raster output is produced anywhere in this repository.

    ``scale`` is the supersampling factor used when building the figure. Several
    manuscript figures are drawn at ``scale`` times their final size with fonts
    scaled to match, so the AGU width and height checks divide by it.
    """
    target_dir = FIG_DIR if subdir is None else FIG_DIR / subdir
    target_dir.mkdir(parents=True, exist_ok=True)
    path = target_dir / f"{name}.pdf"
    fig.savefig(path, format="pdf", bbox_inches="tight", facecolor="white")
    width_mm, height_mm = [v * MM_PER_INCH / scale for v in fig.get_size_inches()]
    if width_mm > AGU_MAX_WIDTH_MM + 0.5:
        print(f"WARNING {name}: print width {width_mm:.1f} mm exceeds the AGU "
              f"limit of {AGU_MAX_WIDTH_MM:.0f} mm")
    if height_mm > AGU_MAX_HEIGHT_MM + 0.5:
        print(f"WARNING {name}: print height {height_mm:.1f} mm exceeds the AGU "
              f"limit of {AGU_MAX_HEIGHT_MM:.0f} mm")
    print(f"saved {path}  ({width_mm:.0f} x {height_mm:.0f} mm at print size)")
    return path


SMALL_AIMAG_QUANTILE = 0.25

WRAPPED_NAMES = {
    "Govi-Altai": "Govi-\nAltai",
    "Bayankhongor": "Bayan-\nkhongor",
    "Uvurkhangai": "Uvur-\nkhangai",
    "Darkhan-Uul": "Darkhan-Uul",
    "Govisumber": "Govisumber",
}

LEADER_DIRECTIONS = {
    "Selenge": (0.35, 1.0),
    "Darkhan-Uul": (1.0, 0.45),
    "Orkhon": (-0.55, 1.0),
    "Govisumber": (0.55, -1.0),
    "Bulgan": (-0.30, 1.0),
    "Ulaanbaatar": (-1.0, -0.55),
}


def draw_aimag_labels(ax, frame, fontsize, scale=1.0, leader_length=52,
                      small_quantile=SMALL_AIMAG_QUANTILE, offsets=None,
                      directions=None, leader_color="#404040"):
    """Label aimag polygons, using leader lines for the small crowded ones.

    Polygons whose area falls below ``small_quantile`` of the distribution get
    their label placed outside the map with a thin line pointing back, because
    an 8 pt label does not fit inside them. Everything else is labelled in
    place. Leader direction is radial from the map centroid by default and can
    be overridden per aimag through ``directions``.

    ``frame`` is a GeoDataFrame with an ``Aimag`` column and polygon geometry.
    ``offsets`` nudges in-place labels, in points.
    """
    import matplotlib.patheffects as pe

    offsets = {**(offsets or {})}
    directions = {**LEADER_DIRECTIONS, **(directions or {})}

    areas = frame.geometry.area
    threshold = areas.quantile(small_quantile)
    centre_x = frame.geometry.union_all().centroid.x
    centre_y = frame.geometry.union_all().centroid.y

    labels = []
    for row, area in zip(frame.itertuples(), areas):
        point = row.geometry.representative_point()
        text = WRAPPED_NAMES.get(row.Aimag, row.Aimag)

        if area <= threshold:
            if row.Aimag in directions:
                dx, dy = directions[row.Aimag]
            else:
                dx = point.x - centre_x
                dy = point.y - centre_y
                norm = max((dx ** 2 + dy ** 2) ** 0.5, 1e-9)
                dx, dy = dx / norm, dy / norm
            label = ax.annotate(
                text, xy=(point.x, point.y),
                xytext=(dx * leader_length, dy * leader_length),
                textcoords="offset points", ha="center", va="center",
                fontsize=fontsize, fontweight="bold", color="black",
                linespacing=0.88, annotation_clip=False, zorder=6,
                arrowprops={"arrowstyle": "-", "color": leader_color,
                            "linewidth": 0.35 * scale,
                            "shrinkA": 1.5 * scale, "shrinkB": 1.5 * scale})
        else:
            label = ax.annotate(
                text, xy=(point.x, point.y),
                xytext=offsets.get(row.Aimag, (0, 0)),
                textcoords="offset points", ha="center", va="center",
                fontsize=fontsize, fontweight="bold", color="black",
                linespacing=0.88, annotation_clip=False, zorder=5)

        label.set_path_effects([pe.withStroke(linewidth=1.6 * scale,
                                              foreground="white")])
        labels.append(label)

    return labels


def parse_yyyymm(filepath):
    """Extract (year, month) from an ERA5-Drought SPEI-3 filename."""
    match = re.search(r"_(\d{6})\.", Path(filepath).name)
    if match is None:
        return (None, None)
    stamp = match.group(1)
    return (int(stamp[:4]), int(stamp[4:]))


def extract_spei_archive(destination=None):
    """Unzip the SPEI-3 archive once and return the sorted NetCDF file list."""
    destination = Path(destination or SCRATCH_DIR / "spei3")
    destination.mkdir(parents=True, exist_ok=True)
    if not any(destination.glob("*.nc")):
        with zipfile.ZipFile(raw_path("spei_zip"), "r") as archive:
            archive.extractall(destination)
    files = sorted(str(p) for p in destination.glob("*.nc") if "SPEI3" in p.name)
    if not files:
        raise FileNotFoundError(f"No SPEI3 NetCDF files found under {destination}")
    return files


def netcdf_engine():
    """Return the first available xarray engine that can read NetCDF4 files.

    Colab ships h5netcdf but not always netCDF4, so the engine is detected at
    runtime rather than hardcoded.
    """
    import xarray as xr

    available = xr.backends.list_engines()
    for candidate in ("netcdf4", "h5netcdf", "scipy"):
        if candidate in available:
            return candidate
    raise ImportError(
        "No NetCDF engine available. Install one with "
        "`pip install netCDF4` or `pip install h5netcdf`. "
        f"xarray reports: {sorted(available)}")


def read_spei_months(files, months=None):
    """Read SPEI-3 NetCDF files into a tidy latitude/longitude/year/month frame."""
    import xarray as xr

    engine = netcdf_engine()
    records = []
    for filepath in files:
        year, month = parse_yyyymm(filepath)
        if year is None:
            continue
        if months is not None and month not in months:
            continue
        with xr.open_dataset(filepath, engine=engine) as dataset:
            name = next((v for v in dataset.data_vars if "spei" in v.lower()),
                        list(dataset.data_vars)[0])
            frame = (dataset[name].to_dataframe().reset_index()
                     .rename(columns={name: "SPEI"}))
        lat_col = [c for c in frame.columns if "lat" in c.lower()][0]
        lon_col = [c for c in frame.columns if "lon" in c.lower()][0]
        frame = frame.rename(columns={lat_col: "latitude", lon_col: "longitude"})
        frame["Year"] = year
        frame["Month"] = month
        records.append(frame[["latitude", "longitude", "Year", "Month", "SPEI"]]
                       .dropna(subset=["SPEI"]))
    if not records:
        raise ValueError("No SPEI records were read from the supplied files.")
    return pd.concat(records, ignore_index=True)


def load_aimag_boundaries(dissolve=True):
    """Load aimag polygons, harmonise names and drop the non-aimag city units."""
    import geopandas as gpd

    source = PROCESSED_DIR / "aimag_boundaries.geojson"
    if not source.exists():
        source = raw_path("aimags")
    frame = gpd.read_file(source)
    name_col = "Aimag" if "Aimag" in frame.columns else "prefecture"
    frame["Aimag"] = frame[name_col].replace(RENAME_GEO).astype(str).str.strip()
    frame = frame[~frame["Aimag"].isin(NON_AIMAG_UNITS)]
    frame = frame[["Aimag", "geometry"]]
    if dissolve:
        frame = frame.dissolve(by="Aimag", as_index=False)
    return frame.reset_index(drop=True)


def build_cell_area_weights(latitudes, longitudes, aimags):
    """Area of overlap between each SPEI grid cell and each aimag polygon."""
    import geopandas as gpd
    from shapely.geometry import box

    latitudes = np.asarray(latitudes, dtype=float)
    longitudes = np.asarray(longitudes, dtype=float)
    res_lat = abs(latitudes[1] - latitudes[0])
    res_lon = abs(longitudes[1] - longitudes[0])

    cells = gpd.GeoDataFrame(
        [{"latitude": la, "longitude": lo,
          "geometry": box(lo - res_lon / 2, la - res_lat / 2,
                          lo + res_lon / 2, la + res_lat / 2)}
         for la in latitudes for lo in longitudes],
        crs="EPSG:4326")

    overlay = gpd.overlay(cells.to_crs(EQUAL_AREA_CRS),
                          aimags.to_crs(EQUAL_AREA_CRS), how="intersection")
    overlay["weight"] = overlay.geometry.area
    return overlay[["latitude", "longitude", "Aimag", "weight"]].copy()


def area_weighted_mean(cells, weights, group_cols):
    """Area-weighted mean of SPEI over grid cells, grouped by group_cols."""
    merged = weights.merge(cells, on=["latitude", "longitude"], how="inner")
    if merged.empty:
        raise ValueError("No grid cells matched between weights and SPEI values.")
    merged["wx"] = merged["SPEI"] * merged["weight"]
    return (merged.groupby(group_cols, as_index=False)
            .agg(num=("wx", "sum"), den=("weight", "sum"))
            .assign(SPEI=lambda d: d["num"] / d["den"])
            .drop(columns=["num", "den"]))


def load_spei(kind="aimag_jja"):
    """Load a derived SPEI-3 table from data/processed.

    kind
        ``aimag_jja``      area-weighted JJA mean SPEI-3 per aimag-year, 1950-2024
        ``national_jja``   area-weighted national JJA mean SPEI-3, 1950-2024
        ``aimag_seasonal`` area-weighted seasonal mean SPEI-3 per aimag-year
        ``aimag_trends``   OLS drying rates per aimag for both analysis periods
    """
    names = {
        "aimag_jja": "spei3_jja_aimag_1950_2024.csv",
        "national_jja": "spei3_jja_national_1950_2024.csv",
        "aimag_seasonal": "spei3_seasonal_aimag_1950_2024.csv",
        "aimag_trends": "spei3_jja_aimag_trends.csv",
    }
    if kind not in names:
        raise KeyError(f"kind must be one of {sorted(names)}")
    return pd.read_csv(processed_path(names[kind]))


def load_temperature(kind="djf_aimag"):
    """Load derived ERA5 temperature tables from data/processed.

    kind
        ``djf_aimag``    DJF mean temperature and Z-scores per aimag-year
        ``seasonal``     all four seasonal means per aimag-year
    """
    names = {
        "djf_aimag": "era5_djf_temperature_aimag.csv",
        "seasonal": "era5_seasonal_temperature_aimag.csv",
    }
    if kind not in names:
        raise KeyError(f"kind must be one of {sorted(names)}")
    return pd.read_csv(processed_path(names[kind]))


def load_mortality_panel(zscore_reference="study"):
    """Load the analysis panel: 21 aimags by 33 years, n = 693.

    Columns include the five species mortality rates, the unweighted species mean
    ``All``, the Equation (2) SFU-weighted rate ``All_SFU``, previous-summer
    SPEI-3, DJF temperature and both Z-score variants.

    zscore_reference
        ``study``    ``Temp_Winter_Z`` standardised over 1992-2024 (published)
        ``climate``  ``Temp_Winter_Z`` standardised over 1950-2024
    """
    panel = pd.read_csv(processed_path("mortality_panel.csv"))
    if zscore_reference == "study":
        panel["Temp_Winter_Z"] = panel["Temp_Winter_Z_study"]
    elif zscore_reference == "climate":
        panel["Temp_Winter_Z"] = panel["Temp_Winter_Z_climate"]
    else:
        raise KeyError("zscore_reference must be 'study' or 'climate'")
    panel["Drought_PrevSummer"] = panel["SPEI_PrevSummer"] < DRY_THRESHOLD
    panel["Severe_Drought"] = panel["SPEI_PrevSummer"] < SEVERE_DROUGHT_THRESHOLD
    panel["Severe_Cold"] = panel["Temp_Winter_Z"] < SEVERE_COLD_THRESHOLD
    return panel


def load_population(kind="national_species"):
    """Load derived NSO livestock population tables.

    kind
        ``national_species``  national head counts by species and year
        ``national_total``    reported national total and year-over-year change
        ``aimag_species``     aimag-level head counts by species and year
    """
    names = {
        "national_species": "livestock_population_national_species.csv",
        "national_total": "livestock_population_national_total.csv",
        "aimag_species": "livestock_population_aimag_species.csv",
    }
    if kind not in names:
        raise KeyError(f"kind must be one of {sorted(names)}")
    return pd.read_csv(processed_path(names[kind]))


def load_losses(kind="national_annual"):
    """Load derived absolute-loss tables in millions of head.

    kind
        ``national_annual``  national deaths by species and year
    """
    names = {"national_annual": "livestock_losses_national_annual.csv"}
    if kind not in names:
        raise KeyError(f"kind must be one of {sorted(names)}")
    return pd.read_csv(processed_path(names[kind]))


def sfu_weighted_rate(deaths_by_species, population_by_species):
    """Equation (2): sum(deaths x SFU) / sum(prior population x SFU).

    Both arguments are mappings from species label to a value in the same units.
    This is a ratio of SFU-weighted totals, not an SFU-weighted average of the
    five species rates.
    """
    numerator = sum(deaths_by_species[s] * SFU_BY_NAME[s] for s in SFU_BY_NAME
                    if s in deaths_by_species)
    denominator = sum(population_by_species[s] * SFU_BY_NAME[s] for s in SFU_BY_NAME
                      if s in population_by_species)
    return numerator / denominator if denominator else np.nan


def describe_paths():
    """Print the resolved directories, for the top of every notebook."""
    print(f"DATA_DIR      {DATA_DIR}")
    print(f"RAW_DIR       {RAW_DIR}")
    print(f"PROCESSED_DIR {PROCESSED_DIR}")
    print(f"FIG_DIR       {FIG_DIR}")
