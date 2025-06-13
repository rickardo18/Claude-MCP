import os
import subprocess
import requests
from datetime import datetime

NOTION_TOKEN = os.environ['NOTION_TOKEN']
NOTION_PAGE_ID = os.environ['NOTION_CHANGELOG_DATABASE_ID']  # Notion page for changelog entries

CHANGELOG_FILE = 'CHANGELOG.md'


def get_latest_commit():
    # Get the latest commit info
    log = subprocess.check_output([
        'git', 'log', '-1', '--pretty=format:%h %s (%an, %ad)', '--date=short'
    ]).decode('utf-8').strip()
    return log

def format_changelog_entry(commit):
    date_str = datetime.now().strftime('%Y-%m-%d')
    entry = f'\n## {date_str}\n\n- {commit}\n'
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
    # Add the entry as a new block (as a paragraph, could be improved to support markdown)
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
    commit = get_latest_commit()
    entry = format_changelog_entry(commit)
    append_to_changelog(entry)
    append_to_notion_page(entry)
    print('Changelog updated and entry appended to Notion page.')

if __name__ == '__main__':
    main() 