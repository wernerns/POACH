"""Combine POACH's scored layers into a single glade-suitability surface."""


def combine(pitch_score, aspect_score, overstory_score, aspect_weight=0.3):
    """Combine scored layers (all on the same grid) into glade suitability (0-1).

    Pitch and Overstory act as GATES -- a glade needs skiable slope AND
    forested gap structure, so either near zero kills the score. Aspect
    MODULATES snow quality within that, its strength set by aspect_weight
    (0 = ignore aspect, 1 = full multiply).
    """
    aspect_factor = (1 - aspect_weight) + aspect_weight * aspect_score
    return pitch_score * overstory_score * aspect_factor


def align_to(reference, *layers):
    """Reproject/resample each layer onto the reference grid (CRS, resolution,
    extent) so they can be combined pixel-for-pixel. Returns a list."""
    return [layer.rio.reproject_match(reference) for layer in layers]