import requests

url = "https://apps.land.gov.il/MichrazimSite/api/SearchApi/Search"
payload = {
    "pageNumber": 1,
    "pageSize": 50,
    "statusId": 1
}
headers = {
    "Content-Type": "application/json"
}

response = requests.post(url, json=payload, headers=headers)
print(response.json())
