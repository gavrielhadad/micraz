import requests
import csv
import time

# --- CONFIG ---
API_URL = "https://apps.land.gov.il/MichrazimSite/api/SearchApi/Search"
PAGE_SIZE = 200
STATUS_ID = 1  # 1 = Active tenders, 2 = Closed tenders
OUTPUT_FILE = "michrazim_tenders.csv"


def fetch_all_tenders(status_id=STATUS_ID):
    page = 1
    all_items = []

    while True:
        print(f"Fetching page {page}...")

        payload = {
            "pageNumber": page,
            "pageSize": PAGE_SIZE,
            "statusId": status_id
        }

        headers = {
            "Content-Type": "application/json"
        }

        try:
            response = requests.post(API_URL, json=payload, headers=headers)
            response.raise_for_status()
            data = response.json()
        except Exception as e:
            print(f"Error on page {page}: {e}")
            break

        # Handle if response is list or dict
        if isinstance(data, dict) and "Items" in data:
            items = data["Items"]
        elif isinstance(data, list):
            items = data
        else:
            print(f"Unexpected data format: {data}")
            break

        if not items:
            print("No more results.")
            break

        for item in items:
            all_items.append({
                "TenderId": item.get("TenderId"),
                "TenderNumber": item.get("TenderNumber"),
                "Description": item.get("TenderDescription"),
                "City": item.get("City"),
                "Gush": item.get("Gush"),
                "Helka": item.get("Helka"),
                "Area": item.get("Area"),
                "Status": item.get("StatusDesc"),
                "LastDateForBids": item.get("LastDateForBids")
            })

        page += 1
        #time.sleep(0.5)  # Be polite

    return all_items


def save_to_csv(data, filename=OUTPUT_FILE):
    if not data:
        print("No data found!")
        return

    with open(filename, "w", newline='', encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=data[0].keys())
        writer.writeheader()
        writer.writerows(data)

    print(f"Saved {len(data)} records to {filename}")


if __name__ == "__main__":
    print("Starting scraper for Israel Land Authority tenders...")
    tenders = fetch_all_tenders()
    save_to_csv(tenders)
    print("Done.")
