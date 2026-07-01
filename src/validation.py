"""Validate POACH suitability against mapped ground-truth routes."""

import numpy as np
import geopandas as gpd
import matplotlib.pyplot as plt


def load_routes(path, crs=5070):
    """Load a route GeoJSON/shapefile and reproject to the project CRS."""
    return gpd.read_file(path).to_crs(crs)


def sample_along_routes(score, routes, buffer=15):
    """Mean suitability score under the routes.
    Buffers the route lines by `buffer` meters, then averages the score
    pixels that fall within. Returns the mean (ignoring NaN)."""
    corridor = routes.buffer(buffer).union_all()
    clipped = score.rio.clip([corridor], routes.crs, drop=True)
    vals = clipped.values[np.isfinite(clipped.values)]
    return float(vals.mean()) if vals.size else float("nan")


def plot_overlay(score, routes, trail_xy=None, title="POACH suitability + routes",
                 cmap="RdYlGn", robust=True, buffer_view=300):
    """Overlay routes on a score surface, framed on the routes with a margin."""
    minx, miny, maxx, maxy = routes.total_bounds
    fig, ax = plt.subplots(figsize=(11, 9))
    score.plot(ax=ax, cmap=cmap, robust=robust,
               cbar_kwargs={"label": "Suitability (relative)"})
    routes.plot(ax=ax, color="white", linewidth=3.5)
    routes.plot(ax=ax, color="black", linewidth=1.5)
    if trail_xy is not None:
        ax.plot(*trail_xy, marker="^", color="red", markersize=13,
                markeredgecolor="white")
    ax.set_xlim(minx - buffer_view, maxx + buffer_view)
    ax.set_ylim(miny - buffer_view, maxy + buffer_view)
    ax.set_title(title)
    ax.set_aspect("equal")
    return fig, ax