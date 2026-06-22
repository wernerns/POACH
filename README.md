# POACH

**P**itch · **O**verstory · **A**spect · **C**ontinuity · **H**azard

A terrain-analysis tool for identifying potential backcountry glade skiing in the
US Northeast. POACH combines elevation-derived terrain metrics with forest-canopy
structure to score the landscape for gladed skiability, then validates those
predictions against real, mapped glade zones.

> **Status:** Early development — proof of concept in progress.

## The idea

Backcountry skiers and glade-cutting groups scout skiable tree terrain by eye,
looking for the same handful of features: the right steepness, a slope that holds
snow, and a forest open enough to ski. POACH automates that scouting by scoring
each factor from open geospatial data and combining them into a single
suitability surface.

The factors behind the name:

| Factor | What it captures | Source |
| --- | --- | --- |
| **Pitch** | Slope steepness — too flat won't ski, too steep isn't a glade | USGS 3DEP DEM |
| **Overstory** | Forest canopy height/density — a mature, open understory skis best | Canopy height model |
| **Aspect** | Slope direction — drives snow retention and quality | USGS 3DEP DEM |
| **Continuity** | Whether skiable terrain connects into a coherent line | Derived |
| **Hazard** | Terrain risk to avoid: cliffs, traps (*planned*) | Derived (future) |

## Validation

POACH is tested against glade zones mapped by the
[Granite Backcountry Alliance](https://granitebackcountryalliance.org/) (GBA).
The model is built on the surrounding terrain, then GBA's published routes are
overlaid to check whether high-suitability areas line up with real glades.

- **First test — Maple Villa:** a fully below-treeline hardwood glade, for a clean
  validation signal.
- **Headline test — Baldface:** a mixed alpine/glade zone on the NH/Maine line — a
  harder case where the model must handle the transition from forest to open
  alpine terrain.

## Data sources

- **USGS 3DEP** elevation via `py3dep` — slope, aspect, elevation
- **Canopy height / cover** product — forest structure
- **GBA glade maps** — validation ground truth

## Tech stack

Python (geopandas, rasterio, rioxarray, xarray, py3dep, numpy, matplotlib),
JupyterLab for exploration, QGIS for visual checks. All analysis in **EPSG:5070**
(CONUS Albers, equal-area).

## Setup

```bash
conda env create -f environment.yml
conda activate geo
```

## Repository structure

```
POACH/
├── data/
│   ├── raw/         # downloaded source data (not tracked)
│   ├── processed/   # derived layers (not tracked)
│   └── validation/  # GBA ground-truth routes (tracked)
├── notebooks/       # exploratory analysis
├── src/             # reusable analysis code
├── outputs/         # maps and figures
├── environment.yml
└── README.md
```

## Roadmap

- [ ] Pull and visualize a 3DEP DEM for a test zone
- [ ] Derive slope (Pitch) and aspect layers
- [ ] Integrate the canopy (Overstory) layer
- [ ] Combine factors into a weighted suitability surface
- [ ] Overlay and validate against GBA's Maple Villa routes
- [ ] Generalize to Baldface
- [ ] Add Continuity and Hazard layers

## Disclaimer

POACH is an experimental terrain-suitability model, **not a safety tool**. It does
not assess avalanche danger, and a high score is not a recommendation to ski
anywhere. Backcountry travel carries serious risk — always consult current
avalanche forecasts, check conditions, and make your own informed decisions.

## License

MIT — see [LICENSE](LICENSE).