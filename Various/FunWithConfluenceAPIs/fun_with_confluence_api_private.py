import sys
import os
import json
import requests
from requests.auth import HTTPBasicAuth

email = "ebbe.melo.sorensen@gmail.com"  # Your Atlassian account email
personal_access_token = os.environ.get("ATLASSIAN_API_TOKEN")
base_url = "https://melo.atlassian.net/wiki"

def retrieve_page_content(page_id):
    url = f"{base_url}/rest/api/content/{page_id}"
    params = {"expand": "body.storage,version"}

    response = requests.get(
        url,
        params=params,
        auth=HTTPBasicAuth(email, personal_access_token)
    )

    if response.status_code == 200:
        data = response.json()
        title = data["title"]
        version = data["version"]["number"]
        content = data["body"]["storage"]["value"]

        print(f"Title: {title}")
        print(f"Version: {version}")
        print("Content:\n", content)
    else:
        print("Failed to retrieve page:", response.status_code, response.text)    

def create_confluence_page_hello_world(title: str): 

    space_key = "ESP"
    parent_page_id = "704806913"

    # ----- Page data -----
    url = f"{base_url}/rest/api/content/"
    headers = {
        "Content-Type": "application/json"
    }

    data = {
        "type": "page",
        "title": title,
        "ancestors": [{"id": parent_page_id}],  # omit if creating at root of space
        "space": {"key": space_key},
        "body": {
            "storage": {
                "value": "<p>Hello from Python!</p>",
                "representation": "storage"
            }
        }
    }

    # ----- API call -----
    response = requests.post(
        url,
        data=json.dumps(data),
        headers=headers,
        auth=HTTPBasicAuth(email, personal_access_token)
    )

    # ----- Check result -----
    if response.status_code == 200 or response.status_code == 201:
        print("Page created successfully!")
        print("URL:", json.loads(response.text)['_links']['base'] +
            json.loads(response.text)['_links']['webui'])
    else:
        print("Failed to create page:", response.status_code, response.text)


if __name__ == "__main__":
    try:
        if True:
            retrieve_page_content(page_id="704806913")
        if False:
            # title must be unique
            create_confluence_page_hello_world("My New Page from API - 7")

    except Exception as e:
        print("Error:", e)
        sys.exit(1)

