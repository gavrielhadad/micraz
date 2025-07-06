import requests
import pandas as pd
import time
import traceback
from tqdm import tqdm

OUTPUT_FILE = "all_michrazim_data.xlsx"

# === Config
LIST_URL = "https://apps.land.gov.il/MichrazimSite/api/SearchApi/Search"
DETAIL_URL = "https://apps.land.gov.il/MichrazimSite/api/MichrazDetailsApi/Get"

HEADERS = {
    "Content-Type": "application/json",
    "Origin": "https://apps.land.gov.il",
    "Referer": "https://apps.land.gov.il/MichrazimSite/"
}


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

    data = res.json()
    if isinstance(data, dict) and "Results" in data:
        records = data["Results"]
    elif isinstance(data, list):
        records = data
    else:
        raise ValueError("❌ Unexpected API response format")

    if not records:
        raise ValueError("❌ No results returned from Search API!")

    df = pd.DataFrame(records)
    print(f"✅ Got {len(df)} Michraz IDs.")
    return df["MichrazID"].drop_duplicates().tolist()


def flatten_json(data, prefix=''):
    rows = {}

    def recurse(obj, name=''):
        if isinstance(obj, dict):
            for k, v in obj.items():
                recurse(v, f"{name}{k}_")
        elif isinstance(obj, list):
            joined = ",".join([str(i) for i in obj])
            rows[name[:-1]] = joined
        else:
            rows[name[:-1]] = obj

    recurse(data, prefix)
    return rows


def fetch_michraz_details(michraz_id, sleep_sec=0.01):
    try:
        params = {"michrazID": michraz_id}
        res = requests.get(DETAIL_URL, headers=HEADERS, params=params, timeout=30)
        if res.status_code == 404:
            return None, None, "404 Not Found"
        res.raise_for_status()
        data = res.json()

        if not data:
            return None, None, "Empty JSON"

        # Split main + doclist
        doclist = data.get("MichrazDocList", [])
        details_flat = flatten_json(data)
        return details_flat, doclist, None

    except Exception as ex:
        return None, None, str(ex)

    finally:
        time.sleep(sleep_sec)  # avoid hammering server


def main():
    all_ids = fetch_all_michraz_ids()

    all_records = []
    all_docs = []
    failures = []

    print("\n📥 Starting detail fetch for all IDs...\n")
    for michraz_id in tqdm(all_ids):
        details, docs, error = fetch_michraz_details(michraz_id)
        if error:
            print(f"⚠️ ID {michraz_id} error: {error}")
            failures.append({"MichrazID": michraz_id, "Error": error})
            continue

        if details:
            all_records.append(details)

        if docs:
            for doc in docs:
                doc_flat = flatten_json(doc)
                doc_flat["MichrazID"] = michraz_id
                all_docs.append(doc_flat)

    if not all_records:
        print("❌ No detailed records fetched. Exiting.")
        return

    # Create DataFrames
    df_main = pd.DataFrame(all_records)
    df_docs = pd.DataFrame(all_docs)
    df_fail = pd.DataFrame(failures)

    # Write to Excel
    print(f"\n💾 Writing to {OUTPUT_FILE}...")
    with pd.ExcelWriter(OUTPUT_FILE) as writer:
        df_main.to_excel(writer, index=False, sheet_name="Details")
        df_docs.to_excel(writer, index=False, sheet_name="Attachments")
        df_fail.to_excel(writer, index=False, sheet_name="Errors")

    print("✅ Done!")


if __name__ == "__main__":
    main()
