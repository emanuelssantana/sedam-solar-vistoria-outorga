# -*- coding: utf-8 -*-
"""
Testador de Conectividade Mesh Tailscale e Contingencia SEDAM M:\\
Executar em qualquer host (Dell G3 ou A320MH) para validar se a rede esta 100%
"""
import subprocess
import os
import sys

print("=== VERIFICANDO CONECTIVIDADE TAILSCALE & REDE SEDAM ===")

# 1. Tailscale status
try:
    res = subprocess.run(["tailscale", "status"], capture_output=True, text=True, errors="replace", check=True)
    print("[OK] Tailscale ativo:")
    for line in res.stdout.splitlines()[:5]:
        print("  ", line)
except Exception as e:
    print("[ERRO] Tailscale nao encontrado ou inativo:", e)

# 2. Tailscale IPs
try:
    ip = subprocess.run(["tailscale", "ip", "-4"], capture_output=True, text=True, errors="replace").stdout.strip()
    print(f"\n[OK] Meu IP Tailscale IPv4: {ip}")
except Exception as e:
    print("[AVISO] Nao foi possivel obter IP:", e)

# 3. Teste de ping para peers conhecidos
peers = [
    ("Dell G3 Notebook", "100.84.144.1"),
    ("Desktop A320MH", "100.68.232.83")
]
print("\n--- Teste de Ping Mesh ---")
for name, peer_ip in peers:
    res_ping = subprocess.run(["ping", "-n", "1", "-w", "1000", peer_ip], capture_output=True, text=True, errors="replace")
    if res_ping.returncode == 0:
        print(f"  [CONECTADO] {name} ({peer_ip}) - Ping OK")
    else:
        print(f"  [OFFLINE / SEM RESPOSTA] {name} ({peer_ip})")

# 4. Verificacao da Unidade M:\
print("\n--- Verificacao de Armazenamento SEDAM ---")
if os.path.exists("M:\\"):
    print("[CONECTADO] Unidade M:\\ acessivel! Servidor 172.16.6.10 disponivel.")
    try:
        itens = os.listdir("M:\\")
        print(f"  Pastas raiz encontradas em M:\\: {itens[:6]}")
    except Exception as e:
        print("  Erro ao listar raiz de M:\\:", e)
else:
    print("[DESCONECTADO] Unidade M:\\ offline. Use o cache local em G:\\Meu Drive\\...\\BASES_INDEXADAS_GERAIS\\")

print("\n[FIM DO DIAGNOSTICO]")
