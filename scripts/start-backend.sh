#!/usr/bin/env bash
# =============================================================
# Start the Odoo backend (Odoo + PostgreSQL)
# =============================================================
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_DIR="$(dirname "$SCRIPT_DIR")"
cd "$PROJECT_DIR"

echo "Starting Cosmetics E-Commerce backend..."
echo ""

# Load .env if present
if [ -f .env ]; then
    echo "Using configuration from .env"
fi

# Start services
if command -v docker compose &> /dev/null; then
    docker compose up "$@"
elif command -v docker-compose &> /dev/null; then
    docker-compose up "$@"
else
    echo "Error: Docker Compose not found."
    echo "Install: https://docs.docker.com/compose/install/"
    exit 1
fi
