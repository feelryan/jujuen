import argparse
import json
import re
import time
from pathlib import Path

from google import genai
from google.genai import types

# ================= Configuration =================

# 使用與 generate_chapter_original_content.py 相同的專案設定
PROJECT_ID = "qwiklabs-gcp-00-0adfec6c0f1b"
LOCATION = "global"
MODEL_NAME = "gemini-3-pro-preview"

REQUEST_DELAY_SECONDS = 6
MAX_RETRIES_PER_CHAPTER = 3
MAX_LINES_FOR_QUIZ_CONTEXT = 240  # 每章最多提供多少原文句子給題目生成時參考

BASE_DIR = Path(__file__).resolve().parent
MENU_PATH_FILE = BASE_DIR / "menu-path.json"
OUTPUT_DIR = BASE_DIR / "output"
PROMPT_QUESTIONS_FILE = BASE_DIR / "prompt-questions.md"


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


def _strip_trailing_commas(json_str: str) -> str:
    """Best-effort removal of trailing commas before } or ]."""

    return re.sub(r",(\s*[}\]])", r"\1", json_str)


def extract_json_array(text: str):
    """Extract a JSON array from raw model response.

    優先嘗試把整個回應視為 JSON 陣列解析，若失敗再從中提取第一個陣列，
    並容忍少量尾逗號（trailing commas）。
    """

    if not text:
        print("    ! Empty response text.")
        return None

    stripped = text.strip()

    # 1) 若整段本身就是 JSON 陣列
    if stripped.startswith("["):
        try:
            return json.loads(stripped)
        except json.JSONDecodeError:
            cleaned = _strip_trailing_commas(stripped)
            try:
                return json.loads(cleaned)
            except json.JSONDecodeError as e:
                print(f"    ! Failed to decode JSON array as-is: {e}")

    # 2) 處理 ```json ... ``` 區塊
    match = re.search(r"```json\s*(\[.*?\])\s*```", text, re.DOTALL)
    if match:
        json_str = match.group(1)
    else:
        # 3) 從全文中取第一個看起來像陣列的片段
        match = re.search(r"(\[.*\])", text, re.DOTALL)
        json_str = match.group(0) if match else None

    if not json_str:
        print("    ! Could not find JSON array in response.")
        return None

    json_str = json_str.strip()
    try:
        return json.loads(json_str)
    except json.JSONDecodeError:
        cleaned = _strip_trailing_commas(json_str)
        try:
            return json.loads(cleaned)
        except json.JSONDecodeError as e:
            print(f"    ! Failed to decode extracted JSON array: {e}")
            return None


def send_to_vertex_for_questions(client: genai.Client, prompt: str) -> str | None:
    """Call Vertex AI to generate life-scenario questions for a chapter."""

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
        response_mime_type="application/json",
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


def load_menu_items():
    data = json.loads(MENU_PATH_FILE.read_text(encoding="utf-8"))
    return data.get("items", [])


def get_book_items(menu_items):
    """Pick book nodes from menu-path.json (parent != null)."""

    return [item for item in menu_items if item.get("parent") is not None]


def load_content_info(book_id: str) -> dict | None:
    info_path = OUTPUT_DIR / book_id / "content.info"
    if not info_path.exists():
        print(f"  ! content.info not found for book '{book_id}': {info_path}")
        return None
    try:
        return json.loads(info_path.read_text(encoding="utf-8"))
    except Exception as e:
        print(f"  ! Failed to read content.info for '{book_id}': {e}")
        return None


def load_content_json(book_id: str) -> dict | None:
    content_path = OUTPUT_DIR / book_id / "content.json"
    if not content_path.exists():
        print(f"  ! content.json not found for book '{book_id}': {content_path}")
        return None
    try:
        return json.loads(content_path.read_text(encoding="utf-8"))
    except Exception as e:
        print(f"  ! Failed to read content.json for '{book_id}': {e}")
        return None


def load_chapter_original_info(book_id: str, chapter_id: str) -> dict | None:
    info_path = OUTPUT_DIR / book_id / f"{chapter_id}_original.info"
    if not info_path.exists():
        print(f"  ! {chapter_id}_original.info not found for book '{book_id}': {info_path}")
        return None
    try:
        return json.loads(info_path.read_text(encoding="utf-8"))
    except Exception as e:
        print(f"  ! Failed to read {chapter_id}_original.info for '{book_id}': {e}")
        return None


def get_chapter_items_from_content(content_data: dict) -> list[dict]:
    """Return top-level chapter items (exclude quiz rows)."""

    items = content_data.get("items", [])
    chapters = []
    for item in items:
        if item.get("parent") is None and not str(item.get("id", "")).endswith("-quiz"):
            chapters.append(item)
    return chapters


# ================= Main Logic =================


def build_original_lines_for_chapter(original_info: dict) -> list[str]:
    """Flatten all sections' original sentences into a single list, with a cap."""

    sections = original_info.get("sections") or []
    lines: list[str] = []

    def sort_key(sec: dict):
        name = str(sec.get("sectionIndexOrName", ""))
        try:
            return int(name)
        except ValueError:
            return name

    for sec in sorted(sections, key=sort_key):
        original = sec.get("original") or []
        for line in original:
            if isinstance(line, str) and line.strip():
                lines.append(line.strip())
            if len(lines) >= MAX_LINES_FOR_QUIZ_CONTEXT:
                return lines

    return lines


def process_chapter_quiz(
    client: genai.Client,
    prompt_template: str,
    book: dict,
    chapter_item: dict,
) -> None:
    book_id = book["id"]
    book_t = book.get("t", book_id)
    book_en = book.get("en", book_id)

    chapter_id = chapter_item.get("id")
    chapter_title = chapter_item.get("t", chapter_id)

    print(f"  → Chapter {chapter_id}: {chapter_title}")

    quiz_path = OUTPUT_DIR / book_id / f"{chapter_id}-quiz.json"
    if quiz_path.exists():
        print("    - Quiz JSON already exists; skip (delete file if you want to regenerate).")
        return

    original_info = load_chapter_original_info(book_id, chapter_id)
    if not original_info:
        print("    ! No original.info for this chapter; skip quiz generation.")
        return

    if not bool(original_info.get("isAllCompleted")):
        print("    - Warning: original sections not fully completed (isAllCompleted != true); proceeding with available content.")

    original_lines = build_original_lines_for_chapter(original_info)
    if not original_lines:
        print("    ! No original lines found in _original.info; skip this chapter.")
        return

    original_lines_json = json.dumps(original_lines, ensure_ascii=False)

    prompt = (
        prompt_template
        .replace("{book_title_traditional}", book_t)
        .replace("{book_title_english}", book_en)
        .replace("{book_id}", book_id)
        .replace("{chapter_id}", chapter_id)
        .replace("{chapter_title}", chapter_title)
        .replace("{original_lines}", original_lines_json)
    )

    success = False
    for attempt in range(1, MAX_RETRIES_PER_CHAPTER + 1):
        if attempt > 1:
            print(f"    → Retry attempt {attempt}/{MAX_RETRIES_PER_CHAPTER} for quiz generation...")

        raw = send_to_vertex_for_questions(client, prompt)
        if not raw:
            print("      ! Empty response from model.")
        else:
            arr = extract_json_array(raw)
            if isinstance(arr, list) and arr:
                save_json(quiz_path, arr)
                success = True
                break
            else:
                print("      ! Parsed result is not a non-empty JSON array.")

        if attempt < MAX_RETRIES_PER_CHAPTER:
            delay = REQUEST_DELAY_SECONDS * attempt
            print(f"      Waiting {delay} seconds before retrying...")
            time.sleep(delay)

    if not success:
        print("    ! Giving up on quiz generation for this chapter for now (will try next run).")
        return

    # Rate-limit between chapters
    time.sleep(REQUEST_DELAY_SECONDS)


def main(book_id_filter: str | None = None) -> None:
    print(f"Initializing Vertex AI Client for project '{PROJECT_ID}' in '{LOCATION}'...")
    try:
        client = genai.Client(vertexai=True, project=PROJECT_ID, location=LOCATION)
    except Exception as e:
        print(f"Vertex AI initialization failed: {e}")
        print("請確認已執行 'gcloud auth application-default login'，且 PROJECT_ID 設定正確。")
        return

    try:
        prompt_template = load_text_file(PROMPT_QUESTIONS_FILE)
    except FileNotFoundError as e:
        print(e)
        return

    if not MENU_PATH_FILE.exists():
        print(f"Menu-path file not found: {MENU_PATH_FILE}")
        return

    menu_items = load_menu_items()
    books = get_book_items(menu_items)

    if not books:
        print("No book items found in menu-path.json (items with parent != null).")
        return

    # Filter books if a specific book_id is requested
    if book_id_filter:
        books = [b for b in books if b.get("id") == book_id_filter]
        if not books:
            print(f"Book with id '{book_id_filter}' not found in menu-path.json.")
            return

    print("Books detected from menu-path.json:")
    for b in books:
        print(f"  - {b.get('id')} : {b.get('t')} / {b.get('en')}")

    for book in books:
        book_id = book["id"]
        book_t = book.get("t", book_id)

        print(f"\n===== Generating life-scenario quizzes for {book_t} ({book_id}) =====")

        # Ensure this book has completed chapter names in content.info
        info_data = load_content_info(book_id)
        if not info_data:
            continue

        if not bool(info_data.get("isChatpersCompleted")):
            print("  - content.info indicates chapters are NOT completed; skip this book.")
            continue

        content_data = load_content_json(book_id)
        if not content_data:
            continue

        chapter_items = get_chapter_items_from_content(content_data)
        if not chapter_items:
            print("  ! No chapter items found in content.json; skip this book.")
            continue

        for chapter_item in chapter_items:
            process_chapter_quiz(client, prompt_template, book, chapter_item)

    print("\n===== Quiz generation complete for all requested books. =====")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description=(
            "Generate 5-8 life-scenario multiple-choice questions per chapter "
            "for ancient classics, based on {chapter}_original.info."
        )
    )
    parser.add_argument(
        "--book-id",
        type=str,
        default=None,
        help="只處理指定 book id（例如 'The Analects'）；若省略則處理所有書。",
    )
    args = parser.parse_args()

    main(book_id_filter=args.book_id)
