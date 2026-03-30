import json
import re
import time
from pathlib import Path

from google import genai
from google.genai import types

# ================= Configuration =================

# Please fill in your Google Cloud Project ID (not the name)
PROJECT_ID = "qwiklabs-gcp-00-77090f1a05c2"
# Set the region (global is recommended for latest model support)
LOCATION = "global"

MODEL_NAME = "gemini-3-pro-preview"
REQUEST_DELAY_SECONDS = 6  # Delay between API requests to avoid rate limits

# Maximum characters per chunk when splitting Markdown material
MAX_CHARS_PER_CHUNK = 4000

# Retry settings for each chunk
MAX_RETRIES_PER_CHUNK = 3
RETRY_DELAY_MULTIPLIER = 1  # delay = REQUEST_DELAY_SECONDS * (retry_index + 1) * multiplier

BASE_DIR = Path(__file__).resolve().parent
TAIWAN_DIR = BASE_DIR / "taiwan"
PROMPT_WORDS_FILE = BASE_DIR / "prompt-words.md"

SUBJECTS = [
    {"slug": "math", "name": "數學"},
    {"slug": "nature", "name": "自然"},
]

GRADES = [
    {"grade_key": "7th", "label": "七年級"},
    {"grade_key": "8th", "label": "八年級"},
    {"grade_key": "9th", "label": "九年級"},
]

PHASES = [
    {"key": "mid1", "t": "期中1"},
    {"key": "mid2", "t": "期中2"},
    {"key": "final2", "t": "期末2"},
    {"key": "final3", "t": "期末3"},
]


# ================= Helper Functions =================


def load_text_file(path: Path) -> str:
    if not path.exists():
        raise FileNotFoundError(f"File not found: {path}")
    return path.read_text(encoding="utf-8")


def save_json(path: Path, data) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)
    print(f"Successfully saved JSON: {path}")


def extract_json_from_response(text: str):
    """Extracts a JSON array from the raw text response.

    We expect the model to return a pure JSON array, but we still
    defensively handle cases where it might be wrapped in ```json fences.
    """

    match = re.search(r"```json\s*(\[.*\])\s*```", text, re.DOTALL)
    if match:
        json_str = match.group(1)
    else:
        match = re.search(r"(\[.*\])", text, re.DOTALL)
        json_str = match.group(0) if match else None

    if not json_str:
        print("Warning: Could not find a JSON array in the response.")
        return None

    try:
        return json.loads(json_str)
    except json.JSONDecodeError as e:
        print(f"Warning: Failed to decode extracted JSON. Error: {e}")
        return None


def send_to_vertex_ai_for_words(client: genai.Client, prompt: str) -> str | None:
    """Sends the prompt (which already包含教材片段內容) to Vertex AI and returns raw text."""

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
        print(f"An error occurred with the Vertex AI API: {e}")
        return None


def build_or_load_split_state(split_path: Path, material_text: str, exam_base: str):
    """Create or load the .split state for a given material.

    The split file tracks chunk start/end indices, total_chunks,
    and per-chunk status (pending/done).
    """

    if split_path.exists():
        try:
            state = json.loads(split_path.read_text(encoding="utf-8"))
            return state
        except Exception as e:
            print(f"  ! Failed to read existing split file {split_path}: {e}")
            # Fall through to rebuild

    print("  - Creating new split plan...")
    text_length = len(material_text)
    chunks = []
    start = 0
    index = 1

    while start < text_length:
        end = min(start + MAX_CHARS_PER_CHUNK, text_length)
        chunks.append({"index": index, "start": start, "end": end, "status": "pending"})
        index += 1
        start = end

    total_chunks = len(chunks)
    state = {
        "exam_base": exam_base,
        "total_chunks": total_chunks,
        "chunks": chunks,
    }

    split_path.write_text(json.dumps(state, ensure_ascii=False, indent=2), encoding="utf-8")
    print(f"  - Saved split plan to {split_path} (total_chunks={total_chunks})")
    return state


def save_split_state(split_path: Path, state) -> None:
    split_path.write_text(json.dumps(state, ensure_ascii=False, indent=2), encoding="utf-8")


# ================= Main Program =================


def main() -> None:
    print(f"Initializing Vertex AI Client for project '{PROJECT_ID}' in '{LOCATION}'...")
    try:
        client = genai.Client(vertexai=True, project=PROJECT_ID, location=LOCATION)
    except Exception as e:
        print(f"Vertex AI initialization failed: {e}")
        print("Please ensure you have run 'gcloud auth application-default login' and the project ID is correct.")
        return

    try:
        prompt_template = load_text_file(PROMPT_WORDS_FILE)
    except FileNotFoundError as e:
        print(e)
        return

    # Iterate through all subject/grade/term combinations
    for subject in SUBJECTS:
        subject_slug = subject["slug"]
        subject_name = subject["name"]

        for grade in GRADES:
            grade_key = grade["grade_key"]
            grade_label = grade["label"]

            for phase in PHASES:
                term_label = phase["t"]  # e.g. "期中1"

                exam_base = f"{subject_slug}_{grade_key}_{term_label}"
                material_path = TAIWAN_DIR / f"{exam_base}.md"
                final_words_path = TAIWAN_DIR / f"{exam_base}.json"
                split_path = TAIWAN_DIR / f"{exam_base}.split"

                if not material_path.exists():
                    print(f"[Skip] Material not found for {subject_name} {grade_label} {term_label}: {material_path}")
                    continue

                if final_words_path.exists():
                    print(f"[Skip] Final Words JSON already exists: {final_words_path}")
                    # 清理殘留的 split（若有）
                    if split_path.exists():
                        try:
                            split_path.unlink()
                        except OSError:
                            pass
                    continue

                print(f"\n===== Generating Words for {subject_name} {grade_label} {term_label} =====")

                try:
                    material_text = load_text_file(material_path)
                except FileNotFoundError as e:
                    print(e)
                    continue

                # 建立或讀取 split 方案
                split_state = build_or_load_split_state(split_path, material_text, exam_base)
                total_chunks = split_state.get("total_chunks", 0)
                chunks = split_state.get("chunks", [])

                if total_chunks == 0 or not chunks:
                    print("  ! Invalid split state, skipping this exam.")
                    continue

                # 逐一處理尚未完成的 chunk
                for chunk in chunks:
                    if chunk.get("status") == "done":
                        continue

                    chunk_index = chunk["index"]
                    start = chunk["start"]
                    end = chunk["end"]

                    chunk_text = material_text[start:end]
                    chunk_json_path = TAIWAN_DIR / f"{exam_base}-chunk{chunk_index}.json"

                    if chunk_json_path.exists():
                        print(f"  - Found existing chunk file, mark done: {chunk_json_path}")
                        chunk["status"] = "done"
                        save_split_state(split_path, split_state)
                        continue

                    print(f"  - Processing chunk {chunk_index}/{total_chunks} (chars {start}–{end})")

                    # 填入 prompt-words 模板
                    prompt = (
                        prompt_template
                        .replace("{subject}", subject_name)
                        .replace("{grade}", grade_label)
                        .replace("{term}", term_label)
                        .replace("{chunk_index}", str(chunk_index))
                        .replace("{total_chunks}", str(total_chunks))
                    )

                    full_prompt = (
                        prompt
                        + "\n\n---\n\n以下是第 "
                        + str(chunk_index)
                        + " 片段的 Markdown 內容，請依此轉換為 Words 陣列：\n\n"
                        + chunk_text
                    )

                    success = False

                    for retry_index in range(MAX_RETRIES_PER_CHUNK):
                        attempt_no = retry_index + 1
                        if attempt_no == 1:
                            print(f"    → Attempt {attempt_no} for chunk {chunk_index}...")
                        else:
                            print(
                                f"    → Retry attempt {attempt_no}/{MAX_RETRIES_PER_CHUNK} "
                                f"for chunk {chunk_index}..."
                            )

                        raw_response = send_to_vertex_ai_for_words(client, full_prompt)

                        if not raw_response:
                            print("      ! No response from API.")
                        else:
                            words = extract_json_from_response(raw_response)
                            if words:
                                save_json(chunk_json_path, words)
                                chunk["status"] = "done"
                                save_split_state(split_path, split_state)
                                success = True
                                break
                            else:
                                print(
                                    f"      ! Failed to parse JSON for chunk {chunk_index} "
                                    f"on attempt {attempt_no}."
                                )

                        if attempt_no < MAX_RETRIES_PER_CHUNK:
                            delay = REQUEST_DELAY_SECONDS * (RETRY_DELAY_MULTIPLIER * attempt_no)
                            print(f"      Waiting {delay} seconds before retrying...")
                            time.sleep(delay)

                    if success:
                        time.sleep(REQUEST_DELAY_SECONDS)
                    else:
                        print(f"  ! Giving up on chunk {chunk_index} for now (will try next run).")

                # 檢查是否所有 chunk 都已完成
                if any(c.get("status") != "done" for c in chunks):
                    print("  ! Not all chunks are completed yet; final Words JSON will not be created this run.")
                    continue

                # 合併所有 chunk 的 Words 陣列
                all_words = []
                for chunk in sorted(chunks, key=lambda c: c["index"]):
                    chunk_index = chunk["index"]
                    chunk_json_path = TAIWAN_DIR / f"{exam_base}-chunk{chunk_index}.json"
                    try:
                        chunk_data = json.loads(chunk_json_path.read_text(encoding="utf-8"))
                        if isinstance(chunk_data, list):
                            all_words.extend(chunk_data)
                    except Exception as e:
                        print(f"  ! Could not read chunk file {chunk_json_path}: {e}")

                if not all_words:
                    print("  ! No Words data collected from chunks; final file will not be created.")
                    continue

                save_json(final_words_path, all_words)

                # 清理 split 與中繼 chunk 檔案
                try:
                    split_path.unlink()
                except OSError:
                    pass

                for chunk in chunks:
                    chunk_index = chunk["index"]
                    chunk_json_path = TAIWAN_DIR / f"{exam_base}-chunk{chunk_index}.json"
                    try:
                        chunk_json_path.unlink()
                    except OSError:
                        pass

                print(f"  - Completed Words JSON: {final_words_path}")

    print("\n===== All materials processed. Words generation complete. =====")


if __name__ == "__main__":
    main()
