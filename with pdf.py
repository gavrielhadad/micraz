import requests, pandas as pd, time, random

BASE = "https://apps.land.gov.il/MichrazimSite/api/"
HEADERS = {
    "Content-Type": "application/json",
    "Origin": "https://apps.land.gov.il",
    "Referer": "https://apps.land.gov.il/MichrazimSite/",
    "User-Agent": "Mozilla/5.0"
}

def safe_json(res):
    if res.status_code != 200:
        return None
    if "application/json" not in res.headers.get("Content-Type", ""):
        return None
    try:
        return res.json()
    except:
        return None

all_ids = []
page = 1
while True:
    payload = {
        "Page": page,
        "ItemsPerPage": 100,
        "Sort": {"Field": "MichrazID", "Direction": "Asc"},
        "SearchCriteria": {
            "FromPirsumDate": "2025-04-01T22:00:00.000Z"
        }
    }
    time.sleep(random.uniform(2, 5))
    res = requests.post(BASE + "Search", headers=HEADERS, json=payload, timeout=30)
    data = safe_json(res)
    if not data or len(data) == 0:
        break
    all_ids.extend([x["MichrazID"] for x in data if "MichrazID" in x])
    page += 1

if not all_ids:
    print("No tenders found")
    exit(0)

details = []
for mid in all_ids:
    item = {"MichrazID": mid}
    try:
        time.sleep(random.uniform(3, 6))
        r1 = requests.get(BASE + "MichrazDetailsApi/Get", params={"michrazID": mid}, headers=HEADERS, timeout=15)
        j1 = safe_json(r1)
        if j1: item["Get"] = j1

        time.sleep(random.uniform(3, 6))
        r2 = requests.get(BASE + "MichrazDetailsApi/GetMichrazMapaDetails", params={"michrazID": mid}, headers=HEADERS, timeout=15)
        j2 = safe_json(r2)
        if j2: item["GetMapa"] = j2

        details.append(item)
    except:
        pass

if details:
    pd.json_normalize(details).to_excel(r"C:\Users\gavrielha\michrazim_from_2025_04_01.xlsx", index=False)
else:
    print("No details to save")
