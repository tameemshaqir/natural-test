#!/usr/bin/env bash
# =============================================================
# Stop the Odoo backend (Odoo + PostgreSQL)
# =============================================================
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_DIR="$(dirname "$SCRIPT_DIR")"
cd "$PROJECT_DIR"

echo "Stopping Cosmetics E-Commerce backend..."

if command -v docker compose &> /dev/null; then
    docker compose down "$@"
elif command -v docker-compose &> /dev/null; then
    docker-compose down "$@"
else
    echo "Error: Docker Compose not found."
    exit 1
fi

echo "Backend stopped."
