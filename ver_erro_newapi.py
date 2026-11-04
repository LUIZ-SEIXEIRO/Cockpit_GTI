# -*- coding: utf-8 -*-
import json, urllib.request, urllib.error

url = "http://10.20.40.212:3001/v1/chat/completions"
chave = "sk-CmqHIGhOuIW1lnPO0MTnLbzeoFERorWpvELyAhgvgp0ynRpn"

payload = {
    "model": "deepseek-r1:14b",
    "messages": [{"role": "user", "content": "teste"}],
    "max_tokens": 10
}

req = urllib.request.Request(url, data=json.dumps(payload).encode("utf-8"), headers={"Authorization": f"Bearer {chave}", "Content-Type": "application/json"})
try:
    with urllib.request.urlopen(req, timeout=5) as resp:
        print("[OK]", resp.read().decode())
except urllib.error.HTTPError as e:
    corpo = e.read().decode("utf-8")
    print(f"[STATUS HTTP {e.code}] Mensagem interna da New API:")
    print(corpo)
except Exception as e:
    print(f"[ERRO GERAL]: {e}")
