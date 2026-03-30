import json
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent
MENU_PATH_FILE = BASE_DIR / "menu-path.json"
OUTPUT_DIR = BASE_DIR / "output"
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


def load_menu_items():
    if not MENU_PATH_FILE.exists():
        raise FileNotFoundError(f"menu-path.json not found: {MENU_PATH_FILE}")
    data = json.loads(MENU_PATH_FILE.read_text(encoding="utf-8"))
    return data.get("items", [])


def get_skill_items(menu_items):
    """從 menu-path.json 中挑出所有 skill 子項目（parent != null）。"""

    return [item for item in menu_items if item.get("parent") is not None]


def ensure_handbook_item(skill_id: str) -> None:
    skill_dir = OUTPUT_DIR / skill_id
    content_path = skill_dir / CATEGORY_FILENAME

    if not content_path.exists():
        print(f"  - [Skip] content.json not found for skill '{skill_id}': {content_path}")
        return

    try:
        content_obj = load_json(content_path)
    except Exception as e:
        print(f"  ! Failed to load {content_path}: {e}")
        return

    items = content_obj.get("items") or []
    if not isinstance(items, list):
        print(f"  ! Invalid items format in {content_path}, expected list.")
        return

    # 若已存在 id == "foundamental" 的項目，則不插入 handbook
    has_foundamental = any(str(it.get("id")) == "foundamental" for it in items)
    if has_foundamental:
        print(f"  - Skill '{skill_id}' already has 'foundamental' item, skip adding handbook.")
        return

    # 避免重複插入 handbook
    has_handbook = any(str(it.get("id")) == "handbook" for it in items)
    if has_handbook:
        print(f"  - Skill '{skill_id}' already has 'handbook' item, nothing to do.")
        return

    handbook_item = {
        "id": "handbook",
        "t": "技術手冊",
        "en": "Handbook",
        "pointTo": {
            "type": "category",
            "data": "github/json",
            "dataLocation": f"{GITHUB_BASE}/{skill_id}/handbook.json",
        },
    }

    new_items = [handbook_item] + items
    content_obj["items"] = new_items

    save_json(content_path, content_obj)
    print(f"  - Inserted 'handbook' item at beginning for skill '{skill_id}'.")


def main(only_skill_id: str | None = None) -> None:
    try:
        menu_items = load_menu_items()
    except FileNotFoundError as e:
        print(e)
        return

    skills = get_skill_items(menu_items)

    if only_skill_id:
        skills = [s for s in skills if s.get("id") == only_skill_id]
        if not skills:
            print(f"No skill item found with id '{only_skill_id}' in menu-path.json.")
            return

    if not skills:
        print("No skill items (parent != null) found in menu-path.json.")
        return

    print("Skills detected from menu-path.json:")
    for s in skills:
        print(f"  - {s.get('id')} : {s.get('t')}")

    for skill in skills:
        skill_id = skill.get("id")
        if not skill_id:
            continue
        print(f"\n===== Processing skill '{skill_id}' =====")
        ensure_handbook_item(skill_id)

    print("\nDone. Handbook items ensured for all skills.")


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(
        description=(
            "Ensure each skill's content.json has a 'handbook' item at the beginning "
            "when no 'foundamental' item is present."
        )
    )
    parser.add_argument(
        "--skill-id",
        dest="only_skill_id",
        help="Only process a specific skill id (directory name under output/).",
    )
    args = parser.parse_args()

    main(only_skill_id=args.only_skill_id)
