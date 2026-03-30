import json
import re
import time
import os
import sys
from pathlib import Path
# 1. 匯入全新的 google-genai SDK
from google import genai
from google.genai import types

# ================= Configuration =================
# Set the region (us-central1 is recommended for latest model support)
LOCATION = "global"

# Model settings
MODEL_NAME = "gemini-3-pro-preview"
REQUEST_DELAY_SECONDS = 2 # Delay between API requests to avoid rate limits

# File and directory paths
BASE_DIR = Path(__file__).resolve().parent
PROJECT_ID_PATH = BASE_DIR / "PROJECT_ID.txt"
MENU_PATH_FILE = "menu-path.json"
TOPICS_FILE = "topics.json"
DIFFICULTIES_FILE = "difficulties.json"
CODELANGS_FILE = "codeLangs.json"
PROMPT_CONCEPTS_FILE = "prompt-concepts.md"
PROMPT_QUESTIONS_FILE = "prompt-questions.md"
OUTPUT_DIR = "output"

# ================= Helper Functions =================

def load_project_id() -> str:
    if PROJECT_ID_PATH.exists():
        return PROJECT_ID_PATH.read_text(encoding="utf-8").strip()
    raise RuntimeError(f"PROJECT_ID.txt not found at {PROJECT_ID_PATH}. Please create it with your GCP project id.")


def load_json_file(filepath):
    """Loads a JSON file and returns its content."""
    try:
        with open(filepath, "r", encoding="utf-8") as f:
            return json.load(f)
    except FileNotFoundError:
        print(f"Error: JSON file not found at {filepath}")
        sys.exit(1)
    except json.JSONDecodeError:
        print(f"Error: Could not decode JSON from {filepath}")
        sys.exit(1)

def load_prompt_template(filepath):
    """Loads a prompt template file and returns its content."""
    try:
        with open(filepath, "r", encoding="utf-8") as f:
            return f.read()
    except FileNotFoundError:
        print(f"Error: Prompt file not found at {filepath}")
        sys.exit(1)

# 2. 修改 API 呼叫函式：接收 client 物件，並使用新的型別 (types)
def send_to_vertex_ai(client, prompt_content):
    """Sends a prompt to Vertex AI and returns the text response."""
    
    # 使用新版的 types.SafetySetting 陣列寫法
    safety_settings = [
        types.SafetySetting(
            category=types.HarmCategory.HARM_CATEGORY_HATE_SPEECH,
            threshold=types.HarmBlockThreshold.BLOCK_ONLY_HIGH
        ),
        types.SafetySetting(
            category=types.HarmCategory.HARM_CATEGORY_DANGEROUS_CONTENT,
            threshold=types.HarmBlockThreshold.BLOCK_ONLY_HIGH
        ),
        types.SafetySetting(
            category=types.HarmCategory.HARM_CATEGORY_SEXUALLY_EXPLICIT,
            threshold=types.HarmBlockThreshold.BLOCK_ONLY_HIGH
        ),
        types.SafetySetting(
            category=types.HarmCategory.HARM_CATEGORY_HARASSMENT,
            threshold=types.HarmBlockThreshold.BLOCK_ONLY_HIGH
        )
    ]

    # 使用新版的 types.GenerateContentConfig 寫法
    config = types.GenerateContentConfig(
        max_output_tokens=65535,
        temperature=0.5,
        top_p=0.95,
        safety_settings=safety_settings
    )

    try:
        # 使用 client.models.generate_content 呼叫模型
        response = client.models.generate_content(
            model=MODEL_NAME,
            contents=prompt_content,
            config=config
        )
        return response.text
    except Exception as e:
        print(f"An error occurred with the Vertex AI API: {e}")
        return None

def extract_json_from_response(text):
    """Extracts a JSON array from the raw text response."""
    # Find the JSON array within ```json ... ``` or just the array itself
    match = re.search(r"```json\s*(\[.*\])\s*```", text, re.DOTALL)
    if match:
        json_str = match.group(1)
    else:
        # Fallback to finding the first occurrence of a JSON array
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

def save_content(filepath, content, is_json=False):
    """Saves content to a file, creating directories if they don't exist."""
    try:
        os.makedirs(os.path.dirname(filepath), exist_ok=True)
        with open(filepath, "w", encoding="utf-8") as f:
            if is_json:
                json.dump(content, f, ensure_ascii=False, indent=2)
            else:
                f.write(content)
        print(f"Successfully saved file: {filepath}")
    except IOError as e:
        print(f"Error saving file {filepath}: {e}")

# ================= Main Program =================

def main():
    project_id = load_project_id()
    """Main function to run the automation script."""
    # 3. 初始化 Client (取代舊的 vertexai.init)
    print(f"Initializing Vertex AI Client for project '{project_id}' in '{LOCATION}'...")
    try:
        # vertexai=True 參數非常重要，它確保你使用的是 Google Cloud Vertex AI 後端
        client = genai.Client(vertexai=True, project=project_id, location=LOCATION)
    except Exception as e:
        print(f"Vertex AI initialization failed: {e}")
        print("Please ensure you have run 'gcloud auth application-default login' and the project ID is correct.")
        return

    # Load input files
    print("Loading configuration and prompt files...")
    menu_data = load_json_file(MENU_PATH_FILE)
    topics_config = load_json_file(TOPICS_FILE)
    difficulties = load_json_file(DIFFICULTIES_FILE)
    code_langs = load_json_file(CODELANGS_FILE)
    concept_prompt_template = load_prompt_template(PROMPT_CONCEPTS_FILE)
    questions_prompt_template = load_prompt_template(PROMPT_QUESTIONS_FILE)

    # topics 以 topics.json 為主，menu-path.json 主要作為整體導航設定
    topics = topics_config or []
    if not isinstance(topics, list) or not topics:
        print("No topics found in topics.json. Exiting.")
        return

    if not isinstance(difficulties, list) or not difficulties:
        print("No difficulties found in difficulties.json. Exiting.")
        return

    if not isinstance(code_langs, list) or not code_langs:
        print("No code languages found in codeLangs.json. Exiting.")
        return

    # Process each topic
    for topic_id in topics:
        print(f"\n----- Processing Topic: {topic_id} -----")
        
        # Create output directory for the topic
        topic_output_dir = os.path.join(OUTPUT_DIR, topic_id)
        os.makedirs(topic_output_dir, exist_ok=True)
        
        # Generate concept markdown files
        for difficulty in difficulties:
            for code_lang in code_langs:
                if not difficulty or not code_lang:
                    continue

                # Check if the file already exists before generating
                filename = f"{topic_id}_{difficulty}_{code_lang}.md"
                filepath = os.path.join(topic_output_dir, filename)
                if os.path.exists(filepath):
                    print(f"  - Skipping existing file: {filepath}")
                    continue

                print(f"  - Generating concept material for: {difficulty}, {code_lang}")

                # Replace placeholders in the concept prompt
                prompt = concept_prompt_template.replace('{topic}', topic_id)
                prompt = prompt.replace('{difficulty}', difficulty)
                prompt = prompt.replace('{codeLang}', code_lang)

                # 4. 傳入 client 物件呼叫生成
                generated_content = send_to_vertex_ai(client, prompt)

                # Save the generated content
                if generated_content:
                    save_content(filepath, generated_content)
                else:
                    print(f"    Failed to generate content for {topic_id} ({difficulty}, {code_lang}).")

                time.sleep(REQUEST_DELAY_SECONDS) # Add a small delay to avoid hitting API rate limits

    print("\n----- All topics processed. Automation complete. -----")

    # Final Completeness Check
    print("\n----- Performing Completeness Check -----")
    missing_files = []
    for topic_id in topics:
        topic_output_dir = os.path.join(OUTPUT_DIR, topic_id)

        # Check for concept markdown files for every (difficulty, codeLang) 組合
        for difficulty in difficulties:
            for code_lang in code_langs:
                if not difficulty or not code_lang:
                    continue

                filename = f"{topic_id}_{difficulty}_{code_lang}.md"
                filepath = os.path.join(topic_output_dir, filename)
                if not os.path.exists(filepath):
                    missing_files.append(filepath)

    if not missing_files:
        print("\n✅ All expected files have been generated successfully!")
    else:
        print(f"\n⚠️ Found {len(missing_files)} missing files:")
        for f in missing_files:
            print(f"  - {f}")

if __name__ == "__main__":
    main()