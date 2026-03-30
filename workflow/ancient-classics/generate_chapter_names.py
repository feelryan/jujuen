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

REQUEST_DELAY_SECONDS = 5
MAX_RETRIES_PER_CALL = 3

BASE_DIR = Path(__file__).resolve().parent
MENU_PATH_FILE = BASE_DIR / "menu-path.json"
OUTPUT_DIR = BASE_DIR / "output"
PROMPT_CHAPTER_NAMES_FILE = BASE_DIR / "prompt-chapter-names.md"


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
    """從模型回應中抽出單一 JSON 物件。

    預期模型直接回傳一個 JSON 物件，但仍防禦性處理 ```json 區塊。
    """

    match = re.search(r"```json\s*(\{.*?\})\s*```", text, re.DOTALL)
    if match:
        json_str = match.group(1)
    else:
        match = re.search(r"(\{.*\})", text, re.DOTALL)
        json_str = match.group(0) if match else None

    if not json_str:
        print("    ! 無法在回應中找到 JSON 物件。")
        return None

    try:
        return json.loads(json_str)
    except json.JSONDecodeError as e:
        print(f"    ! JSON 解析失敗: {e}")
        return None


def send_to_vertex_for_chapter_names(client: genai.Client, prompt: str) -> str | None:
    """呼叫 Vertex AI 取得章節總數與章節名稱（可能僅部分），回傳原始文字。"""

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
    """從 menu-path.json 中挑出「各本書」的節點（parent != null）。"""

    return [item for item in menu_items if item.get("parent") is not None]


# ================= Core Logic =================


def compute_is_completed(total_chapters: int, chapters: list[str]) -> bool:
    return total_chapters > 0 and len(chapters) >= total_chapters


def ensure_info_structure(raw: dict) -> dict:
    """正規化模型或既有檔案載入的章節資訊。"""

    total = raw.get("totalChapterNumber") or raw.get("total_chapter_number") or 0
    chapters = raw.get("chapters") or []

    if not isinstance(total, int):
        try:
            total = int(total)
        except Exception:
            total = 0

    if not isinstance(chapters, list):
        chapters = []

    # 僅保留字串章節名稱
    chapters = [str(c) for c in chapters if isinstance(c, (str, int, float))]

    info = {
        "totalChapterNumber": total,
        "chapters": chapters,
        "isChatpersCompleted": compute_is_completed(total, chapters),
    }
    return info


def main() -> None:
    print(f"Initializing Vertex AI Client for project '{PROJECT_ID}' in '{LOCATION}'...")
    try:
        client = genai.Client(vertexai=True, project=PROJECT_ID, location=LOCATION)
    except Exception as e:
        print(f"Vertex AI initialization failed: {e}")
        print("請確認已執行 'gcloud auth application-default login'，且 PROJECT_ID 設定正確。")
        return

    try:
        prompt_template = load_text_file(PROMPT_CHAPTER_NAMES_FILE)
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

        print(f"\n===== Getting chapter names for {book_t} ({book_id}) =====")

        book_dir = OUTPUT_DIR / book_id
        info_path = book_dir / "content.info"

        # 載入既有 info，或建立空白結構
        existing_info_raw = {}
        if info_path.exists():
            try:
                existing_info_raw = json.loads(info_path.read_text(encoding="utf-8"))
            except Exception as e:
                print(f"  ! Failed to read existing content.info for '{book_id}': {e}")

        info = ensure_info_structure(existing_info_raw)

        if info["isChatpersCompleted"]:
            print("  - Chapters already completed; skip this book.")
            continue

        total_before = info["totalChapterNumber"]
        chapters_before = info["chapters"]

        print(f"  - Current known totalChapterNumber: {total_before}")
        print(f"  - Currently have {len(chapters_before)} chapter names.")

        existing_info_json = json.dumps(
            {
                "totalChapterNumber": total_before,
                "chapters": chapters_before,
            },
            ensure_ascii=False,
        )

        # 準備 prompt：把 {existing_info} 帶入（第一次呼叫時為 total=0, chapters=[]）
        prompt = (
            prompt_template
            .replace("{book_title_traditional}", book_t)
            .replace("{book_title_english}", book_en)
            .replace("{book_id}", book_id)
            .replace("{existing_info}", existing_info_json)
        )

        response_obj = None

        for attempt in range(1, MAX_RETRIES_PER_CALL + 1):
            if attempt > 1:
                print(f"  → Retry attempt {attempt}/{MAX_RETRIES_PER_CALL} for {book_id}...")

            raw_text = send_to_vertex_for_chapter_names(client, prompt)
            if not raw_text:
                print("    ! Empty response from model.")
            else:
                parsed = extract_json_object(raw_text)
                if isinstance(parsed, dict):
                    response_obj = parsed
                    break
                else:
                    print("    ! Parsed result is not a JSON object.")

            if attempt < MAX_RETRIES_PER_CALL:
                delay = REQUEST_DELAY_SECONDS * attempt
                print(f"    Waiting {delay} seconds before next attempt...")
                time.sleep(delay)

        if response_obj is None:
            print(f"  ! Failed to get chapter info for {book_id}. Skipping this book.")
            continue

        # 將回應正規化並合併進 info
        new_info = ensure_info_structure(response_obj)

        # totalChapterNumber 若之前為 0，採用模型回應；若之前已有值，優先沿用舊值
        if total_before > 0:
            total = total_before
        else:
            total = new_info["totalChapterNumber"]

        # 合併章節名稱：先前已知 + 這次新回應
        new_chapters = new_info["chapters"]
        merged_chapters = chapters_before + [c for c in new_chapters if c not in chapters_before]

        final_info = {
            "totalChapterNumber": total,
            "chapters": merged_chapters,
            "isChatpersCompleted": compute_is_completed(total, merged_chapters),
        }

        save_json(info_path, final_info)

        print(
            f"  - Now have {len(merged_chapters)}/{total} chapter names. "
            f"Completed: {final_info['isChatpersCompleted']}"
        )

        # 替下一本書前稍作等待，避免過快觸發限流
        time.sleep(REQUEST_DELAY_SECONDS)

    print("\n===== All books processed. Chapter-name collection complete. =====")


if __name__ == "__main__":
    main()
