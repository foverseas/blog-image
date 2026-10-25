import inspect

import pytest
from PIL import Image, ImageDraw

from blog_image.draw.motifs import MOTIFS, Motif, draw_motif
from blog_image.spec.vocabulary import MOTIF_ALIASES


def _overlay(size=(400, 200)):
    image = Image.new("RGBA", size, (0, 0, 0, 0))
    return image, ImageDraw.Draw(image)


def _draw(name, box=(0.0, 0.0, 400.0, 200.0), *, seed=7, scale=1000.0):
    image, draw = _overlay()
    draw_motif(name, draw, box, accent=(0, 255, 153), foreground=(255, 255, 255), seed=seed, scale=scale)
    return image


@pytest.mark.parametrize("name", sorted(MOTIFS))
def test_every_registered_motif_accepts_the_contract(name):
    assert _draw(name).mode == "RGBA"


@pytest.mark.parametrize("name", ["particles", "grid"])
def test_a_motif_puts_marks_on_the_overlay(name):
    assert _draw(name).getbbox() is not None


def test_none_leaves_the_band_empty():
    assert _draw("none").getbbox() is None


@pytest.mark.parametrize("box", [(0.0, 0.0, 0.0, 0.0), (0.0, 0.0, -5.0, 200.0), (0.0, 0.0, 400.0, 0.0)])
@pytest.mark.parametrize("name", ["particles", "grid"])
def test_a_degenerate_box_draws_nothing_rather_than_raising(name, box):
    assert _draw(name, box).getbbox() is None


def test_the_seed_makes_particles_reproducible():
    assert _draw("particles", seed=1).tobytes() == _draw("particles", seed=1).tobytes()
    assert _draw("particles", seed=1).tobytes() != _draw("particles", seed=2).tobytes()


def test_marks_are_sized_from_scale_not_from_the_box():
    """A tall 1:1 band and a shallow 16:9 one must not change the mark size."""
    small = _draw("grid", scale=600.0)
    large = _draw("grid", scale=1600.0)
    assert small.tobytes() != large.tobytes()


def test_an_unknown_motif_name_is_a_keyerror():
    with pytest.raises(KeyError):
        _draw("tartiflette")


def test_every_registered_motif_matches_the_declared_protocol():
    """Nothing type-checks this project, so the Protocol is enforced here instead."""
    declared = inspect.signature(Motif.__call__)
    expected = declared.replace(parameters=list(declared.parameters.values())[1:])
    for name, motif in MOTIFS.items():
        assert inspect.signature(motif) == expected, f"{name} ne respecte pas le contrat Motif"


def test_the_vocabulary_names_exactly_the_registered_motifs():
    """spec/ validates motif names that draw/ must then execute. The two lists
    live in different packages on purpose -- spec/ never imports draw/ -- so
    this is the only thing tying them together: a name validated but absent
    from the registry would surface as a bare KeyError after validation."""
    assert set(MOTIF_ALIASES.values()) == set(MOTIFS)
