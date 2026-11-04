import os
import shutil
import re
import json
import sqlite3

print("🚀 Iniciando implantação da Fase 2: Login & RBAC Escalonado...")

# 1. Configurar Base de Usuários (MariaDB com Fallback JSON/SQLite)
caminho_dados = r"C:\Cockpit_GTI\data"
os.makedirs(caminho_dados, exist_ok=True)
arquivo_usuarios = os.path.join(caminho_dados, "usuarios_cockpit.json")

usuarios_iniciais = [
    {
        "id": 1,
        "nome": "Luiz Antonio Seixeiro",
        "email": "luiz.seixeiro@spaguas.sp.gov.br",
        "matricula": "SP-00197",
        "senha": "admin", # Pode alterar para a senha que desejar
        "nivel": "SUPER_ADMIN",
        "diretoria": "todas",
        "cargo": "Gestor de Projetos Sênior / Governança SA-GTI"
    },
    {
        "id": 2,
        "nome": "Diretoria Administrativa",
        "email": "gestor.sa@spaguas.sp.gov.br",
        "matricula": "SP-00102",
        "senha": "gestor123",
        "nivel": "GESTOR",
        "diretoria": "spaguas-sa",
        "cargo": "Superintendente Administrativo"
    },
    {
        "id": 3,
        "nome": "Analista Técnico DIF/DGD",
        "email": "analista.gti@spaguas.sp.gov.br",
        "matricula": "SP-00155",
        "senha": "analista123",
        "nivel": "ANALISTA",
        "diretoria": "spaguas-sa-gti",
        "cargo": "Analista de Tecnologia da Informação"
    },
    {
        "id": 4,
        "nome": "Demandante Bacias (UGRHI)",
        "email": "demandante.bacias@spaguas.sp.gov.br",
        "matricula": "SP-00210",
        "senha": "consulta123",
        "nivel": "DEMANDANTE",
        "diretoria": "spaguas-sd",
        "cargo": "Técnico de Recursos Hídricos"
    }
]

with open(arquivo_usuarios, "w", encoding="utf-8") as f:
    json.dump(usuarios_iniciais, f, indent=4, ensure_ascii=False)
print(f"✅ Base de usuários inicial gravada em: {arquivo_usuarios}")

# Tentar gravar no MariaDB se disponível
try:
    import pymysql
    conn = pymysql.connect(host="127.0.0.1", port=3306, user="root", password="", database="glpidb", autocommit=True)
    with conn.cursor() as cur:
        cur.execute("""
            CREATE TABLE IF NOT EXISTS usuarios_cockpit (
                id INT AUTO_INCREMENT PRIMARY KEY,
                nome VARCHAR(150) NOT NULL,
                email VARCHAR(150) NOT NULL UNIQUE,
                matricula VARCHAR(40) UNIQUE,
                senha VARCHAR(100) NOT NULL,
                nivel VARCHAR(40) NOT NULL,
                diretoria VARCHAR(40) NOT NULL,
                cargo VARCHAR(150),
                ativo TINYINT(1) DEFAULT 1,
                criado_em TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;
        """)
        for u in usuarios_iniciais:
            cur.execute("""
                INSERT INTO usuarios_cockpit (id, nome, email, matricula, senha, nivel, diretoria, cargo)
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
                ON DUPLICATE KEY UPDATE nome=%s, senha=%s, nivel=%s, diretoria=%s, cargo=%s;
            """, (u["id"], u["nome"], u["email"], u["matricula"], u["senha"], u["nivel"], u["diretoria"], u["cargo"],
                  u["nome"], u["senha"], u["nivel"], u["diretoria"], u["cargo"]))
    conn.close()
    print("✅ Tabela usuarios_cockpit sincronizada no MariaDB (:3306 glpidb)!")
except Exception as e:
    print(f"ℹ️ MariaDB não conectado diretamente (usando fallback JSON): {e}")

# 2. Injetar a Tela de Login e Lógica de Sessão no painel.html
painel_path = r"C:\Cockpit_GTI\frontend\painel.html"
backup_path = painel_path + ".bak_fase2_login"
shutil.copy(painel_path, backup_path)
print(f"📦 Backup criado: {backup_path}")

with open(painel_path, "r", encoding="utf-8", errors="ignore") as f:
    html = f.read()

bloco_login_html = """
<!-- ======================================================== -->
<!-- TELA DE LOGIN INSTITUCIONAL GLASSMORPHISM (FASE 2 RBAC) -->
<!-- ======================================================== -->
<div id="view-login-gate" style="display: none; position: fixed; top: 0; left: 0; width: 100vw; height: 100vh; z-index: 99999; background: #090d16; background-image: radial-gradient(at 15% 15%, rgba(5,68,207,0.3) 0px, transparent 50%), radial-gradient(at 85% 85%, rgba(124,58,237,0.25) 0px, transparent 50%); align-items: center; justify-content: center;">
    <div style="width: 440px; max-width: 90vw; background: rgba(15, 23, 42, 0.75); backdrop-filter: blur(24px); -webkit-backdrop-filter: blur(24px); border: 1px solid rgba(255, 255, 255, 0.14); border-radius: 18px; box-shadow: 0 16px 48px 0 rgba(0, 0, 0, 0.5); padding: 36px 32px; text-align: center; color: #ffffff;">
        <div style="display: flex; justify-content: center; align-items: center; gap: 10px; margin-bottom: 12px;">
            <img src="" data-spaguas-logo="1" alt="SP-Águas" style="height: 38px; width: auto; object-fit: contain;">
        </div>
        <h2 style="font-size: 18px; font-weight: 800; letter-spacing: 0.5px; margin: 0 0 4px 0; color: #ffffff;">COCKPIT GTI • SP-ÁGUAS</h2>
        <p style="font-size: 11.5px; color: #94a3b8; margin: 0 0 24px 0;">Plataforma de Governança, Processos SEI & Orquestração Multi-IA</p>

        <form id="form-cockpit-login" onsubmit="window.executarLoginCockpit(event)" style="text-align: left;">
            <div style="margin-bottom: 16px;">
                <label style="font-size: 11px; font-weight: 700; color: #cbd5e1; text-transform: uppercase; letter-spacing: 0.5px; display: block; margin-bottom: 6px;">E-mail ou Matrícula:</label>
                <input type="text" id="login-input-usuario" value="luiz.seixeiro@spaguas.sp.gov.br" required style="width: 100%; box-sizing: border-box; padding: 11px 14px; background: rgba(255, 255, 255, 0.06); border: 1px solid rgba(255, 255, 255, 0.15); border-radius: 8px; color: #ffffff; font-size: 12.5px; outline: none; transition: all 0.2s ease;">
            </div>

            <div style="margin-bottom: 20px;">
                <label style="font-size: 11px; font-weight: 700; color: #cbd5e1; text-transform: uppercase; letter-spacing: 0.5px; display: block; margin-bottom: 6px;">Senha de Acesso:</label>
                <div style="position: relative;">
                    <input type="password" id="login-input-senha" value="admin" required style="width: 100%; box-sizing: border-box; padding: 11px 40px 11px 14px; background: rgba(255, 255, 255, 0.06); border: 1px solid rgba(255, 255, 255, 0.15); border-radius: 8px; color: #ffffff; font-size: 12.5px; outline: none;">
                    <button type="button" onclick="window.alternarVisibilidadeSenhaLogin()" style="position: absolute; right: 10px; top: 50%; transform: translateY(-50%); background: transparent; border: none; color: #94a3b8; cursor: pointer; font-size: 14px;">👁️</button>
                </div>
            </div>

            <button type="submit" style="width: 100%; padding: 12px; background: linear-gradient(135deg, #4f46e5 0%, #2563eb 100%); border: 1px solid rgba(96, 165, 250, 0.5); border-radius: 8px; color: #ffffff; font-size: 13px; font-weight: 800; cursor: pointer; box-shadow: 0 4px 16px rgba(37, 99, 235, 0.4); transition: transform 0.2s ease;">
                🔐 ACESSAR COCKPIT GTI
            </button>
        </form>

        <div id="login-alerta-erro" style="display: none; margin-top: 14px; padding: 10px; border-radius: 6px; background: rgba(239, 68, 68, 0.15); border: 1px solid #f87171; color: #fca5a5; font-size: 11.5px;"></div>

        <div style="margin-top: 24px; padding-top: 16px; border-top: 1px solid rgba(255, 255, 255, 0.08); font-size: 10.5px; color: #64748b;">
            Autenticação Segura • Acesso Escalonado por Perfil (RBAC) & Diretoria
        </div>
    </div>
</div>

<script id="script-auth-rbac-v11">
(function() {
    window.usuariosMockados = """ + json.dumps(usuarios_iniciais, ensure_ascii=False) + """;

    window.obterUsuarioSessao = function() {
        try {
            var raw = localStorage.getItem("cockpit_usuario_ativo");
            return raw ? JSON.parse(raw) : null;
        } catch(e) { return null; }
    };

    window.salvarUsuarioSessao = function(user) {
        localStorage.setItem("cockpit_usuario_ativo", JSON.stringify(user));
    };

    window.limparUsuarioSessao = function() {
        localStorage.removeItem("cockpit_usuario_ativo");
        window.location.reload();
    };

    window.alternarVisibilidadeSenhaLogin = function() {
        var inp = document.getElementById("login-input-senha");
        if (inp) inp.type = (inp.type === "password") ? "text" : "password";
    };

    window.executarLoginCockpit = function(ev) {
        if (ev) ev.preventDefault();
        var emailOuMatricula = (document.getElementById("login-input-usuario").value || "").trim().toLowerCase();
        var senha = document.getElementById("login-input-senha").value;
        var alerta = document.getElementById("login-alerta-erro");

        var user = window.usuariosMockados.find(function(u) {
            return (u.email.toLowerCase() === emailOuMatricula || u.matricula.toLowerCase() === emailOuMatricula) && u.senha === senha;
        });

        if (user) {
            if (alerta) alerta.style.display = "none";
            window.salvarUsuarioSessao(user);
            window.aplicarPermissoesUsuarioLogado(user);
            var gate = document.getElementById("view-login-gate");
            if (gate) gate.style.setProperty("display", "none", "important");
        } else {
            if (alerta) {
                alerta.innerText = "❌ Credenciais inválidas. Verifique seu e-mail/matrícula e senha.";
                alerta.style.display = "block";
            }
        }
    };

    window.aplicarPermissoesUsuarioLogado = function(user) {
        if (!user) return;
        
        // 1. Atualizar informações de perfil no Header/Sidebar
        var selectPerfil = document.getElementById("select-perfil-ativo");
        if (selectPerfil) selectPerfil.value = user.nivel === "SUPER_ADMIN" ? "Super-Admin" : (user.nivel === "GESTOR" ? "Gestor" : (user.nivel === "ANALISTA" ? "Analista" : "Demandante"));

        var selectDir = document.getElementById("select-diretoria-spaguas");
        if (selectDir && user.diretoria !== "todas") selectDir.value = user.diretoria;

        // Injetar badge do usuário logado na Sidebar com botão de Sair
        var userBadgeContainer = document.getElementById("sidebar-user-session-badge");
        if (!userBadgeContainer) {
            var sidebar = document.getElementById("sidebar");
            if (sidebar) {
                userBadgeContainer = document.createElement("div");
                userBadgeContainer.id = "sidebar-user-session-badge";
                userBadgeContainer.style.cssText = "padding: 12px 14px; margin: 12px; background: rgba(255,255,255,0.06); border: 1px solid rgba(255,255,255,0.12); border-radius: 10px; font-size: 11px; color: #cbd5e1;";
                sidebar.appendChild(userBadgeContainer);
            }
        }
        if (userBadgeContainer) {
            userBadgeContainer.innerHTML = 
                '<div style="font-weight: 800; color: #ffffff; display: flex; align-items: center; gap: 6px;">' +
                    '<span>👤</span> <span style="white-space: nowrap; overflow: hidden; text-overflow: ellipsis;">' + user.nome + '</span>' +
                '</div>' +
                '<div style="font-size: 10px; color: #94a3b8; margin: 3px 0 8px 0;">' + user.cargo + ' (' + user.nivel + ')</div>' +
                '<button type="button" onclick="window.limparUsuarioSessao()" style="width: 100%; padding: 5px; background: rgba(239,68,68,0.2); border: 1px solid rgba(248,113,113,0.4); border-radius: 6px; color: #fca5a5; font-size: 10px; font-weight: 700; cursor: pointer;">🚪 Sair (Logout)</button>';
        }

        // 2. Bloqueio de Abas por Nível RBAC
        var itemConfig = document.querySelector('#sidebar .nav-item[data-tab="configuracoes"]');
        if (itemConfig) {
            itemConfig.style.display = (user.nivel === "SUPER_ADMIN") ? "flex" : "none";
        }
    };

    // Checar sessão ao carregar
    window.addEventListener("DOMContentLoaded", function() {
        var sessao = window.obterUsuarioSessao();
        var gate = document.getElementById("view-login-gate");
        if (!sessao) {
            if (gate) gate.style.setProperty("display", "flex", "important");
        } else {
            if (gate) gate.style.setProperty("display", "none", "important");
            window.aplicarPermissoesUsuarioLogado(sessao);
        }
    });
})();
</script>
"""

# Remover injeção anterior se houver
html = re.sub(r'<!-- ===.*?TELA DE LOGIN INSTITUCIONAL GLASSMORPHISM.*?<\/script>', '', html, flags=re.DOTALL)

# Injetar logo antes de </body>
if "</body>" in html:
    idx = html.rfind("</body>")
    html = html[:idx] + "\n" + bloco_login_html + "\n" + html[idx:]
else:
    html = html + "\n" + bloco_login_html

tmp_path = painel_path + ".tmp"
with open(tmp_path, "w", encoding="utf-8", errors="ignore") as f:
    f.write(html)

shutil.move(tmp_path, painel_path)
print("✅ Tela de Login Glassmorphism e RBAC integrados com sucesso no painel.html!")
print("\n👉 Pressione F5 no navegador para visualizar a Tela de Login da SP-Águas!")
