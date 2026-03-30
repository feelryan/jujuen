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

REQUEST_DELAY_SECONDS = 4
MAX_RETRIES = 3

BASE_DIR = Path(__file__).resolve().parent
PROJECT_ID_FILE = BASE_DIR / "PROJECT_ID.txt"
OUTPUT_DIR = BASE_DIR / "output"
PROMPT_SECTIONS_FILE = BASE_DIR / "prompt-interview-sections-category.md"

GITHUB_BASE = "https://github.com/feelryan/jujuen/blob/ryan"


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
    """從模型回應中抽出一個 JSON 物件。

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


def send_to_vertex_ai_with_pdfs(
    client: genai.Client,
    prompt_content: str,
    resume_pdf_path: Path,
    jd_pdf_path: Path | None,
) -> str | None:
    """呼叫 Vertex AI，將文字指示與履歷 / JD PDF 一起送入，回傳純文字回應。

    模式類似 junior-high/generate_materials_from_pdfs.py：
    - contents[0]: textual prompt
    - contents[1]: resume PDF bytes
    - contents[2]: (optional) JD PDF bytes
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
        temperature=0.3,
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

        contents: list[types.Part | str] = [prompt_content, resume_part]

        if jd_pdf_path is not None:
            print(f"  - Reading JD PDF bytes: {jd_pdf_path}")
            jd_bytes = jd_pdf_path.read_bytes()
            jd_part = types.Part.from_bytes(
                data=jd_bytes,
                mime_type="application/pdf",
            )
            contents.append(jd_part)

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


def main(resume_path: Path, jd_path: Path | None, force: bool = False) -> None:
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
        prompt_template = load_text_file(PROMPT_SECTIONS_FILE)
    except FileNotFoundError as e:
        print(e)
        return

    if not resume_path.exists():
        print(f"Resume PDF file not found: {resume_path}")
        return
    resume_base = resume_path.stem

    jd_base = None
    if jd_path is not None:
        if not jd_path.exists():
            print(f"JD PDF file not found: {jd_path}")
            return
        jd_base = jd_path.stem

    if jd_base:
        dir_name = f"{resume_base}_{jd_base}"
    else:
        dir_name = resume_base

    output_dir = OUTPUT_DIR / dir_name
    output_dir.mkdir(parents=True, exist_ok=True)

    content_path = output_dir / "content.json"
    if content_path.exists() and not force:
        print(f"content.json already exists: {content_path}")
        print("Use --force to overwrite.")
        return

    print(f"Generating interview sections for resume='{resume_base}' jd='{jd_base or ''}'...")

    # 準備 prompt（內容只描述任務，實際履歷與 JD 以 PDF bytes 傳入）
    prompt = prompt_template

    result_obj = None

    for attempt in range(1, MAX_RETRIES + 1):
        if attempt > 1:
            print(f"  → Retry attempt {attempt}/{MAX_RETRIES}...")

        raw = send_to_vertex_ai_with_pdfs(client, prompt, resume_path, jd_path)
        if not raw:
            print("    ! 模型回應為空。")
        else:
            parsed = extract_json_object(raw)
            if isinstance(parsed, dict) and parsed.get("items"):
                result_obj = parsed
                break
            else:
                print("    ! 解析後結果不是包含 items 的 JSON 物件。")

        if attempt < MAX_RETRIES:
            delay = REQUEST_DELAY_SECONDS * attempt
            print(f"    Waiting {delay} seconds before next attempt...")
            time.sleep(delay)

    if result_obj is None:
        print("  ! 無法成功取得有效的 Category JSON，請稍後重試或檢查 prompt。")
        return

    # 重新包裝成我們要的 Category 結構，並補上 pointTo
    items = result_obj.get("items") or []
    normalized_items = []

    for idx, item in enumerate(items, start=1):
        sec_id = item.get("id") or f"section{idx:02d}"
        t = item.get("t") or sec_id
        en = item.get("en") or t
        desc = item.get("description", "")

        # 建立 pointTo，GitHub 目錄根據履歷檔名（不含副檔名）
        point_to = {
            "type": "document",
            "data": "github/md",
            "dataLocation": f"{GITHUB_BASE}/{dir_name}/{sec_id}.md",
        }

        normalized_items.append(
            {
                "id": sec_id,
                "t": t,
                "en": en,
                "description": desc,
                "pointTo": point_to,
            }
        )

    # 若有提供 JD，額外加入一個「最佳策略 / Best Strategy」節點，指向 strategy.json
    if jd_base:
        strategy_item = {
            "id": "strategy",
            "t": "最佳策略 / Best Strategy",
            "en": "Best Strategy",
            "description": "根據該 JD 與履歷所設計的整體應試策略與重點總覽。",
            "pointTo": {
                "type": "category",
                "data": "github/json",
                "dataLocation": f"{GITHUB_BASE}/{dir_name}/strategy.json",
            },
        }
        normalized_items.append(strategy_item)

    category_obj = {
        "id": dir_name,
        "title": f"Interview Topics for {resume_base}",
        "items": normalized_items,
    }

    save_json(content_path, category_obj)

    print("\nDone. content.json generated at:")
    print(f"  {content_path}")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description=(
            "Generate workflow/job/output/{resume_name}[_{jd_name}]/content.json "
            "(Category) from resume and optional JD."
        )
    )
    parser.add_argument(
        "--resume",
        required=True,
        help="Path to resume text file (UTF-8).",
    )
    parser.add_argument(
        "--jd",
        required=False,
        help="Optional path to job description text file (UTF-8).",
    )
    parser.add_argument(
        "--force",
        action="store_true",
        help="Overwrite existing content.json if present.",
    )

    args = parser.parse_args()

    resume_path = Path(args.resume)
    jd_path = Path(args.jd) if args.jd else None

    main(resume_path=resume_path, jd_path=jd_path, force=args.force)
