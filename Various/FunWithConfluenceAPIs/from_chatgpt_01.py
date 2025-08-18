import requests
from requests.auth import HTTPBasicAuth
import json

# ----- Config -----
#email = "you@example.com"  # Your Atlassian account email
email = "ebbe.melo.sorensen@gmail.com"  # Your Atlassian account email

api_token = "YOUR_API_TOKEN"  # Generated from Atlassian account

#base_url = "https://your-domain.atlassian.net/wiki"
base_url = "https://melo.atlassian.net/wiki/"

#space_key = "TEST"
space_key = "ESP"

#parent_page_id = "123456"  # Optional: to nest under a parent page
parent_page_id = "704806913"

# ----- Page data -----
url = f"{base_url}/rest/api/content/"
headers = {
    "Content-Type": "application/json"
}

data = {
    "type": "page",
    "title": "My New Page from API",
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
    auth=HTTPBasicAuth(email, api_token)
)

# ----- Check result -----
if response.status_code == 200 or response.status_code == 201:
    print("Page created successfully!")
    print("URL:", json.loads(response.text)['_links']['base'] +
          json.loads(response.text)['_links']['webui'])
else:
    print("Failed to create page:", response.status_code, response.text)


print('Bye')