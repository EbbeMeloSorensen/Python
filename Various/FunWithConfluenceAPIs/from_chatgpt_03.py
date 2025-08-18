'''
Here’s a complete example that takes a local Markdown or HTML file and uploads it as a Confluence page via the REST API in Python.
It will:

Read your file

Convert Markdown → Confluence storage format (XHTML) if needed

Create or update the page in the specified space
----
HOW TO USE:
python push_to_confluence.py "report.md" "Weekly Status Report"
If "report.md" exists locally, it’ll be converted from Markdown → HTML → Confluence Storage format.

If the page already exists in the SPACE_KEY space, it will be updated in-place (with version increment).

If it doesn’t exist, it will be created.
'''

import os
import sys
import json
import requests
from requests.auth import HTTPBasicAuth
import markdown

# --- CONFIG ---
EMAIL = "you@example.com"            # Atlassian email
API_TOKEN = "YOUR_API_TOKEN"         # From https://id.atlassian.com/manage/api-tokens
BASE_URL = "https://your-domain.atlassian.net/wiki"
SPACE_KEY = "TEST"
PARENT_PAGE_ID = None  # Optional: set to an existing page ID to nest

# --- FUNCTIONS ---

def read_content(file_path):
    with open(file_path, "r", encoding="utf-8") as f:
        text = f.read()
    if file_path.lower().endswith(".md"):
        html = markdown.markdown(text, extensions=['tables', 'fenced_code'])
    else:
        html = text
    return html

def create_or_update_page(title, html_content):
    # Check if page exists
    search_url = f"{BASE_URL}/rest/api/content"
    params = {"title": title, "spaceKey": SPACE_KEY}
    resp = requests.get(search_url, params=params,
                        auth=HTTPBasicAuth(EMAIL, API_TOKEN))
    resp.raise_for_status()
    results = resp.json().get("results", [])

    if results:
        # Page exists → update
        page_id = results[0]["id"]
        version_number = results[0]["version"]["number"] + 1
        update_url = f"{BASE_URL}/rest/api/content/{page_id}"

        data = {
            "id": page_id,
            "type": "page",
            "title": title,
            "space": {"key": SPACE_KEY},
            "body": {
                "storage": {
                    "value": html_content,
                    "representation": "storage"
                }
            },
            "version": {"number": version_number}
        }
        resp = requests.put(update_url, data=json.dumps(data),
                            headers={"Content-Type": "application/json"},
                            auth=HTTPBasicAuth(EMAIL, API_TOKEN))
        resp.raise_for_status()
        print(f"✅ Updated page '{title}' → {BASE_URL}{results[0]['_links']['webui']}")
    else:
        # Create new page
        data = {
            "type": "page",
            "title": title,
            "space": {"key": SPACE_KEY},
            "body": {
                "storage": {
                    "value": html_content,
                    "representation": "storage"
                }
            }
        }
        if PARENT_PAGE_ID:
            data["ancestors"] = [{"id": PARENT_PAGE_ID}]

        resp = requests.post(f"{BASE_URL}/rest/api/content/",
                             data=json.dumps(data),
                             headers={"Content-Type": "application/json"},
                             auth=HTTPBasicAuth(EMAIL, API_TOKEN))
        resp.raise_for_status()
        page = resp.json()
        print(f"✅ Created new page '{title}' → {BASE_URL}{page['_links']['webui']}")

# --- MAIN ---
if __name__ == "__main__":
    if len(sys.argv) < 3:
        print("Usage: python push_to_confluence.py <file> <page-title>")
        sys.exit(1)

    file_path = sys.argv[1]
    page_title = sys.argv[2]

    if not os.path.exists(file_path):
        print(f"File not found: {file_path}")
        sys.exit(1)

    html_content = read_content(file_path)
    create_or_update_page(page_title, html_content)
