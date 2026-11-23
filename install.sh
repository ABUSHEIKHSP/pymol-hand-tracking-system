#!/usr/bin/env bash
set -euo pipefail

PROJECT_DIR="$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")" && pwd)"
cd "$PROJECT_DIR"

PYTHON_BIN="${PYTHON:-python3}"

if ! command -v "$PYTHON_BIN" >/dev/null 2>&1; then
    echo "Error: $PYTHON_BIN was not found. Install Python 3 or set PYTHON=/path/to/python3."
    exit 1
fi

if ! command -v curl >/dev/null 2>&1; then
    echo "Error: curl is required to download the MediaPipe model."
    exit 1
fi

if [[ ! -d ".venv" ]]; then
    echo "Creating virtual environment..."
    "$PYTHON_BIN" -m venv .venv
fi

# Activate the project-local environment for all dependency installation.
# shellcheck disable=SC1091
source ".venv/bin/activate"

echo "Installing Python dependencies..."
python -m pip install --upgrade pip
python -m pip install -r requirements.txt

MODEL_FILE="gesture_recognizer.task"
MODEL_URL="https://storage.googleapis.com/mediapipe-models/gesture_recognizer/gesture_recognizer/float16/1/gesture_recognizer.task"

if [[ ! -s "$MODEL_FILE" ]]; then
    echo "Downloading MediaPipe Gesture Recognizer model..."
    curl --fail --location --progress-bar "$MODEL_URL" --output "${MODEL_FILE}.tmp"
    mv "${MODEL_FILE}.tmp" "$MODEL_FILE"
else
    echo "MediaPipe model already exists; skipping download."
fi

echo
echo "Setup complete."
echo "Next:"
echo "  1. Start PyMOL with: pymol -R"
echo "  2. In another terminal, run: bash run.sh"
