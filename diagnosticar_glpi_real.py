# -*- coding: utf-8 -*-
import pymysql

print("=" * 70)
print(" DIAGNÓSTICO DO BANCO DE DADOS MARIADB (glpidb:3306)")
print("=" * 70)

try:
    conn = pymysql.connect(host='127.0.0.1', port=3306, user='glpi', password='glpi', database='glpidb', charset='utf8mb4')
    with conn.cursor() as cur:
        cur.execute("SHOW TABLES")
        todas_tabelas = [t[0] for t in cur.fetchall()]
        print(f"[*] Total de tabelas encontradas no banco 'glpidb': {len(todas_tabelas)}")

        # Verificar se existem as tabelas nativas de produção do GLPI
        tabelas_glpi_nativas = [t for t in todas_tabelas if t in ['glpi_tickets', 'glpi_computers', 'glpi_problems', 'glpi_users']]
        
        if 'glpi_tickets' in tabelas_glpi_nativas:
            print("\n[OK] BANCO REAL DO GLPI ENCONTRADO! Tabelas nativas detectadas:")
            print(f"     {tabelas_glpi_nativas}")
            
            # Consultar os 13 chamados não solucionados diretamente na tabela glpi_tickets
            # No GLPI, status NOT IN (5, 6) significa Não Solucionado / Não Fechado
            cur.execute("""
                SELECT id, name, date, status, users_id_recipient 
                FROM glpi_tickets 
                WHERE is_deleted = 0 AND status NOT IN (5, 6) 
                ORDER BY id DESC LIMIT 15
            """)
            chamados_reais = cur.fetchall()
            print(f"\n[OK] Encontrados {len(chamados_reais)} chamados reais não solucionados na tabela 'glpi_tickets':")
            for c in chamados_reais:
                print(f"     • #{c[0]} - {c[1]} (Data: {c[2]} | Status GLPI: {c[3]})")
        else:
            print("\n[!] O banco 'glpidb' local NÃO possui a tabela 'glpi_tickets'.")
            print("    Tabelas atuais do banco:", todas_tabelas)
            print("\n    -> DIAGNÓSTICO: O seu GLPI de produção roda no servidor 'https://atendimento.spaguas.sp.gov.br/'")
            print("       e a tabela do Cockpit está exibindo o mock antigo gravado localmente.")
    conn.close()
except Exception as e:
    print(f"[ERRO DE CONEXÃO AO MARIADB]: {e}")

print("=" * 70)
