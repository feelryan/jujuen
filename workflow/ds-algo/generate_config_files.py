import json
import os
import re


TOPICS_FILE = "topics.json"
DIFFICULTIES_FILE = "difficulties.json"
CODELANGS_FILE = "codeLangs.json"


def generate_config_files():
    """Reads topics/difficulties/codeLangs JSON and generates a config file for each topic."""

    output_dir = "."  # Save in the same directory as the script

    try:
        with open(TOPICS_FILE, "r", encoding="utf-8") as f:
            topics = json.load(f)
    except FileNotFoundError:
        print(f"Error: '{TOPICS_FILE}' not found.")
        return
    except json.JSONDecodeError:
        print(f"Error: Could not decode JSON from '{TOPICS_FILE}'.")
        return

    try:
        with open(DIFFICULTIES_FILE, "r", encoding="utf-8") as f:
            difficulties = json.load(f)
    except FileNotFoundError:
        print(f"Error: '{DIFFICULTIES_FILE}' not found.")
        return
    except json.JSONDecodeError:
        print(f"Error: Could not decode JSON from '{DIFFICULTIES_FILE}'.")
        return

    try:
        with open(CODELANGS_FILE, "r", encoding="utf-8") as f:
            code_langs = json.load(f)
    except FileNotFoundError:
        print(f"Error: '{CODELANGS_FILE}' not found.")
        return
    except json.JSONDecodeError:
        print(f"Error: Could not decode JSON from '{CODELANGS_FILE}'.")
        return

    if not isinstance(topics, list) or not topics:
        print(f"No topics found in '{TOPICS_FILE}'.")
        return

    if not isinstance(difficulties, list) or not difficulties:
        print(f"No difficulties found in '{DIFFICULTIES_FILE}'.")
        return

    if not isinstance(code_langs, list) or not code_langs:
        print(f"No code languages found in '{CODELANGS_FILE}'.")
        return

    # Pre-defined translations for knowledge levels, keyed by difficulty
    translations = {
        "beginner": {
            "t": "基礎知識",
            "c": "基础知识",
            "p": "jī chǔ zhī shí",
            "z": "ㄐㄧ ㄔㄨˇ ㄓ ㄕˋ",
            "en_label": "Basic Knowledge",
        },
        "intermediate": {
            "t": "中階知識",
            "c": "中阶知识",
            "p": "zhōng jiē zhī shí",
            "z": "ㄓㄨㄥ ㄐㄧㄝ ㄓ ㄕˋ",
            "en_label": "Intermediate Knowledge",
        },
        "advanced": {
            "t": "進階知識",
            "c": "进阶知识",
            "p": "jìn jiē zhī shí",
            "z": "ㄐㄧㄣˋ ㄐㄧㄝ ㄓ ㄕˋ",
            "en_label": "Advanced Knowledge",
        },
    }

    for topic_id in topics:
        if not topic_id:
            continue

        # URL-encode the topic_id for use in paths, replacing spaces with %20
        encoded_topic_id = topic_id.replace(" ", "%20")

        items: list[dict] = []

        # Build knowledge items for each (codeLang, difficulty) chain
        for code_lang in code_langs:
            previous_id = None
            for difficulty in difficulties:
                trans = translations.get(difficulty)
                if not trans:
                    print(f"Warning: No translation defined for difficulty '{difficulty}', skipping.")
                    continue

                node_id = f"{topic_id}_{difficulty}-knowledge ({code_lang})"
                parent_id = previous_id

                item = {
                    "id": node_id,
                    "parent": parent_id,
                    "t": trans["t"],
                    "c": trans["c"],
                    "p": trans["p"],
                    "z": trans["z"],
                    "en": f"{trans['en_label']} ({code_lang})",
                    "pointTo": {
                        "type": "document",
                        "data": "github/md",
                        "dataLocation": (
                            f"https://github.com/feelryan/jujuen/blob/Data-Structure-%26-Algorithm/"
                            f"{encoded_topic_id}/{encoded_topic_id}_{difficulty}_{code_lang}.md"
                        ),
                    },
                }

                items.append(item)
                previous_id = node_id

        # For Questions, create one per codeLang, parented to the highest difficulty for that codeLang
        highest_difficulty = difficulties[-1]
        for code_lang in code_langs:
            questions_item = {
                "id": f"{topic_id}_{code_lang}_questions",
                "parent": f"{topic_id}_{highest_difficulty}-knowledge ({code_lang})",
                "t": f"Questions ({code_lang})",
                "en": f"Questions ({code_lang})",
                "showLinkLine": False,
                "pointTo": {
                    "type": "document",
                    "data": "github/json",
                    "dataLocation": (
                        "https://github.com/feelryan/jujuen/blob/Data-Structure-%26-Algorithm/"
                        f"{encoded_topic_id}/questions({code_lang}).json"
                    ),
                    "renderObject": "Question",
                },
            }
            items.append(questions_item)

        # Coding problems remains a single item per topic
        items.append(
            {
                "id": f"{topic_id}_coding-problems",
                "parent": f"{topic_id}_advanced-knowledge (Python)",
                "t": "Coding Problems",
                "en": "coding problems",
                "showLinkLine": False,
                "pointTo": {
                    "type": "category",
                    "data": "github/json",
                    "dataLocation": (
                        "https://github.com/feelryan/jujuen/blob/Data-Structure-%26-Algorithm/"
                        f"{encoded_topic_id}/coding problems.json"
                    ),
                },
            }
        )

        config = {
            "id": topic_id,
            "title": topic_id,
            "items": items,
        }

        # Sanitize the topic_id to create a valid filename
        # Replace characters that are problematic in filenames
        safe_filename = re.sub(r"[\\/*?:\"<>|]", "_", topic_id)
        output_filename = os.path.join(output_dir, f"{safe_filename}.json")

        try:
            with open(output_filename, "w", encoding="utf-8") as f:
                json.dump(config, f, ensure_ascii=False, indent=4)
            print(f"Successfully created '{output_filename}'")
        except IOError as e:
            print(f"Error writing to file '{output_filename}': {e}")


if __name__ == "__main__":
    generate_config_files()
