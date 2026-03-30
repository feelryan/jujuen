import argparse
import json
import re
import time
from datetime import datetime
from pathlib import Path

from google import genai
from google.genai import types


# ================= Configuration =================

LOCATION = "global"
MODEL_NAME = "gemini-3.1-pro-preview"
REQUEST_DELAY_SECONDS = 2
MAX_RETRIES_PER_BATCH = 5
DEFAULT_MAX_QUESTIONS_PER_REQUEST = 8

BASE_DIR = Path(__file__).resolve().parent
PROJECT_ID_FILE = BASE_DIR / "PROJECT_ID.txt"
OUTPUT_ROOT = BASE_DIR / "output"


# ================= Helper Functions =================


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


def send_to_vertex_for_repair(client: genai.Client, prompt: str) -> str | None:
    """Call Vertex AI to normalize options/answer for a batch of questions, return raw text."""

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
        print(f"    ! Vertex AI call failed: {e}")
        return None


def is_question_array(data) -> bool:
    """Heuristic: treat as question JSON if it's a non-empty list of dicts and has 'answer'."""

    if not isinstance(data, list) or not data:
        return False

    for item in data:
        if isinstance(item, dict) and "answer" in item:
            return True
    return False


def find_json_files_under_output(skill_id: str | None = None, reverse: bool = False) -> list[Path]:
    """Find all JSON files under output/, optionally limited to a specific skill directory.

    If reverse=True, the resulting file list order will be reversed so that the
    last file (in the original traversal order) is placed first. This lets you
    start processing from the "last" file when iterating in order.
    """

    if not OUTPUT_ROOT.exists():
        return []

    root = OUTPUT_ROOT
    if skill_id:
        root = OUTPUT_ROOT / skill_id
        if not root.exists():
            print(f"  ! Specified skill directory not found under output: {root}")
            return []

    files = list(root.rglob("*.json"))
    if reverse:
        files.reverse()
    return files


def chunk_list(seq, size):
    for i in range(0, len(seq), size):
        yield seq[i : i + size]


def build_repair_prompt(batch_questions: list[dict]) -> str:
    """Build instruction prompt for repairing one batch of questions."""

    questions_json = json.dumps(batch_questions, ensure_ascii=False, indent=2)

    prompt = f"""
你是一位資深軟體工程師與題庫維護者，負責「修正題庫 JSON 的選項與答案格式」。

【任務說明】
- 系統會提供一個 JSON 陣列，裡面每個元素是一題題目物件。
- 每個物件中已經包含欄位（例如 no, level, question, options, type, answer, why 等）。
- 你必須根據 `question` 文字、`options` 內容以及 `type`（單選題 / 複選題）來判斷正確解答，並統一 `options` 與 `answer` 的格式。
- 除非為了修正選項標號或答案格式，否則請保持其他欄位內容與結構完全不變（包含中文字、英文與 wg 結構）。
- **不要新增或修改 `verified` 欄位**，此欄位由外部程式負責填入。

【options 格式規則】
- `options` 為一個陣列，依照陣列順序對第 1、2、3、4⋯ 個選項分別加上 `(A) `、`(B) `、`(C) `、`(D) `⋯ 作為前綴。
- 此前綴必須同時加在該選項的 `t` 與 `en` 字串開頭。
- 若原本文字已經有其它標號（例如 `A.`、`(A)`、`(1)` 等），請先移除，再改用標準的 `(A) `、`(B) `⋯，避免重複標號。
- 除了加入與修正標號前綴之外，請不要改變選項原本的語意與句子內容。

【answer 格式規則】
- 若為單選題（Single Choice / 單選題），`"answer"` 必須是一個單一大寫英文字母，例如 `"A"`、`"B"`，對應正確選項的標號。
- 若為複選題（Multiple Choice / 複選題），`"answer"` 必須是一個由一個或多個大寫英文字母組成的字串，使用半形逗號分隔且不含空白，例如 `"A,B"` 或 `"B,D"`。
- 不可以使用數字索引（例如 0,1,2 或 1,2,3⋯），也不可以用完整文字句子描述答案，必須只用選項標號字母。

【輸出要求】
- 回傳一個與輸入長度相同的 JSON 陣列。
- 每個題目物件的欄位名稱與結構必須與輸入保持一致，只允許調整 `options` 內容（加入/修正標號）與 `answer` 字串格式。
- 請勿新增或修改 `verified` 欄位。
- 不要在 JSON 陣列以外輸出任何說明文字或程式碼區塊標籤（不要使用 ```json 標籤）。
- 回應必須是 RFC 8259 標準的合法 JSON 陣列。

以下是需要修正的題目 JSON 陣列：

{questions_json}
"""

    return prompt

def is_valid_answer(answer):
    """
    Verifies that the answer is a single uppercase letter 
    or a comma-separated list of uppercase letters.
    Matches formats like: "A", "A,B", "A, B", "A, B, C"
    """
    if not isinstance(answer, str):
        return False
    
    # Regular Expression Breakdown:
    # ^[A-Z]           - Starts with a single uppercase letter
    # (?:,\s*[A-Z])* - Followed by zero or more groups of:
    #                   a comma, optional whitespace (\s*), and another letter
    # $                - End of the string
    pattern = r'^[A-Z](?:,\s*[A-Z])*$'
    
    return bool(re.match(pattern, answer.strip()))

# ================= Main Logic =================


def main(max_per_request: int, skill_id: str | None, single_file: str | None, reverse_order: bool) -> None:
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

    # Determine target JSON files
    json_files: list[Path] = []

    if single_file:
        single_path = Path(single_file)
        if not single_path.is_absolute():
            single_path = OUTPUT_ROOT / single_path

        if not single_path.exists():
            print(f"Specified file does not exist: {single_path}")
            return
        if not single_path.is_file() or single_path.suffix.lower() != ".json":
            print(f"Specified path is not a JSON file: {single_path}")
            return

        json_files = [single_path]
        print(f"Processing single JSON file: {single_path.relative_to(OUTPUT_ROOT) if single_path.is_relative_to(OUTPUT_ROOT) else single_path}")
    else:
        json_files = find_json_files_under_output(skill_id=skill_id, reverse=reverse_order)

    if not json_files:
        print(f"No JSON files found under {OUTPUT_ROOT}.")
        return

    print(f"Discovered {len(json_files)} JSON files under {OUTPUT_ROOT}.")

    for json_path in json_files:
        rel_path = json_path.relative_to(OUTPUT_ROOT)
        print(f"\n===== Processing file: {rel_path} =====")

        data = load_json_file(json_path)
        if data is None:
            print("  ! Skip file due to JSON parse error.")
            continue

        if not is_question_array(data):
            print("  - Not a question-array JSON (no 'answer' field found), skip.")
            continue

        # Collect indices of questions that still need verification
        pending_indices: list[int] = []
        for idx, q in enumerate(data):
            if not isinstance(q, dict):
                continue
            if "answer" not in q:
                continue
            if "verified" in q and q["verified"]:
                continue
            if is_valid_answer(q["answer"]):
                continue

            pending_indices.append(idx)

        if not pending_indices:
            print("  - All questions already have 'verified', nothing to do.")
            continue

        print(f"  - Total questions: {len(data)}, pending verification: {len(pending_indices)}")

        for batch_indices in chunk_list(pending_indices, max_per_request):
            batch_questions = [data[i] for i in batch_indices]

            prompt = build_repair_prompt(batch_questions)

            repaired_batch = None
            for attempt in range(1, MAX_RETRIES_PER_BATCH + 1):
                if attempt > 1:
                    print(f"    → Retry attempt {attempt}/{MAX_RETRIES_PER_BATCH} for batch in {rel_path}...")

                raw = send_to_vertex_for_repair(client, prompt)
                if not raw:
                    print("      ! Empty response from model.")
                else:
                    parsed = extract_json_array(raw)
                    if isinstance(parsed, list) and len(parsed) == len(batch_questions):
                        repaired_batch = parsed
                        break
                    else:
                        print(
                            "      ! Parsed result is not a JSON array of expected length "
                            f"(expected {len(batch_questions)})."
                        )

                if attempt < MAX_RETRIES_PER_BATCH:
                    delay = REQUEST_DELAY_SECONDS * attempt
                    print(f"      Waiting {delay} seconds before next attempt...")
                    time.sleep(delay)

            if repaired_batch is None:
                print("  ! Failed to repair this batch after retries, skip remaining batches for this file.")
                break

            # Merge repaired questions back into original data and add verified timestamp
            now_str = datetime.now().isoformat(timespec="seconds")
            for local_idx, global_idx in enumerate(batch_indices):
                repaired_q = repaired_batch[local_idx]
                if isinstance(repaired_q, dict):
                    repaired_q["verified"] = now_str
                data[global_idx] = repaired_q

            print(f"  - Repaired and marked verified for questions at indices: {batch_indices}")

            # Basic delay to avoid hitting rate limits too aggressively
            time.sleep(REQUEST_DELAY_SECONDS)

        # Save back updated file after finishing all batches for this file
        save_json_file(json_path, data)

    print("\n===== Question options/answer verification complete for all JSON files. =====")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description=(
            "Scan workflow/skills/output for question JSON files, "
            "normalize options labels and answer format via Vertex AI, and mark verified questions."
        )
    )
    parser.add_argument(
        "--max-per-request",
        type=int,
        default=DEFAULT_MAX_QUESTIONS_PER_REQUEST,
        help=(
            "Maximum number of questions to send to the model per request. "
            "Use a smaller number if individual questions are very long."
        ),
    )
    parser.add_argument(
        "--skill-id",
        required=False,
        help=(
            "Only process JSON files under output/{skill_id}. "
            "If omitted, all skills under output/ will be scanned. "
            "Ignored when --file is provided."
        ),
    )
    parser.add_argument(
        "--file",
        required=False,
        help=(
            "Only process a single JSON file. Can be an absolute path, "
            "or a path relative to workflow/skills/output/. "
            "When provided, --skill-id is ignored."
        ),
    )
    parser.add_argument(
        "--reverse",
        action="store_true",
        help=(
            "Process discovered JSON files in reverse order (last file first). "
            "Useful when you want to start checking from the most recently found files."
        ),
    )

    args = parser.parse_args()

    main(
        max_per_request=args.max_per_request,
        skill_id=args.skill_id,
        single_file=args.file,
        reverse_order=args.reverse,
    )
