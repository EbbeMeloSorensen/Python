'''
Alright — here’s a Python example that reads a local file (either Markdown or HTML) and pushes it to Confluence using the REST API.

I’ll make it flexible so:

If it’s Markdown, it converts it to Confluence storage format (XHTML) first.

If it’s already HTML, it sends it as-is.
---
HOW IT WORKS

Markdown to Confluence HTML
Uses pypandoc to convert Markdown into HTML, which is then sent in Confluence storage format.

HTML passthrough
If your file is already HTML (valid Confluence storage HTML), it just sends it as-is.

API Authentication
Uses Atlassian Cloud API token + email for HTTP basic auth.

Parent Page Nesting
Optional — set PARENT_PAGE_ID to nest under a specific page.
---
If you want, I can make a version that also updates the page if it already exists instead of creating duplicates — which is a very common automation requirement.
That way you can re-run the script and it works like “sync to Confluence.”

Do you want me to make that update-capable version?
'''

import requests
from requests.auth import HTTPBasicAuth
import json
import os
import sys
import pypandoc  # pip install pypandoc

# ------------- CONFIG -------------
EMAIL = "you@example.com"                  # Atlassian account email
API_TOKEN = "YOUR_API_TOKEN"               # Generated in Atlassian account settings
BASE_URL = "https://your-domain.atlassian.net/wiki"
SPACE_KEY = "TEST"                          # Confluence space key
PARENT_PAGE_ID = "123456"                   # Optional: Parent page ID (string)
TITLE = "My Page from File"                 # Page title in Confluence
FILE_PATH = "example.md"                    # Local file to upload
# -----------------------------------

def file_to_storage_format(file_path):
    ext = os.path.splitext(file_path)[1].lower()
    if ext == ".md":
        print("Converting Markdown to Confluence storage format...")
        return pypandoc.convert_file(file_path, "html", format="md")
    elif ext in (".html", ".htm"):
        print("Reading HTML file...")
        with open(file_path, "r", encoding="utf-8") as f:
            return f.read()
    else:
        raise ValueError("Unsupported file type. Use .md or .html")

def create_confluence_page(title, storage_value):
    url = f"{BASE_URL}/rest/api/content/"
    headers = {"Content-Type": "application/json"}

    data = {
        "type": "page",
        "title": title,
        "space": {"key": SPACE_KEY},
        "body": {
            "storage": {
                "value": storage_value,
                "representation": "storage"
            }
        }
    }

    # Add parent page if set
    if PARENT_PAGE_ID:
        data["ancestors"] = [{"id": PARENT_PAGE_ID}]

    response = requests.post(
        url,
        data=json.dumps(data),
        headers=headers,
        auth=HTTPBasicAuth(EMAIL, API_TOKEN)
    )

    if response.status_code in (200, 201):
        resp_json = response.json()
        page_url = resp_json["_links"]["base"] + resp_json["_links"]["webui"]
        print(f"✅ Page created: {page_url}")
    else:
        print(f"❌ Failed ({response.status_code}): {response.text}")

if __name__ == "__main__":
    try:
        html_content = file_to_storage_format(FILE_PATH)
        create_confluence_page(TITLE, html_content)
    except Exception as e:
        print("Error:", e)
        sys.exit(1)
