import requests
import pandas as pd
import time

BASE_URL = "https://apps.land.gov.il/MichrazimSite/api"
SEARCH_URL = f"{BASE_URL}/SearchApi/Search"
DETAIL_URL = f"{BASE_URL}/DetailsApi/GetTenderDetails"

HEADERS = {
    "Content-Type": "application/json",
    "Origin": "https://apps.land.gov.il",
    "Referer": "https://apps.land.gov.il/MichrazimSite/"
}

OUTPUT_FILE = r"C:\Users\gavrielha\michrazim_miluim_details.xlsx"

# Miluim Uchlusiya codes
MILUIM_CODES = {"6", "7", "8"}

def fetch_all_active_ids():
    print("➡️ Fetching ALL tenders (one bulk call)...")
    payload = {
        "Page": 1,
        "ItemsPerPage": 20000,
        "Sort": {"Field": "MichrazID", "Direction": "Asc"},
        "SearchCriteria": {}
    }
    resp = requests.post(SEARCH_URL, json=payload, headers=HEADERS)
    resp.raise_for_status()
    data = resp.json()

    print(f"✅ Fetched {len(data)} total records.")
    # Filter on StatusMichraz == 1 (published)
    ids = [
        item["MichrazID"]
        for item in data
        if item.get("StatusMichraz") == 1
    ]
    print(f"✅ Filtered active IDs (StatusMichraz == 1): {len(ids)}")
    return ids

def fetch_details(michraz_id):
    try:
        url = f"{DETAIL_URL}?id={michraz_id}"
        resp = requests.get(url, headers=HEADERS)
        if resp.status_code == 404:
            print(f"❌ 404 Not Found for ID: {michraz_id}")
            return None
        resp.raise_for_status()
        return resp.json()
    except Exception as e:
        print(f"❌ Error for ID {michraz_id}: {e}")
        return None

def is_miluim(uchlus):
    if isinstance(uchlus, list):
        return any(code in MILUIM_CODES for code in uchlus)
    return False

def main():
    all_ids = fetch_all_active_ids()
    if not all_ids:
        print("❌ No active tenders found. Exiting.")
        return

    miluim_records = []
    count = 0

    for mid in all_ids:
        count += 1
        print(f"➡️ Fetching details {count}/{len(all_ids)} for ID: {mid}")
        details = fetch_details(mid)
        if not details:
            continue

        uchlus = details.get("Uchlusiya")
        if is_miluim(uchlus):
            miluim_records.append(details)

        time.sleep(0.1)  # Rate limit

    if not miluim_records:
        print("⚠️ No Miluim tenders found.")
        return

    df = pd.DataFrame(miluim_records)
    print(f"✅ Total Miluim tenders collected: {len(df)}")
    df.to_excel(OUTPUT_FILE, index=False)
    print(f"✅ Saved to: {OUTPUT_FILE}")

if __name__ == "__main__":
    main()
