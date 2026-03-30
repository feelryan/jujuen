import argparse
import json
import re
import time
from pathlib import Path

from google import genai
from google.genai import types

# ================= Configuration =================

LOCATION = "global"
MODEL_NAME = "gemini-3-pro-preview"
REQUEST_DELAY_SECONDS = 2
MAX_RETRIES_PER_TOPIC = 3
DEFAULT_TOTAL_QUESTIONS_PER_TOPIC = 15

BASE_DIR = Path(__file__).resolve().parent
PROJECT_ID_FILE = BASE_DIR / "PROJECT_ID.txt"
OUTPUT_DIR = BASE_DIR / "output"
PROMPT_QUESTIONS_FILE = BASE_DIR / "prompt-strategy-questions.md"
STRATEGY_FILENAME = "strategy.json"


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


def save_json_file(path: Path, data) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)
    print(f"  - Saved JSON: {path}")


def extract_json_array(text: str):
    """Extract a JSON array from model response, handling optional ```json fences."""

    match = re.search(r"```json\s*(\[.*?\])\s*```", text, re.DOTALL)
    if match:
        json_str = match.group(1)
    else:
        match = re.search(r"(\[.*\])", text, re.DOTALL)
        json_str = match.group(0) if match else None

    if not json_str:
        print("      ! Could not find a JSON array in the response.")
        return None

    try:
        return json.loads(json_str)
    except json.JSONDecodeError as e:
        print(f"      ! Failed to decode extracted JSON. Error: {e}")
        return None


def send_to_vertex_for_questions_with_pdfs(
    client: genai.Client,
    prompt: str,
    resume_pdf_path: Path,
    jd_pdf_path: Path,
) -> str | None:
    """Call Vertex AI to generate questions, sending prompt + resume/JD PDFs, return raw text."""

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
        temperature=0.4,
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

        contents: list[types.Part | str] = [prompt, resume_part, jd_part]

        response = client.models.generate_content(
            model=MODEL_NAME,
            contents=contents,
            config=config,
        )
        return response.text
    except Exception as e:
        print(f"    ! Vertex AI call failed: {e}")
        return None


def build_existing_questions_summary(meta: dict) -> str:
    """Build a lightweight text summary from questions-meta for prompt context."""

    questions = meta.get("questions", []) or []
    lines: list[str] = []
    for q in questions:
        qid = q.get("id", "")
        diff = q.get("difficulty", "") or q.get("level", "")
        qtype = q.get("type", "")
        tags = ",".join(q.get("topicTags", []) or q.get("tags", []))
        zh = q.get("questionSummaryZh", "")
        en = q.get("questionSummaryEn", "")
        snippet = zh or en
        snippet = snippet[:80]
        lines.append(f"[{qid}] ({diff}/{qtype}) tags={tags} :: {snippet}")
    return "\n".join(lines)


# ================= Main =================


def main(
    resume_path: Path,
    jd_path: Path,
    dir_name: str,
    force: bool = False,
    only_topic_id: str | None = None,
) -> None:
    # Read PROJECT_ID
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
        prompt_template = load_text_file(PROMPT_QUESTIONS_FILE)
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
    strategy_path = project_dir / STRATEGY_FILENAME

    if not strategy_path.exists():
        print(f"strategy.json not found: {strategy_path}")
        print("請先執行 generate_strategy_sections.py 產生該目錄下的 strategy.json。")
        return

    strategy_obj = load_json_file(strategy_path)
    if not strategy_obj:
        print("  ! Invalid strategy.json, aborting.")
        return

    items = strategy_obj.get("items") or []
    if not isinstance(items, list) or not items:
        print("  ! strategy.json.items 為空，無策略主題可產生題目。")
        return

    # 只針對主策略節點（排除 id 以 -quiz 結尾者）產生題目
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

        topic_title = it.get("t", topic_id)
        topic_en = it.get("en", topic_title)

        material_dir = project_dir / "strategy"
        material_path = material_dir / f"{topic_id}.md"
        if not material_path.exists():
            print(f"  - [Skip] Strategy material not found for topic {topic_id}: {material_path}")
            continue

        questions_path = material_dir / f"{topic_id}.json"
        meta_path = material_dir / f"{topic_id}.questions-meta.json"

        print(f"\n  --- Topic {topic_id}: {topic_title} ---")

        # Load or initialize meta
        meta: dict
        if meta_path.exists():
            meta = load_json_file(meta_path) or {}
        else:
            meta = {}

        total = meta.get("totalQuestionsNum")
        if not isinstance(total, int) or total <= 0:
            total = DEFAULT_TOTAL_QUESTIONS_PER_TOPIC
            meta["totalQuestionsNum"] = total

        if force:
            # 重跑此主題：清除既有題目與 meta 中紀錄
            if questions_path.exists():
                try:
                    questions_path.unlink()
                except OSError as e:
                    print(f"  ! Could not delete existing questions file {questions_path}: {e}")
            meta["questions"] = []
            meta["isAllCompleted"] = False

        existing_meta_questions = meta.get("questions") or []
        existing_count = len(existing_meta_questions)

        remaining = max(total - existing_count, 0)
        if remaining <= 0 and not force:
            print(f"  - No remaining questions needed for topic {topic_id}. Marking as completed.")
            meta["isAllCompleted"] = True
            save_json_file(meta_path, meta)
            continue

        print(f"  - Existing questions: {existing_count}, target: {total}, remaining: {remaining}")

        try:
            material_text = load_text_file(material_path)
        except FileNotFoundError as e:
            print(f"  ! {e}")
            continue

        questions_meta_for_prompt = json.dumps(meta, ensure_ascii=False, indent=2)
        existing_summary = build_existing_questions_summary(meta)

        prompt = (
            prompt_template
            .replace("{topic_id}", topic_id)
            .replace("{topic_title}", topic_title)
            .replace("{topic_en}", topic_en)
            .replace("{questions_meta}", questions_meta_for_prompt)
            .replace("{total_questions_num}", str(total))
            .replace("{remaining_questions_num}", str(remaining))
        )

        full_prompt = (
            prompt
            + "\n\n---\n\n"  # 分隔指示與策略內容
            + "以下是完整的策略主題 Markdown 內容，請依此出題（避免重複既有題目）：\n\n"
            + material_text
            + ("\n\n---\n\n已存在題目摘要（供你避免重複）：\n" + existing_summary if existing_summary else "")
        )

        questions_array = None

        for attempt in range(1, MAX_RETRIES_PER_TOPIC + 1):
            if attempt > 1:
                print(f"    → Retry attempt {attempt}/{MAX_RETRIES_PER_TOPIC} for topic {topic_id}...")

            raw = send_to_vertex_for_questions_with_pdfs(client, full_prompt, resume_path, jd_path)
            if not raw:
                print("      ! Empty response from model.")
            else:
                parsed = extract_json_array(raw)
                if isinstance(parsed, list) and parsed:
                    questions_array = parsed
                    break
                else:
                    print("      ! Parsed result is not a non-empty JSON array.")

            if attempt < MAX_RETRIES_PER_TOPIC:
                delay = REQUEST_DELAY_SECONDS * attempt
                print(f"      Waiting {delay} seconds before next attempt...")
                time.sleep(delay)

        if questions_array is None:
            print(f"  ! Failed to generate questions for topic {topic_id} after retries. Skipping this topic.")
            continue

        # Trim to remaining quota if model 產生過多題目
        if len(questions_array) > remaining:
            print(f"  - Model returned {len(questions_array)} questions, trimming to remaining quota {remaining}.")
            questions_array = questions_array[:remaining]

        # 讀取既有最終 JSON（若存在且為陣列），避免覆蓋舊題目
        existing_questions_data = []
        if questions_path.exists():
            existing_questions_data = load_json_file(questions_path) or []
            if not isinstance(existing_questions_data, list):
                existing_questions_data = []

        # Append new questions and update meta
        start_index = len(existing_meta_questions)
        for i, q in enumerate(questions_array, start=1):
            # Ensure question has an id/no（若模型只給 no 或只給 id，也嘗試補齊）
            qid = q.get("id") or q.get("no")
            if not qid:
                seq = start_index + i
                qid = f"{topic_id}-q{seq:02d}"
                q["id"] = qid
                q["no"] = str(seq)

            # Build meta info entry
            question_text = ""
            q_field = q.get("question")
            if isinstance(q_field, dict):
                question_text = q_field.get("t") or q_field.get("en") or ""
            elif isinstance(q_field, list) and q_field:
                first = q_field[0]
                if isinstance(first, dict):
                    question_text = first.get("t") or first.get("en") or ""
            elif isinstance(q_field, str):
                question_text = q_field

            info_entry = {
                "id": qid,
                "difficulty": q.get("difficulty") or q.get("level"),
                "type": q.get("type"),
                "topicTags": q.get("topicTags") or q.get("tags") or (q.get("keywords", "").split(",") if q.get("keywords") else []),
                "focus": q.get("focus", ""),
                "questionSummaryZh": question_text[:80],
                "questionSummaryEn": "",
            }

            existing_meta_questions.append(info_entry)
            existing_questions_data.append(q)

        # Update meta state
        meta["questions"] = existing_meta_questions
        meta["isAllCompleted"] = len(existing_meta_questions) >= total

        save_json_file(meta_path, meta)
        save_json_file(questions_path, existing_questions_data)

        print(
            f"  - After this run: total stored questions = {len(existing_meta_questions)} / {total} "
            f"(completed={meta['isAllCompleted']})."
        )

        # 基本間隔，避免過於頻繁呼叫 API
        time.sleep(REQUEST_DELAY_SECONDS)

    print("\n===== All strategy topics processed. Question generation complete. =====")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description=(
            "Generate question JSON files for each strategy topic under workflow/job/output/{dir_name}/strategy/ "
            "based on strategy Markdown, resume PDF, and JD PDF."
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
        help="Directory name under output/ where strategy.json and strategy/*.md are located.",
    )
    parser.add_argument(
        "--topic-id",
        required=False,
        help="Only generate questions for the specified strategy topic id.",
    )
    parser.add_argument(
        "--force",
        action="store_true",
        help="Regenerate questions even if meta indicates completion; overwrite existing question files.",
    )

    args = parser.parse_args()

    main(
        resume_path=Path(args.resume),
        jd_path=Path(args.jd),
        dir_name=args.dir_name,
        force=args.force,
        only_topic_id=args.topic_id,
    )
