import pytest

from blog_image.cli import main


def _spec(tmp_path, body="titre: Combien coûte une application mobile\nformats: [200x200]\n"):
    path = tmp_path / "image.yml"
    path.write_text(body, encoding="utf-8")
    return path


def test_a_plain_run_writes_the_cards_and_reports_success(tmp_path, capsys):
    assert main([str(_spec(tmp_path))]) == 0
    assert (tmp_path / "article-200x200.png").is_file()
    assert "article-200x200.png" in capsys.readouterr().out


def test_quiet_prints_nothing_but_still_writes(tmp_path, capsys):
    assert main([str(_spec(tmp_path)), "--quiet"]) == 0
    assert capsys.readouterr().out == ""
    assert (tmp_path / "article-200x200.png").is_file()


def test_dry_run_lists_the_files_without_writing_them(tmp_path, capsys):
    assert main([str(_spec(tmp_path)), "--dry-run"]) == 0
    assert "would write" in capsys.readouterr().out
    assert list(tmp_path.glob("*.png")) == []


def test_dry_run_does_not_need_a_resolvable_font(tmp_path):
    """No face is loaded when nothing is drawn, so an absent family is not fatal."""
    spec = _spec(tmp_path, "titre: T\nformats: [200x200]\npolice: ZzFamilleInexistante\n")
    assert main([str(spec), "--dry-run"]) == 0


def test_the_out_option_overrides_the_spec(tmp_path):
    spec = _spec(tmp_path, "titre: T\nformats: [200x200]\nsortie: depuis-le-yaml\n")
    assert main([str(spec), "--out", str(tmp_path / "depuis-la-cli"), "--quiet"]) == 0
    assert (tmp_path / "depuis-la-cli" / "article-200x200.png").is_file()
    assert not (tmp_path / "depuis-le-yaml").exists()


def test_the_format_option_is_repeatable_and_replaces_the_spec_list(tmp_path):
    spec = _spec(tmp_path, "titre: T\nformats: [16x9, 4x3, 1x1]\n")
    assert main([str(spec), "-f", "200x200", "-f", "120x240", "--quiet"]) == 0
    assert sorted(p.name for p in tmp_path.glob("*.png")) == ["article-120x240.png", "article-200x200.png"]


def test_the_name_option_is_slugified(tmp_path):
    assert main([str(_spec(tmp_path)), "--name", "Combien coûte une app ?", "--quiet"]) == 0
    assert (tmp_path / "combien-coute-une-app-200x200.png").is_file()


def test_an_unreadable_spec_fails_with_a_message_not_a_traceback(tmp_path, capsys):
    assert main([str(tmp_path / "absent.yml")]) == 2
    err = capsys.readouterr().err
    assert err.startswith("blog-image: ")
    assert "no such spec file" in err


@pytest.mark.parametrize(
    ("body", "expected"),
    [
        ("titre: [\n", "invalid YAML"),
        ("", "is empty"),
        ("pied: exemple.fr\n", "required"),
        ("titre: T\ntiter: typo\n", "unknown key"),
        ("titre: T\nfond: vert\n", "hex colour"),
    ],
)
def test_a_bad_spec_exits_two(tmp_path, capsys, body, expected):
    assert main([str(_spec(tmp_path, body))]) == 2
    assert expected in capsys.readouterr().err


def test_an_unresolvable_font_exits_two(tmp_path, capsys):
    spec = _spec(tmp_path, "titre: T\nformats: [200x200]\npolice: ZzFamilleInexistante\n")
    assert main([str(spec)]) == 2
    assert "could not find a font" in capsys.readouterr().err


def test_a_bad_format_on_the_command_line_exits_two(tmp_path, capsys):
    assert main([str(_spec(tmp_path)), "-f", "widescreen"]) == 2
    assert "unknown format" in capsys.readouterr().err


def test_version_exits_cleanly(capsys):
    with pytest.raises(SystemExit) as exit_code:
        main(["--version"])
    assert exit_code.value.code == 0
    assert "blog-image" in capsys.readouterr().out


def test_the_spec_directory_anchors_a_relative_output_path(tmp_path):
    nested = tmp_path / "articles"
    nested.mkdir()
    spec = _spec(nested, "titre: T\nformats: [200x200]\nsortie: cartes\n")
    assert main([str(spec), "--quiet"]) == 0
    assert (nested / "cartes" / "article-200x200.png").is_file()


def _two_specs(tmp_path):
    a = tmp_path / "a.yml"
    a.write_text("titre: Premier article\nnom: a\nformats: [200x200]\n", encoding="utf-8")
    b = tmp_path / "b.yml"
    b.write_text("titre: Second article\nnom: b\nformats: [200x200]\n", encoding="utf-8")
    return a, b


def test_several_specs_render_in_one_call(tmp_path):
    a, b = _two_specs(tmp_path)
    assert main([str(a), str(b), "--quiet"]) == 0
    assert (tmp_path / "a-200x200.png").is_file()
    assert (tmp_path / "b-200x200.png").is_file()


def test_a_bad_spec_does_not_stop_the_batch(tmp_path, capsys):
    """Each spec is independent: the batch reports the failure, renders the
    rest, and exits 2 so a script still sees that something went wrong."""
    a, b = _two_specs(tmp_path)
    a.write_text("pied: sans-titre\n", encoding="utf-8")
    assert main([str(a), str(b), "--quiet"]) == 2
    err = capsys.readouterr().err
    assert "a.yml" in err and "required" in err
    assert (tmp_path / "b-200x200.png").is_file()


def test_the_name_option_refuses_several_specs(tmp_path, capsys):
    """One base name over two specs would write the same files twice."""
    a, b = _two_specs(tmp_path)
    assert main([str(a), str(b), "--name", "unique"]) == 2
    assert "--name" in capsys.readouterr().err
    assert list(tmp_path.glob("*.png")) == []


def test_dry_run_covers_the_whole_batch(tmp_path, capsys):
    a, b = _two_specs(tmp_path)
    assert main([str(a), str(b), "--dry-run"]) == 0
    out = capsys.readouterr().out
    assert "a-200x200.png" in out and "b-200x200.png" in out
    assert list(tmp_path.glob("*.png")) == []
