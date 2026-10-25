import pytest

from blog_image.draw.colour import rgba


@pytest.mark.parametrize(
    ("alpha", "expected"),
    [(255, 255), (0, 0), (128.7, 128), (-20, 0), (400, 255)],
)
def test_alpha_is_clamped_and_truncated_to_a_byte(alpha, expected):
    """Callers compute alphas as floats from distances and ratios; Pillow wants a byte."""
    assert rgba((0, 255, 153), alpha) == (0, 255, 153, expected)


def test_the_triple_passes_through_untouched():
    assert rgba((28, 28, 34), 255)[:3] == (28, 28, 34)
