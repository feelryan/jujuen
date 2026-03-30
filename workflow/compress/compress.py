import os
import shutil
import tempfile
from datetime import datetime
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parents[2]  # C:\Data_Sets\ai

# Configuration: folders and exclusion rules
FOLDERS = [
    {"path": BASE_DIR / "jujuen", "exclude": ["node_modules"]},
    {"path": BASE_DIR / "workflow/ancient-classics", "exclude": ["Lib", "Scripts", "output"]},
    {"path": BASE_DIR / "workflow/ds-algo", "exclude": ["Lib", "Scripts"]},
    {"path": BASE_DIR / "workflow/job", "exclude": ["Lib", "Scripts"]},
    {"path": BASE_DIR / "workflow/junior-high", "exclude": ["Lib", "Scripts", "tcool.cc"]},
    {"path": BASE_DIR / "workflow/skills", "exclude": ["Lib", "Scripts"]},
    {"path": BASE_DIR / "workflow/compress", "exclude": ["Lib", "Scripts"]},
]


CURRENT_DATE = datetime.now().strftime("%Y%m%d")


def should_exclude(path: Path, exclude_names: list[str]) -> bool:
    """Return True if the path is inside any excluded subfolder.

    We check folder names in the path components, similar to the PowerShell regex
    that excluded any path containing the given folder names.
    """

    path_parts = set(path.parts)
    return any(name in path_parts for name in exclude_names)


def compress_folder(folder_path: Path, exclude_subfolders: list[str]) -> None:
    folder_path = folder_path.resolve()
    folder_name = folder_path.name
    zip_base_name = Path.cwd() / f"{folder_name}_{CURRENT_DATE}"
    zip_file_name = f"{folder_name}_{CURRENT_DATE}.zip"
    zip_path = zip_base_name.with_suffix(".zip")

    # If the zip file already exists, skip this folder
    if zip_path.exists():
        print(f"Skip (already exists): {zip_file_name}")
        return

    # Temporary folder used to stage filtered contents
    temp_dir = Path(tempfile.mkdtemp())

    try:
        base_path = folder_path

        for src in base_path.rglob("*"):
            if should_exclude(src, exclude_subfolders):
                continue

            rel = src.relative_to(base_path)
            dest = temp_dir / rel

            if src.is_dir():
                dest.mkdir(parents=True, exist_ok=True)
            else:
                dest.parent.mkdir(parents=True, exist_ok=True)
                shutil.copy2(src, dest)

        # Create the zip archive from the temporary directory
        shutil.make_archive(str(zip_base_name), "zip", root_dir=temp_dir)
        print(f"Created zip file: {zip_file_name}")
    except Exception as e:
        print(f"An error occurred while compressing {folder_path}: {e}")
    finally:
        shutil.rmtree(temp_dir, ignore_errors=True)


def main() -> None:
    for entry in FOLDERS:
        folder_path: Path = entry["path"]
        exclude = entry["exclude"]

        try:
            full_path = folder_path.resolve(strict=True)
        except FileNotFoundError:
            print(f"Folder not found: {folder_path}")
            continue

        print(f"Processing folder: {folder_path}")
        compress_folder(full_path, exclude)


if __name__ == "__main__":
    main()
