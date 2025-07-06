import requests

michraz_id = input("Enter MichrazID: ").strip()

url = "https://apps.land.gov.il/MichrazimSite/api/MichrazDetailsApi/Get"
params = {"michrazID": michraz_id}

HEADERS = {
    "User-Agent": ("Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
                   "(KHTML, like Gecko) Chrome/126.0.0.0 Safari/537.36"),
    "Accept": "application/json, text/plain, */*",
    "Accept-Language": "he-IL,he;q=0.9,en-US;q=0.8,en;q=0.7",
    "Origin": "https://apps.land.gov.il",
    "Referer": "https://apps.land.gov.il/MichrazimSite/",
    "Connection": "keep-alive"
}

res = requests.get(url, headers=HEADERS, params=params, timeout=30)

print("Status:", res.status_code)
print("Content-Type:", res.headers.get("Content-Type"))

if "application/json" not in res.headers.get("Content-Type", ""):
    print("\n❌ Server returned HTML (likely blocking or maintenance):")
    print(res.text)
else:
    print("\n✅ JSON response:")
    print(res.json())
