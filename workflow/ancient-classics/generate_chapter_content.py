import argparse
import json
import re
import time
from pathlib import Path

from google import genai
from google.genai import types

# ================= Configuration =================

PROJECT_ID = "qwiklabs-gcp-00-0adfec6c0f1b"
LOCATION = "global"
MODEL_NAME = "gemini-3-pro-preview"

REQUEST_DELAY_SECONDS = 4
MAX_RETRIES_PER_SEGMENT = 6

BASE_DIR = Path(__file__).resolve().parent
MENU_PATH_FILE = BASE_DIR / "menu-path.json"
OUTPUT_DIR = BASE_DIR / "output"
PROMPT_CONTENT_FILE = BASE_DIR / "prompt-content.md"


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

    # Example: {"a": 1,} -> {"a": 1}
    #          [1, 2, ]  -> [1, 2]
    return re.sub(r",(\s*[}\]])", r"\1", json_str)


def extract_json_array(text: str):
    """Extract a JSON array from raw model response.

    回傳三個值：(parsed_array or None, problem_json_str or None, had_decode_error: bool)

    - parsed_array: 解析成功時的 Python list
    - problem_json_str: 若發生 JSONDecodeError，這裡會放下游可寫入 .failed.txt 的原始字串
    - had_decode_error: True 代表是 decode 錯誤（可用來決定是否要停止 retry）
    """

    if not text:
        print("    ! Empty response text.")
        return None, None, False

    stripped = text.strip()

    # 1) 如果整段本身就是 JSON 陣列，直接解析
    if stripped.startswith("["):
        try:
            return json.loads(stripped), stripped, False
        except json.JSONDecodeError:
            # 試著移除尾逗號之類的小錯誤再試一次
            cleaned = _strip_trailing_commas(stripped)
            try:
                return json.loads(cleaned), cleaned, False
            except json.JSONDecodeError as e:
                print(f"    ! Failed to decode JSON array as-is: {e}")
                # 回傳原始字串，讓呼叫端可以存成 .failed.txt
                return None, stripped, True

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
        return None, None, False

    json_str = json_str.strip()
    try:
        return json.loads(json_str), json_str, False
    except json.JSONDecodeError:
        cleaned = _strip_trailing_commas(json_str)
        try:
            return json.loads(cleaned), cleaned, False
        except json.JSONDecodeError as e:
            print(f"    ! Failed to decode extracted JSON array: {e}")
            return None, json_str, True


def send_to_vertex_for_content(client: genai.Client, prompt: str) -> str | None:
    """Call Vertex AI to generate Words content for a chapter segment."""

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
        # 強制模型輸出為 application/json，降低格式錯誤機率
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
    """Load {chapter}_original.info for a given chapter if it exists."""

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


def merge_chapter_sections(book_id: str, chapter_id: str, sections: list[dict]) -> None:
    """Merge all per-section Words JSON files into a single {chapter_id}.json.

    只在所有 section 的輸出檔都存在時才產生最終 {chapter}.json，
    讓你可以透過多次執行腳本補齊缺漏的 section。
    """

    all_words: list = []
    missing: list[str] = []

    # 依 sectionIndexOrName 的排序順序合併
    def sort_key(sec: dict):
        name = str(sec.get("sectionIndexOrName", ""))
        try:
            return int(name)
        except ValueError:
            return name

    for sec in sorted(sections, key=sort_key):
        name = str(sec.get("sectionIndexOrName"))
        seg_path = OUTPUT_DIR / book_id / f"{chapter_id}_sec_{name}.json"
        if not seg_path.exists():
            missing.append(name)
            continue
        try:
            data = json.loads(seg_path.read_text(encoding="utf-8"))
            if isinstance(data, list):
                all_words.extend(data)
        except Exception as e:
            print(f"    ! Failed to read section file {seg_path}: {e}")

    if missing:
        print(
            f"    ! Skip final merge for chapter {chapter_id} because "
            f"these sections have no Words JSON yet: {', '.join(missing)}"
        )
        return

    if not all_words:
        print("    ! No Words data collected from sections; final chapter JSON not created.")
        return

    final_path = OUTPUT_DIR / book_id / f"{chapter_id}.json"
    save_json(final_path, all_words)
    print(f"  - Completed chapter JSON: {final_path}")

    # 合併成功後，清理各 section 的中繼檔 {chapter_id}_sec_{section}.json
    for sec in sorted(sections, key=sort_key):
        name = str(sec.get("sectionIndexOrName"))
        seg_path = OUTPUT_DIR / book_id / f"{chapter_id}_sec_{name}.json"
        if seg_path.exists():
            try:
                seg_path.unlink()
                print(f"    - Removed section file: {seg_path}")
            except Exception as e:
                print(f"    ! Failed to remove section file {seg_path}: {e}")

        # 同時移除可能存在的 decode 失敗紀錄檔 {chapter_id}_sec_{section}.failed.txt
        failed_path = OUTPUT_DIR / book_id / f"{chapter_id}_sec_{name}.failed.txt"
        if failed_path.exists():
            try:
                failed_path.unlink()
                print(f"    - Removed failed record file: {failed_path}")
            except Exception as e:
                print(f"    ! Failed to remove failed record file {failed_path}: {e}")


# ================= Main Logic =================


def process_chapter(
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
    original_info = load_chapter_original_info(book_id, chapter_id)
    if not original_info:
        print("    ! No original.info for this chapter; skip Words generation.")
        return

    final_chapter_path = OUTPUT_DIR / book_id / f"{chapter_id}.json"
    if final_chapter_path.exists():
        print(f"    - Final chapter JSON already exists, skip chapter: {final_chapter_path}")
        return

    sections = original_info.get("sections") or []
    if not isinstance(sections, list) or not sections:
        print("    ! {chapter_id}_original.info has no 'sections'; skip this chapter.")
        return

    if not bool(original_info.get("isAllCompleted")):
        print("    - Warning: original sections not marked as completed (isAllCompleted != true). Proceeding anyway.")

    # 依 sectionIndexOrName 逐段處理原文 → Words 轉譯
    def sort_key(sec: dict):
        name = str(sec.get("sectionIndexOrName", ""))
        try:
            return int(name)
        except ValueError:
            return name

    for sec in sorted(sections, key=sort_key):
        sec_name = str(sec.get("sectionIndexOrName"))
        original_lines = sec.get("original") or []
        if not original_lines:
            continue

        section_path = OUTPUT_DIR / book_id / f"{chapter_id}_sec_{sec_name}.json"
        if section_path.exists():
            print(f"    - Section {sec_name} already has Words JSON; skip.")
            continue

        print(f"    - Processing section {sec_name} with {len(original_lines)} lines...")

        original_lines_json = json.dumps(original_lines, ensure_ascii=False)

        prompt = (
            prompt_template
            .replace("{book_title_traditional}", book_t)
            .replace("{book_title_english}", book_en)
            .replace("{book_id}", book_id)
            .replace("{chapter_id}", chapter_id)
            .replace("{chapter_title}", chapter_title)
            .replace("{section_index_or_name}", sec_name)
            .replace("{original_lines}", original_lines_json)
        )

        success = False
        for attempt in range(1, MAX_RETRIES_PER_SEGMENT + 1):
            if attempt > 1:
                print(
                    f"    → Retry attempt {attempt}/{MAX_RETRIES_PER_SEGMENT} "
                    f"for section {sec_name}..."
                )

            raw = send_to_vertex_for_content(client, prompt)
            if not raw:
                print("      ! Empty response from model.")
            else:
                words, problem_json, had_decode_error = extract_json_array(raw)
                if isinstance(words, list) and words:
                    save_json(section_path, words)
                    success = True
                    break
                else:
                    # 若是 JSON decode 錯誤，將原始 JSON 片段存成 .failed.txt，且不再 retry
                    if had_decode_error and problem_json:
                        failed_path = OUTPUT_DIR / book_id / f"{chapter_id}_sec_{sec_name}.failed.txt"
                        failed_path.parent.mkdir(parents=True, exist_ok=True)
                        failed_path.write_text(problem_json, encoding="utf-8")
                        print(f"      ! Saved problematic JSON to {failed_path}")
                        break
                    else:
                        print("      ! Parsed result is not a non-empty JSON array.")

            if not success and attempt < MAX_RETRIES_PER_SEGMENT:
                delay = REQUEST_DELAY_SECONDS * attempt
                print(f"      Waiting {delay} seconds before retrying...")
                time.sleep(delay)

        if not success:
            print(f"    ! Giving up on section {sec_name} for now (will try next run).")
            # Don't abort whole chapter; continue to next section

        # Rate-limit between sections
        time.sleep(REQUEST_DELAY_SECONDS)

    # 嘗試合併所有已完成的 section Words 至最終 {chapter}.json
    merge_chapter_sections(book_id, chapter_id, sections)


def main(book_id_filter: str | None = None) -> None:
    print(f"Initializing Vertex AI Client for project '{PROJECT_ID}' in '{LOCATION}'...")
    try:
        client = genai.Client(vertexai=True, project=PROJECT_ID, location=LOCATION)
    except Exception as e:
        print(f"Vertex AI initialization failed: {e}")
        print("請確認已執行 'gcloud auth application-default login'，且 PROJECT_ID 設定正確。")
        return

    try:
        prompt_template = load_text_file(PROMPT_CONTENT_FILE)
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

        print(f"\n===== Generating chapter content for {book_t} ({book_id}) =====")

        # Ensure this book has completed chapter names in content.info
        info_data = load_content_info(book_id)
        if not info_data:
            continue

        if not bool(info_data.get("isChatpersCompleted")):
            print("  - content.info indicates chapters are NOT completed; skip this book.")
            continue

        chapters_list = info_data.get("chapters") or []
        if not isinstance(chapters_list, list) or not chapters_list:
            print("  ! content.info has no 'chapters' list; skip this book.")
            continue

        content_data = load_content_json(book_id)
        if not content_data:
            continue

        chapter_items = get_chapter_items_from_content(content_data)
        if not chapter_items:
            print("  ! No chapter items found in content.json; skip this book.")
            continue

        # Align chapters by index between content.info.chapters and content.json chapter items
        for idx, chapter_item in enumerate(chapter_items):
            chapter_title = chapter_item.get("t")
            title_from_info = chapters_list[idx] if idx < len(chapters_list) else None

            if title_from_info and chapter_title and title_from_info != chapter_title:
                print(
                    f"  ! Title mismatch at index {idx}: "
                    f"content.json='{chapter_title}', content.info='{title_from_info}'"
                )

            process_chapter(client, prompt_template, book, chapter_item)

    print("\n===== All requested books processed. Chapter content generation complete. =====")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="Generate Words JSON chapter content for ancient classics (per book, per chapter, resumable)."
    )
    parser.add_argument(
        "--book-id",
        type=str,
        default=None,
        help="只處理指定 book id（例如 'The Analects'）；若省略則處理所有書。",
    )
    args = parser.parse_args()

    main(book_id_filter=args.book_id)
