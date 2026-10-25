"""The words a spec file may use: sizes, key spellings, motif names.

Everything here is data. Adding a ratio, or a second spelling of a key, is
an edit to this file and to nothing else -- which is the whole reason it
sits apart from the code that reads it.
"""

from __future__ import annotations

# Pixel sizes for the ratios people actually ask for. 16x9 covers Open Graph
# and most blog headers, 4x3 the Google Discover slot, 1x1 the social avatar
# crop. A size written as WxH in pixels is accepted too.
PRESETS: dict[str, tuple[int, int]] = {
    "16x9": (1600, 900),
    "4x3": (1600, 1200),
    "1x1": (1200, 1200),
    "3x2": (1600, 1067),
    "2x1": (1600, 800),
    "4x5": (1080, 1350),
    "9x16": (1080, 1920),
}

DEFAULT_FORMATS = ("16x9", "4x3", "1x1")

ALIASES = {
    "titre": "title",
    "sous-titre": "subtitle",
    "sous_titre": "subtitle",
    "soustitre": "subtitle",
    "chapeau": "eyebrow",
    "surtitre": "eyebrow",
    "pied": "footer",
    "fond": "background",
    "texte": "foreground",
    "police": "font",
    "nom": "name",
    "sortie": "out",
    "graine": "seed",
    "point": "dot",
    "lignes-max": "max_lines",
    "lignes_max": "max_lines",
}

FIELDS = {
    "title",
    "subtitle",
    "eyebrow",
    "footer",
    "background",
    "foreground",
    "accent",
    "font",
    "motif",
    "formats",
    "name",
    "out",
    "seed",
    "dot",
    "max_lines",
}

MOTIF_ALIASES = {
    "particules": "particles",
    "particles": "particles",
    "grille": "grid",
    "grid": "grid",
    "aucun": "none",
    "none": "none",
}
