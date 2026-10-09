import json
import requests

BASE = "http://127.0.0.1:8000/api/v1"
XLSX = r"data/test_dataset/chainpulse_test_dataset.xlsx"

EMAIL = "abhishek.mishra@avantika.edu.in"

password = input("Enter your ChainPulse password: ")

session = requests.Session()

print("\n=== AUTH ===")

r = session.post(
    f"{BASE}/auth/login",
    json={
        "email": EMAIL,
        "password": password,
    },
)

print("LOGIN:", r.status_code)

if r.status_code != 200:
    print(r.text)
    raise SystemExit

token = r.json().get("access_token")

session.headers.update({
    "Authorization": f"Bearer {token}"
})

print("PASS  Authentication successful")

print("\n=== USER ===")

r = session.get(f"{BASE}/auth/me")
print("ME:", r.status_code)

if r.status_code != 200:
    print(r.text)
    raise SystemExit

user = r.json()
org_id = user["organization_id"]

print("Organization:", org_id)

print("\n=== UPLOAD XLSX ===")

with open(XLSX, "rb") as f:
    r = session.post(
        f"{BASE}/uploads",
        files={
            "file": (
                "chainpulse_test_dataset.xlsx",
                f,
                "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
            )
        },
    )

print("UPLOAD:", r.status_code)

if r.status_code not in (200, 201):
    print(r.text)
    raise SystemExit

upload = r.json()
path = upload["path"]

print("Stored path:", path)

print("\n=== CREATE CONNECTION ===")

connection_body = {
    "name": "Canonical E2E XLSX",
    "connector_type": "xlsx",
    "description": "ChainPulse canonical ingestion E2E",
    "config": {
        "path": path,
        "original_filename": "chainpulse_test_dataset.xlsx",
    },
    "secrets": {},
}

r = session.post(
    f"{BASE}/data-connections",
    json=connection_body,
)

print("CONNECTION:", r.status_code)

if r.status_code not in (200, 201):
    print(r.text)
    raise SystemExit

connection = r.json()
connection_id = connection["id"]

print("Connection ID:", connection_id)

print("\n=== CONNECTION TEST ===")

r = session.post(
    f"{BASE}/data-connections/{connection_id}/test"
)

print("TEST:", r.status_code)
print(r.text)

if r.status_code != 200:
    raise SystemExit

print("\n=== SHEETS ===")

r = session.get(
    f"{BASE}/canonical-import/sheets/{connection_id}"
)

print("SHEETS:", r.status_code)

if r.status_code != 200:
    print(r.text)
    raise SystemExit

sheets = r.json()["sheets"]

print("Sheets:", sheets)

def find_sheet(name):
    for sheet in sheets:
        if isinstance(sheet, dict):
            value = (
                sheet.get("name")
                or sheet.get("sheet_name")
                or sheet.get("title")
            )
            if value == name:
                return value

        if sheet == name:
            return sheet

    return name

def auto_map(target):
    print(f"\n=== {target.upper()} ===")

    sheet = find_sheet(target)

    # Configure connection sheet
    r = session.post(
        f"{BASE}/data-connections/{connection_id}/sheet",
        params={"sheet": sheet},
    )

    print("SHEET CONFIG:", r.status_code)

    if r.status_code not in (200, 201):
        print(r.text)
        raise SystemExit

    # Preview
    r = session.post(
        f"{BASE}/ingestion/preview",
        json={
            "connection_id": connection_id,
            "limit": 100,
        },
    )

    print("PREVIEW:", r.status_code)

    if r.status_code != 200:
        print(r.text)
        raise SystemExit

    preview = r.json()

    print(
        "Rows:",
        preview.get("total_rows"),
        "Columns:",
        preview.get("columns"),
    )

    # Auto map
    r = session.post(
        f"{BASE}/ingestion/auto-map",
        json={
            "connection_id": connection_id,
            "target": target,
            "limit": 100,
        },
    )

    print("AUTO-MAP:", r.status_code)

    if r.status_code != 200:
        print(r.text)
        raise SystemExit

    result = r.json()

    print(
        "Missing:",
        result.get("missing_required"),
        "Ready:",
        result.get("ready"),
    )

    # IMPORTANT:
    # AutoMapper returns nested objects.
    # Extract .target, NOT the whole PowerShell/Python object.
    mapping = {
        source: details["target"]
        for source, details in result["suggestions"].items()
    }

    print("RESOLVED MAPPING:", mapping)

    # Target-specific required fields
    required = {
        "products": [
            "product_sku",
            "product_name",
        ],
        "demand": [
            "demand_date",
            "product_sku",
            "quantity",
        ],
        "inventory": [
            "inventory_date",
            "product_sku",
            "on_hand",
        ],
    }[target]

    # Mapped preview
    r = session.post(
        f"{BASE}/ingestion/mapped-preview",
        json={
            "connection_id": connection_id,
            "mapping": mapping,
        },
    )

    print("MAPPED PREVIEW:", r.status_code)

    if r.status_code != 200:
        print(r.text)
        raise SystemExit

    mapped = r.json()

    print("Mapped rows:", mapped.get("count"))

    # Validation
    r = session.post(
        f"{BASE}/ingestion/validate",
        json={
            "connection_id": connection_id,
            "mapping": mapping,
            "required_fields": required,
        },
    )

    print("VALIDATE:", r.status_code)

    if r.status_code != 200:
        print(r.text)
        raise SystemExit

    validation = r.json()

    print(
        "Valid:",
        validation.get("valid_rows"),
        "Invalid:",
        validation.get("invalid_rows"),
        "Issues:",
        validation.get("issues"),
    )

    if validation.get("invalid_rows", 0) > 0:
        print("VALIDATION FAILED")
        raise SystemExit

    # Import
    r = session.post(
        f"{BASE}/ingestion/import",
        json={
            "connection_id": connection_id,
            "mapping": mapping,
            "required_fields": required,
            "target": target,
        },
    )

    print("IMPORT:", r.status_code)

    if r.status_code not in (200, 201):
        print(r.text)
        raise SystemExit

    imported = r.json()

    print(
        "Received:",
        imported.get("rows_received"),
        "Imported:",
        imported.get("rows_imported"),
        "Errors:",
        imported.get("errors"),
    )

    if not imported.get("success"):
        raise SystemExit

    return imported

products = auto_map("products")
demand = auto_map("demand")
inventory = auto_map("inventory")

print("\n=== FINAL ===")

print("Products imported:", products["rows_imported"])
print("Demand imported:", demand["rows_imported"])
print("Inventory imported:", inventory["rows_imported"])

print("\n=== PIPELINE ===")

r = session.post(
    f"{BASE}/pipeline/run",
    params={
        "periods": 7,
        "window": 3,
    },
)

print("PIPELINE:", r.status_code)
print(r.text)

if r.status_code != 200:
    raise SystemExit

print("\nRESULT: PASS")

