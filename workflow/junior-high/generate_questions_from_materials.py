import json
import re
import time
from pathlib import Path

from google import genai
from google.genai import types

# ================= Configuration =================

# Please fill in your Google Cloud Project ID (not the name)
PROJECT_ID = "qwiklabs-gcp-00-bdb326949df8"
# Set the region (global is recommended for latest model support)
LOCATION = "global"

MODEL_NAME = "gemini-3-pro-preview"
REQUEST_DELAY_SECONDS = 6  # Delay between API requests to avoid rate limits

BASE_DIR = Path(__file__).resolve().parent
TAIWAN_DIR = BASE_DIR / "taiwan"
PROMPT_QUESTIONS_FILE = BASE_DIR / "prompt-questions.md"

# Subjects and grades configuration (aligned with other junior-high scripts)
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

# How many batches of questions to generate per exam
TOTAL_BATCHES = 3

# How many times to retry a failed batch within a single script run
MAX_RETRIES_PER_BATCH = 3

# Base delay (in seconds) before retrying a failed batch.
# Actual delay will be REQUEST_DELAY_SECONDS * (retry_index + 1).
RETRY_DELAY_MULTIPLIER = 1


# ================= Helper Functions =================


def load_text_file(path: Path) -> str:
    if not path.exists():
        raise FileNotFoundError(f"File not found: {path}")
    return path.read_text(encoding="utf-8")


def extract_json_from_response(text: str):
    """Extracts a JSON array from the raw text response.

    We expect the model to return a pure JSON array, but we still
    defensively handle cases where it might be wrapped in ```json fences.
    """

    # Prefer content inside ```json ... ``` if present
    match = re.search(r"```json\s*(\[.*\])\s*```", text, re.DOTALL)
    if match:
        json_str = match.group(1)
    else:
        # Fallback: first JSON array occurrence
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


def save_json(path: Path, data) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)
    print(f"Successfully saved JSON: {path}")


def build_previous_batches_summary(batch_files: list[Path]) -> str:
    """Build a short text summary of previous batches to help avoid duplicates.

    We summarize using each question's keywords and第一句中文題幹。
    """

    summaries: list[str] = []

    for idx, batch_path in enumerate(batch_files, start=1):
        try:
            batch_data = json.loads(batch_path.read_text(encoding="utf-8"))
        except Exception as e:
            print(f"  ! Could not read previous batch {batch_path}: {e}")
            continue

        batch_lines: list[str] = []
        for q in batch_data:
            keywords = q.get("keywords", "")
            question_list = q.get("question", [])
            first_chinese = ""
            if question_list and isinstance(question_list[0], dict):
                first_chinese = question_list[0].get("t", "")
            if keywords or first_chinese:
                snippet = first_chinese[:30]
                batch_lines.append(f"題: {snippet}... | keywords: {keywords}")

        if batch_lines:
            summaries.append(f"[Batch {idx}]\n" + "\n".join(batch_lines))

    return "\n\n".join(summaries) if summaries else ""


def send_to_vertex_ai_for_questions(client: genai.Client, prompt: str) -> str | None:
    """Sends the prompt (which already包含教材內容) to Vertex AI and returns raw text."""

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
        prompt_template = load_text_file(PROMPT_QUESTIONS_FILE)
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

                material_filename = f"{subject_slug}_{grade_key}_{term_label}.md"
                material_path = TAIWAN_DIR / material_filename

                if not material_path.exists():
                    print(f"[Skip] Material not found for {subject_name} {grade_label} {term_label}: {material_path}")
                    continue

                # Final combined questions file: {科目}_{年級}_{期別}考題.json
                exam_base = f"{subject_slug}_{grade_key}_{term_label}"
                final_questions_path = TAIWAN_DIR / f"{exam_base}考題.json"

                if final_questions_path.exists():
                    print(f"[Skip] Final questions already exists: {final_questions_path}")
                    continue

                print(f"\n===== Generating questions for {subject_name} {grade_label} {term_label} =====")

                try:
                    material_text = load_text_file(material_path)
                except FileNotFoundError as e:
                    print(e)
                    continue

                batch_files: list[Path] = []

                for batch_num in range(1, TOTAL_BATCHES + 1):
                    batch_path = TAIWAN_DIR / f"{exam_base}考題-batch{batch_num}.json"
                    if batch_path.exists():
                        print(f"  - Skipping existing batch file: {batch_path}")
                        batch_files.append(batch_path)
                        continue

                    print(f"  - Generating batch {batch_num}/{TOTAL_BATCHES}...")

                    previous_summary = ""
                    if batch_num > 1 and batch_files:
                        previous_summary = build_previous_batches_summary(batch_files)

                    # Fill in the prompt template
                    prompt = (
                        prompt_template
                        .replace("{subject}", subject_name)
                        .replace("{grade}", grade_label)
                        .replace("{term}", term_label)
                        .replace("{batch_num}", str(batch_num))
                        .replace("{previous_batches_summary}", previous_summary)
                    )

                    # Attach material content after the instructions
                    full_prompt = (
                        prompt
                        + "\n\n---\n\n以下是完整的教材內容，請依此出題（不要逐句抄寫題幹，可改寫重組）：\n\n"
                        + material_text
                    )

                    success = False

                    for retry_index in range(MAX_RETRIES_PER_BATCH):
                        attempt_no = retry_index + 1
                        if attempt_no == 1:
                            print(f"    → Attempt {attempt_no} for batch {batch_num}...")
                        else:
                            print(
                                f"    → Retry attempt {attempt_no}/{MAX_RETRIES_PER_BATCH} "
                                f"for batch {batch_num}..."
                            )

                        raw_response = send_to_vertex_ai_for_questions(client, full_prompt)

                        if not raw_response:
                            print("      ! No response from API.")
                        else:
                            questions = extract_json_from_response(raw_response)
                            if questions:
                                save_json(batch_path, questions)
                                batch_files.append(batch_path)
                                success = True
                                break
                            else:
                                print(
                                    f"      ! Failed to parse JSON for batch {batch_num} "
                                    f"on attempt {attempt_no}."
                                )

                        # If not successful and we still have retries, wait before retrying
                        if attempt_no < MAX_RETRIES_PER_BATCH:
                            delay = REQUEST_DELAY_SECONDS * (RETRY_DELAY_MULTIPLIER * attempt_no)
                            print(f"      Waiting {delay} seconds before retrying...")
                            time.sleep(delay)

                    # Small delay between batches on success, to avoid rate limits
                    if success:
                        time.sleep(REQUEST_DELAY_SECONDS)

                # Merge all batch files into final questions JSON
                # We only consider the exam "complete" when **all** expected
                # batch files (1..TOTAL_BATCHES) 存在且可讀取。

                # Recompute expected batch paths to avoid relying solely on
                # the in-memory batch_files (which可能在本次執行中部分失敗)。
                expected_batch_paths = [
                    TAIWAN_DIR / f"{exam_base}考題-batch{i}.json"
                    for i in range(1, TOTAL_BATCHES + 1)
                ]

                missing_batches = [
                    i
                    for i, path in enumerate(expected_batch_paths, start=1)
                    if not path.exists()
                ]

                if missing_batches:
                    print(
                        "  ! Some batch files are missing, skip final merge this run. "
                        f"Missing batch indices: {missing_batches}."
                    )
                    print(
                        "    → 已產生的 batch JSON 會保留，請稍後重新執行程式，"
                        "只會補齊缺少的批次，待全部批次都存在後再自動合併。"
                    )
                    continue

                all_questions = []
                for batch_path in expected_batch_paths:
                    try:
                        batch_data = json.loads(batch_path.read_text(encoding="utf-8"))
                        if isinstance(batch_data, list):
                            all_questions.extend(batch_data)
                    except Exception as e:
                        print(f"  ! Could not read batch file {batch_path}: {e}")

                if not all_questions:
                    print(
                        "  ! No questions collected from batches; final file will not be created."
                    )
                    continue

                save_json(final_questions_path, all_questions)

                # Optional: clean up batch files after successful merge
                for batch_path in expected_batch_paths:
                    try:
                        batch_path.unlink()
                    except OSError as e:
                        print(f"  ! Could not delete batch file {batch_path}: {e}")

    print("\n===== All exams processed. Question generation complete. =====")


if __name__ == "__main__":
    main()
