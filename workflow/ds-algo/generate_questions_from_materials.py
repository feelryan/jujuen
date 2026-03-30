import argparse
import json
import os
import time
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional

from google import genai
from google.genai import types

BASE_DIR = Path(__file__).resolve().parent
PROJECT_ID_PATH = BASE_DIR / "PROJECT_ID.txt"
TOPICS_FILE = BASE_DIR / "topics.json"
CODELANGS_FILE = BASE_DIR / "codeLangs.json"
OUTPUT_DIR = BASE_DIR / "output"
PROMPT_QUESTIONS_FILE = BASE_DIR / "prompt-questions.md"

LOCATION = "global"
MODEL_NAME = "gemini-3-pro-preview"
MAX_OUTPUT_TOKENS = 65535
TEMPERATURE = 0.3
TOP_P = 0.95
REQUEST_DELAY_SECONDS = 2.0
DEFAULT_TOTAL_QUESTIONS_PER_TOPIC = 15


def load_project_id() -> str:
    if PROJECT_ID_PATH.exists():
        return PROJECT_ID_PATH.read_text(encoding="utf-8").strip()
    raise RuntimeError(f"PROJECT_ID.txt not found at {PROJECT_ID_PATH}. Please create it with your GCP project id.")


def load_json_file(path: Path) -> Any:
    if not path.exists():
        return None
    with path.open("r", encoding="utf-8") as f:
        return json.load(f)


def save_json_file(path: Path, data: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)


def extract_json_array(text: str) -> List[Dict[str, Any]]:
    text = text.strip()
    if text.startswith("```"):
        # strip markdown fences if present
        lines = text.splitlines()
        if len(lines) >= 3 and lines[0].startswith("```") and lines[-1].startswith("```"):
            text = "\n".join(lines[1:-1])
            text = text.strip()
    try:
        data = json.loads(text)
        if isinstance(data, list):
            return data
        raise ValueError("Top-level JSON is not a list")
    except Exception as e:
        raise ValueError(f"Failed to parse JSON array from model response: {e}")


def build_questions_prompt(template: str, topic_id: str, remaining: int, total: int, existing_meta: Dict[str, Any]) -> str:
    meta_json = json.dumps(existing_meta or {}, ensure_ascii=False, indent=2)
    prompt = template
    prompt = prompt.replace("{topic}", topic_id)
    prompt = prompt.replace("{remaining_questions}", str(remaining))
    prompt = prompt.replace("{total_questions}", str(total))
    prompt = prompt.replace("{questions_meta}", meta_json)
    return prompt


def send_to_vertex_ai(client: genai.Client, prompt: str) -> str:
    safety_settings = {
        "HATE": "BLOCK_ONLY_HIGH",
        "DANGEROUS_CONTENT": "BLOCK_ONLY_HIGH",
        "SEXUAL": "BLOCK_ONLY_HIGH",
        "HARASSMENT": "BLOCK_ONLY_HIGH",
    }
    generation_config = types.GenerateContentConfig(
        max_output_tokens=MAX_OUTPUT_TOKENS,
        temperature=TEMPERATURE,
        top_p=TOP_P,
        response_mime_type="application/json",
    )
    response = client.models.generate_content(
        model=MODEL_NAME,
        contents=[prompt],
        config=generation_config,
        safety_settings=safety_settings,
    )
    if not response.candidates:
        raise RuntimeError("Empty response from model")
    return response.candidates[0].content.parts[0].text  # type: ignore[return-value]


def build_meta_from_questions(questions: List[Dict[str, Any]], total: int) -> Dict[str, Any]:
    meta_questions: List[Dict[str, Any]] = []
    for idx, q in enumerate(questions, start=1):
        qid = q.get("id") or q.get("no") or f"q{idx:03d}"
        q["id"] = qid
        title = q.get("question") or q.get("title") or ""
        if isinstance(title, list) and title:
            # DS-ALGO schema: array of sentences
            first = title[0]
            if isinstance(first, dict):
                title = first.get("t") or first.get("en") or ""
            else:
                title = str(first)
        elif not isinstance(title, str):
            title = str(title)
        meta_questions.append({
            "id": qid,
            "title": title[:80],
        })
    return {
        "totalQuestionsNum": total,
        "questions": meta_questions,
        "isAllCompleted": len(questions) >= total,
        "updatedAt": datetime.utcnow().isoformat(timespec="seconds") + "Z",
    }


def generate_questions_for_topic(
    client: genai.Client,
    topic_id: str,
    questions_prompt_template: str,
    total_target: int,
) -> None:
    topic_output_dir = OUTPUT_DIR / topic_id
    topic_output_dir.mkdir(parents=True, exist_ok=True)

    questions_path = topic_output_dir / "questions.json"
    meta_path = topic_output_dir / "questions-meta.json"

    existing_questions: List[Dict[str, Any]] = []
    if questions_path.exists():
        loaded = load_json_file(questions_path)
        if isinstance(loaded, list):
            existing_questions = loaded

    existing_count = len(existing_questions)
    remaining = max(total_target - existing_count, 0)

    # Rebuild meta from existing questions
    meta = build_meta_from_questions(existing_questions, total_target)
    save_json_file(meta_path, meta)

    if remaining <= 0:
        print(f"  - Topic {topic_id}: already has {existing_count} questions (>= target {total_target}), skipping.")
        return

    print(f"  - Topic {topic_id}: {existing_count} existing questions, need {remaining} more (target {total_target}).")

    # Build prompt with current meta so the model can avoid duplicates
    prompt = build_questions_prompt(
        questions_prompt_template,
        topic_id=topic_id,
        remaining=remaining,
        total=total_target,
        existing_meta=meta,
    )

    try:
        raw = send_to_vertex_ai(client, prompt)
    except Exception as e:
        print(f"    Error calling model for topic {topic_id}: {e}")
        return

    try:
        new_questions = extract_json_array(raw)
    except ValueError as e:
        print(f"    Failed to parse questions JSON for topic {topic_id}: {e}")
        return

    if not new_questions:
        print(f"    Model returned empty questions array for topic {topic_id}.")
        return

    # Trim to remaining if model returned more than requested
    if len(new_questions) > remaining:
        new_questions = new_questions[:remaining]

    print(f"    Parsed {len(new_questions)} new questions for topic {topic_id}.")

    all_questions = existing_questions + new_questions
    meta = build_meta_from_questions(all_questions, total_target)

    save_json_file(questions_path, all_questions)
    save_json_file(meta_path, meta)

    print(f"    Saved questions.json and questions-meta.json for topic {topic_id}.")



def main(only_topic_id: Optional[str] = None, total_questions: Optional[int] = None) -> None:
    project_id = load_project_id()
    client = genai.Client(vertexai=True, project=project_id, location=LOCATION)

    topics = load_json_file(TOPICS_FILE) or []
    code_langs = load_json_file(CODELANGS_FILE) or []

    if not isinstance(topics, list) or not topics:
        raise RuntimeError(f"Invalid or empty topics list in {TOPICS_FILE}")

    # Even though we currently generate one shared questions.json per topic,
    # we keep code_langs loaded so the config generator and this script stay aligned.
    if not isinstance(code_langs, list) or not code_langs:
        raise RuntimeError(f"Invalid or empty codeLangs list in {CODELANGS_FILE}")

    questions_prompt_template = Path(PROMPT_QUESTIONS_FILE).read_text(encoding="utf-8")

    effective_total = total_questions or DEFAULT_TOTAL_QUESTIONS_PER_TOPIC

    for topic_id in topics:
        if only_topic_id and topic_id != only_topic_id:
            continue

        print(f"\n=== Generating questions for topic: {topic_id} ===")
        generate_questions_for_topic(
            client=client,
            topic_id=topic_id,
            questions_prompt_template=questions_prompt_template,
            total_target=effective_total,
        )

        # For now, DS-ALGO produces one questions.json per topic.
        # We also mirror it into per-language files questions({codeLang}).json
        topic_output_dir = OUTPUT_DIR / topic_id
        questions_path = topic_output_dir / "questions.json"
        if questions_path.exists():
            questions_data = load_json_file(questions_path)
            if isinstance(questions_data, list):
                for code_lang in code_langs:
                    lang_path = topic_output_dir / f"questions({code_lang}).json"
                    save_json_file(lang_path, questions_data)
        time.sleep(REQUEST_DELAY_SECONDS)

    print("\n----- Question generation complete. -----")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Generate DS-ALGO questions from topics using Vertex AI.")
    parser.add_argument("--topic-id", help="Only process a single topic id", default=None)
    parser.add_argument("--total-questions", type=int, help="Target total questions per topic (default: 20)", default=None)
    args = parser.parse_args()

    main(only_topic_id=args.topic_id, total_questions=args.total_questions)
