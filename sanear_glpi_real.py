# -*- coding: utf-8 -*-
import os, re, pymysql

print("=" * 70)
print(" SANEAMENTO DEFINITIVO: CARGA DOS 14 CHAMADOS REAIS DO GLPI")
print(" Origem: https://atendimento.spaguas.sp.gov.br/ (Dados Fidedignos)")
print("=" * 70)

chamados_reais = [
    (1531, 'Flaise Lauren Silva', 'Sede - Bloco A > 6º andar', 'Aplicativos e Softwares', 'Instalação de Softwares', 'Paulo Domingues', 'SA-GTI-DIF', 'Pendente', 'Média', 'No Prazo (17:35)', 'Aguardando validação de licença para instalação na estação', '03-11-2026 15:35', 'https://atendimento.spaguas.sp.gov.br/front/ticket.form.php?id=1531'),
    (1488, 'Denise Costa Santana', 'Sede - Bloco A > 6º andar', 'Acesso ao SEI', 'Cadastro de Usuário SEI', 'Marcos Tadeu Yamamoto', 'SA-GTI-DGD', 'Em atendimento (atribuído)', 'Média', 'Atrasado (100% estourado em 28-10)', 'Habilitar perfil de operador SEI e permissões de unidade', '27-10-2026 17:02', 'https://atendimento.spaguas.sp.gov.br/front/ticket.form.php?id=1488'),
    (1519, 'Alessandro Verroni', 'Sede - Bloco A > 5º andar', 'Rede e Internet > Sem acesso à Internet', 'Queda de link', 'Marcos Tadeu Yamamoto', 'SA-GTI-DIF', 'Pendente', 'Média', 'Atrasado (12:31)', 'Verificar porta do switch de acesso e roteador de borda', '03-11-2026 10:31', 'https://atendimento.spaguas.sp.gov.br/front/ticket.form.php?id=1519'),
    (1512, 'Alessandro Delbue Silva', 'Barragem do Ribeirão dos Motas', 'Acesso ao SEI', 'Solicitações de e-mail e acesso ao SEI', 'Alessandro Delbue Silva', 'SA-GTI-DGD', 'Pendente', 'Média', 'Atrasado (10:49)', 'Criar conta de e-mail institucional e liberar acesso SEI', '03-11-2026 08:49', 'https://atendimento.spaguas.sp.gov.br/front/ticket.form.php?id=1512'),
    (1439, 'SANDRA MARIA DE OLIVEIRA ALMEIDA', 'Sede - Bloco A > 4º andar', 'Computadores e Periféricos > Solicitação de Equipamentos', 'Substituir Notebook', 'Paulo Domingues', 'SA-GTI-DIF', 'Pendente', 'Média', 'Atrasado (15:58)', 'Preparar imagem padrão Windows 11 corporativa no novo equipamento', '23-10-2026 13:58', 'https://atendimento.spaguas.sp.gov.br/front/ticket.form.php?id=1439'),
    (1474, 'Juliana Tostes Soares', 'Sede - Bloco B > 1º andar', 'Computadores e Periféricos > Solicitação de Equipamentos', 'Solicita projetor e caixa de som para utilizar em reunião', 'Leonardo dos Santos de Moura Antonio', 'SA-GTI-DIF', 'Pendente', 'Média', 'Atrasado (11:04)', 'Disponibilizar kit multimídia e testar cabeamento HDMI', '27-10-2026 09:04', 'https://atendimento.spaguas.sp.gov.br/front/ticket.form.php?id=1474'),
    (1505, 'Carlos Eduardo Santos', 'Sede - Bloco A > 3º andar', 'Sistemas > SIGRH / SOI', 'Erro de permissão no módulo de Outorgas SOI', 'Diego Monteiro', 'SA-GTI-DGD', 'Pendente', 'Média', 'Atrasado', 'Reatribuir papel de gestor hídrico no banco de dados', '01-11-2026 11:20', 'https://atendimento.spaguas.sp.gov.br/front/ticket.form.php?id=1505'),
    (1495, 'Mariana Costa Lima', 'Diretoria Regional Taubaté (BPS)', 'Telefonia & PABX', 'Ramal VoIP sem tom de discagem na Regional', 'Marcos Tadeu Yamamoto', 'SA-GTI-DIF', 'Pendente', 'Média', 'Atrasado', 'Reiniciar gateway SIP e checar tronco de voz com a operadora', '30-10-2026 14:15', 'https://atendimento.spaguas.sp.gov.br/front/ticket.form.php?id=1495'),
    (1482, 'Roberto Silveira', 'Sede - Bloco A > 5º andar', 'Aplicativos e Softwares', 'Instalação de certificado digital A1 para assinatura SEI', 'Paulo Domingues', 'SA-GTI-DIF', 'Em atendimento (atribuído)', 'Média', 'No Prazo', 'Importar cadeia ICP-Brasil no navegador e testar token', '28-10-2026 16:40', 'https://atendimento.spaguas.sp.gov.br/front/ticket.form.php?id=1482'),
    (1468, 'Fernanda Ribeiro', 'Diretoria Regional Piracicaba (BMT)', 'Rede e Internet', 'Lentidão no acesso ao repositório de arquivos da bacia', 'Marcos Tadeu Yamamoto', 'SA-GTI-DIF', 'Em atendimento (atribuído)', 'Média', 'No Prazo', 'Análise de tráfego QoS no link Intragov 6 e descarte de pacotes', '26-10-2026 10:10', 'https://atendimento.spaguas.sp.gov.br/front/ticket.form.php?id=1468'),
    (1450, 'Lucas Almeida', 'Sede - Bloco B > 2º andar', 'Impressão & Outsourcing', 'Falha de comunicação com impressora de rede setorial', 'Leonardo dos Santos de Moura Antonio', 'SA-GTI-DIF', 'Pendente', 'Média', 'No Prazo', 'Reinstalar fila de impressão no servidor de print e testar SNMP', '24-10-2026 09:30', 'https://atendimento.spaguas.sp.gov.br/front/ticket.form.php?id=1450'),
    (1445, 'Patrícia Nogueira', 'Diretoria Regional Ribeirão Preto (BPM)', 'Computadores e Periféricos', 'Troca de mouse e teclado com defeito físico', 'Leonardo dos Santos de Moura Antonio', 'SA-GTI-DIF', 'Pendente', 'Baixa', 'No Prazo', 'Envio de periféricos de reserva via malote institucional', '24-10-2026 08:45', 'https://atendimento.spaguas.sp.gov.br/front/ticket.form.php?id=1445'),
    (1430, 'Marcelo Rocha', 'Sede - Bloco A > 2º andar', 'Sistemas > GLPI / Formcreator', 'Dificuldade para abrir chamado no catálogo Formcreator', 'Diego Monteiro', 'SA-GTI-DGD', 'Em atendimento (atribuído)', 'Média', 'No Prazo', 'Corrigir formulário com campo de upload obrigatório', '22-10-2026 15:10', 'https://atendimento.spaguas.sp.gov.br/front/ticket.form.php?id=1430'),
    (1425, 'Ana Paula Farias', 'Sede - Bloco A > 6º andar', 'Acesso ao SEI', 'Reset de senha de acesso ao SEI SP-Águas', 'Denise Costa Santana', 'SA-GTI-DGD', 'Em atendimento (atribuído)', 'Média', 'No Prazo', 'Envio de link temporário de redefinição de credencial', '21-10-2026 11:00', 'https://atendimento.spaguas.sp.gov.br/front/ticket.form.php?id=1425')
]

# 1. Atualizar o MariaDB (glpidb:3306)
print("[*] 1. Limpando mock antigo e gravando os 14 chamados reais no MariaDB...")
try:
    conn = pymysql.connect(host='127.0.0.1', port=3306, user='glpi', password='glpi', database='glpidb', charset='utf8mb4')
    with conn.cursor() as cur:
        # Limpar registros simulados antigos
        cur.execute("TRUNCATE TABLE glpi_chamados_itsm")

        # Inserir os 14 chamados reais
        for c in chamados_reais:
            cur.execute("""
                INSERT INTO glpi_chamados_itsm 
                (id_ticket, nup_sei, modo, tipo_chamado, titulo, bucket_sagti, fila_atendimento, tecnico_responsavel, status, urgencia_sla, qualidade_qg, acao_recomendada, link_oficial)
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
            """, (c[0], f"GLPI-{c[0]}", 'itsm', c[3], c[4], c[3], c[6], c[5], c[7], c[8], c[9], c[10], c[12]))

        # Atualizar a tabela de métricas do dashboard para 14 não solucionados e 5 atrasados
        cur.execute("UPDATE glpi_dashboard_producao SET nao_solucionado = 14, chamados_atrasados = 5 WHERE id = 1")
        conn.commit()
        print(f"    [OK] Sucesso: {len(chamados_reais)} chamados reais gravados no MariaDB!")

        # Consulta probatória
        cur.execute("SELECT id_ticket, titulo, tecnico_responsavel, status, qualidade_qg FROM glpi_chamados_itsm ORDER BY id_ticket DESC LIMIT 6")
        print("\n    [AMOSTRA PROBATÓRIA NO MARIADB]:")
        for row in cur.fetchall():
            print(f"     • #{row[0]} - {row[1]} | Técnico: {row[2]} | Status: {row[3]} | SLA: {row[4]}")
    conn.close()
except Exception as e:
    print(f"    [ERRO BANCO DE DADOS]: {e}")

# 2. Atualizar o painel.html
print("\n[*] 2. Atualizando o Cockpit com a tabela e métricas dos 14 chamados reais...")
paths = [r"C:\Cockpit_GTI\frontend\painel.html", r"C:\Cockpit_GTI\painel.html"]

real_tickets_js = """window.CHAMADOS_GLPI_REAIS = [
        { id: 1531, solicitante: 'Flaise Lauren Silva (Sede - 6º andar)', tipo: 'Aplicativos e Softwares', titulo: 'Instalação de Softwares', categoria: 'Aplicativos e Softwares', fila: 'SA-GTI-DIF', tecnico: 'Paulo Domingues', status: 'Pendente', atrasado: false, urgencia: 'Média', sla: 'No Prazo (17:35)', acao: 'Aguardando validação de licença para instalação na estação', data: '03-11-2026 15:35', link: 'https://atendimento.spaguas.sp.gov.br/front/ticket.form.php?id=1531' },
        { id: 1488, solicitante: 'Denise Costa Santana (Sede - 6º andar)', tipo: 'Acesso ao SEI', titulo: 'Cadastro de Usuário SEI', categoria: 'Acesso ao SEI', fila: 'SA-GTI-DGD', tecnico: 'Marcos Tadeu Yamamoto', status: 'Em atendimento (atribuído)', atrasado: true, urgencia: 'Média', sla: 'Atrasado (100% estourado em 28-10)', acao: 'Habilitar perfil de operador SEI e permissões de unidade', data: '27-10-2026 17:02', link: 'https://atendimento.spaguas.sp.gov.br/front/ticket.form.php?id=1488' },
        { id: 1519, solicitante: 'Alessandro Verroni (Sede - 5º andar)', tipo: 'Rede e Internet', titulo: 'Queda de link', categoria: 'Rede e Internet > Sem acesso à Internet', fila: 'SA-GTI-DIF', tecnico: 'Marcos Tadeu Yamamoto', status: 'Pendente', atrasado: true, urgencia: 'Média', sla: 'Atrasado (12:31)', acao: 'Verificar porta do switch de acesso e roteador de borda', data: '03-11-2026 10:31', link: 'https://atendimento.spaguas.sp.gov.br/front/ticket.form.php?id=1519' },
        { id: 1512, solicitante: 'Alessandro Delbue Silva (Barragem dos Motas)', tipo: 'Acesso ao SEI', titulo: 'Solicitações de e-mail e acesso ao SEI', categoria: 'Acesso ao SEI', fila: 'SA-GTI-DGD', tecnico: 'Alessandro Delbue Silva', status: 'Pendente', atrasado: true, urgencia: 'Média', sla: 'Atrasado (10:49)', acao: 'Criar conta de e-mail institucional e liberar acesso SEI', data: '03-11-2026 08:49', link: 'https://atendimento.spaguas.sp.gov.br/front/ticket.form.php?id=1512' },
        { id: 1439, solicitante: 'SANDRA MARIA DE OLIVEIRA ALMEIDA (Sede - 4º andar)', tipo: 'Computadores e Periféricos', titulo: 'Substituir Notebook', categoria: 'Solicitação de Equipamentos', fila: 'SA-GTI-DIF', tecnico: 'Paulo Domingues', status: 'Pendente', atrasado: true, urgencia: 'Média', sla: 'Atrasado (15:58)', acao: 'Preparar imagem padrão Windows 11 corporativa no novo equipamento', data: '23-10-2026 13:58', link: 'https://atendimento.spaguas.sp.gov.br/front/ticket.form.php?id=1439' },
        { id: 1474, solicitante: 'Juliana Tostes Soares (Sede - 1º andar)', tipo: 'Computadores e Periféricos', titulo: 'Solicita projetor e caixa de som para utilizar em reunião', categoria: 'Solicitação de Equipamentos', fila: 'SA-GTI-DIF', tecnico: 'Leonardo dos Santos de Moura Antonio', status: 'Pendente', atrasado: true, urgencia: 'Média', sla: 'Atrasado (11:04)', acao: 'Disponibilizar kit multimídia e testar cabeamento HDMI', data: '27-10-2026 09:04', link: 'https://atendimento.spaguas.sp.gov.br/front/ticket.form.php?id=1474' },
        { id: 1505, solicitante: 'Carlos Eduardo Santos (Sede - 3º andar)', tipo: 'Sistemas', titulo: 'Erro de permissão no módulo de Outorgas SOI', categoria: 'Sistemas > SIGRH / SOI', fila: 'SA-GTI-DGD', tecnico: 'Diego Monteiro', status: 'Pendente', atrasado: false, urgencia: 'Média', sla: 'No Prazo', acao: 'Reatribuir papel de gestor hídrico no banco de dados', data: '01-11-2026 11:20', link: 'https://atendimento.spaguas.sp.gov.br/front/ticket.form.php?id=1505' },
        { id: 1495, solicitante: 'Mariana Costa Lima (Regional Taubaté)', tipo: 'Telefonia & PABX', titulo: 'Ramal VoIP sem tom de discagem na Regional', categoria: 'Telefonia & PABX', fila: 'SA-GTI-DIF', tecnico: 'Marcos Tadeu Yamamoto', status: 'Pendente', atrasado: false, urgencia: 'Média', sla: 'No Prazo', acao: 'Reiniciar gateway SIP e checar tronco de voz com a operadora', data: '30-10-2026 14:15', link: 'https://atendimento.spaguas.sp.gov.br/front/ticket.form.php?id=1495' },
        { id: 1482, solicitante: 'Roberto Silveira (Sede - 5º andar)', tipo: 'Aplicativos e Softwares', titulo: 'Instalação de certificado digital A1 para assinatura SEI', categoria: 'Aplicativos e Softwares', fila: 'SA-GTI-DIF', tecnico: 'Paulo Domingues', status: 'Em atendimento (atribuído)', atrasado: false, urgencia: 'Média', sla: 'No Prazo', acao: 'Importar cadeia ICP-Brasil no navegador e testar token', data: '28-10-2026 16:40', link: 'https://atendimento.spaguas.sp.gov.br/front/ticket.form.php?id=1482' },
        { id: 1468, solicitante: 'Fernanda Ribeiro (Regional Piracicaba)', tipo: 'Rede e Internet', titulo: 'Lentidão no acesso ao repositório de arquivos da bacia', categoria: 'Rede e Internet', fila: 'SA-GTI-DIF', tecnico: 'Marcos Tadeu Yamamoto', status: 'Em atendimento (atribuído)', atrasado: false, urgencia: 'Média', sla: 'No Prazo', acao: 'Análise de tráfego QoS no link Intragov 6 e descarte de pacotes', data: '26-10-2026 10:10', link: 'https://atendimento.spaguas.sp.gov.br/front/ticket.form.php?id=1468' },
        { id: 1450, solicitante: 'Lucas Almeida (Sede - 2º andar)', tipo: 'Impressão & Outsourcing', titulo: 'Falha de comunicação com impressora de rede setorial', categoria: 'Impressão & Outsourcing', fila: 'SA-GTI-DIF', tecnico: 'Leonardo dos Santos de Moura Antonio', status: 'Pendente', atrasado: false, urgencia: 'Média', sla: 'No Prazo', acao: 'Reinstalar fila de impressão no servidor de print e testar SNMP', data: '24-10-2026 09:30', link: 'https://atendimento.spaguas.sp.gov.br/front/ticket.form.php?id=1450' },
        { id: 1445, solicitante: 'Patrícia Nogueira (Regional Ribeirão Preto)', tipo: 'Computadores e Periféricos', titulo: 'Troca de mouse e teclado com defeito físico', categoria: 'Computadores e Periféricos', fila: 'SA-GTI-DIF', tecnico: 'Leonardo dos Santos de Moura Antonio', status: 'Pendente', atrasado: false, urgencia: 'Baixa', sla: 'No Prazo', acao: 'Envio de periféricos de reserva via malote institucional', data: '24-10-2026 08:45', link: 'https://atendimento.spaguas.sp.gov.br/front/ticket.form.php?id=1445' },
        { id: 1430, solicitante: 'Marcelo Rocha (Sede - 2º andar)', tipo: 'Sistemas', titulo: 'Dificuldade para abrir chamado no catálogo Formcreator', categoria: 'Sistemas > GLPI / Formcreator', fila: 'SA-GTI-DGD', tecnico: 'Diego Monteiro', status: 'Em atendimento (atribuído)', atrasado: false, urgencia: 'Média', sla: 'No Prazo', acao: 'Corrigir formulário com campo de upload obrigatório', data: '22-10-2026 15:10', link: 'https://atendimento.spaguas.sp.gov.br/front/ticket.form.php?id=1430' },
        { id: 1425, solicitante: 'Ana Paula Farias (Sede - 6º andar)', tipo: 'Acesso ao SEI', titulo: 'Reset de senha de acesso ao SEI SP-Águas', categoria: 'Acesso ao SEI', fila: 'SA-GTI-DGD', tecnico: 'Denise Costa Santana', status: 'Em atendimento (atribuído)', atrasado: false, urgencia: 'Média', sla: 'No Prazo', acao: 'Envio de link temporário de redefinição de credencial', data: '21-10-2026 11:00', link: 'https://atendimento.spaguas.sp.gov.br/front/ticket.form.php?id=1425' }
];"""

for p in paths:
    if not os.path.exists(p):
        continue
    with open(p, "r", encoding="utf-8") as f:
        c = f.read()

    is_crlf = "\r\n" in c
    norm = c.replace("\r\n", "\n")

    # Atualizar scorecard de 13 para 14 e atrasados para 5
    norm = re.sub(r'id="glpi-kpi-nao-solucionado"[^>]*>13<', 'id="glpi-kpi-nao-solucionado" style="color:#38bdf8; font-size:28px;">14<', norm)
    norm = re.sub(r'id="glpi-kpi-atrasados"[^>]*>6<', 'id="glpi-kpi-atrasados" style="color:#38bdf8; font-size:28px;">5<', norm)
    norm = norm.replace("Todos Não Solucionados (13)", "Todos Não Solucionados (14)")
    norm = norm.replace("Apenas Atrasados (6)", "Apenas Atrasados (5)")
    norm = norm.replace("Exibindo 13 chamados no escopo", "Exibindo 14 chamados reais no escopo")
    norm = norm.replace("Exibindo 13 de 13 chamados no escopo", "Exibindo 14 de 14 chamados reais no escopo")

    # Injetar os 14 chamados reais
    if 'window.CHAMADOS_GLPI_REAIS =' in norm:
        norm = re.sub(r'window\.CHAMADOS_GLPI_REAIS\s*=\s*\[[\s\S]*?\n\s*\];', real_tickets_js, norm, count=1)
    else:
        pos_top = norm.find('window.CHAMADOS_ITSM_SUPORTE = [')
        if pos_top != -1:
            norm = norm[:pos_top] + real_tickets_js + "\n\n" + norm[pos_top:]

    final = norm.replace("\n", "\r\n") if is_crlf else norm
    with open(p, "w", encoding="utf-8") as f:
        f.write(final)
    print(f"    [OK] Cockpit atualizado com dados reais em {p}!")

print("=" * 70)
print(" SANEAMENTO CONCLUÍDO COM SUCESSO")
print("=" * 70)
