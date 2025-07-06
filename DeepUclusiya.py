import requests
import pandas as pd

# ========================
# CONFIG
# ========================
url = "https://apps.land.gov.il/MichrazimSite/api/SearchApi/Search"

headers = {
    "Content-Type": "application/json",
    "Origin": "https://apps.land.gov.il",
    "Referer": "https://apps.land.gov.il/MichrazimSite/",
}

output_path = r"C:\Users\gavrielha\michrazim_miluim_only.xlsx"

# ========================
# STEP 1: Fetch all tenders
# ========================
print("➡️ Fetching ALL tenders in one big call...")

payload = {
    "Page": 1,
    "ItemsPerPage": 20000,  # big number to get them all at once
    "Sort": {"Field": "MichrazID", "Direction": "Asc"},
    "SearchCriteria": {}
}

response = requests.post(url, json=payload, headers=headers)
response.raise_for_status()
data = response.json()

print(f"✅ Got {len(data)} total records.")

# ========================
# STEP 2: Load to DataFrame
# ========================
df = pd.DataFrame(data)
print(f"✅ DataFrame shape BEFORE filtering: {df.shape}")

# ========================
# STEP 3: Filter only Miluim tenders
# ========================
def is_miluim(uchlus):
    if isinstance(uchlus, list):
        return "8" in uchlus
    return False

if "Uchlusiya" in df.columns:
    df = df[df["Uchlusiya"].apply(is_miluim)]
    print(f"✅ AFTER filtering Miluim only: {df.shape}")
else:
    print("⚠️ WARNING: Uchlusiya column not found in data!")

# ========================
# STEP 4: Remove duplicates by MichrazID
# ========================
if "MichrazID" in df.columns:
    before = len(df)
    df = df.drop_duplicates(subset=['MichrazID'])
    after = len(df)
    print(f"✅ Removed duplicates: {before - after} removed. Final count: {after}")
else:
    print("⚠️ WARNING: MichrazID column not found for deduplication.")

# ========================
# STEP 5: Save to Excel
# ========================
if not df.empty:
    df.to_excel(output_path, index=False)
    print(f"✅ Miluim tenders saved to Excel: {output_path}")
else:
    print("⚠️ No Miluim tenders found after filtering. Nothing to save.")
