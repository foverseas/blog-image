import pytest

from blog_image.errors import SpecError
from blog_image.spec import parse_colour, parse_format, slugify, spec_from_mapping


def test_french_and_english_keys_are_equivalent():
    fr = spec_from_mapping({"titre": "Bonjour", "fond": "#000", "pied": "exemple.fr"})
    en = spec_from_mapping({"title": "Bonjour", "background": "#000", "footer": "exemple.fr"})
    assert (fr.title, fr.background, fr.footer) == (en.title, en.background, en.footer)


def test_defaults_cover_the_three_ratios():
    spec = spec_from_mapping({"titre": "Bonjour"})
    assert [fmt.key for fmt in spec.formats] == ["16x9", "4x3", "1x1"]
    assert [(f.width, f.height) for f in spec.formats] == [(1600, 900), (1600, 1200), (1200, 1200)]


def test_unknown_key_is_rejected_rather_than_ignored():
    with pytest.raises(SpecError, match="unknown key 'titer'"):
        spec_from_mapping({"titer": "typo", "titre": "Bonjour"})


def test_title_is_required():
    with pytest.raises(SpecError, match="required"):
        spec_from_mapping({"pied": "exemple.fr"})


@pytest.mark.parametrize(
    ("value", "expected"),
    [("#00ff99", (0, 255, 153)), ("00FF99", (0, 255, 153)), ("#0f9", (0, 255, 153)), ([28, 28, 34], (28, 28, 34))],
)
def test_colour_forms(value, expected):
    assert parse_colour(value, "accent") == expected


@pytest.mark.parametrize("value", ["#00ff9", "vert", "#gggggg", [1, 2], [1, 2, 300]])
def test_bad_colour_is_rejected(value):
    with pytest.raises(SpecError):
        parse_colour(value, "accent")


def test_explicit_pixel_size():
    fmt = parse_format("1240x700")
    assert (fmt.key, fmt.width, fmt.height) == ("1240x700", 1240, 700)


def test_unknown_format_lists_the_known_ones():
    with pytest.raises(SpecError, match="16x9"):
        parse_format("widescreen")


def test_accents_fold_rather_than_split_the_slug():
    assert slugify("Combien coûte une app ?") == "combien-coute-une-app"


def test_accent_period_is_dropped_when_the_title_already_closes():
    assert spec_from_mapping({"titre": "Pourquoi ?"}).dot is False
    assert spec_from_mapping({"titre": "Pourquoi"}).dot is True


def test_a_list_subtitle_becomes_hard_line_breaks():
    spec = spec_from_mapping({"titre": "T", "sous-titre": ["une", "deux"]})
    assert spec.subtitle == "une\ndeux"


def test_output_path_is_relative_to_the_spec_file(tmp_path):
    spec = spec_from_mapping({"titre": "T", "nom": "mon-article", "sortie": "out"}, base=tmp_path)
    fmt = spec.formats[0]
    assert spec.path_for(fmt) == tmp_path / "out" / "mon-article-16x9.png"


def test_a_list_eyebrow_folds_to_a_single_line():
    """as_text joins a list with hard breaks; the tracked kicker cannot honour
    them, so the break folds to a space at build time."""
    spec = spec_from_mapping({"titre": "T", "chapeau": ["DEV", "MOBILE"], "sortie": "out"})
    assert spec.eyebrow == "DEV MOBILE"
