#!/usr/bin/env python3
"""
Collect all ``exception.txt`` files from one or more directory trees into a
single folder.

The script recursively searches one or more source directories for files named
``exception.txt``, copies them into an output directory, and generates an
``index.csv`` file mapping each copied file to its original location.

Example
-------
    python3 collect_exceptions.py \
        /path/to/project1 \
        /path/to/project2 \
        /path/to/project3 \
        /path/to/output

This will produce a directory such as::

    output/
    ├── exception_00001.txt
    ├── exception_00002.txt
    ├── ...
    └── index.csv
"""

import argparse
import csv
import shutil
from pathlib import Path


def collect_exception_files(
    source_dirs: list[Path],
    output_dir: Path,
) -> None:
    """Copy all exception.txt files from multiple directory trees into one folder."""
    output_dir = output_dir.resolve()
    output_dir.mkdir(parents=True, exist_ok=True)

    matches: list[tuple[Path, Path]] = []

    for source_dir in source_dirs:
        source_dir = source_dir.resolve()

        if not source_dir.is_dir():
            raise ValueError(f"Source directory does not exist: {source_dir}")

        for path in source_dir.rglob("exception.txt"):
            if output_dir not in path.resolve().parents:
                matches.append((source_dir, path))

    matches.sort(key=lambda x: str(x[1]))

    index_path = output_dir / "index.csv"

    with index_path.open("w", newline="", encoding="utf-8") as index_file:
        writer = csv.DictWriter(
            index_file,
            fieldnames=[
                "copied_filename",
                "source_root",
                "original_relative_path",
                "original_absolute_path",
            ],
        )
        writer.writeheader()

        for number, (source_root, original_path) in enumerate(
            matches, start=1
        ):
            copied_filename = f"exception_{number:05d}.txt"
            copied_path = output_dir / copied_filename

            shutil.copy2(original_path, copied_path)

            writer.writerow(
                {
                    "copied_filename": copied_filename,
                    "source_root": str(source_root),
                    "original_relative_path": str(
                        original_path.relative_to(source_root)
                    ),
                    "original_absolute_path": str(original_path),
                }
            )

    print(f"Found and copied {len(matches)} file(s).")
    print(f"Output directory: {output_dir}")
    print(f"Index written to: {index_path}")


def main() -> None:
    """Parse command-line arguments and run the collection."""
    parser = argparse.ArgumentParser(
        description=(
            "Recursively find exception.txt files in one or more directories, "
            "copy them into one folder, and create an index of their original "
            "locations."
        )
    )

    parser.add_argument(
        "paths",
        nargs="+",
        type=Path,
        help=(
            "Input directories followed by the output directory. "
            "The last path is interpreted as the output directory."
        ),
    )

    args = parser.parse_args()

    if len(args.paths) < 2:
        parser.error(
            "Specify at least one input directory and one output directory."
        )

    *source_dirs, output_dir = args.paths
    collect_exception_files(source_dirs, output_dir)


if __name__ == "__main__":
    main()
