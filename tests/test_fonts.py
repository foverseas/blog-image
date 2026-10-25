import shutil

import pytest
from PIL import ImageFont

from blog_image.errors import FontError
from blog_image.fonts import resolve_fonts, search_dirs


@pytest.fixture
def family(tmp_path):
    """A real face copied under predictable Regular/Bold names."""
    source = resolve_fonts(None).regular_path
    suffix = source.suffix
    for weight in ("Regular", "Bold"):
        shutil.copy(source, tmp_path / f"Essai-{weight}{suffix}")
    return tmp_path / f"Essai-%s{suffix}"


def test_the_fallbacks_find_something_on_this_machine():
    fonts = resolve_fonts(None)
    assert fonts.regular_path.is_file()
    assert fonts.bold_path.is_file()


def test_search_dirs_only_lists_directories_that_exist():
    assert all(path.is_dir() for path in search_dirs())


def test_an_explicit_pair_is_used_as_given(family):
    regular, bold = str(family) % "Regular", str(family) % "Bold"
    fonts = resolve_fonts({"regular": regular, "bold": bold})
    assert (str(fonts.regular_path), str(fonts.bold_path)) == (regular, bold)


def test_a_mapping_needs_both_weights(family):
    with pytest.raises(FontError, match="bold"):
        resolve_fonts({"regular": str(family) % "Regular"})


def test_a_mapping_pointing_at_nothing_says_which_file(tmp_path):
    missing = tmp_path / "absente.ttf"
    with pytest.raises(FontError, match="no such font file"):
        resolve_fonts({"regular": str(missing), "bold": str(missing)})


def test_a_template_fills_in_the_weight(family):
    fonts = resolve_fonts(str(family))
    assert fonts.regular_path.name.endswith("Essai-Regular" + fonts.regular_path.suffix)
    assert fonts.bold_path.name.endswith("Essai-Bold" + fonts.bold_path.suffix)


def test_a_template_that_resolves_to_nothing_is_an_error(tmp_path):
    with pytest.raises(FontError, match="template produced a missing file"):
        resolve_fonts(str(tmp_path / "Absente-%s.ttf"))


def test_a_lone_file_serves_as_both_weights(family):
    one = str(family) % "Regular"
    fonts = resolve_fonts(one)
    assert fonts.regular_path == fonts.bold_path


def test_an_unknown_family_reports_where_it_looked():
    with pytest.raises(FontError, match="could not find a font for ZzFamilleInexistante"):
        resolve_fonts("ZzFamilleInexistante")


def test_the_same_size_is_loaded_once(family):
    fonts = resolve_fonts(str(family))
    assert fonts.regular(40) is fonts.regular(40)
    assert fonts.regular(40) is not fonts.regular(41)
    assert isinstance(fonts.regular(40), ImageFont.FreeTypeFont)


def test_regular_and_bold_are_cached_apart(family):
    fonts = resolve_fonts(str(family))
    assert fonts.regular(40) is not fonts.bold(40)


def test_a_size_of_zero_is_clamped_rather_than_refused(family):
    assert resolve_fonts(str(family)).regular(0).size == 1
