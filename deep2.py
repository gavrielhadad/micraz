import requests, pandas as pd

url = "https://apps.land.gov.il/MichrazimSite/api/SearchApi/Search"
headers = {
    "Content-Type": "application/json",
    "Origin": "https://apps.land.gov.il",
    "Referer": "https://apps.land.gov.il/MichrazimSite/"
}
payload = {
    "Page": 1,
    "ItemsPerPage": 20000,
    "Sort": {"Field": "MichrazID", "Direction": "Asc"},
    "SearchCriteria": {}
}

try:
    r = requests.post(url, json=payload, headers=headers, timeout=30)
    r.raise_for_status()
    items = r.json()
except Exception as e:
    print("❌", e)
    exit(1)

df = pd.DataFrame(items).drop_duplicates(subset="MichrazID", ignore_index=True)
df.to_excel(r"C:\Users\gavrielha\michrazim_all_clean.xlsx", index=False)
print("✅ Done:", len(df), "records saved")
