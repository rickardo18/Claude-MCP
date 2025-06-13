import os
import subprocess
import requests
from datetime import datetime

GEMINI_API_KEY = os.environ.get('GEMINI_API_KEY')
NOTION_TOKEN = os.environ['NOTION_TOKEN']
NOTION_PAGE_ID = os.environ['NOTION_CHANGELOG_DATABASE_ID']  # Notion page for changelog entries

CHANGELOG_FILE = 'CHANGELOG.md'

def get_latest_commit_hash():
    return subprocess.check_output(['git', 'rev-parse', 'HEAD']).decode('utf-8').strip()

def get_commit_diff(commit_hash):
    # Get the diff for the latest commit
    diff = subprocess.check_output([
        'git', 'show', commit_hash, '--pretty=format:%h %s (%an, %ad)', '--date=short', '--unified=3'
    ]).decode('utf-8')
    return diff

def ai_generate_changelog(diff):
    if not GEMINI_API_KEY:
        return f"(AI changelog unavailable: GEMINI_API_KEY not set)\n\n{diff}"
    prompt = (
        "You are a release note generator. Given the following git commit diff, "
        "write a concise, clear changelog entry describing the change in plain English. "
        "Focus on what was changed, added, or fixed, and why if possible.\n\n"
        f"Commit diff:\n{diff}\n\nChangelog entry:"
    )
    headers = {"Content-Type": "application/json"}
    data = {"contents": [{"parts": [{"text": prompt}]}]}
    url = "https://generativelanguage.googleapis.com/v1beta/models/gemini-2.0-flash:generateContent"
    response = requests.post(url, headers=headers, params={"key": GEMINI_API_KEY}, json=data)
    if response.status_code == 200:
        try:
            return response.json()['candidates'][0]['content']['parts'][0]['text'].strip()
        except Exception as e:
            return f"(AI changelog failed: Unexpected Gemini response: {str(e)})\n\n{diff}"
    else:
        return f"(AI changelog failed: {response.text})\n\n{diff}"

def format_changelog_entry(summary):
    date_str = datetime.now().strftime('%Y-%m-%d')
    entry = f'\n## {date_str}\n\n- {summary}\n'
    return entry

def append_to_changelog(entry):
    # Insert entry after the header and before previous entries
    with open(CHANGELOG_FILE, 'r', encoding='utf-8') as f:
        lines = f.readlines()
    header_end = 0
    for i, line in enumerate(lines):
        if line.strip() == '---':
            header_end = i + 1
            break
    new_lines = lines[:header_end] + [entry + '\n'] + lines[header_end:]
    with open(CHANGELOG_FILE, 'w', encoding='utf-8') as f:
        f.writelines(new_lines)

def append_to_notion_page(entry):
    url = f'https://api.notion.com/v1/blocks/{NOTION_PAGE_ID}/children'
    headers = {
        'Authorization': f'Bearer {NOTION_TOKEN}',
        'Content-Type': 'application/json',
        'Notion-Version': '2022-06-28'
    }
    data = {
        'children': [
            {
                'object': 'block',
                'type': 'paragraph',
                'paragraph': {
                    'rich_text': [{
                        'type': 'text',
                        'text': {'content': entry}
                    }]
                }
            }
        ]
    }
    response = requests.patch(url, headers=headers, json=data)
    if response.status_code not in (200, 204):
        raise Exception(f'Failed to append to Notion page: {response.text}')

def main():
    commit_hash = get_latest_commit_hash()
    diff = get_commit_diff(commit_hash)
    summary = ai_generate_changelog(diff)
    entry = format_changelog_entry(summary)
    append_to_changelog(entry)
    append_to_notion_page(entry)
    print('Changelog updated and entry appended to Notion page.')

if __name__ == '__main__':
    main() 