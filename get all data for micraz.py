import requests
import pandas as pd

# Get MichrazID from user
michraz_id = input("Enter MichrazID: ").strip()

url = "https://apps.land.gov.il/MichrazimSite/api/MichrazDetailsApi/Get"
params = {"michrazID": michraz_id}

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/126.0.0.0 Safari/537.36",
    "Accept": "application/json, text/plain, */*",
    "Accept-Language": "he-IL,he;q=0.9,en-US;q=0.8,en;q=0.7",
    "Origin": "https://apps.land.gov.il",
    "Referer": "https://apps.land.gov.il/MichrazimSite/",
    "Connection": "keep-alive"
}

res = requests.get(url, headers=HEADERS, params=params, timeout=30)
print("Status:", res.status_code)

if "application/json" not in res.headers.get("Content-Type", ""):
    print("\n❌ Server returned non-JSON response")
    print(res.text)
    exit()

data = res.json()
print("\n✅ JSON received")

# ----------------------------------------------------------
# 1️⃣ Extract GeneralData (flatten lists to comma-separated strings)
general_fields = {}
for k, v in data.items():
    if isinstance(v, list):
        general_fields[k] = ",".join(str(item) for item in v)
    elif not isinstance(v, dict):
        general_fields[k] = v

general_df = pd.DataFrame([general_fields])

# ----------------------------------------------------------
# 2️⃣ Extract Tik (plots)
plots_list = []
for tik in data.get("Tik", []):
    item = {}
    for k, v in tik.items():
        if isinstance(v, list):
            item[k] = ",".join(str(sub) for sub in v)
        elif not isinstance(v, dict):
            item[k] = v

    # TochnitMigrash
    if tik.get("TochnitMigrash"):
        t_m = tik["TochnitMigrash"][0]
        item["Tochnit"] = t_m.get("Tochnit")
        item["MigrashName"] = t_m.get("MigrashName")
        item["TochnitMigrashID"] = t_m.get("TochnitMigrashID")
    # GushHelka
    if tik.get("GushHelka"):
        gh = tik["GushHelka"][0]
        item["Gush"] = gh.get("Gush")
        item["Helka"] = gh.get("Helka")
    plots_list.append(item)

plots_df = pd.DataFrame(plots_list)

# ----------------------------------------------------------
# 3️⃣ Extract Documents
documents_list = []
for doc in data.get("MichrazDocList", []):
    doc_row = {}
    for k, v in doc.items():
        if isinstance(v, list):
            doc_row[k] = ",".join(str(sub) for sub in v)
        else:
            doc_row[k] = v
    documents_list.append(doc_row)

# Add MichrazFullDocument
if data.get("MichrazFullDocument"):
    full_doc = data["MichrazFullDocument"]
    full_doc_row = {}
    for k, v in full_doc.items():
        if isinstance(v, list):
            full_doc_row[k] = ",".join(str(sub) for sub in v)
        else:
            full_doc_row[k] = v
    documents_list.append(full_doc_row)

docs_df = pd.DataFrame(documents_list)

# ----------------------------------------------------------
# 4️⃣ Extract Links
links_list = []
for link in data.get("MichrazLinks", []):
    link_row = {}
    for k, v in link.items():
        if isinstance(v, list):
            link_row[k] = ",".join(str(sub) for sub in v)
        else:
            link_row[k] = v
    links_list.append(link_row)
links_df = pd.DataFrame(links_list)

# ----------------------------------------------------------
# 5️⃣ Extract Comments
comments_list = data.get("Comments", [])
comments_df = pd.DataFrame({"Comment": comments_list})

# ----------------------------------------------------------
# 6️⃣ Write to Excel
file_name = f"michraz_{michraz_id}.xlsx"
with pd.ExcelWriter(file_name) as writer:
    general_df.to_excel(writer, sheet_name='GeneralData', index=False)
    plots_df.to_excel(writer, sheet_name='Plots', index=False)
    docs_df.to_excel(writer, sheet_name='Documents', index=False)
    if not links_df.empty:
        links_df.to_excel(writer, sheet_name='Links', index=False)
    if not comments_df.empty:
        comments_df.to_excel(writer, sheet_name='Comments', index=False)

print(f"\n✅ Data saved to {file_name}")
