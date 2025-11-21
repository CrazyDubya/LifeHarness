import urllib.request
import json

api_key = "LWGRSXVD5YFAFIHTKM6Z5TS4I7YXNRGXYDVQ"
url = "https://api.vultrinference.com/v1/models"
headers = {
    "Authorization": f"Bearer {api_key}",
    "Content-Type": "application/json"
}

req = urllib.request.Request(url, headers=headers)
try:
    with urllib.request.urlopen(req) as response:
        data = json.load(response)
        print(json.dumps(data, indent=2))
except Exception as e:
    print(f"Error: {e}")
