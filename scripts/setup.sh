#!/usr/bin/env bash
# =============================================================
# Cosmetics E-Commerce System — Setup Script
# =============================================================
# This script sets up the development environment.
# Run once after cloning the repository.
# =============================================================
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_DIR="$(dirname "$SCRIPT_DIR")"

echo "============================================="
echo " Cosmetics E-Commerce System — Setup"
echo "============================================="
echo ""

# ---- Step 1: Create .env if it doesn't exist ----
if [ ! -f "$PROJECT_DIR/.env" ]; then
    echo "[1/4] Creating .env from .env.example..."
    cp "$PROJECT_DIR/.env.example" "$PROJECT_DIR/.env"
    echo "      ✅ Created .env — edit it with your credentials"
else
    echo "[1/4] .env already exists — skipping"
fi

# ---- Step 2: Check Docker is installed ----
echo "[2/4] Checking Docker..."
if command -v docker &> /dev/null; then
    echo "      ✅ Docker found: $(docker --version)"
else
    echo "      ❌ Docker not found!"
    echo "      Install Docker: https://docs.docker.com/get-docker/"
    echo ""
    echo "      Quick install on Ubuntu:"
    echo "        curl -fsSL https://get.docker.com | sh"
    echo "        sudo usermod -aG docker \$USER"
    exit 1
fi

if command -v docker compose &> /dev/null; then
    echo "      ✅ Docker Compose found"
elif command -v docker-compose &> /dev/null; then
    echo "      ✅ docker-compose found (legacy)"
else
    echo "      ❌ Docker Compose not found!"
    echo "      Install: https://docs.docker.com/compose/install/"
    exit 1
fi

# ---- Step 3: Check Flutter (optional) ----
echo "[3/4] Checking Flutter (optional, for mobile app)..."
if command -v flutter &> /dev/null; then
    echo "      ✅ Flutter found: $(flutter --version | head -1)"
else
    echo "      ⚠️  Flutter not found — needed only for mobile app development"
    echo "      Install: https://docs.flutter.dev/get-started/install"
fi

# ---- Step 4: Summary ----
echo "[4/4] Setup complete!"
echo ""
echo "============================================="
echo " Next Steps:"
echo "============================================="
echo ""
echo "  1. Edit .env with your credentials (PayPal, Firebase, etc.)"
echo ""
echo "  2. Start the Odoo backend + database:"
echo "       docker compose up -d"
echo ""
echo "  3. Open the Odoo admin dashboard:"
echo "       http://localhost:8069"
echo ""
echo "  4. Install the Cosmetics Store module:"
echo "       - Log in with admin/admin"
echo "       - Go to Apps → Update Apps List"
echo "       - Search for 'Cosmetics Store'"
echo "       - Click Install"
echo ""
echo "  5. (Optional) Run the Flutter app:"
echo "       cd flutter_app"
echo "       flutter pub get"
echo "       flutter run"
echo ""
echo "  See README.md for full documentation."
echo "============================================="
