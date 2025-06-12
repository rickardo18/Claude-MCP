import os
import subprocess
import requests

# Get API keys and Notion page ID from environment variables
GEMINI_API_KEY = os.environ.get('GEMINI_API_KEY')
NOTION_TOKEN = os.environ['NOTION_TOKEN']
NOTION_FEATURES_PAGE_ID = os.environ['NOTION_FEATURES_PAGE_ID']


def get_latest_commit_hash():
    """Return the hash of the latest commit in the repository."""
    return subprocess.check_output(['git', 'rev-parse', 'HEAD']).decode('utf-8').strip()


def get_changed_files(commit_hash):
    """Return a list of files changed in the given commit."""
    files = subprocess.check_output([
        'git', 'diff-tree', '--no-commit-id', '--name-only', '-r', commit_hash
    ]).decode('utf-8').strip().split('\n')
    return [f for f in files if f.strip()]


def get_code_diff(files, commit_hash):
    """Return a dictionary mapping filenames to their diffs for the given commit."""
    diffs = {}
    for file in files:
        try:
            # Get the diff for each file between the previous and current commit
            diff = subprocess.check_output([
                'git', 'diff', f'{commit_hash}~1', commit_hash, '--', file
            ]).decode('utf-8')
            diffs[file] = diff
        except subprocess.CalledProcessError:
            # If diff fails (e.g., file is new), store empty string
            diffs[file] = ''
    return diffs


def infer_features_from_diff(diffs):
    """Use Gemini API to infer features from code diffs. Returns a summary string."""
    if not GEMINI_API_KEY:
        return "(AI feature inference unavailable: GEMINI_API_KEY not set)"
    prompt = (
        "Given the following code diffs, infer and summarize any new features or significant changes "
        "that have been introduced. Be concise and use bullet points.\n\n"
    )
    for file, diff in diffs.items():
        prompt += f"File: {file}\nDiff:\n{diff}\n\n"
    prompt += "\nFeatures/changes introduced:"
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
            # Extract the AI-generated summary from the response
            return response.json()['candidates'][0]['content']['parts'][0]['text'].strip()
        except Exception:
            return f"(AI feature inference failed: Unexpected Gemini response: {response.text})"
    else:
        return f"(AI feature inference failed: {response.text})"


def get_notion_page_content(page_id):
    """Fetch and return the current content of the Notion page as plain text."""
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
            # Extract text from different block types
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
    """Append the new features summary to the Notion features page."""
    headers = {
        'Authorization': f'Bearer {NOTION_TOKEN}',
        'Content-Type': 'application/json',
        'Notion-Version': '2022-06-28'
    }
    # Get current content to preserve previous entries
    current_content = get_notion_page_content(NOTION_FEATURES_PAGE_ID)
    # Prepare new content by appending the new features
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
    """Main entry point: get commit, infer features, and update Notion."""
    try:
        commit_hash = get_latest_commit_hash()  # Get latest commit hash
        changed_files = get_changed_files(commit_hash)  # Get changed files in commit
        diffs = get_code_diff(changed_files, commit_hash)  # Get diffs for changed files
        features_summary = infer_features_from_diff(diffs)  # AI-infer features from diffs
        update_notion_features_page(features_summary)  # Update Notion page
        print("Successfully updated Notion features page with new features.")
    except Exception as e:
        print(f"Error updating Notion features page: {str(e)}")
        exit(1)


if __name__ == '__main__':
    main()