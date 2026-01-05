#!/usr/bin/env python3
"""Genera tokens para los autores configurados y guarda en secrets.json.

Uso:
  .\venv\Scripts\Activate.ps1
  python scripts/generate_tokens.py

El archivo `secrets.json` se crea/actualiza en la raíz del proyecto.
"""
import json
import sys
from datetime import datetime, timezone
from pathlib import Path

# ensure project root is on sys.path so `import app` works
ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from app.auth import generate_token
from app.config import AUTHORS


OUT = ROOT / "secrets.json"


def main():
    data = {}
    now = datetime.now(timezone.utc).isoformat()
    for a in AUTHORS:
        t = generate_token(a)
        data[a] = {"token": t, "created_at": now}

    with OUT.open("w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

    print("Saved tokens to", OUT)


if __name__ == "__main__":
    main()
