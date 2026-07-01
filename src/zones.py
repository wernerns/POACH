"""Zone definitions for POACH — each zone is fully described by a small dict."""

ZONES = {
    "maple_villa": {
        "name": "Maple Villa",
        "trail_lat": 44.101448,
        "trail_lon": -71.143607,
        "routes": "../data/validation/maple_villa_route.geojson",
        "descents": "../data/validation/maple_villa_descents.geojson",
        "canopy_file": "../data/raw/maple_villa_canopy_1m_full.tif",
    },
    "black_and_white_sub": {
        "name": "Black and White Glades (sub-area)",
        "trail_lat": 44.550275,
        "trail_lon": -70.683531,
        "routes": "../data/validation/black_and_white_route_sub.geojson",
        "descents": "../data/validation/black_and_white_descents_sub.geojson",
        "canopy_file": "../data/raw/black_and_white_sub_canopy_1m.tif",
    },
}