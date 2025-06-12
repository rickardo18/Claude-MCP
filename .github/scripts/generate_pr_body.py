import os
import subprocess
import requests
import argparse

GEMINI_API_KEY = os.environ.get('GEMINI_API_KEY')
GITHUB_TOKEN = os.environ.get('GITHUB_TOKEN')

def get_pr_diff(base, head):
    """Get the diff for the current PR (between base and head)."""
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

def update_github_pr_body(repo, pr_number, pr_body):
    """Update the PR body using the GitHub API."""
    if not (GITHUB_TOKEN and repo and pr_number):
        print("Missing GitHub environment variables or arguments.")
        return
    url = f"https://api.github.com/repos/{repo}/pulls/{pr_number}"
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
    parser = argparse.ArgumentParser(description="Generate and update a PR body using Gemini.")
    parser.add_argument('--repo', type=str, help='GitHub repository in owner/repo format')
    parser.add_argument('--pr', type=str, help='Pull request number')
    parser.add_argument('--base', type=str, default=None, help='Base branch or ref')
    parser.add_argument('--head', type=str, default='HEAD', help='Head branch or ref')
    args = parser.parse_args()

    repo = args.repo or os.environ.get('GITHUB_REPOSITORY')
    pr_number = args.pr or os.environ.get('GITHUB_PR_NUMBER')
    base_ref = args.base or os.environ.get('GITHUB_BASE_REF') or 'main'
    base = f'origin/{base_ref}'
    head = args.head

    if not (repo and pr_number):
        print("You must specify --repo and --pr, or set GITHUB_REPOSITORY and GITHUB_PR_NUMBER.")
        return

    diff = get_pr_diff(base, head)
    pr_body = generate_pr_summary(diff)
    update_github_pr_body(repo, pr_number, pr_body)

if __name__ == "__main__":
    main() 