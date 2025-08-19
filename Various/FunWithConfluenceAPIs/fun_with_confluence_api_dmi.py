import sys
import os
import requests

def retrieve_page_content(page_id):
    base_url = "https://confluence.dmi.dk"
    url = f"{base_url}/rest/api/content/{page_id}"
    params = {"expand": "body.storage,version"}
    
    personal_access_token = os.environ.get("ATLASSIAN_API_TOKEN_DMI")

    headers = {
        "Authorization": f"Bearer {personal_access_token}"
    }

    response = requests.get(
        url,
        headers=headers,
        params=params
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



if __name__ == "__main__":
    try:
        if True:
            retrieve_page_content(page_id="114858299")

    except Exception as e:
        print("Error:", e)
        sys.exit(1)

