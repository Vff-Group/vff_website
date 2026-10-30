#!/bin/bash
# Run this on the production server (e.g. /root/vff_website) so gunicorn
# picks up the latest code, nginx reloads, and logs stream.

set -euo pipefail

APP_DIR="${APP_DIR:-/root/vff_website}"
VENV_PY="${VENV_PY:-/root/vff_website/myprojectenv/bin/python}"

RED='\033[0;31m'
GREEN='\033[0;32m'
NC='\033[0m'

step() { echo -e "${GREEN}==> $1${NC}"; }
fail() { echo -e "${RED}Error: $1${NC}"; exit 1; }

cd "$APP_DIR" || fail "Cannot cd to $APP_DIR"

if [ -d .git ]; then
  step "Pulling latest code"
  git pull || fail "git pull failed"
else
  echo "No git repo in $APP_DIR — skipping pull"
fi

if [ -x "$VENV_PY" ]; then
  step "Collecting static files"
  "$VENV_PY" manage.py collectstatic --noinput || echo "collectstatic skipped/failed (not fatal)"
else
  echo "Python venv not found at $VENV_PY — skipping collectstatic"
fi

step "Restarting gunicorn"
sudo systemctl restart gunicorn
sudo systemctl status gunicorn --no-pager

step "Testing nginx config"
sudo nginx -t || fail "nginx -t failed — not reloading nginx"

step "Reloading nginx"
sudo systemctl reload nginx

echo -e "${GREEN}Deploy complete. Following gunicorn logs (Ctrl+C to stop).${NC}"
sudo journalctl -u gunicorn -f
