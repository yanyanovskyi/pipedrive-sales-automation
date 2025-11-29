import os
import time
import requests
import pandas as pd

# API token is taken from environment variable for safety
API_TOKEN = os.getenv("PIPEDRIVE_API_TOKEN")
BASE_URL = "https://api.pipedrive.com/v1"

if not API_TOKEN:
    raise RuntimeError(
        "Environment variable PIPEDRIVE_API_TOKEN is not set. "
        "Set it before running the script."
    )

# Custom field keys (replace with real IDs from Pipedrive)
FIELD_KEYS = {
    "Website link": "CUSTOM_FIELD_WEBSITE_LINK",
    "Google reviews": "CUSTOM_FIELD_GOOGLE_REVIEWS",
    "Followers total": "CUSTOM_FIELD_FOLLOWERS_TOTAL",
    "Marketplaces in use": "CUSTOM_FIELD_MARKETPLACES_IN_USE",
    "Instagram link": "CUSTOM_FIELD_INSTAGRAM_LINK",
    "Facebook link": "CUSTOM_FIELD_FACEBOOK_LINK",
}

# Lead source field (replace with real key + option ID)
LEAD_SOURCE_KEY = "CUSTOM_FIELD_LEAD_SOURCE"
LEAD_SOURCE_OPTION_ID = 1  # example value — replace with actual enum option

# Marketplace enum option IDs (replace with your system values)
MARKETPLACE_OPTIONS = {
    "Bistro Sk": 1001,
    "Bolt Food": 1002,
    "Bond": 1003,
    "Foodora": 1004,
    "Glovo": 1005,
    "Loko": 1006,
    "None": 1007,
    "Other": 1008,
    "Pyszne": 1009,
    "Uber Eats": 1010,
    "Wolt": 1011,
}


def main():
    df = pd.read_excel("leads.xlsx")

    # Ensure Link column exists
    if "Link" not in df.columns:
        df["Link"] = ""
    df["Link"] = df["Link"].astype(str)

    leads = df.to_dict(orient="records")

    for i, lead in enumerate(leads):
        name = lead.get("Name", "").strip()
        phone = str(lead.get("Phone")) if pd.notna(lead.get("Phone")) else ""
        email = lead.get("Email") if pd.notna(lead.get("Email")) else ""

        if not name:
            print(f"Skipping row {i}: empty Name field.")
            continue

        # ---------------------------
        # 1) Create Organization
        # ---------------------------
        org_data = {"name": name, "visible_to": 3}

        # Fill custom fields
        for field_name, field_key in FIELD_KEYS.items():
            value = lead.get(field_name)
            if pd.notna(value):
                if field_name == "Marketplaces in use":
                    raw_values = str(value).split(",")
                    ids = []
                    for v in raw_values:
                        cleaned = v.strip().title()
                        if cleaned == "Uber":
                            cleaned = "Uber Eats"
                        elif cleaned == "Pyszne.Pl":
                            cleaned = "Pyszne"
                        if cleaned in MARKETPLACE_OPTIONS:
                            ids.append(MARKETPLACE_OPTIONS[cleaned])
                    if ids:
                        org_data[field_key] = ids
                else:
                    org_data[field_key] = value

        org_resp = requests.post(
            f"{BASE_URL}/organizations",
            params={"api_token": API_TOKEN},
            json=org_data,
            timeout=30,
        )

        if org_resp.status_code != 201 or not org_resp.json().get("data"):
            print(f"❌ Organization '{name}' error: {org_resp.text}")
            continue

        org_id = org_resp.json()["data"]["id"]
        print(f"✅ Organization created: {name} (id={org_id})")

        # ---------------------------
        # 2) Create Person
        # ---------------------------
        person_data = {"name": name, "phone": phone, "email": email, "org_id": org_id}

        person_resp = requests.post(
            f"{BASE_URL}/persons",
            params={"api_token": API_TOKEN},
            json=person_data,
            timeout=30,
        )

        if person_resp.status_code != 201 or not person_resp.json().get("data"):
            print(f"❌ Person '{name}' error: {person_resp.text}")
            continue

        person_id = person_resp.json()["data"]["id"]
        print(f"✅ Person created: {name} (id={person_id})")

        # ---------------------------
        # 3) Create Deal
        # ---------------------------
        deal_data = {
            "title": f"Deal with {name}",
            "person_id": person_id,
            "org_id": org_id,
            "currency": "USD",
            LEAD_SOURCE_KEY: LEAD_SOURCE_OPTION_ID,
        }

        deal_resp = requests.post(
            f"{BASE_URL}/deals",
            params={"api_token": API_TOKEN},
            json=deal_data,
            timeout=30,
        )

        if deal_resp.status_code == 201 and deal_resp.json().get("data"):
            deal = deal_resp.json()["data"]
            deal_link = f"https://app.pipedrive.com/deal/{deal['id']}"
            df.at[i, "Link"] = deal_link
            print(f"✅ Deal created: {deal_link}")
        else:
            print(f"❌ Deal creation error: {deal_resp.text}")

        time.sleep(0.5)

    # ---------------------------
    # Save output
    # ---------------------------
    df.to_excel("leads_with_links.xlsx", index=False)
    print("📁 Saved → leads_with_links.xlsx")


if __name__ == "__main__":
    main()
