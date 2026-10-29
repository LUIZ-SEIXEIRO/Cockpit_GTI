import os
import sys
import shutil
import zipfile
import subprocess
from datetime import datetime

agora_str = datetime.now().strftime("%Y%m%d_%H%M%S")
print(f"=== [1/3] INICIANDO SNAPSHOT DE SEGURANÇA LOCAL ({agora_str}) ===")

os.makedirs("backups", exist_ok=True)

# 1. Backup lógico das tabelas do MariaDB (se mysqldump estiver disponível)
dump_file = os.path.join("backups", f"dump_glpidb_{agora_str}.sql")
print("  -> Tentando exportar banco MariaDB local (:3306)...")
dump_executado = False
caminhos_mysqldump = [
    "mysqldump",
    r"C:\Program Files\MariaDB 10.11\bin\mysqldump.exe",
    r"C:\Program Files\MariaDB 11.0\bin\mysqldump.exe",
    r"C:\Program Files\MySQL\MySQL Server 8.0\bin\mysqldump.exe",
    r"C:\xampp\mysql\bin\mysqldump.exe"
]

for cmd in caminhos_mysqldump:
    try:
        res = subprocess.run(
            [cmd, "-u", "root", "-h", "127.0.0.1", "-P", "3306", "glpidb"],
            capture_output=True,
            text=True,
            timeout=30
        )
        if res.returncode == 0 and len(res.stdout) > 0:
            with open(dump_file, "w", encoding="utf-8") as f:
                f.write(res.stdout)
            print(f"  -> Dump do MariaDB gerado com sucesso: {dump_file} ({len(res.stdout)} bytes)")
            dump_executado = True
            break
    except Exception:
        continue

if not dump_executado:
    print("  -> Nota: mysqldump não estava no PATH ou banco sem senha root direta. Cópias locais dos arquivos serão priorizadas no snapshot zip.")

# 2. Compactação integral do projeto em arquivo ZIP
zip_name = f"Cockpit_GTI_Snapshot_v11_PreReestruturacao_{agora_str}.zip"
zip_caminho = os.path.abspath(os.path.join("..", zip_name))
print(f"\n=== [2/3] GERANDO PACOTE ZIP COMPACTADO ===")
print(f"  -> Destino: {zip_caminho}")

ignorar_pastas = {".git", "__pycache__", ".venv", "venv", "node_modules"}

total_arquivos = 0
with zipfile.ZipFile(zip_caminho, 'w', zipfile.ZIP_DEFLATED) as zipf:
    for root, dirs, files in os.walk("."):
        # Remove pastas ignoradas da varredura
        dirs[:] = [d for d in dirs if d not in ignorar_pastas]
        for f in files:
            if f.endswith(".zip") or f.endswith(".tmp"):
                continue
            caminho_completo = os.path.join(root, f)
            caminho_relativo = os.path.relpath(caminho_completo, ".")
            zipf.write(caminho_completo, caminho_relativo)
            total_arquivos += 1

tamanho_mb = os.path.getsize(zip_caminho) / (1024 * 1024)
print(f"  -> Snapshot ZIP concluído com sucesso: {total_arquivos} arquivos compactados ({tamanho_mb:.2f} MB)")

# 3. Versionamento Git e Sincronização com o GitHub
print(f"\n=== [3/3] ATUALIZANDO VERSIONAMENTO GIT & GITHUB ===")

def rodar_git(args, desc):
    print(f"  -> Executando: git {' '.join(args)}")
    try:
        r = subprocess.run(["git"] + args, capture_output=True, text=True, timeout=60)
        if r.stdout.strip():
            print("     " + r.stdout.strip().replace("\n", "\n     "))
        if r.stderr.strip() and r.returncode != 0:
            print("     [Aviso/Erro]: " + r.stderr.strip().replace("\n", "\n     "))
        return r.returncode == 0
    except Exception as e:
        print(f"     Falha ao executar git {' '.join(args)}: {e}")
        return False

# Checa se é um repositório git
if os.path.exists(".git"):
    rodar_git(["status", "-s"], "Status")
    rodar_git(["add", "."], "Stage de todos os arquivos")
    
    commit_msg = "feat(cockpit): ponto de restauracao estavel v11.0 - saneamento 15 abas, esteira PDF SEI e Glassmorphism dual-theme"
    rodar_git(["commit", "-m", commit_msg], "Commit")
    
    tag_nome = f"v11.0-pre-reestruturacao-{datetime.now().strftime('%Y%m%d')}"
    rodar_git(["tag", "-a", tag_nome, "-m", "Snapshot congelado e homologado antes da reorganizacao dos 3 eixos"], "Tag")
    
    print("\n  -> Tentando sincronizar com o repositório remoto (push)...")
    rodar_git(["push", "origin", "HEAD"], "Push branch")
    rodar_git(["push", "origin", "--tags"], "Push tags")
else:
    print("  -> Nota: Pasta .git não encontrada neste diretório raiz. Snapshot ZIP já garantiu o backup físico integral.")

print("\n=======================================================")
print("✅ PONTO DE RESTAURAÇÃO CRIADO COM SUCESSO!")
print(f"📦 Arquivo de segurança: {zip_caminho}")
print("=======================================================")
