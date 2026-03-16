#!/usr/bin/env bash
# =============================================================
# Install the Cosmetics Store module into Odoo
# =============================================================
# Run this after the Odoo container is up and the database exists.
# It triggers Odoo to install/update the cosmetics_store module.
# =============================================================
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_DIR="$(dirname "$SCRIPT_DIR")"
cd "$PROJECT_DIR"

# Load .env
if [ -f .env ]; then
    set -a
    source .env
    set +a
fi

DB_NAME="${POSTGRES_DB:-cosmetics}"

echo "Installing/Updating Cosmetics Store module..."
echo "Database: $DB_NAME"
echo ""

if command -v docker compose &> /dev/null; then
    COMPOSE="docker compose"
elif command -v docker-compose &> /dev/null; then
    COMPOSE="docker-compose"
else
    echo "Error: Docker Compose not found."
    exit 1
fi

# Run Odoo install/update command
$COMPOSE run --rm odoo \
    odoo --config=/etc/odoo/odoo.conf \
    --database="$DB_NAME" \
    --init=cosmetics_store \
    --stop-after-init \
    --no-http

echo ""
echo "✅ Module installed successfully!"
echo "Start the backend with: scripts/start-backend.sh -d"
