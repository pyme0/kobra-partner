#!/usr/bin/env bash
set -euo pipefail
ROOT="$(cd "$(dirname "$0")/.." && pwd)"
cd "$ROOT"
python -m pip install -q -U build twine
rm -rf dist build src/*.egg-info
python -m build
python -m twine check dist/*
if [[ -n "${TWINE_PASSWORD:-}${PYPI_API_TOKEN:-}" ]]; then
  export TWINE_USERNAME="${TWINE_USERNAME:-__token__}"
  export TWINE_PASSWORD="${TWINE_PASSWORD:-$PYPI_API_TOKEN}"
  python -m twine upload dist/*
  echo "published to PyPI"
else
  echo "FALLO: defina PYPI_API_TOKEN o TWINE_PASSWORD (token pypi)" >&2
  exit 1
fi
