import sys
import os
import json
import requests

base_url = "https://confluence.dmi.dk"
personal_access_token = os.environ.get("ATLASSIAN_API_TOKEN_DMI")

def retrieve_page_content(page_id):
    url = f"{base_url}/rest/api/content/{page_id}"
    params = {"expand": "body.storage,version"}
    headers = {"Authorization": f"Bearer {personal_access_token}"}

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


def create_confluence_page(space_key: str, parent_page_id: str, title: str, data: dict[str, any]): 

    url = f"{base_url}/rest/api/content/"

    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {personal_access_token}"
    }

    data["space"] = {"key": space_key}
    data["ancestors"] = [{"id": parent_page_id}] # omit if creating at root of space
    data["title"] = title

    response = requests.post(
        url,
        data=json.dumps(data),
        headers=headers
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
        if False:
            retrieve_page_content(page_id="114858299")
        if False:
            create_confluence_page(
                space_key="~ebs",
                parent_page_id="222553283",
                title="Kylling2",
                data={
                    "type": "page",
                    "body": {
                        "storage": {
                            "value": "<p>Hello from Python!!!</p>",
                            "representation": "storage"
                        }
                    }
                })
        if True:
            body = """
            <ac:layout>
              <ac:layout-section ac:type="single">
                <ac:layout-cell>
                  <p>Hallo</p>
                  <ac:structured-macro ac:name="html-bobswift">
                    <ac:parameter ac:name="location">https://example.com/file1.html</ac:parameter>
                  </ac:structured-macro>                  
                </ac:layout-cell>
              </ac:layout-section>
            </ac:layout>
            """            

            create_confluence_page(
                space_key="~ebs",
                parent_page_id="222553283",
                title="Side med sektioner og en html-bobswift macro",
                data={
                    "type": "page",
                    "body": {
                        "storage": {
                            "value": body,
                            "representation": "storage"
                        }
                    }
                })

    except Exception as e:
        print("Error:", e)
        sys.exit(1)

