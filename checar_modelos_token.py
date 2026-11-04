# -*- coding: utf-8 -*-
import sys, json, urllib.request

chave = sys.argv[1]
url_models = "http://10.20.40.212:3001/v1/models"

print("=" * 70)
print(f" MODELOS PERMITIDOS PARA ESTE TOKEN NA NEW API:")
print("=" * 70)
try:
    req = urllib.request.Request(url_models, headers={"Authorization": f"Bearer {chave}"})
    with urllib.request.urlopen(req, timeout=4) as resp:
        res = json.loads(resp.read().decode("utf-8"))
        modelos = [m.get("id") for m in res.get("data", [])]
        print(f"[OK] Total de modelos liberados para este token: {len(modelos)}")
        print(f"Lista de modelos liberados: {modelos}")
except Exception as e:
    print(f"[ERRO]: {e}")
print("=" * 70)
