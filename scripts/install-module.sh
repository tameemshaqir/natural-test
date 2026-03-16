#!/usr/bin/env bash
# =============================================================
# Initialize the database and install the Cosmetics Store module
# =============================================================
# Run this after starting the PostgreSQL container with:
#   docker compose up -d db
#
# This creates the 'cosmetics' database and installs all required
# modules. It runs Odoo once in init mode (no HTTP server) and exits.
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

echo "Initializing database and installing Cosmetics Store module..."
echo "Database: $DB_NAME"
echo "This may take 1-2 minutes..."
echo ""

if command -v docker compose &> /dev/null; then
    COMPOSE="docker compose"
elif command -v docker-compose &> /dev/null; then
    COMPOSE="docker-compose"
else
    echo "Error: Docker Compose not found."
    exit 1
fi

# Run Odoo init command
$COMPOSE run --rm odoo odoo \
    --config=/etc/odoo/odoo.conf \
    --database="$DB_NAME" \
    --init=cosmetics_store \
    --stop-after-init \
    --no-http \
    --without-demo=all

echo ""
echo "✅ Module installed successfully!"
echo ""
echo "Start the Odoo server with:"
echo "  docker compose up -d"
echo ""
echo "Then open http://localhost:8069"
echo "Login: admin / admin"
