import argparse
import json
import re
import time
from pathlib import Path

from google import genai
from google.genai import types

# ================= Configuration =================

PROJECT_ID = "qwiklabs-gcp-02-6deaa64ae3d1"
LOCATION = "global"
MODEL_NAME = "gemini-3-pro-preview"

REQUEST_DELAY_SECONDS = 6
MAX_RETRIES_PER_CALL = 5

BASE_DIR = Path(__file__).resolve().parent
MENU_PATH_FILE = BASE_DIR / "menu-path.json"
OUTPUT_DIR = BASE_DIR / "output"
PROMPT_ORIGINAL_FILE = BASE_DIR / "prompt-chapter-original.md"


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
    """Extract a JSON object from raw model response.

    We expect the model to output a pure JSON object, but defensively
    handle ```json fenced blocks as well.
    """

    if not text:
        print("    ! Empty response text.")
        return None

    stripped = text.strip()

    # 1) If the whole text looks like an object, try directly
    if stripped.startswith("{") and stripped.endswith("}"):
        try:
            return json.loads(stripped)
        except json.JSONDecodeError:
            pass

    # 2) Try ```json ... ``` fenced block
    match = re.search(r"```json\s*(\{.*?\})\s*```", text, re.DOTALL)
    if match:
        json_str = match.group(1)
    else:
        # 3) Fallback: first {...} block
        match = re.search(r"(\{.*\})", text, re.DOTALL)
        json_str = match.group(0) if match else None

    if not json_str:
        print("    ! Could not find JSON object in response.")
        return None

    try:
        return json.loads(json_str)
    except json.JSONDecodeError as e:
        print(f"    ! Failed to decode JSON object: {e}")
        return None


def send_to_vertex_for_original(client: genai.Client, prompt: str) -> str | None:
    """Call Vertex AI to generate original text sections for a chapter."""

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


def get_chapter_items_from_content(content_data: dict) -> list[dict]:
    """Return top-level chapter items (exclude quiz rows)."""

    items = content_data.get("items", [])
    chapters = []
    for item in items:
        if item.get("parent") is None and not str(item.get("id", "")).endswith("-quiz"):
            chapters.append(item)
    return chapters


def ensure_original_info_structure(data: dict | None) -> dict:
    """Normalize {chapter}_original.info structure."""

    if not isinstance(data, dict):
        data = {}

    total = data.get("totalSectionNumber")
    if not isinstance(total, int):
        total = 0

    sections = data.get("sections") or []
    if not isinstance(sections, list):
        sections = []

    norm_sections = []
    for s in sections:
        if not isinstance(s, dict):
            continue
        name = s.get("sectionIndexOrName")
        original = s.get("original") or []
        if not name or not isinstance(original, list):
            continue
        # Keep as-is
        norm_sections.append({
            "sectionIndexOrName": str(name),
            "original": [str(x) for x in original if isinstance(x, str)],
        })

    result = {
        "totalSectionNumber": total,
        "sections": norm_sections,
        "isAllCompleted": False,
    }

    # compute completion flag
    if total > 0 and len(norm_sections) >= total:
        result["isAllCompleted"] = True

    return result


def load_or_init_chapter_original_info(book_id: str, chapter_id: str) -> tuple[dict, Path]:
    info_path = OUTPUT_DIR / book_id / f"{chapter_id}_original.info"
    if info_path.exists():
        try:
            raw = json.loads(info_path.read_text(encoding="utf-8"))
        except Exception as e:
            print(f"  ! Failed to read {chapter_id}_original.info for '{book_id}': {e}")
            raw = {}
    else:
        raw = {}

    info = ensure_original_info_structure(raw)
    save_json(info_path, info)  # keep normalized
    return info, info_path


def save_original_info(info_path: Path, info: dict) -> None:
    save_json(info_path, info)


def build_existing_info_for_prompt(info: dict) -> str:
    """Build a compact JSON string to send into the prompt as {existing_info}.

    為了節省 token，這裡只帶出已存在段落的索引／名稱，不再重送完整原文內容。
    """

    total = info.get("totalSectionNumber", 0)
    sections = info.get("sections") or []
    simple_sections = [
        {"sectionIndexOrName": s.get("sectionIndexOrName")}
        for s in sections
        if s.get("sectionIndexOrName") is not None
    ]

    prompt_info = {
        "totalSectionNumber": total,
        "sections": simple_sections,
    }
    return json.dumps(prompt_info, ensure_ascii=False)


# ================= Main Logic =================


def process_chapter_original(
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

    info, info_path = load_or_init_chapter_original_info(book_id, chapter_id)
    if info.get("isAllCompleted"):
        print("    - Original content already completed; skip.")
        return

    existing_info_json = build_existing_info_for_prompt(info)

    prompt = (
        prompt_template
        .replace("{book_title_traditional}", book_t)
        .replace("{book_title_english}", book_en)
        .replace("{book_id}", book_id)
        .replace("{chapter_id}", chapter_id)
        .replace("{chapter_title}", chapter_title)
        .replace("{existing_info}", existing_info_json)
    )

    for attempt in range(1, MAX_RETRIES_PER_CALL + 1):
        if attempt > 1:
            print(f"    → Retry attempt {attempt}/{MAX_RETRIES_PER_CALL}...")

        raw = send_to_vertex_for_original(client, prompt)
        if not raw:
            print("      ! Empty response from model.")
        else:
            obj = extract_json_object(raw)
            if isinstance(obj, dict):
                total_new = obj.get("totalSectionNumber")
                sections_new = obj.get("sections") or []

                # Merge totalSectionNumber
                total_old = info.get("totalSectionNumber", 0)
                if isinstance(total_new, int) and total_new > 0:
                    if total_old == 0:
                        info["totalSectionNumber"] = total_new
                    else:
                        # Keep old value; ignore conflicting new value
                        pass

                # Merge sections by sectionIndexOrName
                existing_names = {
                    s.get("sectionIndexOrName")
                    for s in info.get("sections", [])
                }

                merged_sections = info.get("sections", [])
                added_count = 0
                for s in sections_new:
                    if not isinstance(s, dict):
                        continue
                    name = s.get("sectionIndexOrName")
                    original_list = s.get("original") or []
                    if not name or not isinstance(original_list, list):
                        continue
                    if name in existing_names:
                        continue
                    clean_original = [
                        str(x) for x in original_list if isinstance(x, str) and x.strip()
                    ]
                    if not clean_original:
                        continue
                    merged_sections.append(
                        {
                            "sectionIndexOrName": str(name),
                            "original": clean_original,
                        }
                    )
                    existing_names.add(name)
                    added_count += 1

                info["sections"] = merged_sections

                total = info.get("totalSectionNumber", 0)
                if total > 0 and len(merged_sections) >= total:
                    info["isAllCompleted"] = True
                else:
                    info["isAllCompleted"] = False

                save_original_info(info_path, info)
                print(
                    f"    - Merged {added_count} new sections; "
                    f"now {len(merged_sections)}/{info.get('totalSectionNumber', 0)} sections."
                )

                break
            else:
                print("      ! Parsed result is not a JSON object.")

        if attempt < MAX_RETRIES_PER_CALL:
            delay = REQUEST_DELAY_SECONDS * attempt
            print(f"      Waiting {delay} seconds before retrying...")
            time.sleep(delay)

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
        prompt_template = load_text_file(PROMPT_ORIGINAL_FILE)
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

        print(f"\n===== Collecting original chapter content for {book_t} ({book_id}) =====")

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
            process_chapter_original(client, prompt_template, book, chapter_item)

    print("\n===== Original content collection pass complete. You can run this script multiple times until all {chapter}_original.info files show isAllCompleted = true. =====")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description=(
            "Iteratively collect original text for each chapter into {chapter}_original.info, "
            "similar to generate_chapter_names.py."
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
