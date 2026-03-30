import json
import os
import re
import time
import sys
from urllib.parse import urlparse

# Assuming the new genai SDK is used, similar to the updated generate_materials.py
from google import genai
from google.genai import types

# ================= Configuration =================
# Please fill in your Google Cloud Project ID
PROJECT_ID = "qwiklabs-gcp-00-2200bc248a74" 
LOCATION = "global"

# Model settings
MODEL_NAME = "gemini-1.5-flash-001" # Using Flash for speed and cost-effectiveness
REQUEST_DELAY_SECONDS = 10 # Increased delay for potentially longer analysis tasks

# File and directory paths
CODING_PROBLEMS_FILE = "parameters_coding-problems.json"
PROMPT_ANALYSIS_FILE = "prompt-analysis.md"
OUTPUT_DIR = "output"

# ================= Helper Functions =================

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

def send_to_vertex_ai(client, prompt_content):
    """Sends a prompt to Vertex AI and returns the text response."""
    safety_settings = [
        types.SafetySetting(category=types.HarmCategory.HARM_CATEGORY_HATE_SPEECH, threshold=types.HarmBlockThreshold.BLOCK_ONLY_HIGH),
        types.SafetySetting(category=types.HarmCategory.HARM_CATEGORY_DANGEROUS_CONTENT, threshold=types.HarmBlockThreshold.BLOCK_ONLY_HIGH),
        types.SafetySetting(category=types.HarmCategory.HARM_CATEGORY_SEXUALLY_EXPLICIT, threshold=types.HarmBlockThreshold.BLOCK_ONLY_HIGH),
        types.SafetySetting(category=types.HarmCategory.HARM_CATEGORY_HARASSMENT, threshold=types.HarmBlockThreshold.BLOCK_ONLY_HIGH)
    ]
    config = types.GenerateContentConfig(
        max_output_tokens=8192, # Using a large token limit for detailed analysis
        temperature=0.4,
        top_p=0.95,
        safety_settings=safety_settings
    )
    try:
        # The new SDK uses a client object
        response = client.models.generate_content(
            model=MODEL_NAME,
            contents=prompt_content,
            config=config
        )
        return response.text
    except Exception as e:
        print(f"An error occurred with the Vertex AI API: {e}")
        # Adding a retry mechanism for resource exhausted errors
        if "Resource exhausted" in str(e):
            print("Resource exhausted. Waiting for 60 seconds before retrying...")
            time.sleep(60)
            try:
                response = client.models.generate_content(model=MODEL_NAME, contents=prompt_content, config=config)
                return response.text
            except Exception as retry_e:
                print(f"Retry failed: {retry_e}")
                return None
        return None

def save_content(filepath, content):
    """Saves content to a file, creating directories if they don't exist."""
    try:
        os.makedirs(os.path.dirname(filepath), exist_ok=True)
        with open(filepath, "w", encoding="utf-8") as f:
            f.write(content)
        print(f"  Successfully saved file: {filepath}")
    except IOError as e:
        print(f"  Error saving file {filepath}: {e}")

# This is a placeholder. A real implementation would need a robust web scraping library
# like BeautifulSoup and requests. For this script, we'll simulate it.
def fetch_webpage_content(url):
    """
    Placeholder function to simulate fetching web content.
    In a real scenario, this would use libraries like requests and BeautifulSoup
    to scrape the LeetCode problem description.
    For now, it just returns the URL itself as a marker.
    """
    print(f"  (Simulating) Fetching content from: {url}")
    # This is where you would integrate a real web scraper.
    # For example:
    # import requests
    # from bs4 import BeautifulSoup
    # page = requests.get(url)
    # soup = BeautifulSoup(page.content, 'html.parser')
    # problem_div = soup.find('div', class_='_1l1MA') # This class name might change
    # return problem_div.get_text() if problem_div else "Content not found"
    return f"Content for {url} would be scraped here."


# ================= Main Program =================

def main():
    """Main function to run the analysis generation script."""
    print("Starting analysis generation process...")
    
    # 1. Initialize Vertex AI Client
    print(f"Initializing Vertex AI Client for project '{PROJECT_ID}' in '{LOCATION}'...")
    try:
        client = genai.Client(vertexai=True, project=PROJECT_ID, location=LOCATION)
    except Exception as e:
        print(f"Vertex AI initialization failed: {e}")
        print("Please ensure you have run 'gcloud auth application-default login'.")
        return

    # 2. Load configuration and prompt files
    print("Loading configuration and prompt files...")
    coding_problems_data = load_json_file(CODING_PROBLEMS_FILE)
    analysis_prompt_template = load_prompt_template(PROMPT_ANALYSIS_FILE)

    # 3. Iterate through each topic and its problems
    for topic_config in coding_problems_data:
        topic_id = topic_config.get('id')
        problem_urls = topic_config.get('items', [])

        if not topic_id:
            continue

        print(f"\n----- Processing Topic: {topic_id} -----")
        topic_output_dir = os.path.join(OUTPUT_DIR, topic_id)

        for url in problem_urls:
            try:
                path_parts = urlparse(url).path.strip('/').split('/')
                problem_name = next((part for part in reversed(path_parts) if part), None)

                if not problem_name:
                    print(f"  - Could not extract problem name from URL: {url}")
                    continue
                
                # Define the output filename and check if it already exists
                output_filename = f"{problem_name}_analysis.md"
                output_filepath = os.path.join(topic_output_dir, output_filename)

                if os.path.exists(output_filepath):
                    print(f"  - Skipping existing analysis file: {output_filepath}")
                    continue

                print(f"\n  -> Generating analysis for: {problem_name}")

                # 4. Fetch problem content (simulated)
                problem_content = fetch_webpage_content(url)
                if "Content not found" in problem_content:
                    print(f"     Could not fetch content for {url}. Skipping.")
                    continue

                # 5. Prepare the prompt
                prompt = analysis_prompt_template.replace('{problem_name}', problem_name.replace('-', ' ').title())
                prompt = prompt.replace('{problem_content}', problem_content)

                # 6. Send to AI for analysis
                generated_analysis = send_to_vertex_ai(client, prompt)

                # 7. Save the generated content
                if generated_analysis:
                    save_content(output_filepath, generated_analysis)
                else:
                    print(f"     Failed to generate analysis for {problem_name}.")
                
                # Delay to respect API rate limits
                print(f"     Waiting for {REQUEST_DELAY_SECONDS} seconds...")
                time.sleep(REQUEST_DELAY_SECONDS)

            except Exception as e:
                print(f"  - An unexpected error occurred while processing {url}: {e}")

    print("\n----- Analysis generation process complete. -----")

if __name__ == "__main__":
    main()
