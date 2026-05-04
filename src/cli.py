from __future__ import annotations
from config import OUTPUT_DIR
import argparse
from pathlib import Path

from analyzers.metadata import analyze_metadata
from analyzers.steganography import analyze_steganography
from formatters import (
    format_metadata_report,
    format_steganography_report,
)


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="image-inspector",
        description="Welcome to Image Inspector",
    )
    parser.add_argument("image", help="Path to the image file to inspect")
    parser.add_argument(
        "-m",
        "--metadata",
        action="store_true",
        help="Extract metadata from the image",
    )
    parser.add_argument(
        "-s",
        "--steganography",
        action="store_true",
        help="Detect hidden data through LSB extraction",
    )
    parser.add_argument(
        "-o",
        "--output",
        help="Write the analysis result to the given file",
    )
    return parser


def main() -> int:
    parser = build_parser()
    args = parser.parse_args()

    # Require at least one analysis mode for each run.
    if not args.metadata and not args.steganography:
        parser.error("choose at least one analysis mode: --metadata and/or --steganography")

    image_path = Path(args.image)
    if not image_path.is_file():
        parser.error(f"image file not found: {image_path}")

    outputs: list[str] = []
    if args.metadata:
        metadata_report = analyze_metadata(str(image_path))
        outputs.append(format_metadata_report(metadata_report))

    if args.steganography:
        steg_report = analyze_steganography(str(image_path))
        outputs.append(format_steganography_report(steg_report))

    # Merge enabled analysis reports into a single console output.
    result = "\n\n".join(outputs)

    print(result)

    if args.output:
        OUTPUT_DIR.mkdir(exist_ok=True)
        # Store exported reports under the project output directory.
        output_path =f"{OUTPUT_DIR}/{args.output}"
        path = Path(output_path)
        path.write_text(result + "\n", encoding="utf-8")
        print(f"Data saved in {args.output}")

    return 0
