from PIL import Image, ImageFont

from blog_image.config import spec_from_mapping
from blog_image.fonts import resolve_fonts
from blog_image.render import fit, render, wrap


def _font(size=40):
    return resolve_fonts(None).regular(size)


def test_wrap_never_exceeds_the_measured_width():
    font = _font()
    width = 300.0
    lines = wrap("Combien coûte une application mobile en 2026", font, width)
    assert len(lines) > 1
    assert all(font.getlength(line) <= width for line in lines)


def test_wrap_keeps_every_word():
    font = _font()
    text = "Combien coûte une application mobile"
    assert " ".join(wrap(text, font, 240.0)).split() == text.split()


def test_fit_shrinks_until_the_line_budget_is_met():
    fonts = resolve_fonts(None)
    _, lines, size = fit("Un titre long qui ne tient pas sur deux lignes", fonts.bold, 90, 420, 2, 10)
    assert len(lines) <= 2
    assert size < 90


def test_fit_stops_at_the_floor_rather_than_looping():
    fonts = resolve_fonts(None)
    font, _, size = fit("Incassablementlongmotunique", fonts.bold, 90, 20, 1, 12)
    assert size == 12
    assert isinstance(font, ImageFont.FreeTypeFont)


def test_hard_newlines_are_honoured():
    font = _font(20)
    _, lines, _ = fit("une\ndeux", lambda _size: font, 20, 10_000, 4, 10)
    assert lines == ["une", "deux"]


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


def test_a_single_long_word_is_shrunk_to_fit_the_width():
    fonts = resolve_fonts(None)
    font, lines, _ = fit("Incassablementlongmotunique", fonts.bold, 90, 300, 2, 8)
    assert max(font.getlength(line) for line in lines) <= 300


def test_a_bare_title_renders_without_the_optional_parts(tmp_path):
    spec = spec_from_mapping({"titre": "Un titre seul", "formats": ["16x9"], "sortie": str(tmp_path)})
    path = render(spec, resolve_fonts(spec.font), spec.formats[0], spec.path_for(spec.formats[0]))
    assert path.is_file()


def test_a_non_breaking_space_is_not_a_break_point():
    """French sets one before '?'; the mark must not land on its own line."""
    font = _font(40)
    lines = wrap("Combien coûte une application mobile ?", font, 420.0)
    assert all(line != "?" for line in lines)
    assert lines[-1].endswith(" ?")
