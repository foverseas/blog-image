from PIL import ImageFont

from blog_image.draw.text import fit, tracked_width, wrap
from blog_image.fonts import resolve_fonts


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


def test_a_single_long_word_is_shrunk_to_fit_the_width():
    fonts = resolve_fonts(None)
    font, lines, _ = fit("Incassablementlongmotunique", fonts.bold, 90, 300, 2, 8)
    assert max(font.getlength(line) for line in lines) <= 300


def test_a_non_breaking_space_is_not_a_break_point():
    """French sets one before '?'; the mark must not land on its own line."""
    font = _font(40)
    lines = wrap("Combien coûte une application mobile ?", font, 420.0)
    assert all(line != "?" for line in lines)
    assert lines[-1].endswith(" ?")


def test_tracked_width_accounts_for_the_gaps_between_glyphs():
    """One gap fewer than there are characters; a single glyph has none."""
    font = _font(40)
    assert tracked_width("ab", font, 10.0) == font.getlength("a") + font.getlength("b") + 10.0
    assert tracked_width("a", font, 10.0) == font.getlength("a")
    assert tracked_width("", font, 10.0) == 0.0
