import os
import subprocess
import requests

OPENAI_API_KEY = os.environ.get('OPENAI_API_KEY')
NOTION_TOKEN = os.environ['NOTION_TOKEN']
NOTION_FEATURES_PAGE_ID = os.environ['NOTION_FEATURES_PAGE_ID']


def get_latest_commit_hash():
    return subprocess.check_output(['git', 'rev-parse', 'HEAD']).decode('utf-8').strip()

def get_changed_files(commit_hash):
    files = subprocess.check_output([
        'git', 'diff-tree', '--no-commit-id', '--name-only', '-r', commit_hash
    ]).decode('utf-8').strip().split('\n')
    return [f for f in files if f.strip()]

def get_code_diff(files, commit_hash):
    diffs = {}
    for file in files:
        try:
            diff = subprocess.check_output([
                'git', 'diff', f'{commit_hash}~1', commit_hash, '--', file
            ]).decode('utf-8')
            diffs[file] = diff
        except subprocess.CalledProcessError:
            diffs[file] = ''
    return diffs

def infer_features_from_diff(diffs):
    if not OPENAI_API_KEY:
        return "(AI feature inference unavailable: OPENAI_API_KEY not set)"
    prompt = (
        "Given the following code diffs, infer and summarize any new features or significant changes "
        "that have been introduced. Be concise and use bullet points.\n\n"
    )
    for file, diff in diffs.items():
        prompt += f"File: {file}\nDiff:\n{diff}\n\n"
    prompt += "\nFeatures/changes introduced:"
    headers = {
        "Authorization": f"Bearer {OPENAI_API_KEY}",
        "Content-Type": "application/json"
    }
    data = {
        "model": "gpt-3.5-turbo",
        "messages": [
            {"role": "system", "content": "You are a helpful assistant that summarizes code changes as new features."},
            {"role": "user", "content": prompt}
        ],
        "max_tokens": 300
    }
    response = requests.post("https://api.openai.com/v1/chat/completions", headers=headers, json=data)
    if response.status_code == 200:
        return response.json()['choices'][0]['message']['content'].strip()
    else:
        return f"(AI feature inference failed: {response.text})"

def get_notion_page_content(page_id):
    url = f"https://api.notion.com/v1/blocks/{page_id}/children"
    headers = {
        'Authorization': f'Bearer {NOTION_TOKEN}',
        'Notion-Version': '2022-06-28'
    }
    response = requests.get(url, headers=headers)
    if response.status_code == 200:
        blocks = response.json().get('results', [])
        content = []
        for block in blocks:
            if block['type'] == 'paragraph':
                texts = block['paragraph']['rich_text']
                content.append(''.join([t['plain_text'] for t in texts]))
            elif block['type'] == 'heading_1':
                texts = block['heading_1']['rich_text']
                content.append('# ' + ''.join([t['plain_text'] for t in texts]))
            elif block['type'] == 'heading_2':
                texts = block['heading_2']['rich_text']
                content.append('## ' + ''.join([t['plain_text'] for t in texts]))
            elif block['type'] == 'heading_3':
                texts = block['heading_3']['rich_text']
                content.append('### ' + ''.join([t['plain_text'] for t in texts]))
        return '\n'.join(content)
    else:
        return ""

def update_notion_features_page(features_summary):
    headers = {
        'Authorization': f'Bearer {NOTION_TOKEN}',
        'Content-Type': 'application/json',
        'Notion-Version': '2022-06-28'
    }
    # Get current content
    current_content = get_notion_page_content(NOTION_FEATURES_PAGE_ID)
    # Prepare new content (append new features to the end)
    content = f"{current_content}\n\n## New Features Added\n{features_summary}"
    url = f'https://api.notion.com/v1/blocks/{NOTION_FEATURES_PAGE_ID}/children'
    data = {
        "children": [{
            "object": "block",
            "type": "paragraph",
            "paragraph": {
                "rich_text": [{
                    "type": "text",
                    "text": {
                        "content": content
                    }
                }]
            }
        }]
    }
    response = requests.patch(url, headers=headers, json=data)
    if response.status_code != 200:
        raise Exception(f"Failed to update Notion features page: {response.text}")

def main():
    try:
        commit_hash = get_latest_commit_hash()
        changed_files = get_changed_files(commit_hash)
        diffs = get_code_diff(changed_files, commit_hash)
        features_summary = infer_features_from_diff(diffs)
        update_notion_features_page(features_summary)
        print("Successfully updated Notion features page with new features.")
    except Exception as e:
        print(f"Error updating Notion features page: {str(e)}")
        exit(1)

if __name__ == '__main__':
    main() 