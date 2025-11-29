🚀 pipedrive-sales-automation

Automation tools for creating and updating Pipedrive deals, organizations, and custom fields using Python.

This repository contains two scripts that automate core CRM workflows:

• Bulk creation of Organizations, Persons and Deals
• Bulk updating of Organization Marketplaces and Deal City fields
• Normalization and validation of marketplace values
• Secure handling of API credentials

Designed for sales teams, lead-generation operations, and large data imports into Pipedrive.

⸻

📦 Project Structure

pipedrive-sales-automation/
• create_deals_from_leads.py – creates Organizations → Persons → Deals from Excel
• sync_marketplaces_and_city.py – updates Marketplaces and City in existing deals
• requirements.txt
• .gitignore
• README.md

⸻

🔐 Security Notice

The project does NOT store API tokens inside the code.

Before running scripts, set your token:

export PIPEDRIVE_API_TOKEN=“your_token_here”

or store it securely in a local .env file (ignored by Git):

PIPEDRIVE_API_TOKEN=your_token_here

All custom field identifiers use placeholders like:

CUSTOM_FIELD_XXXXX

Replace them with your real field keys from Pipedrive.

⸻

1️⃣ create_deals_from_leads.py

Bulk creation script for:

✔ Organizations
✔ Persons
✔ Deals

Input file: leads.xlsx

Required columns:
• Name
• Phone (optional)
• Email (optional)
• Website link
• Google reviews
• Followers total
• Marketplaces in use
• Instagram link
• Facebook link
• Link (auto-filled after creation)

What the script does

• Creates an organization and fills custom fields
• Creates a person linked to that organization
• Creates a deal with a predefined lead source
• Writes back the Pipedrive deal URL into Excel
• Saves the output to leads_with_links.xlsx

How to run

pip install -r requirements.txt
export PIPEDRIVE_API_TOKEN=“your_token”
python create_deals_from_leads.py

⸻

2️⃣ sync_marketplaces_and_city.py

Bulk updater for:

✔ Organization Marketplaces
✔ Deal City

Input file: market.xlsx

Required columns:
• LINK – deal URL containing /deal/{id}
• Market – comma-separated marketplace names
• City – deal city

What the script does

• Extracts deal IDs from the URLs
• Resolves the linked organization ID
• Normalizes marketplace labels
• Maps marketplaces to Pipedrive enum IDs
• Updates:
– Organization.marketplaces
– Deal.city
• Logs unmatched marketplace labels

How to run

pip install -r requirements.txt
export PIPEDRIVE_API_TOKEN=“your_token”
python sync_marketplaces_and_city.py

⸻

🛠 Requirements

• pandas
• requests
• openpyxl
• python-dotenv (optional)

Install everything:

pip install -r requirements.txt

⸻

📌 Additional Notes

• .xlsx files are ignored in Git for privacy
• .env is ignored for local secret storage
• Scripts include minimal delays for API rate safety
• Safe to re-run (idempotent updates)
