#!/usr/bin/env bash
set -euo pipefail
# Simple script to install dev tools (if not already installed) and run automated fixes.
# Usage: from repo root: ./scripts/format.sh

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$ROOT_DIR"

echo "Installing dev tools (ruff, black, isort, autoflake) into the active environment..."
# Find a python executable (try `python` then `python3`), fail with a helpful message if none found
if command -v python >/dev/null 2>&1; then
	PYTHON=python
elif command -v python3 >/dev/null 2>&1; then
	PYTHON=python3
else
	echo "Error: Python 3 is not installed or 'python'/'python3' is not in PATH."
	echo "Install Python 3 or activate a virtualenv. Example (Debian/Ubuntu):"
	echo "  sudo apt update && sudo apt install -y python3 python3-venv python3-pip"
	exit 1
fi

$PYTHON -m pip install --upgrade pip
$PYTHON -m pip install --no-deps ruff black isort autoflake

echo "Normalizing leading tabs to 4 spaces in Python files (safe: only leading tabs are replaced)..."
$PYTHON - <<'PY'
from pathlib import Path
for p in Path('.').rglob('*.py'):
	text = p.read_text()
	new_lines = []
	changed = False
	for line in text.splitlines(True):
		# count leading tabs only and replace with 4 spaces each
		i = 0
		while i < len(line) and line[i] == '\t':
			i += 1
		if i:
			line = ' ' * (4 * i) + line[i:]
			changed = True
		new_lines.append(line)
	if changed:
		p.write_text(''.join(new_lines))
PY

echo "Running ruff --fix ..."
ruff --fix . || true

echo "Running isort ..."
isort . || true

echo "Running black ..."
black . || true

echo "Done. You can run 'flake8 .' to see remaining lint issues (if any)."
