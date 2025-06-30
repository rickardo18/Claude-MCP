import os
import subprocess
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
    if len(commit_info) < 4:
        print("DEBUG: commit_info =", commit_info)
        raise Exception(f"Unexpected commit_info format: {commit_info}")
    
    # Get changed files
    changed_files = subprocess.check_output([
        'git', 'diff-tree', '--no-commit-id', '--name-only', '-r', latest_commit
    ]).decode('utf-8').strip().split('\n')
    
    return {
        'hash': latest_commit,
        'message': commit_info[0],
        'author': commit_info[1],
        'email': commit_info[2],
        'timestamp': datetime.fromtimestamp(int(commit_info[3])).isoformat(),
        'changed_files': changed_files
    }

def update_notion_page(commit_info):
    """Append the latest commit information as new blocks to the Notion page, preserving previous content."""
    notion_token = os.environ['NOTION_TOKEN']
    page_id = os.environ['NOTION_PAGE_ID']
    
    headers = {
        'Authorization': f'Bearer {notion_token}',
        'Content-Type': 'application/json',
        'Notion-Version': '2022-06-28'
    }
    
    # Prepare Notion blocks
    blocks = [
        {"object": "block", "type": "heading_1", "heading_1": {"rich_text": [{"type": "text", "text": {"content": "Latest Commit Update"}}]}},
        {"object": "block", "type": "heading_2", "heading_2": {"rich_text": [{"type": "text", "text": {"content": "Commit Details"}}]}},
        {"object": "block", "type": "paragraph", "paragraph": {"rich_text": [{"type": "text", "text": {"content": f"Hash: {commit_info['hash'][:8]}"}}]}},
        {"object": "block", "type": "paragraph", "paragraph": {"rich_text": [{"type": "text", "text": {"content": f"Author: {commit_info['author']} ({commit_info['email']})"}}]}},
        {"object": "block", "type": "paragraph", "paragraph": {"rich_text": [{"type": "text", "text": {"content": f"Date: {commit_info['timestamp']}"}}]}},
        {"object": "block", "type": "paragraph", "paragraph": {"rich_text": [{"type": "text", "text": {"content": f"Message: {commit_info['message']}"}}]}},
        {"object": "block", "type": "heading_2", "heading_2": {"rich_text": [{"type": "text", "text": {"content": "Changed Files"}}]}},
    ]
    # Add bulleted list for changed files
    for file in commit_info['changed_files']:
        if file.strip():
            blocks.append({
                "object": "block",
                "type": "bulleted_list_item",
                "bulleted_list_item": {
                    "rich_text": [{"type": "text", "text": {"content": file}}]
                }
            })
    # Divider
    blocks.append({"object": "block", "type": "divider", "divider": {}})
    # Last updated
    blocks.append({
        "object": "block",
        "type": "paragraph",
        "paragraph": {
            "rich_text": [{"type": "text", "text": {"content": f"Last updated: {datetime.now().isoformat()}"}}]
        }
    })
    # Append new blocks to the page (do not delete existing content)
    url = f'https://api.notion.com/v1/blocks/{page_id}/children'
    data = {"children": blocks}
    response = requests.patch(url, headers=headers, json=data)
    if response.status_code not in (200, 201):
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