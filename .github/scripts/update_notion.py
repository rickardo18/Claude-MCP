import os
import subprocess
import json
import requests
from datetime import datetime

def get_commit_info():
    """Get information about the latest commit"""
    # Get the latest commit hash
    latest_commit = subprocess.check_output(['git', 'rev-parse', 'HEAD']).decode('utf-8').strip()
    
    # Get commit details
    commit_info = subprocess.check_output([
        'git', 'log', '-1', '--format=%x1f%B%x1f%an%x1f%ae%x1f%at', latest_commit
    ]).decode('utf-8').strip().split('\x1f')
    
    # Defensive: check length and print for debugging
    if len(commit_info) < 5:
        print("DEBUG: commit_info =", commit_info)
        raise Exception(f"Unexpected commit_info format: {commit_info}")
    
    # Get changed files
    changed_files = subprocess.check_output([
        'git', 'diff-tree', '--no-commit-id', '--name-only', '-r', latest_commit
    ]).decode('utf-8').strip().split('\n')
    
    return {
        'hash': latest_commit,
        'message': commit_info[1],
        'author': commit_info[2],
        'email': commit_info[3],
        'timestamp': datetime.fromtimestamp(int(commit_info[4])).isoformat(),
        'changed_files': changed_files
    }

def update_notion_page(commit_info):
    """Update the Notion page with commit information"""
    notion_token = os.environ['NOTION_TOKEN']
    page_id = os.environ['NOTION_PAGE_ID']
    
    headers = {
        'Authorization': f'Bearer {notion_token}',
        'Content-Type': 'application/json',
        'Notion-Version': '2022-06-28'
    }
    
    # Format changed files as a bulleted list
    files_list = '\n'.join([f'• {file}' for file in commit_info['changed_files']])
    
    # Create the content for the page
    content = f"""# Latest Commit Update
    
## Commit Details
- **Hash**: {commit_info['hash'][:8]}
- **Author**: {commit_info['author']} ({commit_info['email']})
- **Date**: {commit_info['timestamp']}
- **Message**: {commit_info['message']}

## Changed Files
{files_list}

---
Last updated: {datetime.now().isoformat()}"""

    # Update the page
    url = f'https://api.notion.com/v1/blocks/{page_id}/children'
    
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
        raise Exception(f"Failed to update Notion page: {response.text}")

def main():
    try:
        commit_info = get_commit_info()
        update_notion_page(commit_info)
        print("Successfully updated Notion page with commit information")
    except Exception as e:
        print(f"Error updating Notion page: {str(e)}")
        exit(1)

if __name__ == '__main__':
    main() 