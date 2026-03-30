import json
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent
OUTPUT_DIR = BASE_DIR / "output"
INFO_FILENAME = "content.info"
CATEGORY_FILENAME = "content.json"

GITHUB_BASE = "https://github.com/feelryan/jujuen/blob/skills"


def load_json(path: Path):
    if not path.exists():
        raise FileNotFoundError(f"JSON file not found: {path}")
    return json.loads(path.read_text(encoding="utf-8"))


def save_json(path: Path, data) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(
        json.dumps(data, ensure_ascii=False, indent=2),
        encoding="utf-8",
    )
    print(f"  - Saved JSON: {path}")


def build_category_from_info(skill_id: str, info: dict) -> dict:
    skill_title = info.get("skillName") or info.get("skillNameEnglish") or skill_id
    chapters = info.get("chapters", [])

    items = []
    for ch in chapters:
        ch_id = ch.get("id")
        ch_t = ch.get("t", ch_id)
        ch_en = ch.get("en", ch_t)
        ch_desc = ch.get("description", "")

        if not ch_id:
            print(f"    ! Skip chapter without id in skill {skill_id}")
            continue

        # 章節本身，指向 Markdown
        items.append(
            {
                "id": ch_id,
                "t": ch_t,
                "en": ch_en,
                "description": ch_desc,
                "pointTo": {
                    "type": "document",
                    "data": "github/md",
                    "dataLocation": f"{GITHUB_BASE}/{skill_id}/{ch_id}.md",
                },
            }
        )

        # 章節 quiz，指向 JSON 題庫
        items.append(
            {
                "id": f"{ch_id}-quiz",
                "parent": ch_id,
                "t": f"{ch_t}-quiz",
                "en": f"{ch_en}-quiz",
                "pointTo": {
                    "type": "document",
                    "data": "github/json",
                    "dataLocation": f"{GITHUB_BASE}/{skill_id}/{ch_id}.json",
                    "renderObject": "Question",
                },
            }
        )

    return {
        "id": skill_id,
        "title": skill_title,
        "items": items,
    }


def main(only_skill_id: str | None = None, force: bool = False) -> None:
    if not OUTPUT_DIR.exists():
        print(f"Output directory not found: {OUTPUT_DIR}")
        print("請先使用 generate_skill_info.py 產生各 skill 的 content.info。")
        return

    skill_dirs = [
        d for d in OUTPUT_DIR.iterdir()
        if d.is_dir() and (d / INFO_FILENAME).exists()
    ]

    if only_skill_id:
        skill_dirs = [d for d in skill_dirs if d.name == only_skill_id]
        if not skill_dirs:
            print(f"No skill directory with content.info found for id '{only_skill_id}'.")
            return

    print("Skills with content.info:")
    for d in skill_dirs:
        print(f"  - {d.name}")

    for skill_dir in skill_dirs:
        skill_id = skill_dir.name
        info_path = skill_dir / INFO_FILENAME
        category_path = skill_dir / CATEGORY_FILENAME

        print(f"\n===== Building content.json for {skill_id} =====")

        if category_path.exists() and not force:
            print(f"  - content.json already exists: {category_path}")
            print("    Use --force to overwrite.")
            continue

        try:
            info = load_json(info_path)
        except Exception as e:
            print(f"  ! Failed to load {info_path}: {e}")
            continue

        category_obj = build_category_from_info(skill_id, info)
        save_json(category_path, category_obj)

    print("\nDone.")


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(
        description="Generate {skill}/content.json (Category) from content.info chapters."
    )
    parser.add_argument(
        "--skill-id",
        dest="only_skill_id",
        help="Only generate for a specific skill id (directory name under output/).",
    )
    parser.add_argument(
        "--force",
        action="store_true",
        help="Overwrite existing content.json files.",
    )
    args = parser.parse_args()
    main(only_skill_id=args.only_skill_id, force=args.force)