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
MAX_RETRIES_PER_SKILL = 3

BASE_DIR = Path(__file__).resolve().parent
MENU_PATH_FILE = BASE_DIR / "menu-path.json"
PROJECT_ID_FILE = BASE_DIR / "PROJECT_ID.txt"
OUTPUT_DIR = BASE_DIR / "output"
PROMPT_SKILLS_FILE = BASE_DIR / "prompt-chpaters.md"
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


def extract_json_array(text: str):
    """從模型回應中抽出 JSON 陣列。

    預期模型直接回傳一個 JSON 陣列，但仍防禦性處理 ```json 區塊。
    """

    match = re.search(r"```json\s*(\[.*?\])\s*```", text, re.DOTALL)
    if match:
        json_str = match.group(1)
    else:
        match = re.search(r"(\[.*\])", text, re.DOTALL)
        json_str = match.group(0) if match else None

    if not json_str:
        print("    ! 無法在回應中找到 JSON 陣列。")
        return None

    try:
        return json.loads(json_str)
    except json.JSONDecodeError as e:
        print(f"    ! JSON 解析失敗: {e}")
        return None


def send_to_vertex_for_skill_info(client: genai.Client, prompt: str) -> str | None:
    """呼叫 Vertex AI 產生單一 skill 的 content.info 內容，回傳純文字回應。"""

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
        max_output_tokens=8192,
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
    items = data.get("items", [])
    return items


def get_skill_items(menu_items):
    """從 menu-path.json 中挑出所有 skill 子項目。

    規則：parent != null 視為 skill（因為大分類 parent 為 null）。
    """

    skills = [item for item in menu_items if item.get("parent") is not None]
    return skills


def build_category_lookup(menu_items):
    """建立由 id 對應 item 的查詢表，以便由子項目回推其 parent 類別名稱。"""

    return {item.get("id"): item for item in menu_items}


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
        prompt_template = load_text_file(PROMPT_SKILLS_FILE)
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

        print(f"\n===== Generating content.info for {skill_name} ({skill_id}) =====")

        info_path = OUTPUT_DIR / skill_id / INFO_FILENAME
        if info_path.exists() and not force:
            print(f"  - {INFO_FILENAME} already exists for skill '{skill_id}': {info_path}")
            print("    Use --force to overwrite.")
            continue

        # 準備 prompt；目前 prompt-chpaters.md 僅使用 {skill}
        prompt = prompt_template.replace("{skill}", skill_name)

        chapters = None

        for attempt in range(1, MAX_RETRIES_PER_SKILL + 1):
            if attempt > 1:
                print(f"  → Retry attempt {attempt}/{MAX_RETRIES_PER_SKILL} for {skill_id}...")

            raw = send_to_vertex_for_skill_info(client, prompt)
            if not raw:
                print("    ! Empty response from model.")
            else:
                parsed = extract_json_array(raw)
                if isinstance(parsed, list) and parsed:
                    chapters = parsed
                    break
                else:
                    print("    ! Parsed result is not a non-empty JSON array.")

            if attempt < MAX_RETRIES_PER_SKILL:
                delay = REQUEST_DELAY_SECONDS * attempt
                print(f"    Waiting {delay} seconds before next attempt...")
                time.sleep(delay)

        if chapters is None:
            print(f"  ! Failed to generate chapters for {skill_id}. Skipping this skill.")
            continue

        # 將章節陣列包裝成 content.info，包含基本 skill 資訊
        info_obj = {
            "skillId": skill_id,
            "skillName": skill_name,
            "skillNameEnglish": skill_en,
            "categoryName": category_name,
            "totalChapterNumber": len(chapters),
            "isChaptersCompleted": True,
            "chapters": chapters,
        }

        save_json(info_path, info_obj)

        # 在處理下一個 skill 之前稍作等待，降低連續呼叫導致 429 的風險
        time.sleep(REQUEST_DELAY_SECONDS)

    print("\n===== All skills processed. Skill info generation complete. =====")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Generate or overwrite content.info for skills.")
    parser.add_argument(
        "--force",
        action="store_true",
        help="覆寫已存在的 content.info。",
    )
    parser.add_argument(
        "--skill-id",
        type=str,
        help="只處理指定 id 的 skill（例如: typescript）。",
    )
    args = parser.parse_args()

    main(force=args.force, only_skill_id=args.skill_id)
