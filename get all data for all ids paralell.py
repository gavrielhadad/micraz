import requests
import pandas as pd
from concurrent.futures import ThreadPoolExecutor, as_completed
from tqdm import tqdm
import time
import random
from tenacity import retry, stop_after_attempt, wait_random
import openpyxl

# ----------------------------------------
# CONFIG
# ----------------------------------------
LIST_URL = "https://apps.land.gov.il/MichrazimSite/api/SearchApi/Search"
DETAIL_URL = "https://apps.land.gov.il/MichrazimSite/api/MichrazDetailsApi/Get"
HEADERS = {
    "Content-Type": "application/json",
    "Origin": "https://apps.land.gov.il",
    "Referer": "https://apps.land.gov.il/MichrazimSite/"
}
OUTPUT_FILE = "all_michraz_data.xlsx"
MAX_THREADS = 5  # polite parallelism


# ----------------------------------------
# UTIL: flatten nested JSON
# ----------------------------------------
def flatten_json(y, parent_key='', sep='.'):
    items = []
    if isinstance(y, dict):
        for k, v in y.items():
            new_key = f"{parent_key}{sep}{k}" if parent_key else k
            items.extend(flatten_json(v, new_key, sep=sep).items())
    elif isinstance(y, list):
        items.append((parent_key, ', '.join(map(str, y))))
    else:
        items.append((parent_key, y))
    return dict(items)


# ----------------------------------------
# STEP 1: Fetch ALL IDs (1 big page)
# ----------------------------------------
def fetch_all_michraz_ids():
    print("🚀 Fetching all michraz IDs (one big page)...")
    payload = {
        "Page": 1,
        "ItemsPerPage": 20000,
        "Sort": None,
        "SearchCriteria": {}
    }
    res = requests.post(LIST_URL, json=payload, headers=HEADERS, timeout=60)
    res.raise_for_status()

    results = res.json()
    if isinstance(results, list):
        # Sometimes the API returns directly a list
        df = pd.DataFrame(results)
    else:
        df = pd.DataFrame(results.get("Results", []))

    ids = df["MichrazID"].drop_duplicates().tolist()
    print(f"✅ Got {len(ids)} Michraz IDs.")
    return ids


# ----------------------------------------
# STEP 2: Fetch detail for 1 ID
# ----------------------------------------
@retry(stop=stop_after_attempt(3), wait=wait_random(1, 3))
def fetch_michraz_detail_single(michraz_id):
    try:
        # polite delay to avoid blocks
        time.sleep(random.uniform(0.2, 0.5))
        params = {"michrazID": michraz_id}
        res = requests.get(DETAIL_URL, headers=HEADERS, params=params, timeout=30)
        res.raise_for_status()
        detail = res.json()
        if not isinstance(detail, dict):
            raise ValueError("Invalid JSON object")
        flat = flatten_json(detail)
        flat["MichrazID"] = michraz_id
        return flat
    except Exception as e:
        print(f"⚠️ ID {michraz_id} error: {e}")
        raise


# ----------------------------------------
# STEP 3: Parallel fetch all details
# ----------------------------------------
def fetch_all_details_parallel(ids):
    print(f"\n📥 Starting detail fetch for {len(ids)} IDs in parallel with {MAX_THREADS} threads...\n")
    results = []

    with ThreadPoolExecutor(max_workers=MAX_THREADS) as executor:
        futures = {executor.submit(fetch_michraz_detail_single, i): i for i in ids}

        for future in tqdm(as_completed(futures), total=len(futures)):
            try:
                data = future.result()
                if data:
                    results.append(data)
            except Exception:
                # Failed after retries
                continue

    print(f"\n✅ Completed fetching details. Total successful: {len(results)}")
    return results


# ----------------------------------------
# MAIN
# ----------------------------------------
def main():
    all_ids = fetch_all_michraz_ids()
    details = fetch_all_details_parallel(all_ids)

    if details:
        df = pd.DataFrame(details)
        df.to_excel(OUTPUT_FILE, index=False)
        print(f"\n💾 Saved all details to {OUTPUT_FILE}")
    else:
        print("❌ No details fetched!")


# ----------------------------------------
# RUN
# ----------------------------------------
if __name__ == "__main__":
    main()
