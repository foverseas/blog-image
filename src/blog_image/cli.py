"""Command line entry point: `blog-image image.yml`."""

from __future__ import annotations

import argparse
import sys
from dataclasses import replace
from pathlib import Path

from . import __version__
from .draw import render
from .errors import FontError, SpecError
from .fonts import resolve_fonts
from .spec import load_spec, parse_format, slugify


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="blog-image",
        description="Generate article cover images in several aspect ratios from a short YAML file.",
    )
    parser.add_argument("spec", type=Path, nargs="+", help="YAML file(s), one card each")
    parser.add_argument("-o", "--out", type=Path, help="output directory (overrides `sortie`)")
    parser.add_argument(
        "-f",
        "--format",
        action="append",
        dest="formats",
        metavar="RATIO",
        help="format to render, repeatable; overrides `formats` (e.g. 16x9, 1x1, 1600x900)",
    )
    parser.add_argument("-n", "--name", help="base name for the files (overrides `nom`)")
    parser.add_argument("--dry-run", action="store_true", help="list what would be written and stop")
    parser.add_argument("-q", "--quiet", action="store_true", help="print nothing on success")
    parser.add_argument("--version", action="version", version=f"blog-image {__version__}")
    return parser


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)

    if args.name and len(args.spec) > 1:
        print("blog-image: -n/--name names a single card; it cannot apply to several specs", file=sys.stderr)
        return 2

    # Each spec is independent: a failure is reported and the rest still
    # renders, but the exit code remembers that something went wrong.
    failed = False
    for spec_path in args.spec:
        failed |= not _run_one(spec_path, args)
    return 2 if failed else 0


def _run_one(spec_path: Path, args: argparse.Namespace) -> bool:
    try:
        spec = load_spec(spec_path)
        if args.formats:
            spec = replace(spec, formats=tuple(parse_format(token) for token in args.formats))
        if args.out is not None:
            spec = replace(spec, out=args.out)
        if args.name:
            spec = replace(spec, name=slugify(args.name))
        fonts = None if args.dry_run else resolve_fonts(spec.font)
    except (SpecError, FontError) as error:
        # Name the file unless the message already does (load errors do).
        where = "" if str(spec_path) in str(error) else f"{spec_path}: "
        print(f"blog-image: {where}{error}", file=sys.stderr)
        return False

    for fmt in spec.formats:
        path = spec.path_for(fmt)
        if not args.dry_run:
            render(spec, fonts, fmt, path)
        if not args.quiet:
            prefix = "would write" if args.dry_run else "->"
            print(f"  {prefix} {path}   {fmt.width}x{fmt.height}")

    return True
