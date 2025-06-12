import os
import subprocess
import requests

GEMINI_API_KEY = os.environ.get('GEMINI_API_KEY')
GITHUB_TOKEN = os.environ.get('GITHUB_TOKEN')
GITHUB_REPOSITORY = os.environ.get('GITHUB_REPOSITORY')  # e.g. "owner/repo"
GITHUB_PR_NUMBER = os.environ.get('GITHUB_PR_NUMBER')    # PR number as string

def get_pr_diff():
    """Get the diff for the current PR (between base and head)."""
    # Assumes the workflow checks out the PR branch and fetches the base branch
    base = os.environ.get('GITHUB_BASE_REF')
    head = os.environ.get('GITHUB_HEAD_REF')
    if not base or not head:
        # Fallback: get diff from origin/main
        base = 'origin/main'
        head = 'HEAD'
    diff = subprocess.check_output(['git', 'diff', f'{base}...{head}']).decode('utf-8')
    return diff

def generate_pr_summary(diff):
    """Use Gemini to generate a PR summary and feature list."""
    if not GEMINI_API_KEY:
        return "(AI PR summary unavailable: GEMINI_API_KEY not set)"
    prompt = (
        "Given the following code diff from a pull request, generate a concise PR body including:\n"
        "- A high-level summary of what the PR does\n"
        "- A bullet-point list of key changes or features\n\n"
        "Diff:\n" + diff + "\n\n"
        "Format your response as:\n"
        "SUMMARY:\n[Your summary here]\n\n"
        "FEATURES:\n- [feature 1]\n- [feature 2]\n"
    )
    headers = {"Content-Type": "application/json"}
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
            return result
        except Exception as e:
            return f"(AI PR summary failed: Unexpected Gemini response: {str(e)})"
    else:
        return f"(AI PR summary failed: {response.text})"

def update_github_pr_body(pr_body):
    """Update the PR body using the GitHub API."""
    if not (GITHUB_TOKEN and GITHUB_REPOSITORY and GITHUB_PR_NUMBER):
        print("Missing GitHub environment variables.")
        return
    url = f"https://api.github.com/repos/{GITHUB_REPOSITORY}/pulls/{GITHUB_PR_NUMBER}"
    headers = {
        "Authorization": f"token {GITHUB_TOKEN}",
        "Accept": "application/vnd.github+json"
    }
    data = {"body": pr_body}
    response = requests.patch(url, headers=headers, json=data)
    if response.status_code not in (200, 201):
        print(f"Failed to update PR body: {response.text}")
    else:
        print("PR body updated successfully.")

def main():
    diff = get_pr_diff()
    pr_body = generate_pr_summary(diff)
    update_github_pr_body(pr_body)

if __name__ == "__main__":
    main() 