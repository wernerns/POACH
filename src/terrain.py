"""Terrain layers for POACH: elevation, slope (Pitch), and aspect."""

import py3dep
import xrspatial
from pyproj import Transformer


def get_dem(bbox, resolution=10, crs=5070):
    """Fetch a 3DEP DEM for a lon/lat bbox (west, south, east, north),
    reprojected to the project CRS (default EPSG:5070)."""
    dem = py3dep.get_dem(tuple(bbox), resolution=resolution)
    return dem.rio.reproject(crs)


def score_pitch(slope_deg):
    """Score slope steepness 0-1 for skiability.
    Ramps up from ~12 degrees and stays high into steep terrain;
    steepness *danger* is handled separately in a Hazard layer."""
    import xarray as xr
    s = slope_deg
    return xr.where(
        s < 12, 0.0,
        xr.where(s < 25, (s - 12) / 13, 1.0),
    )


def score_aspect(aspect_deg, optimal_deg=45):
    """Score slope aspect 0-1 for snow retention (peaks at NE = 45 by default).
    Uses a cosine so the 0/360 wraparound is handled automatically.
    Flat cells (aspect < 0) get a neutral 0.5."""
    import numpy as np
    import xarray as xr
    angle_diff = np.deg2rad(aspect_deg - optimal_deg)
    score = (1 + np.cos(angle_diff)) / 2
    return xr.where(aspect_deg < 0, 0.5, score)


def terrain_layers(bbox, resolution=10, crs=5070):
    """Convenience: fetch DEM and return (dem, slope, aspect, pitch_score, aspect_score),
    all on the same grid, with CRS stamped."""
    dem = get_dem(bbox, resolution=resolution, crs=crs)
    slope = xrspatial.slope(dem)
    aspect = xrspatial.aspect(dem)
    pitch_score = score_pitch(slope).rio.write_crs(crs)
    aspect_score = score_aspect(aspect).rio.write_crs(crs)
    return dem, slope, aspect, pitch_score, aspect_score