#!/usr/bin/env python3

import requests
import re
import sys

# ---------------- CONFIG ----------------

PIHOLE_API = "http://192.168.10.134:8080/api/domains/allow/regex"
SID = "EZdgCqCDUV6nKAofWcoHvA="

DOMAINS_URL = "https://raw.githubusercontent.com/mahirmm/whitelist-pihole/refs/heads/master/domains/whitelist.txt"
COMMENTS_URL = "https://raw.githubusercontent.com/mahirmm/whitelist-pihole/refs/heads/master/domains/master-whitelist-comments.txt"

GROUPS = [0, 1]

# ----------------------------------------


def normalize(domain):
    """
    Canonicalize domain / regex from GitHub files
    """
    # Remove BOM
    domain = domain.replace("\ufeff", "")

    # Normalize whitespace
    domain = domain.strip()
    domain = domain.replace("\r", "")
    domain = domain.replace("\t", " ")

    # Collapse spaces
    domain = re.sub(r"\s+", " ", domain)

    return domain




def download_file(url):
    r = requests.get(url, timeout=15)
    r.raise_for_status()
    return r.text.splitlines()


def is_regex(domain):
    """
    Detect Pi-hole regex safely.
    Excludes exact domains like google.com
    """
    regex_indicators = ["^", "$", "(", ")", "[", "]", "\\", "*", "+", "?", "{", "}", "|"]

    if not any(c in domain for c in regex_indicators):
        return False

    try:
        re.compile(domain)
        return True
    except re.error:
        return False


def parse_comments(lines):
    comments = {}

    for line in lines:
        line = normalize(line)
        if not line or " | " not in line:
            continue

        domain, comment = line.split(" | ", 1)
        domain = normalize(domain)
        comment = comment.strip()

        if is_regex(domain):
            comments[domain] = comment

    return comments




def add_regex(domain, comment):
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

    r = requests.post(PIHOLE_API, headers=headers, json=payload)

    if r.ok:
        print(f"✔ Added regex: {domain}  →  {comment}")
    else:
        print(f"✖ Failed: {domain}\n{r.text}")


def main():
    print("Downloading domain lists...")

    domains = download_file(DOMAINS_URL)
    comments_lines = download_file(COMMENTS_URL)

    comment_map = parse_comments(comments_lines)

    regex_domains = []

    for domain in domains:
        domain = normalize(domain)
        if is_regex(domain):
            regex_domains.append(domain)

    print(f"Found {len(regex_domains)} regex entries")

    for domain in regex_domains:
        comment = comment_map.get(domain, "Synced from GitHub")
        if domain not in comment_map:
            print(f"⚠ No comment match for: [{domain}]")

        add_regex(domain, comment)


if __name__ == "__main__":
    main()
