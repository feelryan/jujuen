import json
import os
import re
from urllib.parse import urlparse

def generate_coding_problem_configs():
    """
    Reads parameters_coding-problems.json and generates a 'coding problems.json'
    for each topic directory.
    """
    input_file = 'parameters_coding-problems.json'
    output_base_dir = 'output'

    try:
        with open(input_file, 'r', encoding='utf-8') as f:
            data = json.load(f)
    except FileNotFoundError:
        print(f"Error: Input file not found at '{input_file}'")
        return
    except json.JSONDecodeError:
        print(f"Error: Could not decode JSON from '{input_file}'")
        return

    for topic_config in data:
        topic_id = topic_config.get('id')
        problem_urls = topic_config.get('items', [])

        if not topic_id:
            print("Skipping entry with no 'id'.")
            continue

        print(f"\n----- Processing Topic: {topic_id} -----")

        # Prepare the structure for the new coding problems config
        new_config = {
            "id": topic_id,
            "title": "Coding Problems",
            "items": []
        }

        for url in problem_urls:
            try:
                # --- 1. Create the item for the LeetCode problem ---
                path_parts = urlparse(url).path.strip('/').split('/')
                problem_name = next((part for part in reversed(path_parts) if part), None)

                if not problem_name:
                    print(f"  - Could not extract problem name from URL: {url}")
                    continue

                # Simple translation by replacing hyphens with spaces and capitalizing
                problem_title_en = problem_name.replace('-', ' ').title()
                problem_title_zh = problem_title_en # Placeholder for translation

                problem_item = {
                    "id": problem_name,
                    "t": problem_title_zh,
                    "en": problem_title_en,
                    "pointTo": {
                        "type": "document",
                        "data": "web/page",
                        "dataLocation": url
                    }
                }
                new_config["items"].append(problem_item)

                # --- 2. Create the item for the analysis markdown file ---
                analysis_id = f"{problem_name} (analysis)"
                analysis_title_en = f"{problem_title_en} (Analysis)"
                analysis_title_zh = f"{problem_title_zh} (分析)"
                
                # URL-encode the topic_id for use in paths
                encoded_topic_id = topic_id.replace(' ', '%20')

                analysis_item = {
                    "id": analysis_id,
                    "t": analysis_title_zh,
                    "en": analysis_title_en,
                    "pointTo": {
                        "type": "document",
                        "data": "github/md",
                        "dataLocation": f"https://github.com/feelryan/jujuen/blob/Data-Structure-%26-Algorithm/{encoded_topic_id}/{problem_name}_analysis.md"
                    }
                }
                new_config["items"].append(analysis_item)

            except Exception as e:
                print(f"  - Failed to process URL {url}: {e}")

        # --- 3. Save the new 'coding problems.json' file ---
        if new_config["items"]:
            topic_output_dir = os.path.join(output_base_dir, topic_id)
            os.makedirs(topic_output_dir, exist_ok=True)
            output_filepath = os.path.join(topic_output_dir, 'coding problems.json')

            try:
                with open(output_filepath, 'w', encoding='utf-8') as f:
                    json.dump(new_config, f, ensure_ascii=False, indent=4)
                print(f"  Successfully created '{output_filepath}'")
            except IOError as e:
                print(f"  Error writing to file '{output_filepath}': {e}")
        else:
            print("  - No items were generated for this topic.")

if __name__ == '__main__':
    generate_coding_problem_configs()
