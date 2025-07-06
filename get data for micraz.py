import requests
import pandas as pd

# ------------------ GET JSON DATA ------------------

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
    exit()

data = res.json()
print("\n✅ JSON response received.")

# ------------------ PARSE GENERAL DATA ------------------

general_data = {
    "MichrazID": data.get("MichrazID"),
    "MichrazName": data.get("MichrazName"),
    "KodYeshuv": data.get("KodYeshuv"),
    "YechidotDiur": data.get("YechidotDiur"),
    "Shchuna": data.get("Shchuna"),
    "PirsumDate": data.get("PirsumDate"),
    "SgiraDate": data.get("SgiraDate"),
    "SchumArvut": data.get("SchumArvut"),
    "Comments": "\n".join(data.get("Comments", [])),
    "DocsCount": len(data.get("MichrazDocList", []))
}

general_df = pd.DataFrame([general_data])

print("\n✅ General data parsed.")

# ------------------ PARSE TIK/MIGRASH DATA ------------------

migrash_list = []

for tik in data.get("Tik", []):
    gush = helka = None
    if tik.get("GushHelka"):
        gush = tik["GushHelka"][0].get("Gush")
        helka = tik["GushHelka"][0].get("Helka")

    migrash_entry = {
        "MichrazID": tik.get("MichrazID"),
        "TikID": tik.get("TikID"),
        "MitchamName": tik.get("MitchamName"),
        "Shetach": tik.get("Shetach"),
        "mechirShuma": tik.get("mechirShuma"),
        "SchumArvut": tik.get("SchumArvut"),
        "Gush": gush,
        "Helka": helka
    }
    migrash_list.append(migrash_entry)

migrash_df = pd.DataFrame(migrash_list)

print(f"\n✅ Parsed {len(migrash_list)} migrash entries.")

# ------------------ SAVE TO EXCEL ------------------

filename = f"michraz_{michraz_id}.xlsx"

with pd.ExcelWriter(filename) as writer:
    general_df.to_excel(writer, sheet_name="GeneralData", index=False)
    migrash_df.to_excel(writer, sheet_name="MigrashData", index=False)

print(f"\n✅ Excel file '{filename}' created successfully.")
