import argparse
import json
import re
import time
from pathlib import Path

from google import genai
from google.genai import types

# ================= Configuration =================

# 請填入你的 GCP Project ID（已在 junior-high / ds-algo 使用過的同一個專案）
PROJECT_ID = "qwiklabs-gcp-00-77090f1a05c2"
LOCATION = "global"
MODEL_NAME = "gemini-3-pro-preview"

REQUEST_DELAY_SECONDS = 4
MAX_RETRIES_PER_BOOK = 3

BASE_DIR = Path(__file__).resolve().parent
MENU_PATH_FILE = BASE_DIR / "menu-path.json"
OUTPUT_DIR = BASE_DIR / "output"
PROMPT_CHAPTERS_FILE = BASE_DIR / "prompt-chapters.md"
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


def send_to_vertex_for_chapters(client: genai.Client, prompt: str) -> str | None:
    """呼叫 Vertex AI 產生章節清單，回傳純文字回應。"""

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
    items = data.get("items", [])
    return items


def get_book_items(menu_items):
    """從 menu-path.json 中挑出「各本書」的節點。

    規則：parent != null 視為書（因為大分類 parent 為 null）。
    """

    books = [item for item in menu_items if item.get("parent") is not None]
    return books


def build_chapter_items_for_book(book, chapter_defs):
    """根據模型回傳的章節定義，產生 Category items（含 quiz 子節點）。"""

    book_id = book["id"]

    items = []

    for idx, ch in enumerate(chapter_defs, start=1):
        ch_id = ch.get("id") or f"chapter{idx:02d}"
        t = ch.get("t") or f"第{idx}章"
        c = ch.get("c") or t
        p = ch.get("p", "")
        z = ch.get("z", "")
        en = ch.get("en") or f"Chapter {idx}"

        # 章節主內容 item
        content_item = {
            "id": ch_id,
            "parent": None,
            "t": t,
            "c": c,
            "p": p,
            "z": z,
            "en": en,
            "pointTo": {
                "type": "document",
                "data": "github/json",
                "dataLocation": f"https://github.com/feelryan/jujuen/blob/ancient-classics/{book_id}/{ch_id}.json",
                "renderObject": "Words",
            },
        }
        items.append(content_item)

        # 章節測驗 item（quiz）
        quiz_id = f"{ch_id}-quiz"
        quiz_t = f"{t} 測驗"
        quiz_en = f"{en} Quiz"

        quiz_item = {
            "id": quiz_id,
            "parent": ch_id,
            "t": quiz_t,
            "c": quiz_t,
            "p": "",
            "z": "",
            "en": quiz_en,
            "pointTo": {
                "type": "document",
                "data": "github/json",
                "dataLocation": f"https://github.com/feelryan/jujuen/blob/ancient-classics/{book_id}/{ch_id}-quiz.json",
                "renderObject": "Question",
            },
        }
        items.append(quiz_item)

    return items


# ================= Main =================


def main(clear_only: bool = False) -> None:
    print(f"Initializing Vertex AI Client for project '{PROJECT_ID}' in '{LOCATION}'...")
    try:
        client = genai.Client(vertexai=True, project=PROJECT_ID, location=LOCATION)
    except Exception as e:
        print(f"Vertex AI initialization failed: {e}")
        print("請確認已執行 'gcloud auth application-default login'，且 PROJECT_ID 設定正確。")
        return

    try:
        prompt_template = load_text_file(PROMPT_CHAPTERS_FILE)
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

    print("Books detected from menu-path.json:")
    for b in books:
        print(f"  - {b.get('id')} : {b.get('t')} / {b.get('en')}")

    for book in books:
        book_id = book["id"]
        book_t = book.get("t", book_id)
        book_en = book.get("en", book_id)

        print(f"\n===== Generating chapters for {book_t} ({book_id}) =====")

        content_path = OUTPUT_DIR / book_id / "content.json"
        if not content_path.exists():
            print(f"  ! content.json not found for book '{book_id}': {content_path}")
            continue

        # 讀取對應的 content.info，僅在 isChatpersCompleted 為 true 時才進行章節 items 生成
        info_path = OUTPUT_DIR / book_id / INFO_FILENAME
        if not info_path.exists():
            print(f"  ! {INFO_FILENAME} not found for book '{book_id}': {info_path}")
            continue

        try:
            info_data = json.loads(info_path.read_text(encoding="utf-8"))
        except Exception as e:
            print(f"  ! Failed to read {INFO_FILENAME} for '{book_id}': {e}")
            continue

        is_completed = bool(info_data.get("isChatpersCompleted"))
        chapters = info_data.get("chapters") or []

        if not is_completed:
            print("  - content.info indicates chapters are NOT completed (isChatpersCompleted != true); skip generation.")
            continue

        if not isinstance(chapters, list) or not chapters:
            print("  ! content.info has no valid 'chapters' list; skip this book.")
            continue

        # 若 content.json 已經有 items，先讀取以方便日後擴充；目前策略為覆蓋 items。
        try:
            content_data = json.loads(content_path.read_text(encoding="utf-8"))
        except Exception as e:
            print(f"  ! Failed to read existing content.json for '{book_id}': {e}")
            continue

        existing_items = content_data.get("items", [])
        if existing_items:
            print("  - Existing items detected; they will be overwritten by generated chapters.")

        # 如果只想清空 items 而不重新呼叫模型產生章節，可使用 --clear-only 參數
        if clear_only:
            content_data["items"] = []
            save_json(content_path, content_data)
            print(f"  - Cleared items for {book_id} only (no generation).")
            continue

        # 準備 prompt，帶入 content.info 中的章節資訊
        chapter_info_json = json.dumps(
            {
                "totalChapterNumber": info_data.get("totalChapterNumber", 0),
                "chapters": chapters,
                "isChatpersCompleted": is_completed,
            },
            ensure_ascii=False,
        )

        prompt = (
            prompt_template
            .replace("{book_title_traditional}", book_t)
            .replace("{book_title_english}", book_en)
            .replace("{book_id}", book_id)
            .replace("{chapter_info}", chapter_info_json)
        )

        chapter_defs = None

        for attempt in range(1, MAX_RETRIES_PER_BOOK + 1):
            if attempt > 1:
                print(f"  → Retry attempt {attempt}/{MAX_RETRIES_PER_BOOK} for {book_id}...")

            raw = send_to_vertex_for_chapters(client, prompt)
            if not raw:
                print("    ! Empty response from model.")
            else:
                parsed = extract_json_array(raw)
                if isinstance(parsed, list) and parsed:
                    chapter_defs = parsed
                    break
                else:
                    print("    ! Parsed result is not a non-empty JSON array.")

            # 若本次嘗試失敗且仍有下一次重試，則等待一段時間以避免 429 / RESOURCE_EXHAUSTED
            if attempt < MAX_RETRIES_PER_BOOK:
                delay = REQUEST_DELAY_SECONDS * attempt
                print(f"    Waiting {delay} seconds before next attempt...")
                time.sleep(delay)

        if chapter_defs is None:
            print(f"  ! Failed to generate chapters for {book_id}. Skipping this book.")
            continue

        print(f"  - Received {len(chapter_defs)} chapter definitions from model.")

        items = build_chapter_items_for_book(book, chapter_defs)

        content_data["id"] = book_id
        # 保留原本 title（若想自動更新也可以在此修改）
        content_data.setdefault("title", f"{book_t} {book_en} 目錄")
        content_data["items"] = items

        save_json(content_path, content_data)

        # 在處理下一本書之前稍作等待，降低連續呼叫導致 429 的風險
        time.sleep(REQUEST_DELAY_SECONDS)

    print("\n===== All books processed. Chapter generation complete. =====")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Generate or clear chapter items for ancient classics.")
    parser.add_argument(
        "--clear-only",
        action="store_true",
        help="只清空每本書 content.json 的 items，而不呼叫模型重新產生章節。",
    )
    args = parser.parse_args()

    main(clear_only=args.clear_only)
