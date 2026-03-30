import os
import shutil
from pathlib import Path

from PyPDF2 import PdfMerger
from PyPDF2.errors import PdfReadError

# Base directory containing the PDF files
BASE_DIR = Path(__file__).resolve().parent / "tcool.cc" / "materials" / "9th" / "數學"

# Target folders and the keyword each one matches in the filename
TARGET_FOLDERS = [
    "期中1",
    "期中2",
    "期末2",
    "期末3",
]


def organize_pdfs() -> int:
    """Move PDFs in BASE_DIR into term folders based on filename.

    Returns the number of moved files.
    """

    if not BASE_DIR.exists() or not BASE_DIR.is_dir():
        print(f"Base directory does not exist or is not a directory: {BASE_DIR}")
        return 0

    # Create target folders if they do not exist
    for folder_name in TARGET_FOLDERS:
        target_path = BASE_DIR / folder_name
        target_path.mkdir(parents=True, exist_ok=True)

    moved_count = 0

    # Iterate over PDF files in the base directory (non-recursive)
    for entry in BASE_DIR.iterdir():
        if not entry.is_file():
            continue
        if entry.suffix.lower() != ".pdf":
            continue

        filename = entry.name
        # Check which folder keyword appears in the filename
        for folder_name in TARGET_FOLDERS:
            if folder_name in filename:
                dest_path = BASE_DIR / folder_name / filename
                # If a file with the same name already exists in destination, skip to avoid overwrite
                if dest_path.exists():
                    print(f"Skip (already exists): {dest_path}")
                    break

                print(f"Moving: {entry} -> {dest_path}")
                shutil.move(str(entry), str(dest_path))
                moved_count += 1
                break  # stop checking other folder names for this file

    print(f"Done. Moved {moved_count} PDF file(s).")
    return moved_count


def merge_pdfs_for_terms() -> None:
    """For each term folder, merge its PDFs into a single PDF.

    - Skips any PDF whose filename contains "answer" (case-insensitive).
    - Writes the merged PDF into the grade/subject base directory (BASE_DIR).
    """

    if not BASE_DIR.exists() or not BASE_DIR.is_dir():
        print(f"Base directory does not exist or is not a directory: {BASE_DIR}")
        return

    for folder_name in TARGET_FOLDERS:
        term_dir = BASE_DIR / folder_name
        if not term_dir.exists() or not term_dir.is_dir():
            print(f"Skip {folder_name}: folder does not exist.")
            continue

        pdf_files = sorted(
            [
                p
                for p in term_dir.iterdir()
                if p.is_file()
                and p.suffix.lower() == ".pdf"
                and "answer" not in p.name.lower()
            ]
        )

        if not pdf_files:
            print(f"No PDFs to merge for {folder_name} (after skipping 'answer').")
            continue

        output_name = f"{folder_name}_merged.pdf"
        output_path = BASE_DIR / output_name

        print(
            f"Merging {len(pdf_files)} PDF file(s) for {folder_name} "
            f"into: {output_path}"
        )

        merger = PdfMerger()
        try:
            for pdf_path in pdf_files:
                # Skip clearly empty files to avoid read errors
                try:
                    if pdf_path.stat().st_size == 0:
                        print(f"Skipping empty PDF file: {pdf_path}")
                        continue
                except OSError as e:
                    print(f"Could not stat file {pdf_path}: {e}. Skipping.")
                    continue

                try:
                    merger.append(str(pdf_path))
                except PdfReadError as e:
                    print(f"Skipping invalid/corrupted PDF {pdf_path}: {e}")
                    continue

            with output_path.open("wb") as out_f:
                merger.write(out_f)
        finally:
            merger.close()


def main() -> None:
    # First, organize PDFs into term folders (idempotent if already organized)
    organize_pdfs()

    # Then, merge PDFs inside each term folder
    merge_pdfs_for_terms()


if __name__ == "__main__":
    main()
