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
    <p>Hello from Python - updated version 39</p>
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
    page_id: str, new_body: str):
    
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

def add_section_by_building_it_in_this_function(storage_format: str, header: str, paragraph: str) -> str:
    soup = BeautifulSoup(storage_format, "html.parser")

    # Find the existing layout
    layout = soup.find("ac:layout")
    if not layout:
        # If no layout exists, create one
        layout = soup.new_tag("ac:layout")
        soup.append(layout)

    # Build a new section
    new_section = soup.new_tag("ac:layout-section")
    new_section["ac:type"] = "single"

    new_cell = soup.new_tag("ac:layout-cell")
    h1 = soup.new_tag("h1")
    h1.string = header
    p = soup.new_tag("p")
    p.string = paragraph

    new_cell.append(h1)
    new_cell.append(p)
    new_section.append(new_cell)

    # Append inside the layout
    layout.append(new_section)

    return str(soup)

def add_section(storage_format: str, new_section: str) -> str:
    soup = BeautifulSoup(storage_format, "html")

    # Find or create the layout
    layout = soup.find("ac:layout")
    if not layout:
        layout = soup.new_tag("ac:layout")
        soup.append(layout)

    # Parse the new section string into a tag
    new_section = BeautifulSoup(new_section, "html").find("ac:layout-section")

    if new_section:
        layout.append(new_section)
    else:
        raise ValueError("Provided string does not contain a valid <ac:layout-section>")

    return str(soup)

def insert_section(storage_format: str,
                   new_section: str,
                   before_headers: list[str] = None,
                   after_headers: list[str] = None) -> str:
    """
    Insert a new section into a Confluence storage format page.

    :param storage_format: Existing Confluence storage format string
    :param new_section_str: New section XML string (<ac:layout-section>...</ac:layout-section>)
    :param before_headers: List of header texts that should come before the new section
    :param after_headers: List of header texts that should come after the new section
    :return: Updated storage format string
    """
    before_headers = before_headers or []
    after_headers = after_headers or []

    soup = BeautifulSoup(storage_format, "html")

    # Ensure layout exists
    layout = soup.find("ac:layout")
    if not layout:
        layout = soup.new_tag("ac:layout")
        soup.append(layout)

    # Parse the new section string
    new_section = BeautifulSoup(new_section, "html").find("ac:layout-section")
    if not new_section:
        raise ValueError("Provided string does not contain a valid <ac:layout-section>")

    # Collect all existing sections
    sections = layout.find_all("ac:layout-section", recursive=False)

    # Helper to extract first header text from a section
    def get_header_text(section):
        header = section.find(["h1", "h2", "h3", "h4", "h5", "h6"])
        return header.get_text(strip=True) if header else None

    # Decide insert position
    insert_index = len(sections)  # default to end
    for i, sec in enumerate(sections):
        header = get_header_text(sec)
        if header:
            if header in after_headers:
                # Insert before the first "after" section
                insert_index = i
                break

    # If none of the after_headers matched, but before_headers exist, 
    # we ensure the new section comes after them
    if before_headers:
        for i, sec in enumerate(sections):
            header = get_header_text(sec)
            if header in before_headers:
                insert_index = i + 1

    # Insert at calculated position
    if insert_index >= len(sections):
        layout.append(new_section)
    else:
        sections[insert_index].insert_before(new_section)

    return str(soup)


if __name__ == "__main__":
    try:
        if False:
            #retrieve_page_content(page_id="114858299")
            #retrieve_page_content(page_id="222553654")
            #retrieve_page_content(page_id="222556598") # "Page that is inspected by means of the Confluence API"
            retrieve_page_content(page_id="222556182") # "Page automatically updated by means of Confluence API"

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

        if True:
            
            # En dummy sektion med lidt forskelligt indhold
            # Virker - også når man fjerner spaces og line breaks
            new_body = f"""
            <ac:layout>
              <ac:layout-section ac:type="single">
                <ac:layout-cell>
                  <h1>Hallo</h1>
                  <p>Hallo</p>
                </ac:layout-cell>
              </ac:layout-section>
            </ac:layout>
            """

            # En sektion med en html-bobswift macro (virker)
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

            # En sektion med en json-from-table macro (virker)
            new_body = f"""
            <ac:layout>
              <ac:layout-section ac:type="single">
                <ac:layout-cell>
                  <h1>Møjn</h1>
                  <p>Hallo</p>
                  <ac:structured-macro ac:name="json-from-table" ac:schema-version="1" ac:macro-id="8319cfea-5cc8-42d9-9955-f658410b2c5f">
                    <ac:parameter ac:name="isFirstTimeEnter">true</ac:parameter>
                    <ac:parameter ac:name="url">https://gitlab.dmi.dk/api/v4/projects/1392/repository/files/catalogs_generated%2Fqms_sections%2FAC_SAF_sys_description.json/raw?ref=main&amp;private_token={gitlab_access_token}</ac:parameter>
                  </ac:structured-macro>                  
                </ac:layout-cell>
              </ac:layout-section>
            </ac:layout>
            """

            # En sektion med 3-column format
            # Muligheder: three_equal, three_with_sidebars
            new_body = f"""
            <ac:layout>
              <ac:layout-section ac:type="three_with_sidebars">
                <ac:layout-cell>
                  <h1>Celle 1</h1>
                  <p>hejsa</p>
                </ac:layout-cell>
                <ac:layout-cell>
                  <h1>Celle 2</h1>
                  <p>Goddag</p>
                </ac:layout-cell>
                <ac:layout-cell>
                  <h1>Celle 3</h1>
                  <p>Kuk kuk</p>
                </ac:layout-cell>
              </ac:layout-section>
            </ac:layout>
            """

            # En sektion med 2-column format
            # Muligheder: two_equal, two_left_sidebar, two_right_sidebar
            new_body = f"""
            <ac:layout>
              <ac:layout-section ac:type="two_right_sidebar">
                <ac:layout-cell>
                  <h1>Celle 1</h1>
                  <p>hejsa</p>
                </ac:layout-cell>
                <ac:layout-cell>
                  <h1>Celle 2</h1>
                  <p>Goddag</p>
                </ac:layout-cell>
              </ac:layout-section>
            </ac:layout>
            """

            update_confluence_page_with_arbitrary_content(page_id="222556182", new_body=new_body)

        if False:
            content = retrieve_page_content(page_id="222556598")
            new_content = add_section_by_building_it_in_this_function(content, "Vælling", "Vælling")

            update_confluence_page_with_arbitrary_content(
                page_id="222556598",
                new_body=new_content)

        if False:
            content = retrieve_page_content(page_id="222556598")

            new_section = """
            <ac:layout-section ac:type="single">
            <ac:layout-cell>
                <h1>Section 2</h1>
                <p>Hello from Python</p>
            </ac:layout-cell>
            </ac:layout-section>
            """

            new_content = add_section(content, new_section)

            update_confluence_page_with_arbitrary_content(
                page_id="222556598",
                new_body=new_content)

        if False:
            content = retrieve_page_content(page_id="222556598")

            new_section = f"""
            <ac:layout-section ac:type="single">
            <ac:layout-cell>
                <h1>Section 5</h1>
                <p>Hello from Luna</p>
                <ac:structured-macro ac:name="html-bobswift">
                <ac:parameter ac:name="script">#https://gitlab.dmi.dk/api/v4/projects/1392/repository/files/catalogs_generated%2Faci_mermaid_files%2FARNE.mmd/raw?ref=main&amp;private_token={gitlab_access_token}</ac:parameter>
                <ac:parameter ac:name="atlassian-macro-output-type">INLINE</ac:parameter>
                </ac:structured-macro>
            </ac:layout-cell>
            </ac:layout-section>
            """

            new_content = insert_section(
                content,
                new_section,
                ["Section 1", "Section 2", "Section 3", "Section 4"],
                ["Section 6", "Section 7"])

            update_confluence_page_with_arbitrary_content(
                page_id="222556598",
                new_body=new_content)

        if False:
            meta_data_list = get_child_meta_data_for_child_pages("222553283")

            for meta_data in meta_data_list:
                print(f"id: {meta_data['id']}, title: {meta_data['title']}")

        if False:
            body = """
            <ac:layout>
            <ac:layout-section ac:type="single">
                <ac:layout-cell>
                <h1>Section 1</h1>
                <p>Hello</p>
                </ac:layout-cell>
            </ac:layout-section>
            </ac:layout>
            """            

            new_body = add_section(body, "Section 2", "Hello from Python")
            print(new_body)            


    except Exception as e:
        print("Error:", e)
        sys.exit(1)

