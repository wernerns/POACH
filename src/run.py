"""Run the full POACH pipeline for a single zone."""

import numpy as np
import geopandas as gpd
from shapely.geometry import box
import py3dep
import xrspatial

from src.canopy import fetch_canopy, load_canopy, gap_structure, score_overstory
from src.terrain import score_pitch, score_aspect
from src.model import combine, align_to
from src.validation import load_routes, sample_along_routes


def run_zone(zone, scale=1.0, window=15, aspect_weight=0.3):
    """Run POACH end-to-end for a zone dict. Returns a results dict."""
    routes   = load_routes(zone["routes"])
    descents = load_routes(zone["descents"])

    # Canopy over the routes (buffered), fetched if not already on disk.
    route_bbox = gpd.GeoSeries([box(*routes.buffer(250).total_bounds)], crs=5070) \
                    .to_crs(4326).total_bounds
    fetch_canopy(route_bbox, zone["canopy_file"], scale=scale, crs=5070)
    canopy = load_canopy(zone["canopy_file"])
    overstory = score_overstory(gap_structure(canopy, size=window))

    # Terrain on the canopy grid.
    cb = gpd.GeoSeries([box(*canopy.rio.bounds())], crs=canopy.rio.crs) \
            .to_crs(4326).total_bounds
    dem = py3dep.get_dem(tuple(cb), resolution=1).rio.reproject(5070)
    pitch  = score_pitch(xrspatial.slope(dem)).rio.write_crs(5070)
    aspect = score_aspect(xrspatial.aspect(dem)).rio.write_crs(5070)
    pitch, aspect = align_to(canopy, pitch, aspect)

    poach = combine(pitch, aspect, overstory, aspect_weight=aspect_weight)

    # Validation stats.
    scene = poach.values[np.isfinite(poach.values)]
    stats = {
        "scene_mean":   float(scene.mean()),
        "route_mean":   sample_along_routes(poach, routes, buffer=15),
        "descent_mean": sample_along_routes(poach, descents, buffer=15),
    }
    return {"poach": poach, "canopy": canopy, "routes": routes,
            "descents": descents, "stats": stats}