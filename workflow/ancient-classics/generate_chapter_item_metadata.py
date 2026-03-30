import argparse
import json
import re
import time
from pathlib import Path

from google import genai
from google.genai import types

# ================= Configuration =================

BASE_DIR = Path(__file__).resolve().parent

# PROJECT_ID 由 ancient-classics/PROJECT_ID.txt 提供
PROJECT_ID_FILE = BASE_DIR / "PROJECT_ID.txt"


def load_project_id() -> str:
    try:
        value = PROJECT_ID_FILE.read_text(encoding="utf-8").strip()
    except FileNotFoundError as e:
        raise RuntimeError(f"PROJECT_ID file not found: {PROJECT_ID_FILE}") from e

    if not value:
        raise RuntimeError(f"PROJECT_ID file is empty: {PROJECT_ID_FILE}")

    return value


PROJECT_ID = load_project_id()
LOCATION = "global"
MODEL_NAME = "gemini-3-pro-preview"

REQUEST_DELAY_SECONDS = 4
MAX_RETRIES_PER_CHAPTER = 3

OUTPUT_DIR = BASE_DIR / "output"

# 這個 prompt 檔請你自行撰寫/調整內容，格式類似其他 prompt-*.md
# 需至少說明：
# - 會給你一個 JSON 陣列，每個元素有 id 與 t（繁體中文標題）
# - 請回傳一個等長 JSON 陣列，包含 id, t, c(簡體), p(漢語拼音，空格分詞), z(注音，空格分隔), en(英文語意翻譯)
PROMPT_ITEMS_FILE = BASE_DIR / "prompt-items-metadata.md"


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
    """從模型回應中抽出 JSON 陣列，邏輯同 generate_chapters.py。"""

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


def send_to_vertex_for_items(client: genai.Client, prompt: str) -> str | None:
    """呼叫 Vertex AI 產生每個 item 的 c/p/z/en，回傳純文字回應。"""

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
        temperature=0.2,
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


# ================= Core Logic =================


def collect_chapter_files(book_id: str):
    """回傳指定 book 底下所有 {chapterId}.json 檔案路徑（排除 content*.json 等非章節）。"""

    book_dir = OUTPUT_DIR / book_id
    if not book_dir.exists():
        print(f"  ! Book output directory not found: {book_dir}")
        return []

    chapter_files = []
    for path in sorted(book_dir.glob("chapter*.json")):
        # 避免誤抓 content.json 等檔案
        if path.name.startswith("content"):
            continue
        chapter_files.append(path)

    return chapter_files


def build_items_payload(chapter_data: dict):
    """從 chapter JSON 中擷取需要補全的 items 基本資訊。"""

    items = chapter_data.get("items", [])

    payload = []
    for it in items:
        t = it.get("t")
        item_id = it.get("id")
        if not t or not item_id:
            continue
        payload.append({
            "id": item_id,
            "t": t,
        })

    return payload


def merge_metadata_into_chapter(chapter_data: dict, metadata_list: list):
    """將模型回傳的 c/p/z/en 依照 id merge 回 chapter_data.items。"""

    if not metadata_list:
        return chapter_data

    # 先做成 dict，方便查詢
    meta_by_id = {str(m.get("id")): m for m in metadata_list if m.get("id") is not None}

    for it in chapter_data.get("items", []):
        item_id = str(it.get("id"))
        meta = meta_by_id.get(item_id)
        if not meta:
            continue

        # 保留原本的 t，不被覆蓋；其餘欄位由模型填入
        it.setdefault("t", meta.get("t"))
        if meta.get("c") is not None:
            it["c"] = meta["c"]
        if meta.get("p") is not None:
            it["p"] = meta["p"]
        if meta.get("z") is not None:
            it["z"] = meta["z"]
        if meta.get("en") is not None:
            it["en"] = meta["en"]

    return chapter_data


# ================= Main =================


def process_book(client: genai.Client, book_id: str, overwrite: bool = False):
    print(f"\n===== Filling c/p/z/en for book: {book_id} =====")

    book_dir = OUTPUT_DIR / book_id
    if not book_dir.exists():
        print(f"  ! Book directory not found: {book_dir}")
        return

    # 檢查 prompt 檔
    try:
        prompt_template = load_text_file(PROMPT_ITEMS_FILE)
    except FileNotFoundError as e:
        print(e)
        return

    chapter_files = collect_chapter_files(book_id)
    if not chapter_files:
        print("  ! No chapter*.json files found.")
        return

    print("  - Chapter files:")
    for cf in chapter_files:
        print(f"    * {cf.name}")

    for ch_path in chapter_files:
        print(f"\n  → Processing {ch_path.name} ...")
        try:
            ch_data = json.loads(ch_path.read_text(encoding="utf-8"))
        except Exception as e:
            print(f"    ! Failed to read {ch_path}: {e}")
            continue

        # 如果不想覆蓋已有人為填寫的欄位，可在這裡加入檢查邏輯；目前直接覆蓋或填補。
        payload_items = build_items_payload(ch_data)
        if not payload_items:
            print("    - No valid items to process (missing id or t).")
            continue

        # 準備 prompt
        payload_json = json.dumps(payload_items, ensure_ascii=False)
        prompt = (
            prompt_template
            .replace("{book_id}", book_id)
            .replace("{chapter_filename}", ch_path.name)
            .replace("{items}", payload_json)
        )

        meta_list = None
        for attempt in range(1, MAX_RETRIES_PER_CHAPTER + 1):
            if attempt > 1:
                print(f"    → Retry attempt {attempt}/{MAX_RETRIES_PER_CHAPTER}...")

            raw = send_to_vertex_for_items(client, prompt)
            if not raw:
                print("      ! Empty response from model.")
            else:
                parsed = extract_json_array(raw)
                if isinstance(parsed, list) and parsed:
                    meta_list = parsed
                    break
                else:
                    print("      ! Parsed result is not a non-empty JSON array.")

            if attempt < MAX_RETRIES_PER_CHAPTER:
                delay = REQUEST_DELAY_SECONDS * attempt
                print(f"      Waiting {delay} seconds before next attempt...")
                time.sleep(delay)

        if meta_list is None:
            print(f"    ! Failed to get metadata for {ch_path.name}. Skipping.")
            continue

        print(f"    - Received {len(meta_list)} metadata entries from model.")

        ch_data = merge_metadata_into_chapter(ch_data, meta_list)

        # 直接覆寫原檔
        save_json(ch_path, ch_data)

        # 兩次章節之間稍作等待，降低 429 風險
        time.sleep(REQUEST_DELAY_SECONDS)

    print(f"\n===== Done for book: {book_id} =====")


def main(book_id: str, overwrite: bool = False):
    print(f"Initializing Vertex AI Client for project '{PROJECT_ID}' in '{LOCATION}'...")
    try:
        client = genai.Client(vertexai=True, project=PROJECT_ID, location=LOCATION)
    except Exception as e:
        print(f"Vertex AI initialization failed: {e}")
        print("請確認已執行 'gcloud auth application-default login'，且 PROJECT_ID 設定正確。")
        return

    process_book(client, book_id, overwrite=overwrite)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Fill c/p/z/en for each chapterId.json items using Vertex AI.")
    parser.add_argument(
        "book_id",
        help="書本目錄 ID，例如 'Three Hundred Tang Poems' 或 'The Analects' 等（需與 output 子目錄名稱一致）",
    )
    parser.add_argument(
        "--overwrite",
        action="store_true",
        help="允許覆寫既有的 c/p/z/en（預設為直接覆寫/補上）。",
    )

    args = parser.parse_args()

    main(book_id=args.book_id, overwrite=args.overwrite)
