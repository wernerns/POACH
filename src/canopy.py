"""Canopy layers for POACH: fetch NAIP-CHM from Earth Engine and derive
forest gap structure (the Overstory signal)."""

import os
import numpy as np
import geopandas as gpd
from shapely.geometry import box
from scipy.ndimage import uniform_filter


def fetch_canopy(bbox, out_path, scale=0.9, crs=5070, ee_project=None):
    """Download NAIP-CHM canopy height for a lon/lat bbox to out_path (GeoTIFF).
    Skips the download if the file already exists. Returns out_path.
    Requires an initialized Earth Engine session (or pass ee_project to init)."""
    import ee
    import geemap

    if ee_project is not None:
        ee.Initialize(project=ee_project)

    if os.path.exists(out_path):
        print(f"Canopy already on disk: {out_path}")
        return out_path

    aoi = ee.Geometry.Rectangle(list(bbox))
    chm = (
        ee.ImageCollection("projects/naip-chm/assets/conus-structure-model")
        .filterBounds(aoi)
        .mosaic()
        .clip(aoi)
        .divide(100)                    # centimeters -> meters
        .rename("canopy_height_m")
        .toFloat()
    )

    os.makedirs(os.path.dirname(out_path), exist_ok=True)
    try:
        geemap.ee_export_image(
            chm, filename=out_path, scale=scale, region=aoi,
            crs=f"EPSG:{crs}", file_per_band=False,
        )
    except Exception as e:
        raise RuntimeError(f"Canopy export failed: {e}") from e

    if not os.path.exists(out_path):
        raise RuntimeError(
            "Canopy export produced no file — likely over the size limit. "
            "Reduce the area or coarsen `scale`."
        )
    print(f"Downloaded canopy: {out_path}")
    return out_path


def load_canopy(path):
    """Open a canopy GeoTIFF and scrub -inf / nodata to NaN."""
    import rioxarray
    da = rioxarray.open_rasterio(path).squeeze()
    return da.where(np.isfinite(da))


def _local_std(da, size):
    """NaN-aware moving-window standard deviation (gap structure)."""
    arr = da.values.astype("float64")
    mask = np.isfinite(arr)
    arr0 = np.where(mask, arr, 0.0)
    win = size * size
    s1 = uniform_filter(arr0, size=size, mode="nearest") * win
    s2 = uniform_filter(arr0 ** 2, size=size, mode="nearest") * win
    cnt = uniform_filter(mask.astype("float64"), size=size, mode="nearest") * win
    with np.errstate(invalid="ignore", divide="ignore"):
        mean = s1 / cnt
        var = s2 / cnt - mean ** 2
    var = np.clip(var, 0, None)
    std = np.sqrt(var)
    std[cnt < 0.5 * win] = np.nan
    return da.copy(data=std)


def _window_fraction(da, size, condition):
    """Fraction of each window satisfying a boolean condition array, NaN-aware."""
    mask = np.isfinite(da.values)
    win = size * size
    cond_cnt = uniform_filter((condition & mask).astype("float64"), size=size, mode="nearest") * win
    valid_cnt = uniform_filter(mask.astype("float64"), size=size, mode="nearest") * win
    with np.errstate(invalid="ignore", divide="ignore"):
        frac = cond_cnt / valid_cnt
    frac[valid_cnt < 0.5 * win] = np.nan
    return da.copy(data=frac)


def gap_structure(canopy, size=15, min_forest_height=5.0, ground_height=2.0):
    """Edge-suppressed canopy gap structure -- the Overstory signal.
    High where forest is present AND height varies (thinned glades),
    low on uniform forest, open ground, and forest edges."""
    arr = canopy.values
    gap = _local_std(canopy, size)
    forest = _window_fraction(canopy, size, arr >= min_forest_height)
    near_ground = _window_fraction(canopy, size, arr < ground_height)
    return gap * forest * (1 - near_ground)


def score_overstory(gap_glade, crs=5070):
    """Normalize gap structure to 0-1 (divide by 95th percentile, clip)."""
    p95 = float(np.nanpercentile(gap_glade.values, 95))
    score = (gap_glade / p95).clip(0, 1)
    return score.rio.write_crs(crs)