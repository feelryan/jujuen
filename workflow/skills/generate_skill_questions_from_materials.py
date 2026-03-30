import json
import re
import sys
import time
from pathlib import Path

from google import genai
from google.genai import types

# ================= Configuration =================

LOCATION = "global"
MODEL_NAME = "gemini-3.1-pro-preview"
REQUEST_DELAY_SECONDS = 2
MAX_RETRIES_PER_CHAPTER = 3
DEFAULT_TOTAL_QUESTIONS_PER_CHAPTER = 15

BASE_DIR = Path(__file__).resolve().parent
PROJECT_ID_FILE = BASE_DIR / "PROJECT_ID.txt"
OUTPUT_DIR = BASE_DIR / "output"
PROMPT_QUESTIONS_FILE = BASE_DIR / "prompt-skill-questions.md"
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


def send_to_vertex_for_questions(client: genai.Client, prompt: str) -> str | None:
    """Call Vertex AI to generate questions, return raw text."""

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
        response = client.models.generate_content(
            model=MODEL_NAME,
            contents=prompt,
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
        focus = q.get("focus", "")
        tags = ",".join(q.get("topicTags", []) or q.get("tags", []))
        zh = q.get("questionSummaryZh", "")
        en = q.get("questionSummaryEn", "")
        snippet = zh or en
        snippet = snippet[:80]
        lines.append(f"[{qid}] ({diff}/{qtype}) tags={tags} focus={focus} :: {snippet}")
    return "\n".join(lines)


# ================= Main =================


def main(force: bool = False, only_skill_id: str | None = None, only_chapter_id: str | None = None) -> None:
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

    if not OUTPUT_DIR.exists():
        print(f"Output directory not found: {OUTPUT_DIR}")
        print("請先使用 generate_skill_materials.py 產生各章節的 Markdown 教材，再產生題目。")
        return

    # Find all skill directories (each with content.info)
    skill_dirs: list[Path] = []
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

        print(f"\n===== Generating questions for skill '{skill_id}' =====")

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

        for idx, ch in enumerate(chapters, start=1):
            chapter_id = ch.get("id") or f"chapter{idx:02d}"
            if only_chapter_id and chapter_id != only_chapter_id:
                continue

            chapter_title = ch.get("t") or chapter_id
            chapter_en = ch.get("en") or chapter_title

            material_path = skill_dir / f"{chapter_id}.md"
            if not material_path.exists():
                print(f"  - [Skip] Material not found for {skill_id} {chapter_id}: {material_path}")
                continue

            questions_path = skill_dir / f"{chapter_id}.json"
            meta_path = skill_dir / f"{chapter_id}.questions-meta.json"

            print(f"\n  --- Chapter {chapter_id}: {chapter_title} ---")

            # Load or initialize meta
            meta: dict
            if meta_path.exists():
                meta = load_json_file(meta_path) or {}
            else:
                meta = {}

            total = meta.get("totalQuestionsNum")
            if not isinstance(total, int) or total <= 0:
                total = DEFAULT_TOTAL_QUESTIONS_PER_CHAPTER
                meta["totalQuestionsNum"] = total

            if force:
                # 重跑此章節：清除既有題目與 meta 中紀錄
                if questions_path.exists():
                    try:
                        questions_path.unlink()
                    except OSError as e:
                        print(f"  ! Could not delete existing questions file {questions_path}: {e}")
                meta["questions"] = []
                meta["isAllCompleted"] = False

            existing_meta_questions = meta.get("questions") or []
            existing_count = len(existing_meta_questions)

            # 既有 batch 檔案（例如 chapter01.questions-batch1.json, ...）
            batch_files = sorted(
                skill_dir.glob(f"{chapter_id}.questions-batch*.json"),
                key=lambda p: int(re.search(r"\.questions-batch(\d+)\.json$", p.name).group(1))
                if re.search(r"\.questions-batch(\d+)\.json$", p.name)
                else 0,
            )

            # 如果 meta 標示已完成，但最終 questions JSON 題數 < total，視為不一致，重新補題
            if not force and meta.get("isAllCompleted") and existing_count >= total:
                final_count = 0
                if questions_path.exists():
                    existing_questions_data = load_json_file(questions_path) or []
                    if isinstance(existing_questions_data, list):
                        final_count = len(existing_questions_data)

                if final_count >= total:
                    print(
                        f"  - Questions already completed for {skill_id} {chapter_id} "
                        f"(total={total}, final_json={final_count}). Skipping."
                    )
                    save_json_file(meta_path, meta)
                    continue

                print(
                    f"  ! Inconsistent state for {skill_id} {chapter_id}: "
                    f"meta says {existing_count}/{total} completed but JSON has {final_count}. "
                    "Will treat as incomplete and generate additional questions."
                )

                # 將 meta.questions 修剪到實際 JSON 題數，避免 remaining 為負
                if 0 < final_count < existing_count:
                    existing_meta_questions = existing_meta_questions[:final_count]
                    existing_count = len(existing_meta_questions)
                    meta["questions"] = existing_meta_questions
                meta["isAllCompleted"] = False

            remaining = max(total - existing_count, 0)
            if remaining <= 0:
                print(f"  - No remaining questions needed for {skill_id} {chapter_id}. Marking as completed.")
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
                .replace("{skill_name}", skill_name)
                .replace("{skill_category}", category_name)
                .replace("{chapter_id}", chapter_id)
                .replace("{chapter_title}", chapter_title)
                .replace("{chapter_en}", chapter_en)
                .replace("{questions_meta}", questions_meta_for_prompt)
                .replace("{total_questions_num}", str(total))
                .replace("{remaining_questions_num}", str(remaining))
            )

            full_prompt = (
                prompt
                + "\n\n---\n\n"  # 分隔指示與教材內容
                + "以下是完整的章節教材 Markdown 內容，請依此出題（避免重複既有題目）：\n\n"
                + material_text
                + ("\n\n---\n\n已存在題目摘要（供你避免重複）：\n" + existing_summary if existing_summary else "")
            )

            questions_array = None

            for attempt in range(1, MAX_RETRIES_PER_CHAPTER + 1):
                if attempt > 1:
                    print(f"    → Retry attempt {attempt}/{MAX_RETRIES_PER_CHAPTER} for {skill_id} {chapter_id}...")

                raw = send_to_vertex_for_questions(client, full_prompt)
                if not raw:
                    print("      ! Empty response from model.")
                else:
                    parsed = extract_json_array(raw)
                    if isinstance(parsed, list) and parsed:
                        questions_array = parsed
                        break
                    else:
                        print("      ! Parsed result is not a non-empty JSON array.")

                if attempt < MAX_RETRIES_PER_CHAPTER:
                    delay = REQUEST_DELAY_SECONDS * attempt
                    print(f"      Waiting {delay} seconds before next attempt...")
                    time.sleep(delay)

            if questions_array is None:
                print(f"  ! Failed to generate questions for {skill_id} {chapter_id} after retries. Skipping this chapter.")
                continue

            # Trim to remaining quota if model產生過多題目
            if len(questions_array) > remaining:
                print(f"  - Model returned {len(questions_array)} questions, trimming to remaining quota {remaining}.")
                questions_array = questions_array[:remaining]

            # 以 batch 形式儲存本次新題目：{chapterId}.questions-batch{batchId}.json
            # 計算下一個 batchId（從 1 開始遞增）
            next_batch_idx = 1
            if batch_files:
                max_idx = 0
                for p in batch_files:
                    m = re.search(r"\.questions-batch(\d+)\.json$", p.name)
                    if m:
                        max_idx = max(max_idx, int(m.group(1)))
                next_batch_idx = max_idx + 1

            batch_path = skill_dir / f"{chapter_id}.questions-batch{next_batch_idx}.json"
            save_json_file(batch_path, questions_array)
            batch_files.append(batch_path)

            # Append new questions and update meta
            start_index = len(existing_meta_questions)
            for i, q in enumerate(questions_array, start=1):
                # Ensure question has an id
                qid = q.get("id")
                if not qid:
                    seq = start_index + i
                    qid = f"{chapter_id}-q{seq:02d}"
                    q["id"] = qid

                # Build meta info entry
                question_text = ""
                # 新的 prompt 格式中，question 通常是一個句子陣列，每句含 t/en
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

            # Update meta state
            meta["questions"] = existing_meta_questions
            meta["isAllCompleted"] = len(existing_meta_questions) >= total

            save_json_file(meta_path, meta)

            # 若已達目標題數，合併所有 batch 檔為最終 {chapterId}.json，並刪除 batch 檔
            if meta["isAllCompleted"]:
                print("  - All questions for this chapter reached target. Merging batches into final JSON...")
                merged_questions = []

                # 先納入既有的最終 JSON（若存在且為陣列），避免覆蓋舊題目
                if questions_path.exists():
                    existing_final = load_json_file(questions_path) or []
                    if isinstance(existing_final, list):
                        merged_questions.extend(existing_final)

                merge_batch_files = sorted(
                    skill_dir.glob(f"{chapter_id}.questions-batch*.json"),
                    key=lambda p: int(re.search(r"\.questions-batch(\d+)\.json$", p.name).group(1))
                    if re.search(r"\.questions-batch(\d+)\.json$", p.name)
                    else 0,
                )

                for bp in merge_batch_files:
                    data = load_json_file(bp) or []
                    if isinstance(data, list):
                        merged_questions.extend(data)

                if merged_questions:
                    save_json_file(questions_path, merged_questions)

                    # 清理所有 batch 檔案
                    for bp in merge_batch_files:
                        try:
                            bp.unlink()
                        except OSError as e:
                            print(f"  ! Could not delete batch file {bp}: {e}")

            print(
                f"  - After this run: total stored questions = {len(existing_meta_questions)} / {total} "
                f"(completed={meta['isAllCompleted']})."
            )

            # 基本間隔，避免過於頻繁呼叫 API
            time.sleep(REQUEST_DELAY_SECONDS)

    print("\n===== All skills and chapters processed. Question generation complete. =====")


if __name__ == "__main__":
    force = "--force" in sys.argv
    only_skill_id = None
    only_chapter_id = None

    # 支援 --skill-id=<id> / --chapter-id=<id> 或空白分隔形式
    args = sys.argv[1:]
    i = 0
    while i < len(args):
        arg = args[i]
        if arg.startswith("--skill-id="):
            only_skill_id = arg.split("=", 1)[1]
        elif arg == "--skill-id" and i + 1 < len(args):
            only_skill_id = args[i + 1]
            i += 1
        elif arg.startswith("--chapter-id="):
            only_chapter_id = arg.split("=", 1)[1]
        elif arg == "--chapter-id" and i + 1 < len(args):
            only_chapter_id = args[i + 1]
            i += 1
        i += 1

    main(force=force, only_skill_id=only_skill_id, only_chapter_id=only_chapter_id)
