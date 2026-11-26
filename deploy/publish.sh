#!/bin/sh
# Put Starguard up at https://dev.retroverse.ai/starguard/ : install the service, add the nginx block (once), reload.
# Run from anywhere:  sh ~/projects/luster/deploy/publish.sh
set -e
HERE=$(cd "$(dirname "$0")" && pwd)
CONF=/etc/nginx/sites-enabled/retroverse-dev.conf
MARK='# --- Portal API: rate-limited'

sudo cp "$HERE/starguard.service" /etc/systemd/system/
sudo systemctl daemon-reload
sudo systemctl enable starguard
sudo systemctl restart starguard

if ! sudo grep -q 'location /starguard/' "$CONF"; then
  sudo grep -q "$MARK" "$CONF" || { echo "marker not found in $CONF; add deploy/nginx-starguard.conf by hand" >&2; exit 1; }
  sudo mkdir -p /etc/nginx/backups
  sudo cp "$CONF" "/etc/nginx/backups/retroverse-dev.conf.$(date +%Y%m%d%H%M%S)"
  TMP=$(mktemp)
  # insert our block just above the portal API block
  sudo awk -v block="$HERE/nginx-starguard.conf" -v mark="$MARK" '
    index($0, mark) && !done { while ((getline line < block) > 0) print line; done = 1 }
    { print }' "$CONF" > "$TMP"
  sudo cp "$TMP" "$CONF"; rm -f "$TMP"
fi
if ! sudo nginx -t; then echo "nginx config test failed; restore the newest file in /etc/nginx/backups" >&2; exit 1; fi
sudo systemctl reload nginx
sleep 1
curl -s -o /dev/null -w "service  %{http_code}\n" http://127.0.0.1:5079/
curl -s -o /dev/null -w "public   %{http_code}\n" https://dev.retroverse.ai/starguard/
