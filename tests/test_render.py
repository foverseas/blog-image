from PIL import Image

from blog_image.config import spec_from_mapping
from blog_image.fonts import resolve_fonts
from blog_image.render import render


def test_render_writes_each_requested_size(tmp_path):
    spec = spec_from_mapping(
        {
            "titre": "Combien coûte une application mobile",
            "sous-titre": "Les décisions qui font varier le devis",
            "chapeau": "Mobile",
            "pied": "exemple.fr",
            "sortie": str(tmp_path),
        }
    )
    fonts = resolve_fonts(spec.font)
    for fmt in spec.formats:
        path = render(spec, fonts, fmt, spec.path_for(fmt))
        assert path.is_file()
        with Image.open(path) as image:
            assert image.size == (fmt.width, fmt.height)


def test_background_colour_reaches_the_corners(tmp_path):
    spec = spec_from_mapping(
        {"titre": "T", "fond": "#102030", "formats": ["400x400"], "motif": "aucun", "sortie": str(tmp_path)}
    )
    fonts = resolve_fonts(spec.font)
    path = render(spec, fonts, spec.formats[0], spec.path_for(spec.formats[0]))
    with Image.open(path) as image:
        assert image.convert("RGB").getpixel((2, 2)) == (16, 32, 48)


def test_a_bare_title_renders_without_the_optional_parts(tmp_path):
    spec = spec_from_mapping({"titre": "Un titre seul", "formats": ["16x9"], "sortie": str(tmp_path)})
    path = render(spec, resolve_fonts(spec.font), spec.formats[0], spec.path_for(spec.formats[0]))
    assert path.is_file()
