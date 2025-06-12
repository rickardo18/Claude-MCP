import os
import subprocess
import requests
from pathlib import Path

GEMINI_API_KEY = os.environ.get('GEMINI_API_KEY')
NOTION_TOKEN = os.environ['NOTION_TOKEN']
NOTION_PAGE_ID = os.environ['NOTION_FULL_DESCRIPTION_PAGE']

def get_source_files():
    """Get all Python source files in the repository."""
    repo_root = subprocess.check_output(['git', 'rev-parse', '--show-toplevel']).decode('utf-8').strip()
    source_files = []
    
    for path in Path(repo_root).rglob('*.py'):
        # Skip virtual environments, build directories, etc.
        if any(part.startswith('.') or part == '__pycache__' for part in path.parts):
            continue
        source_files.append(str(path.relative_to(repo_root)))
    
    return source_files

def read_file_content(file_path):
    """Read the content of a file."""
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            return f.read()
    except Exception as e:
        print(f"Error reading {file_path}: {str(e)}")
        return ""

def analyze_codebase(files):
    """Use Gemini to analyze the codebase and generate summary and features."""
    if not GEMINI_API_KEY:
        return "(AI analysis unavailable: GEMINI_API_KEY not set)", []

    all_content = ""
    for file in files:
        content = read_file_content(file)
        all_content += f"\nFile: {file}\nContent:\n{content}\n"

    prompt = (
        "You are a code analyzer. Given the following codebase, provide:\n"
        "1. A brief, clear summary of what the program does (2-3 sentences)\n"
        "2. A bullet-point list of key features and functionality\n\n"
        "Here's the codebase:\n" + all_content + "\n\n"
        "Please format your response as follows:\n"
        "SUMMARY:\n[Your summary here]\n\n"
        "FEATURES:\n- [feature 1]\n- [feature 2]\netc."
    )

    headers = {
        "Content-Type": "application/json"
    }
    
    data = {
        "contents": [
            {"parts": [{"text": prompt}]}
        ]
    }
    
    url = "https://generativelanguage.googleapis.com/v1beta/models/gemini-2.0-flash:generateContent"
    response = requests.post(url, headers=headers, params={"key": GEMINI_API_KEY}, json=data)
    
    if response.status_code == 200:
        try:
            result = response.json()['candidates'][0]['content']['parts'][0]['text'].strip()
            # Split the response into summary and features
            summary_part = result.split('FEATURES:')[0].replace('SUMMARY:', '').strip()
            features_part = result.split('FEATURES:')[1].strip()
            return summary_part, features_part
        except Exception as e:
            return f"(AI analysis failed: Unexpected Gemini response: {str(e)})", ""
    else:
        return f"(AI analysis failed: {response.text})", ""

def get_notion_page_children(page_id):
    """Get all child block IDs of a Notion page."""
    url = f"https://api.notion.com/v1/blocks/{page_id}/children?page_size=100"
    headers = {
        'Authorization': f'Bearer {NOTION_TOKEN}',
        'Notion-Version': '2022-06-28'
    }
    response = requests.get(url, headers=headers)
    if response.status_code == 200:
        blocks = response.json().get('results', [])
        return [block['id'] for block in blocks]
    else:
        return []

def delete_notion_page_children(page_id):
    """Delete all child blocks of a Notion page (except the title)."""
    block_ids = get_notion_page_children(page_id)
    headers = {
        'Authorization': f'Bearer {NOTION_TOKEN}',
        'Notion-Version': '2022-06-28'
    }
    for block_id in block_ids:
        url = f"https://api.notion.com/v1/blocks/{block_id}"
        requests.delete(url, headers=headers)

def parse_features_to_blocks(summary, features):
    """Convert summary and features text into Notion block objects."""
    blocks = []
    # Add summary as a heading and paragraph
    blocks.append({
        "object": "block",
        "type": "heading_1",
        "heading_1": {
            "rich_text": [{
                "type": "text",
                "text": {"content": "Program Summary"}
            }]
        }
    })
    if summary:
        blocks.append({
            "object": "block",
            "type": "paragraph",
            "paragraph": {
                "rich_text": [{
                    "type": "text",
                    "text": {"content": summary}
                }]
            }
        })
    # Add features as a heading and bulleted list
    blocks.append({
        "object": "block",
        "type": "heading_1",
        "heading_1": {
            "rich_text": [{
                "type": "text",
                "text": {"content": "Features"}
            }]
        }
    })
    for line in features.splitlines():
        line = line.strip()
        if line.startswith('- '):
            feature_text = line[2:].strip()
            if feature_text:
                blocks.append({
                    "object": "block",
                    "type": "bulleted_list_item",
                    "bulleted_list_item": {
                        "rich_text": [{
                            "type": "text",
                            "text": {"content": feature_text}
                        }]
                    }
                })
        elif line:
            # If not a bullet, add as a paragraph (fallback)
            blocks.append({
                "object": "block",
                "type": "paragraph",
                "paragraph": {
                    "rich_text": [{
                        "type": "text",
                        "text": {"content": line}
                    }]
                }
            })
    return blocks

def update_notion_page(summary, features):
    """Overwrite the Notion page (except title) with summary and features as formatted blocks."""
    # 1. Delete all children
    delete_notion_page_children(NOTION_PAGE_ID)
    # 2. Add new blocks
    blocks = parse_features_to_blocks(summary, features)
    url = f'https://api.notion.com/v1/blocks/{NOTION_PAGE_ID}/children'
    headers = {
        'Authorization': f'Bearer {NOTION_TOKEN}',
        'Content-Type': 'application/json',
        'Notion-Version': '2022-06-28'
    }
    data = {"children": blocks}
    response = requests.patch(url, headers=headers, json=data)
    if response.status_code not in (200, 204):
        raise Exception(f"Failed to update Notion page: {response.text}")

def main():
    try:
        # Get all source files
        source_files = get_source_files()
        
        # Analyze the codebase
        summary, features = analyze_codebase(source_files)
        
        # Update the Notion page
        update_notion_page(summary, features)
        
        print("Successfully updated Notion page with program summary and features.")
    except Exception as e:
        print(f"Error updating Notion page: {str(e)}")
        exit(1)

if __name__ == '__main__':
    main() 