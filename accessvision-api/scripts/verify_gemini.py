#!/usr/bin/env python3
"""Testa GEMINI_API_KEY e modelo. Uso: cd accessvision-api && python scripts/verify_gemini.py"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

import httpx

from app.config import settings


def main() -> None:
    if not settings.gemini_api_key:
        print("ERRO: GEMINI_API_KEY vazia no .env")
        return

    r = httpx.get(
        "https://generativelanguage.googleapis.com/v1beta/models",
        params={"key": settings.gemini_api_key},
        timeout=30,
    )
    print(f"Listar modelos: HTTP {r.status_code}")
    if r.status_code != 200:
        print(r.json().get("error", {}).get("message", r.text[:300]))
        print("\n→ Crie uma chave nova em https://aistudio.google.com/apikey")
        return

    model = settings.gemini_model_id
    names = [m["name"].replace("models/", "") for m in r.json().get("models", [])]
    if model not in names:
        print(f"AVISO: '{model}' não está na lista. Sugestões com 'flash':")
        for n in sorted(names):
            if "flash" in n:
                print(f"  - {n}")
    else:
        print(f"OK: modelo '{model}' disponível para esta chave.")


if __name__ == "__main__":
    main()
