import sys
import os
import json
import requests
from bs4 import BeautifulSoup  # reformatting of html - here content of a Confluence page

base_url = "https://confluence.dmi.dk"
personal_access_token = os.environ.get("ATLASSIAN_API_TOKEN_DMI")
gitlab_access_token = os.environ.get("GITLAB_TOKEN")

def retrieve_page_content(page_id) -> str:
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

        return content
    else:
        raise Exception('Failed retrieving content of Confluence page - wrong page id?')


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

def update_confluence_page_with_hello_world_message(page_id: str):
    
    headers = {
        "Authorization": f"Bearer {personal_access_token}",
        "Content-Type": "application/json"
    }

    r = requests.get(
        f"{base_url}/rest/api/content/{page_id}?expand=version",
        headers=headers
    )

    r.raise_for_status()
    page_data = r.json()
    current_version = page_data["version"]["number"]

    # Build new body (storage format)
    new_body = """
    <p>Hello from Python - updated version 2</p>
    """

    # Update payload
    update_data = {
        "id": page_id,
        "type": "page",
        "title": page_data["title"],  # must include title unchanged (unless renaming)
        "version": {"number": current_version + 1},
        "body": {
            "storage": {
                "value": new_body,
                "representation": "storage"
            }
        }
    }

    # Send update request
    update_response = requests.put(
        f"{base_url}/rest/api/content/{page_id}",
        headers=headers,
        json=update_data
    )
    update_response.raise_for_status()

    print("Page updated successfully:", update_response.json()["title"])    

def update_confluence_page_with_arbitrary_content(
    page_id: str, new_body):
    
    headers = {
        "Authorization": f"Bearer {personal_access_token}",
        "Content-Type": "application/json"
    }

    r = requests.get(
        f"{base_url}/rest/api/content/{page_id}?expand=version",
        headers=headers
    )

    r.raise_for_status()
    page_data = r.json()
    current_version = page_data["version"]["number"]

    # Update payload
    update_data = {
        "id": page_id,
        "type": "page",
        "title": page_data["title"],  # must include title unchanged (unless renaming)
        "version": {"number": current_version + 1},
        "body": {
            "storage": {
                "value": new_body,
                "representation": "storage"
            }
        }
    }

    # Send update request
    update_response = requests.put(
        f"{base_url}/rest/api/content/{page_id}",
        headers=headers,
        json=update_data
    )
    update_response.raise_for_status()

    print("Page updated successfully:", update_response.json()["title"])    


def get_child_meta_data_for_child_pages(page_id: str):

    url = f"{base_url}/rest/api/content/{page_id}/child/page"

    headers = {
        "Authorization": f"Bearer {personal_access_token}",
        "Content-Type": "application/json"
    }

    response = requests.get(url, headers=headers)
    response.raise_for_status()
    data = response.json()
    
    children = []
    for child in data.get("results", []):
        children.append({
            "id": child["id"],
            "title": child["title"]
        })
    
    return children


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
        if False:

            body = f"""
            <ac:layout>
              <ac:layout-section ac:type="single">
                <ac:layout-cell>
                  <h1>Hallo</h1>
                  <h2>Hallo</h2>
                  <h3>Hallo</h3>
                  <p>Hallo</p>
                  <ac:structured-macro ac:name="html-bobswift">
                    <ac:parameter ac:name="script">#https://gitlab.dmi.dk/api/v4/projects/1392/repository/files/catalogs_generated%2Faci_mermaid_files%2FARNE.mmd/raw?ref=main&amp;private_token={gitlab_access_token}</ac:parameter>
                    <ac:parameter ac:name="atlassian-macro-output-type">INLINE</ac:parameter>
                  </ac:structured-macro>
                </ac:layout-cell>
              </ac:layout-section>
            </ac:layout>
            """

            create_confluence_page(
                space_key="~ebs",
                parent_page_id="222553283",
                title="Side med en html-bobswift macro!",
                data={
                    "type": "page",
                    "body": {
                        "storage": {
                            "value": body,
                            "representation": "storage"
                        }
                    }
                })

        if False:

            files = [
                "ARNE.mmd",
                "HALKA.mmd",
            ]

            base = "https://gitlab.dmi.dk/api/v4/projects/1392/repository/files/catalogs_generated%2Faci_mermaid_files"

            sections = []

            for f in files:
                # Encode filename for URL (spaces, slashes, etc.)
                from urllib.parse import quote
                
                encoded_file = quote(f, safe="")
                url = (
                    f"#"  # hash required by BobSwift
                    f"{base}%2F{encoded_file}/raw?ref=main&amp;private_token={gitlab_access_token}"
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
            
        if False:

            update_confluence_page_with_hello_world_message(page_id="222556182")

        if False:

            new_body = f"""
            <ac:layout>
              <ac:layout-section ac:type="single">
                <ac:layout-cell>
                  <h1>Hallo</h1>
                  <h2>Hallo</h2>
                  <h3>Hallo</h3>
                  <p>Hallo</p>
                  <ac:structured-macro ac:name="html-bobswift">
                    <ac:parameter ac:name="script">#https://gitlab.dmi.dk/api/v4/projects/1392/repository/files/catalogs_generated%2Faci_mermaid_files%2FARNE.mmd/raw?ref=main&amp;private_token={gitlab_access_token}</ac:parameter>
                    <ac:parameter ac:name="atlassian-macro-output-type">INLINE</ac:parameter>
                  </ac:structured-macro>
                </ac:layout-cell>
              </ac:layout-section>
            </ac:layout>
            """

            update_confluence_page_with_arbitrary_content(page_id="222556182", new_body=new_body)

        if False:
            content = retrieve_page_content(page_id="222556598")
            soup = BeautifulSoup(content, "html.parser")
            sections = soup.find_all("ac:layout-section")
            headers = []

            for section in sections:

                # Look at the first cell in this section
                first_cell = section.find("ac:layout-cell")
                if not first_cell:
                    continue

                # Get first child of the cell
                first_child = first_cell.find(True, recursive=False)
                if first_child and first_child.name == "h1":
                    header = first_child.get_text(strip=True)
                    headers.append(header)

            # for header in headers:
            #     print(header)

            page_exists = "Færdighedsgrad" in headers

            if page_exists:
                print("Siden \"Færdighedsgrad\" er der allerede")
            else:
                print("Siden \"Færdighedsgrad\" er der ikke")

            if not page_exists:

                existing_content = content

                new_section = """
                <ac:layout-section ac:type="single">
                <ac:layout-cell>
                    <h1>Færdighedsgrad</h1>
                    <p>Tadaa - denne sektion er tilføjet af et python script</p>
                </ac:layout-cell>
                </ac:layout-section>
                """

                soup = BeautifulSoup(existing_content, "html.parser")
                new_section_soup = BeautifulSoup(new_section, "html.parser")
                soup.append(new_section_soup)

                new_content = f"""{str(soup)}"""

                update_confluence_page_with_arbitrary_content(
                    page_id="222556598",
                    new_body=new_content)

        if True:
            meta_data_list = get_child_meta_data_for_child_pages("222553283")

            for meta_data in meta_data_list:
                print(f"id: {meta_data['id']}, title: {meta_data['title']}")


    except Exception as e:
        print("Error:", e)
        sys.exit(1)

