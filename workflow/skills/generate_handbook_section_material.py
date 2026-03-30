import argparse
import json
import time
from pathlib import Path

from google import genai
from google.genai import types

# ================= Configuration =================

LOCATION = "global"
MODEL_NAME = "gemini-3.1-pro-preview"

REQUEST_DELAY_SECONDS = 2
MAX_RETRIES_PER_TOPIC = 10

BASE_DIR = Path(__file__).resolve().parent
PROJECT_ID_FILE = BASE_DIR / "PROJECT_ID.txt"
OUTPUT_DIR = BASE_DIR / "output"
PROMPT_HANDBOOK_SECTION_FILE = BASE_DIR / "prompt-handbook-section-material.md"


# ================= Helper Functions =================


def load_text_file(path: Path) -> str:
    if not path.exists():
        raise FileNotFoundError(f"File not found: {path}")
    return path.read_text(encoding="utf-8")


def load_json_file(path: Path):
    if not path.exists():
        raise FileNotFoundError(f"JSON file not found: {path}")
    return json.loads(path.read_text(encoding="utf-8"))


def save_text_file(path: Path, content: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content, encoding="utf-8")
    print(f"  - Saved Markdown: {path}")


def send_to_vertex_for_handbook_topic(
    client: genai.Client,
    prompt_content: str,
) -> str | None:
    """呼叫 Vertex AI，回傳單一 handbook 章節的 Markdown。"""

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
        top_p=0.9,
        safety_settings=safety_settings,
    )

    try:
        response = client.models.generate_content(
            model=MODEL_NAME,
            contents=prompt_content,
            config=config,
        )
        return response.text
    except Exception as e:
        print(f"    ! Vertex AI 呼叫失敗: {e}")
        return None



def discover_skills_with_handbook() -> list[str]:
    """掃描 output 目錄，找出所有已產生 handbook.json 的 skill。"""

    if not OUTPUT_DIR.exists():
        return []

    skill_ids: list[str] = []
    for child in OUTPUT_DIR.iterdir():
        if child.is_dir() and (child / "handbook.json").exists():
            skill_ids.append(child.name)

    return sorted(skill_ids)


# ================= Main =================


def main(
    skill_ids: list[str],
    force: bool = False,
    only_topic_id: str | None = None,
) -> None:
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
        prompt_template = load_text_file(PROMPT_HANDBOOK_SECTION_FILE)
    except FileNotFoundError as e:
        print(e)
        return

    if not skill_ids:
        print("No skills to process (skill_ids is empty).")
        return

    for skill_id in skill_ids:
        print(f"\n===== Processing handbook materials for skill '{skill_id}' =====")

        skill_dir = OUTPUT_DIR / skill_id
        handbook_path = skill_dir / "handbook.json"

        if not handbook_path.exists():
            print(f"  - handbook.json not found for skill '{skill_id}': {handbook_path}")
            print("    請先執行 generate_handbook_sections.py 產生 handbook.json。")
            continue

        try:
            handbook_obj = load_json_file(handbook_path)
        except Exception as e:
            print(f"  ! Failed to load handbook.json for skill '{skill_id}': {e}")
            continue

        items = handbook_obj.get("items") or []
        if not isinstance(items, list) or not items:
            print("  ! handbook.json.items 為空，無章節可產生。")
            continue

        # 只針對主 handbook 章節（排除 id 以 -quiz 結尾者）產生 Markdown
        main_topics = [it for it in items if isinstance(it, dict) and not str(it.get("id", "")).endswith("-quiz")]

        # 取得 skill 顯示名稱（若有）
        skill_name = handbook_obj.get("title") or skill_id

        print(f"Handbook topics for skill '{skill_id}' in handbook.json:")
        for it in main_topics:
            print(f"  - {it.get('id')} : {it.get('t')} | {it.get('en')}")

        for it in main_topics:
            topic_id = it.get("id")
            if not topic_id:
                continue

            if only_topic_id and topic_id != only_topic_id:
                continue

            topic_t = it.get("t", topic_id)
            topic_en = it.get("en", topic_t)
            topic_desc = it.get("description", "")

            topic_dir = skill_dir / "handbook"
            md_path = topic_dir / f"{topic_id}.md"

            print(f"\n===== Generating handbook material for skill '{skill_id}' topic '{topic_id}' ({topic_t} | {topic_en}) =====")

            if md_path.exists() and not force:
                print(f"  - Markdown already exists: {md_path}")
                print("    Use --force to overwrite.")
                continue

            # 準備 overview（僅給模型參考，不直接輸出）
            all_topics_overview_lines: list[str] = []
            for other in main_topics:
                sid = other.get("id")
                tt = other.get("t")
                ee = other.get("en")
                all_topics_overview_lines.append(f"- {sid}: {tt} | {ee}")
            all_topics_overview = "\n".join(all_topics_overview_lines)

            prompt = (
                prompt_template
                .replace("{{SKILL_ID}}", skill_id)
                .replace("{{SKILL_NAME}}", skill_name)
                .replace("{{TOPIC_ID}}", topic_id)
                .replace("{{TOPIC_T}}", topic_t)
                .replace("{{TOPIC_EN}}", topic_en)
                .replace("{{TOPIC_DESCRIPTION}}", topic_desc)
                .replace("{{ALL_TOPICS_OVERVIEW}}", all_topics_overview)
            )

            content_text = None

            for attempt in range(1, MAX_RETRIES_PER_TOPIC + 1):
                if attempt > 1:
                    print(f"  → Retry attempt {attempt}/{MAX_RETRIES_PER_TOPIC}...")

                raw = send_to_vertex_for_handbook_topic(client, prompt)
                if raw:
                    content_text = raw.strip()
                    if content_text:
                        break
                    else:
                        print("    ! Empty content returned from model.")
                else:
                    print("    ! Empty response from model.")

                if attempt < MAX_RETRIES_PER_TOPIC:
                    delay = REQUEST_DELAY_SECONDS * attempt
                    print(f"    Waiting {delay} seconds before next attempt...")
                    time.sleep(delay)

            if not content_text:
                print(f"  ! Failed to generate content for topic '{topic_id}' after retries. Skipping.")
                continue

            save_text_file(md_path, content_text)

            # 基本間隔，避免過於頻繁呼叫 API
            time.sleep(REQUEST_DELAY_SECONDS)

    print("\n===== All skills and handbook topics processed. Handbook materials generation complete. =====")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description=(
            "Generate per-handbook-topic Markdown files from workflow/skills/output/{skill}/handbook.json. "
            "If --skill-id is omitted, all skills with handbook.json under output/ will be processed."
        )
    )
    parser.add_argument(
        "--skill-id",
        required=False,
        help="Skill id (directory name under output/) for which to generate handbook materials. If omitted, process all skills with handbook.json.",
    )
    parser.add_argument(
        "--topic-id",
        required=False,
        help="Only generate material for the specified handbook topic id.",
    )
    parser.add_argument(
        "--force",
        action="store_true",
        help="Overwrite existing Markdown files if they already exist.",
    )

    args = parser.parse_args()

    if args.skill_id:
        skill_ids = [args.skill_id]
    else:
        print("No --skill-id provided. Auto-discovering all skills with handbook.json under output/ ...")
        skill_ids = discover_skills_with_handbook()
        if not skill_ids:
            print("No skills with handbook.json found under output/. Nothing to do.")
            raise SystemExit(0)

    main(
        skill_ids=skill_ids,
        force=args.force,
        only_topic_id=args.topic_id,
    )
