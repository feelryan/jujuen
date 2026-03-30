import argparse
import json
import time
from pathlib import Path

from google import genai
from google.genai import types

# ================= Configuration =================

LOCATION = "global"
MODEL_NAME = "gemini-3-pro-preview"

REQUEST_DELAY_SECONDS = 2
MAX_RETRIES_PER_TOPIC = 10

BASE_DIR = Path(__file__).resolve().parent
PROJECT_ID_FILE = BASE_DIR / "PROJECT_ID.txt"
OUTPUT_DIR = BASE_DIR / "output"
PROMPT_STRATEGY_SECTION_FILE = BASE_DIR / "prompt-strategy-section-material.md"


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


def send_to_vertex_ai_with_pdfs_and_topic(
    client: genai.Client,
    prompt_content: str,
    resume_pdf_path: Path,
    jd_pdf_path: Path,
) -> str | None:
    """呼叫 Vertex AI，將文字指示與履歷 / JD PDF 一起送入，回傳單一策略主題的 Markdown。

    - contents[0]: textual prompt（含策略主題資訊與 overview）
    - contents[1]: resume PDF bytes
    - contents[2]: JD PDF bytes
    """

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
        print(f"  - Reading resume PDF bytes: {resume_pdf_path}")
        resume_bytes = resume_pdf_path.read_bytes()
        resume_part = types.Part.from_bytes(
            data=resume_bytes,
            mime_type="application/pdf",
        )

        print(f"  - Reading JD PDF bytes: {jd_pdf_path}")
        jd_bytes = jd_pdf_path.read_bytes()
        jd_part = types.Part.from_bytes(
            data=jd_bytes,
            mime_type="application/pdf",
        )

        contents: list[types.Part | str] = [prompt_content, resume_part, jd_part]

        response = client.models.generate_content(
            model=MODEL_NAME,
            contents=contents,
            config=config,
        )
        return response.text
    except Exception as e:
        print(f"    ! Vertex AI 呼叫失敗: {e}")
        return None


# ================= Main =================


def main(
    resume_path: Path,
    jd_path: Path,
    dir_name: str,
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
        prompt_template = load_text_file(PROMPT_STRATEGY_SECTION_FILE)
    except FileNotFoundError as e:
        print(e)
        return

    if not resume_path.exists():
        print(f"Resume PDF file not found: {resume_path}")
        return

    if not jd_path.exists():
        print(f"JD PDF file not found: {jd_path}")
        return

    project_dir = OUTPUT_DIR / dir_name
    strategy_path = project_dir / "strategy.json"

    if not strategy_path.exists():
        print(f"strategy.json not found: {strategy_path}")
        print("請先執行 generate_strategy_sections.py 產生該目錄下的 strategy.json。")
        return

    try:
        strategy_obj = load_json_file(strategy_path)
    except Exception as e:
        print(f"  ! Failed to load strategy.json: {e}")
        return

    items = strategy_obj.get("items") or []
    if not isinstance(items, list) or not items:
        print("  ! strategy.json.items 為空，無策略主題可產生。")
        return

    # 只針對主策略節點（排除 id 以 -quiz 結尾者）產生 Markdown
    main_topics = [it for it in items if isinstance(it, dict) and not str(it.get("id", "")).endswith("-quiz")]

    print(f"Strategy topics found in {dir_name}/strategy.json:")
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

        topic_dir = project_dir / "strategy"
        md_path = topic_dir / f"{topic_id}.md"

        print(f"\n===== Generating strategy material for topic '{topic_id}' ({topic_t} | {topic_en}) =====")

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

            raw = send_to_vertex_ai_with_pdfs_and_topic(client, prompt, resume_path, jd_path)
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

    print("\n===== All strategy topics processed. Strategy materials generation complete. =====")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description=(
            "Generate per-strategy-topic Markdown files from workflow/job/output/{dir_name}/strategy.json "
            "using resume and JD PDFs."
        )
    )
    parser.add_argument(
        "--resume",
        required=True,
        help="Path to the resume PDF file.",
    )
    parser.add_argument(
        "--jd",
        required=True,
        help="Path to the Job Description PDF file.",
    )
    parser.add_argument(
        "--dir-name",
        required=True,
        help="Directory name under output/ where strategy.json is located.",
    )
    parser.add_argument(
        "--topic-id",
        required=False,
        help="Only generate material for the specified strategy topic id.",
    )
    parser.add_argument(
        "--force",
        action="store_true",
        help="Overwrite existing Markdown files if they already exist.",
    )

    args = parser.parse_args()

    main(
        resume_path=Path(args.resume),
        jd_path=Path(args.jd),
        dir_name=args.dir_name,
        force=args.force,
        only_topic_id=args.topic_id,
    )
