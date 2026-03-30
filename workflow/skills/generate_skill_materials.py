import json
import os
import sys
import time
from pathlib import Path

from google import genai
from google.genai import types

# ================= Configuration =================

LOCATION = "global"
MODEL_NAME = "gemini-3.1-pro-preview"
REQUEST_DELAY_SECONDS = 6
MAX_RETRIES_PER_CHAPTER = 5

BASE_DIR = Path(__file__).resolve().parent
PROJECT_ID_FILE = BASE_DIR / "PROJECT_ID.txt"
OUTPUT_DIR = BASE_DIR / "output"
PROMPT_MATERIALS_FILE = BASE_DIR / "prompt-materials.md"
INFO_FILENAME = "content.info"


# ================= Helper Functions =================


def load_text_file(path: Path) -> str:
    if not path.exists():
        raise FileNotFoundError(f"File not found: {path}")
    return path.read_text(encoding="utf-8")


def load_json_file(path: Path):
    if not path.exists():
        raise FileNotFoundError(f"JSON file not found: {path}")
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except json.JSONDecodeError as e:
        print(f"  ! Failed to decode JSON from {path}: {e}")
        return None


def save_text_file(path: Path, content: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content, encoding="utf-8")
    print(f"  - Saved Markdown: {path}")


def send_to_vertex_for_materials(client: genai.Client, prompt: str) -> str | None:
    """呼叫 Vertex AI 產生章節教材內容，回傳純文字 Markdown。"""

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
        temperature=0.5,
        top_p=0.95,
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
        prompt_template = load_text_file(PROMPT_MATERIALS_FILE)
    except FileNotFoundError as e:
        print(e)
        return

    if not OUTPUT_DIR.exists():
        print(f"Output directory not found: {OUTPUT_DIR}")
        print("請先使用 generate_skill_info.py 產生各 skill 的 content.info。")
        return

    # 找出所有包含 content.info 的 skill 目錄
    skill_dirs = []
    for child in OUTPUT_DIR.iterdir():
        if child.is_dir() and (child / INFO_FILENAME).exists():
            skill_dirs.append(child)

    if only_skill_id:
        skill_dirs = [d for d in skill_dirs if d.name == only_skill_id]
        if not skill_dirs:
            print(f"No skill directory with content.info found for id '{only_skill_id}'.")
            return

    if not skill_dirs:
        print("No skills with content.info found under output/. Nothing to do.")
        return

    print("Skills detected (from output/*/content.info):")
    for d in skill_dirs:
        print(f"  - {d.name}")

    for skill_dir in skill_dirs:
        skill_id = skill_dir.name
        info_path = skill_dir / INFO_FILENAME

        print(f"\n===== Generating materials for skill '{skill_id}' =====")

        info_data = load_json_file(info_path)
        if not info_data:
            print(f"  ! Skip skill '{skill_id}' due to invalid content.info")
            continue

        skill_name = info_data.get("skillName", skill_id)
        skill_en = info_data.get("skillNameEnglish", skill_name)
        category_name = info_data.get("categoryName", "")
        chapters = info_data.get("chapters") or []

        if not isinstance(chapters, list) or not chapters:
            print(f"  ! No chapters found in content.info for '{skill_id}'. Skipping.")
            continue

        print(f"  - Found {len(chapters)} chapters for {skill_name}.")

        for idx, ch in enumerate(chapters, start=1):
            chapter_id = ch.get("id") or f"chapter{idx:02d}"
            chapter_title = ch.get("t") or chapter_id
            chapter_en = ch.get("en") or chapter_title
            chapter_description = ch.get("description", "")

            # 每個章節輸出成：output/{skill_id}/{chapterId}.md
            md_filename = f"{chapter_id}.md"
            md_path = skill_dir / md_filename

            if md_path.exists() and not force:
                print(f"  - Skipping existing file: {md_path}")
                continue

            print(f"  - Generating material for chapter {chapter_id}: {chapter_title}")

            chapter_info = {
                "skillId": skill_id,
                "skillName": skill_name,
                "skillNameEnglish": skill_en,
                "categoryName": category_name,
                "chapterIndex": idx,
                "chapterId": chapter_id,
                "chapterTitle": chapter_title,
                "chapterTitleEnglish": chapter_en,
                "chapterDescription": chapter_description,
            }

            chapter_info_json = json.dumps(chapter_info, ensure_ascii=False, indent=2)

            prompt = (
                prompt_template
                .replace("{skill_name}", skill_name)
                .replace("{skill_en}", skill_en)
                .replace("{skill}", skill_name)
                .replace("{skill_id}", skill_id)
                .replace("{skill_category}", category_name)
                .replace("{chapter_id}", chapter_id)
                .replace("{chapter_title}", chapter_title)
                .replace("{chapter_en}", chapter_en)
                .replace("{chapter_description}", chapter_description)
                .replace("{chapter_info}", chapter_info_json)
            )

            content = None

            for attempt in range(1, MAX_RETRIES_PER_CHAPTER + 1):
                if attempt > 1:
                    print(f"    → Retry attempt {attempt}/{MAX_RETRIES_PER_CHAPTER} for {skill_id}.{chapter_id}...")

                content = send_to_vertex_for_materials(client, prompt)
                if content:
                    break
                else:
                    print("    ! Empty or failed response from model.")

                if attempt < MAX_RETRIES_PER_CHAPTER:
                    delay = REQUEST_DELAY_SECONDS * attempt
                    print(f"    Waiting {delay} seconds before next attempt...")
                    time.sleep(delay)

            if not content:
                print(f"    ! Failed to generate material for {skill_id}.{chapter_id} after retries. Skipping.")
                continue

            save_text_file(md_path, content)

            # 避免過於頻繁呼叫 API（成功後的基本間隔）
            time.sleep(REQUEST_DELAY_SECONDS)

    print("\n===== All skills and chapters processed. Material generation complete. =====")


if __name__ == "__main__":
    force = "--force" in sys.argv
    only_skill_id = None
    # 簡單處理 --skill-id=<id> 形式，或 --skill-id id
    for i, arg in enumerate(sys.argv):
        if arg.startswith("--skill-id="):
            only_skill_id = arg.split("=", 1)[1]
        elif arg == "--skill-id" and i + 1 < len(sys.argv):
            only_skill_id = sys.argv[i + 1]

    main(force=force, only_skill_id=only_skill_id)
