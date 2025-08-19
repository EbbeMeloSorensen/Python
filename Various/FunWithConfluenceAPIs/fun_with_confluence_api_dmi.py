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
            #retrieve_page_content(page_id="222553654")

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

            # body = """
            # <ac:layout>
            #   <ac:layout-section ac:type="single">
            #     <ac:layout-cell>
            #       <p>Hallo</p>
            #       <ac:structured-macro ac:name="html-bobswift">
            #         <ac:parameter ac:name="script">#https://gitlab.dmi.dk/api/v4/projects/1392/repository/files/catalogs_generated%2Faci_mermaid_files%2FARNE.mmd/raw?ref=main&amp;private_token=ERSTAT_MED_GITLAB_TOKEN</ac:parameter>
            #         <ac:parameter ac:name="atlassian-macro-output-type">INLINE</ac:parameter>
            #       </ac:structured-macro>
            #     </ac:layout-cell>
            #   </ac:layout-section>
            # </ac:layout>
            # """            

            files = [
                "ARNE.mmd",
                "HALKA.mmd",
            ]

            base = "https://gitlab.dmi.dk/api/v4/projects/1392/repository/files/catalogs_generated%2Faci_mermaid_files"
            gitlab_token = os.environ.get("GITLAB_TOKEN")

            sections = []

            for f in files:
                # Encode filename for URL (spaces, slashes, etc.)
                from urllib.parse import quote
                
                encoded_file = quote(f, safe="")
                url = (
                    f"#"  # hash required by BobSwift
                    f"{base}%2F{encoded_file}/raw?ref=main&amp;private_token={gitlab_token}"
                )

                section = f"""
                <ac:layout-section ac:type="single">
                <ac:layout-cell>
                    <p>Diagram: {f}</p>
                    <ac:structured-macro ac:name="html-bobswift" ac:schema-version="1">
                    <ac:parameter ac:name="script">{url}</ac:parameter>
                    <ac:parameter ac:name="atlassian-macro-output-type">INLINE</ac:parameter>
                    </ac:structured-macro>
                </ac:layout-cell>
                </ac:layout-section>
                """
                sections.append(section)

                # Wrap everything in <ac:layout>
                body = "<ac:layout>\n" + "\n".join(sections) + "\n</ac:layout>"

            create_confluence_page(
                space_key="~ebs",
                parent_page_id="222553283",
                title="Side med sektioner og en html-bobswift macro 11",
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

