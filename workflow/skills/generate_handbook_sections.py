import argparse
import json
import re
import time
from pathlib import Path

from google import genai
from google.genai import types

# ================= Configuration =================

LOCATION = "global"
MODEL_NAME = "gemini-3.1-pro-preview"

REQUEST_DELAY_SECONDS = 4
MAX_RETRIES = 3

BASE_DIR = Path(__file__).resolve().parent
MENU_PATH_FILE = BASE_DIR / "menu-path.json"
PROJECT_ID_FILE = BASE_DIR / "PROJECT_ID.txt"
OUTPUT_DIR = BASE_DIR / "output"
PROMPT_HANDBOOK_FILE = BASE_DIR / "prompt-handbook-category.md"

GITHUB_BASE = "https://github.com/feelryan/jujuen/blob/skills"
INFO_FILENAME = "content.info"


# ================= Helper Functions =================


def load_text_file(path: Path) -> str:
    if not path.exists():
        raise FileNotFoundError(f"File not found: {path}")
    return path.read_text(encoding="utf-8")


def save_json(path: Path, data) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)
    print(f"  - Saved JSON: {path}")


def extract_json_object(text: str):
    """從模型回應中抽出一個 JSON 物件。預期模型直接回傳一個 JSON 物件，但仍防禦性處理 ```json 區塊。"""

    match = re.search(r"```json\s*(\{.*?\})\s*```", text, re.DOTALL)
    if match:
        json_str = match.group(1)
    else:
        match = re.search(r"(\{.*\})", text, re.DOTALL)
        json_str = match.group(0) if match else None

    if not json_str:
        print("    ! 無法在回應中找到 JSON 物件。")
        return None

    try:
        return json.loads(json_str)
    except json.JSONDecodeError as e:
        print(f"    ! JSON 解析失敗: {e}")
        return None


def send_to_vertex_for_handbook(client: genai.Client, prompt: str) -> str | None:
    """呼叫 Vertex AI 產生單一 skill 的 handbook Category JSON，回傳純文字回應。"""

    safety_settings = [
        types.SafetySetting(
            category=types.HarmCategory.HARM_CATEGORY_HATE_SPEECH,
            threshold=types.HarmBlockThreshold.BLOCK_ONLY_HIGH,
        ),
        types.SafetySetting(
            category=types.HarmCategory.HARM_CATEGORY_DANGEROUS_CONTENT,
            threshold=types.HarmBlockThreshold.BLOCK_ONLY_HIGH,
        ),
        types.SafetySetting(
            category=types.HarmCategory.HARM_CATEGORY_SEXUALLY_EXPLICIT,
            threshold=types.HarmBlockThreshold.BLOCK_ONLY_HIGH,
        ),
        types.SafetySetting(
            category=types.HarmCategory.HARM_CATEGORY_HARASSMENT,
            threshold=types.HarmBlockThreshold.BLOCK_ONLY_HIGH,
        ),
    ]

    config = types.GenerateContentConfig(
        max_output_tokens=65535,
        temperature=0.3,
        top_p=0.9,
        safety_settings=safety_settings,
    )

    try:
        response = client.models.generate_content(
            model=MODEL_NAME,
            contents=prompt,
            config=config,
        )
        return response.text
    except Exception as e:
        print(f"    ! Vertex AI 呼叫失敗: {e}")
        return None


def load_menu_items():
    data = json.loads(MENU_PATH_FILE.read_text(encoding="utf-8"))
    return data.get("items", [])


def get_skill_items(menu_items):
    """從 menu-path.json 中挑出所有 skill 子項目（parent != null）。"""

    return [item for item in menu_items if item.get("parent") is not None]


def build_category_lookup(menu_items):
    return {item.get("id"): item for item in menu_items}


def load_chapters_overview(skill_id: str) -> str:
    info_path = OUTPUT_DIR / skill_id / INFO_FILENAME
    if not info_path.exists():
        return ""

    try:
        info = json.loads(info_path.read_text(encoding="utf-8"))
    except Exception:
        return ""

    chapters = info.get("chapters") or []
    lines: list[str] = []
    for ch in chapters:
        ch_id = ch.get("id")
        ch_t = ch.get("t", ch_id)
        ch_en = ch.get("en", ch_t)
        if ch_id:
            lines.append(f"- {ch_id}: {ch_t} | {ch_en}")
    return "\n".join(lines)


# ================= Main =================


def main(force: bool = False, only_skill_id: str | None = None) -> None:
    # 讀取 PROJECT_ID
    if not PROJECT_ID_FILE.exists():
        print(f"PROJECT_ID file not found: {PROJECT_ID_FILE}")
        print("請在該檔案中填入有效的 GCP Project ID。")
        return

    project_id = PROJECT_ID_FILE.read_text(encoding="utf-8").strip()
    if not project_id:
        print(f"PROJECT_ID file {PROJECT_ID_FILE} is empty.")
        return

    print(f"Initializing Vertex AI Client for project '{project_id}' in '{LOCATION}'...")
    try:
        client = genai.Client(vertexai=True, project=project_id, location=LOCATION)
    except Exception as e:
        print(f"Vertex AI initialization failed: {e}")
        print("請確認已執行 'gcloud auth application-default login'，且 PROJECT_ID 設定正確。")
        return

    try:
        prompt_template = load_text_file(PROMPT_HANDBOOK_FILE)
    except FileNotFoundError as e:
        print(e)
        return

    if not MENU_PATH_FILE.exists():
        print(f"Menu-path file not found: {MENU_PATH_FILE}")
        return

    menu_items = load_menu_items()
    category_lookup = build_category_lookup(menu_items)
    skills = get_skill_items(menu_items)

    if only_skill_id:
        skills = [s for s in skills if s.get("id") == only_skill_id]
        if not skills:
            print(f"No skill item found with id '{only_skill_id}' in menu-path.json.")
            return

    if not skills:
        print("No skill items found in menu-path.json (items with parent != null).")
        return

    print("Skills detected from menu-path.json:")
    for s in skills:
        parent_id = s.get("parent")
        parent_item = category_lookup.get(parent_id, {})
        print(f"  - {s.get('id')} : {s.get('t')} (category: {parent_item.get('t')})")

    for skill in skills:
        skill_id = skill["id"]
        skill_name = skill.get("t", skill_id)
        skill_en = skill.get("en", skill_name)
        parent_id = skill.get("parent")
        parent_item = category_lookup.get(parent_id, {})
        category_name = parent_item.get("t", parent_id)

        print(f"\n===== Generating handbook.json for {skill_name} ({skill_id}) =====")

        handbook_path = OUTPUT_DIR / skill_id / "handbook.json"
        if handbook_path.exists() and not force:
            print(f"  - handbook.json already exists for skill '{skill_id}': {handbook_path}")
            print("    Use --force to overwrite.")
            continue

        chapters_overview = load_chapters_overview(skill_id)

        prompt = (
            prompt_template
            .replace("{{SKILL_ID}}", skill_id)
            .replace("{{SKILL_NAME}}", skill_name)
            .replace("{{SKILL_CATEGORY}}", category_name or "")
            .replace("{{CHAPTERS_OVERVIEW}}", chapters_overview)
        )

        result_obj = None

        for attempt in range(1, MAX_RETRIES + 1):
            if attempt > 1:
                print(f"  → Retry attempt {attempt}/{MAX_RETRIES} for {skill_id}...")

            raw = send_to_vertex_for_handbook(client, prompt)
            if not raw:
                print("    ! 模型回應為空。")
            else:
                parsed = extract_json_object(raw)
                if isinstance(parsed, dict) and parsed.get("items"):
                    result_obj = parsed
                    break
                else:
                    print("    ! 解析後結果不是包含 items 的 JSON 物件。")

            if attempt < MAX_RETRIES:
                delay = REQUEST_DELAY_SECONDS * attempt
                print(f"    Waiting {delay} seconds before next attempt...")
                time.sleep(delay)

        if result_obj is None:
            print(f"  ! 無法成功取得有效的 handbook Category JSON for {skill_id}，請稍後重試或檢查 prompt。")
            continue

        # 重新包裝成我們要的 Handbook Category 結構，並補上 pointTo 與 quiz item
        items = result_obj.get("items") or []
        normalized_items: list[dict] = []

        for idx, item in enumerate(items, start=1):
            topic_id = item.get("id") or f"topic{idx:02d}"
            t = item.get("t") or topic_id
            en = item.get("en") or t
            desc = item.get("description", "")

            # 主 handbook 章節：指向對應的 Markdown 手冊說明
            main_point_to = {
                "type": "document",
                "data": "github/md",
                "dataLocation": f"{GITHUB_BASE}/{skill_id}/handbook/{topic_id}.md",
            }

            main_item = {
                "id": topic_id,
                "t": t,
                "en": en,
                "description": desc,
                "pointTo": main_point_to,
            }
            normalized_items.append(main_item)

            # 對應的 quiz 子節點：指向該主題的題庫 JSON
            quiz_point_to = {
                "type": "document",
                "data": "github/json",
                "dataLocation": f"{GITHUB_BASE}/{skill_id}/handbook/{topic_id}.json",
                "renderObject": "Question",
            }

            quiz_item = {
                "id": f"{topic_id}-quiz",
                "t": f"{t} - 測驗 / Quiz",
                "en": f"{en} - Quiz",
                "parent": topic_id,
                "description": "針對此 handbook 章節主題的練習題與模擬考題。",
                "pointTo": quiz_point_to,
            }
            normalized_items.append(quiz_item)

        handbook_category = {
            "id": "handbook",
            "title": f"Handbook for {skill_name}",
            "items": normalized_items,
        }

        save_json(handbook_path, handbook_category)

        # 稍作間隔，避免過於頻繁呼叫 API
        time.sleep(REQUEST_DELAY_SECONDS)

    print("\n===== All skills processed. Handbook generation complete. =====")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description=(
            "Generate handbook.json (Category) for each skill under workflow/skills/output/{skill}/, "
            "based on menu-path.json and optional content.info chapters."
        )
    )
    parser.add_argument(
        "--force",
        action="store_true",
        help="Overwrite existing handbook.json if it already exists.",
    )
    parser.add_argument(
        "--skill-id",
        type=str,
        help="Only process a specific skill id (directory name under output/).",
    )
    args = parser.parse_args()

    main(force=args.force, only_skill_id=args.skill_id)
