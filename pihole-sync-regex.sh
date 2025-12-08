#!/bin/bash
# Sync regex whitelist from combined GitHub list into specific Pi-hole groups

# Config
LIST_URL="https://raw.githubusercontent.com/mahirmm/whitelist-pihole/refs/heads/master/domains/whitelist.txt"
GROUPS=("Default" "YesGameAds")  # Groups to assign the regex to

TMPFILE=$(mktemp)
curl -s "$LIST_URL" -o "$TMPFILE" || exit 1

# Get existing regex whitelist entries
EXISTING_REGEX=$(pihole -q -all | grep -E '^\^.*\$?$' || true)

# Process each line
while IFS= read -r line; do
  # Skip comments or blank lines
  [[ -z "$line" || "$line" =~ ^# ]] && continue

  # Only process regex-style lines
  if [[ "$line" =~ [\^\$\.\*\(\)\?\|\\] ]]; then
    # Skip if already exists
    if echo "$EXISTING_REGEX" | grep -Fxq "$line"; then
      continue
    fi
    # Add to Pi-hole regex whitelist in all groups
    for group in "${GROUPS[@]}"; do
      echo "Adding regex '$line' to group '$group'"
      pihole --white-regex "$line" --group "$group" >/dev/null 2>&1
    done
  fi
done < "$TMPFILE"

rm "$TMPFILE"

# Reload lists so Pi-hole picks up new rules
pihole restartdns reloadlists
