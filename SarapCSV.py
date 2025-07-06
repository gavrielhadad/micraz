import requests
import csv
import time

API_URL = "https://apps.land.gov.il/MichrazimSite/api/SearchApi/Search"
PAGE_SIZE = 50
STATUS_ID = 1  # 1 = Active tenders, 2 = Closed tenders

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
            print(f"Error fetching page {page}: {e}")
            break

        # Print once to see structure
        if page == 1:
            print("DEBUG FIRST RESPONSE:", type(data))
            if isinstance(data, dict):
                print("Keys:", list(data.keys()))
            elif isinstance(data, list):
                print("First item:", data[0] if data else "EMPTY")

        # Flexible parsing
        if isinstance(data, dict) and "Items" in data:
            items = data["Items"]
        elif isinstance(data, list):
            items = data
        else:
            print(f"Unknown data format on page {page}: {data}")
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
        time.sleep(0.5)

    return all_items

def save_csv(data, filename="michrazim_tenders.csv"):
    if not data:
        print("No data found.")
        return

    with open(filename, "w", newline='', encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=data[0].keys())
        writer.writeheader()
        writer.writerows(data)

    print(f"Saved {len(data)} records to {filename}")

if __name__ == "__main__":
    tenders = fetch_all_tenders()
    save_csv(tenders)
