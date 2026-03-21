"""
Command-line interface for Arabic Documentation Translator.
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

from . import __version__
from .pipeline import BatchTranslator, DocumentTranslator


def build_parser() -> argparse.ArgumentParser:
    """Create the CLI argument parser."""
    parser = argparse.ArgumentParser(
        prog="arabic-translate",
        description="Translate Markdown documentation into Arabic.",
    )
    parser.add_argument(
        "input_path",
        nargs="?",
        help="Input file or folder to translate.",
    )
    parser.add_argument(
        "-o",
        "--output",
        dest="output_path",
        help="Output file or folder path. Defaults to an *_ar sibling path.",
    )
    parser.add_argument(
        "-g",
        "--glossary",
        dest="glossary_path",
        help="Optional custom glossary JSON file.",
    )
    parser.add_argument(
        "--batch",
        action="store_true",
        help="Treat the input as a folder and translate matching files.",
    )
    parser.add_argument(
        "--pattern",
        default="*.md",
        help="Glob pattern for batch mode. Default: *.md",
    )
    parser.add_argument(
        "--non-recursive",
        action="store_true",
        help="Disable recursive folder traversal in batch mode.",
    )
    parser.add_argument(
        "--review",
        action="store_true",
        help="Run the review step after file translation.",
    )
    parser.add_argument(
        "--quality-threshold",
        type=float,
        default=0.8,
        help="Minimum passing quality score. Default: 0.8",
    )
    parser.add_argument(
        "--model",
        default="gpt-4",
        help="Translation model name. Default: gpt-4",
    )
    parser.add_argument(
        "--version",
        action="version",
        version=f"%(prog)s {__version__}",
    )
    return parser


def _default_output_path(input_path: Path, batch_mode: bool) -> Path:
    """Derive a sensible default output path."""
    if batch_mode or input_path.is_dir():
        return input_path.parent / f"{input_path.name}_ar"

    return input_path.with_name(f"{input_path.stem}_ar{input_path.suffix}")


def _run_file_translation(args: argparse.Namespace, input_path: Path) -> int:
    """Translate a single file and print a short JSON summary."""
    output_path = Path(args.output_path) if args.output_path else _default_output_path(input_path, False)

    translator = DocumentTranslator(
        glossary_path=args.glossary_path,
        quality_threshold=args.quality_threshold,
        model=args.model,
    )

    if args.review:
        result = translator.translate_with_review(str(input_path), str(output_path))
    else:
        result = translator.translate_file(str(input_path), str(output_path))

    print(json.dumps(result, ensure_ascii=False, indent=2))
    return 0


def _run_batch_translation(args: argparse.Namespace, input_path: Path) -> int:
    """Translate a folder and print results plus a summary."""
    output_path = Path(args.output_path) if args.output_path else _default_output_path(input_path, True)

    translator = BatchTranslator(
        glossary_path=args.glossary_path,
        quality_threshold=args.quality_threshold,
    )
    results = translator.translate_folder(
        str(input_path),
        str(output_path),
        file_pattern=args.pattern,
        recursive=not args.non_recursive,
    )
    payload = {
        "results": results,
        "summary": translator.get_batch_summary(results),
    }
    print(json.dumps(payload, ensure_ascii=False, indent=2))
    return 0


def main(argv: list[str] | None = None) -> int:
    """CLI entry point."""
    parser = build_parser()
    args = parser.parse_args(argv)

    if not args.input_path:
        parser.print_help()
        return 0

    input_path = Path(args.input_path)
    if not input_path.exists():
        print(f"Input path does not exist: {input_path}", file=sys.stderr)
        return 1

    try:
        if args.batch or input_path.is_dir():
            return _run_batch_translation(args, input_path)

        return _run_file_translation(args, input_path)
    except Exception as exc:
        print(f"Translation failed: {exc}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
