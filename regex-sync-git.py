#!/usr/bin/env python3
import requests
import json

# -----------------------------
# CONFIGURATION
# -----------------------------
GITHUB_URL = "https://raw.githubusercontent.com/YOURUSER/YOURREPO/main/whitelist.txt"
PIHOLE_API_URL = "http://192.168.10.134:8080/api/domains/allow/regex"
SID = "Qn0onkPtx1tZfGQ/sSL/Gw="

GROUPS = [0, 1]   # Default + YesGameAds


# -----------------------------
# DETECT ONLY REAL REGEX ENTRIES
# -----------------------------
def extract_regex_domains(lines):
    # Any of these chars indicates regex (literal dots allowed)
    REGEX_CHARS = "^$*+?()[]{}|\\"

    regex_domains = []

    for line in lines:
        domain = line.strip()

        if not domain or domain.startswith("#"):
            continue

        # TRUE regex if any regex character exists
        if any(c in domain for c in REGEX_CHARS):
            regex_domains.append(domain)
        else:
            print(f"Skipping exact domain: {domain}")

    return regex_domains


# -----------------------------
# ADD REGEX TO PIHOLE
# -----------------------------
def add_regex(domain, comment="Synced via script"):
    headers = {
        "accept": "application/json",
        "content-type": "application/json",
        "sid": SID
    }

    payload = {
        "domain": domain,
        "comment": comment,
        "groups": GROUPS,
        "enabled": True
    }

    r = requests.post(PIHOLE_API_URL, headers=headers, data=json.dumps(payload))

    if r.ok:
        print(f"✔ Added '{domain}' to groups {GROUPS}")
    else:
        print(f"✖ Failed to add '{domain}': {r.text}")


# -----------------------------
# MAIN PROCESS
# -----------------------------
def main():
    print("Downloading GitHub txt file...")

    try:
        r = requests.get(GITHUB_URL)
        r.raise_for_status()
    except Exception as e:
        print("❌ Failed to download GitHub file:", e)
        return

    lines = r.text.splitlines()

    print("\nExtracting regex domains...")
    regex_domains = extract_regex_domains(lines)

    print(f"\nFound {len(regex_domains)} regex entries\n")

    for domain in regex_domains:
        add_regex(domain)


# -----------------------------
# ENTRY POINT
# -----------------------------
if __name__ == "__main__":
    main()
