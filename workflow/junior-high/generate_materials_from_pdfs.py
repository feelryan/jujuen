import os
import time
from pathlib import Path

from google import genai
from google.genai import types

# ================= Configuration =================

# Please fill in your Google Cloud Project ID (not the name)
PROJECT_ID = "qwiklabs-gcp-03-cba49d2607da"
# Set the region (global is recommended for latest model support)
LOCATION = "global"

# Model settings
MODEL_NAME = "gemini-3-pro-preview"
REQUEST_DELAY_SECONDS = 6  # Delay between API requests to avoid rate limits

# Base directories
BASE_DIR = Path(__file__).resolve().parent
PDF_BASE_DIR = BASE_DIR / "tcool.cc" / "materials"
OUTPUT_BASE_DIR = BASE_DIR / "taiwan"
PROMPT_TEMPLATE_FILE = BASE_DIR / "prompt-materials-from-pdfs.md"

# Subjects and grades configuration
SUBJECTS = [
    {"slug": "math", "name": "數學"},
    {"slug": "nature", "name": "自然"},
]

GRADES = [
    {"id": "7th", "grade_key": "7th", "label": "七年級"},
    {"id": "8th", "grade_key": "8th", "label": "八年級"},
    {"id": "9th", "grade_key": "9th", "label": "九年級"},
]

PHASES = [
    {"key": "mid1", "t": "期中1"},
    {"key": "mid2", "t": "期中2"},
    {"key": "final2", "t": "期末2"},
    {"key": "final3", "t": "期末3"},
]


# ================= Helper Functions =================


def load_prompt_template(path: Path) -> str:
    if not path.exists():
        raise FileNotFoundError(f"Prompt template file not found: {path}")
    return path.read_text(encoding="utf-8")


def send_to_vertex_ai_with_pdf(client: genai.Client, prompt_content: str, pdf_path: Path) -> str | None:
    """Sends a prompt and a PDF file to Vertex AI and returns the text response.

    Note: We send the PDF as inline bytes (types.Part.from_bytes) because
    client.files.upload is only supported in the Gemini Developer client,
    not in the Vertex AI backend (vertexai=True).
    """

    # Safety settings (same pattern as ds-algo/generate_materials.py)
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
        top_p=0.95,
        safety_settings=safety_settings,
    )

    try:
        print(f"  - Reading PDF bytes: {pdf_path}")
        pdf_bytes = pdf_path.read_bytes()

        # Build a Part for the PDF content
        pdf_part = types.Part.from_bytes(
            data=pdf_bytes,
            mime_type="application/pdf",
        )

        # Provide both the textual instructions and the PDF file as input
        contents = [prompt_content, pdf_part]

        response = client.models.generate_content(
            model=MODEL_NAME,
            contents=contents,
            config=config,
        )
        return response.text
    except Exception as e:
        print(f"An error occurred with the Vertex AI API for {pdf_path}: {e}")
        return None


def save_markdown(filepath: Path, content: str) -> None:
    filepath.parent.mkdir(parents=True, exist_ok=True)
    filepath.write_text(content, encoding="utf-8")
    print(f"Successfully saved file: {filepath}")


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
        prompt_template = load_prompt_template(PROMPT_TEMPLATE_FILE)
    except FileNotFoundError as e:
        print(e)
        return

    # Iterate over subjects, grades, and phases
    for subject in SUBJECTS:
        subject_slug = subject["slug"]
        subject_name = subject["name"]

        for grade in GRADES:
            grade_id = grade["id"]
            grade_key = grade["grade_key"]
            grade_label = grade["label"]

            for phase in PHASES:
                term_label = phase["t"]  # e.g., "期中1"

                # Expected merged PDF path: materials/{grade_id}/{subject_name}/{term_label}_merged.pdf
                pdf_path = PDF_BASE_DIR / grade_id / subject_name / f"{term_label}_merged.pdf"

                if not pdf_path.exists():
                    print(f"[Skip] PDF not found for {subject_name} {grade_label} {term_label}: {pdf_path}")
                    continue

                # Output file name: {科目}_{年級}_{期別}.md (using subject slug + grade_key + term_label)
                output_filename = f"{subject_slug}_{grade_key}_{term_label}.md"
                output_path = OUTPUT_BASE_DIR / output_filename

                if output_path.exists():
                    print(f"[Skip] Output already exists: {output_path}")
                    continue

                print(f"\n----- Generating material for {subject_name} {grade_label} {term_label} -----")

                # Fill in the prompt template
                prompt = (
                    prompt_template
                    .replace("{subject}", subject_name)
                    .replace("{grade}", grade_label)
                    .replace("{term}", term_label)
                )

                generated_content = send_to_vertex_ai_with_pdf(client, prompt, pdf_path)

                if generated_content:
                    save_markdown(output_path, generated_content)
                else:
                    print(f"  ! Failed to generate content for {subject_name} {grade_label} {term_label}.")

                # Avoid hitting rate limits
                time.sleep(REQUEST_DELAY_SECONDS)

    print("\n----- All materials generation attempts complete. -----")


if __name__ == "__main__":
    main()
