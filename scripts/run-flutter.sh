#!/usr/bin/env bash
# =============================================================
# Run the Flutter mobile app
# =============================================================
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_DIR="$(dirname "$SCRIPT_DIR")"
FLUTTER_DIR="$PROJECT_DIR/flutter_app"

echo "============================================="
echo " Cosmetics Store — Flutter App"
echo "============================================="

# Check Flutter is installed
if ! command -v flutter &> /dev/null; then
    echo "❌ Flutter not found!"
    echo "Install Flutter: https://docs.flutter.dev/get-started/install"
    exit 1
fi

cd "$FLUTTER_DIR"

echo ""
echo "Fetching dependencies..."
flutter pub get

echo ""
echo "Running Flutter app..."
flutter run "$@"
