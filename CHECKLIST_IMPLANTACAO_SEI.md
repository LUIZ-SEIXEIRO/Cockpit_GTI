# CHECKLIST DE IMPLANTAÇÃO E MIGRAÇÃO SEI 4.1.5 (SA-GTI 110050725)
**Cockpit GTI 360° — Automação e Motor de Busca SEI SP**  
**Responsável Técnico:** Luiz Antonio Seixeiro (Gestão de Projetos / Governança de TIC)  
**Data:** 11/11/2026 | **Versão:** 10.0-PROD  

---

## 1. Diretriz Mandatória de Clean Cutover (Migração Não Coexistente)
> **DECLARAÇÃO DE HOMOLOGAÇÃO ARQUITETURAL:**  
> A coexistência simultânea entre processos legados (v9 ou anteriores, baseados em leasing de diretório em espaço de usuário) e a versão v10 (baseada em Kernel File Locking `fcntl.flock` / `msvcrt.locking`) **NÃO É HOMOLOGADA E É ESTRITAMENTE VEDADA EM PRODUÇÃO**.  
> Qualquer tentativa de concorrência ativa entre instâncias v9 e v10 viola as garantias atômicas do armazenamento compartilhado.

---

## 2. Roteiro Passo a Passo de Cutover Pré-Implantação

### Fase I — Interrupção Compulsória de Escritores Legados
- [ ] **1.1. Identificar Processos Ativos:** Localizar todos os processos locais, containers Docker e workers em execução que utilizem versões legadas do `motor_sei.py`:
  ```bash
  # Linux / Container
  ps aux | grep -E "motor_sei|main.py"
  # Windows PowerShell
  Get-Process python* | Where-Object { $_.MainWindowTitle -match "Cockpit" -or $_.CommandLine -match "motor_sei" }
  ```
- [ ] **1.2. Interrupção Ordenada (Graceful Shutdown):** Finalizar todos os processos identificados para assegurar que nenhuma gravação esteja em andamento.
- [ ] **1.3. Limpeza de Artefatos Legados:** Excluir compulsoriamente diretórios de lock residuais antes de iniciar a nova versão:
  ```bash
  # Linux
  rm -rf data/sessao_sei.json.lock
  # Windows PowerShell
  if (Test-Path "data\sessao_sei.json.lock") { Remove-Item -Recurse -Force "data\sessao_sei.json.lock" }
  ```

---

### Fase II — Inicialização e Exclusão Mútua no Kernel (v10)
- [ ] **2.1. Arquivo de Lock Persistente:** O arquivo `data/sessao_sei.json.flock` é criado automaticamente com permissões `0600` e **NUNCA deve ser removido**, garantindo estabilidade permanente do descritor/inode no SO.
- [ ] **2.2. Exclusão Mútua Atômica no Kernel:** Todas as operações de escrita são sincronizadas exclusivamente via `fcntl.flock(LOCK_EX)` no Linux e `msvcrt.locking(LK_NBLCK, 1)` no Windows, garantindo que pausas ou suspensões de processos titulares mantenham o lock 100% retido pelo kernel.
- [ ] **2.3. Timeout Estrito entre Threads:** Concorrentes internos respeitam rigorosamente o `timeout` especificado (ex: 0,05 s) através de `threading.RLock.acquire(timeout)`, abortando com `TimeoutError` sem atrasos residuais.
- [ ] **2.4. Fencing e Limpeza Compulsória de Backups:** Qualquer aborto por divergência concorrente (`fingerprint_atual != fingerprint_inicial`) exclui compulsoriamente os arquivos temporários (`sessao_backup_*.tmp` e `sessao_tmp_*.json`), impedindo o vazamento de cookies ou dados de sessão anteriores.

---

### Fase III — Verificação e Homologação da Operação
- [ ] **3.1. Execução da Suíte de Testes:**
  ```powershell
  python -m unittest -v tests/test_motor_sei.py
  python -m unittest discover tests
  ```
  *(Critério de Aceite: 31/31 testes aprovados em < 2.0 segundos).*
- [ ] **3.2. Validação da Rota de Diagnóstico:**
  ```bash
  curl -X GET http://localhost:5000/api/v1/sei/status
  ```
  *(Critério de Aceite: Retorno HTTP 200 com JSON `{"sucesso": true, "ativa": bool, "unidade": "110050725"}`).*

---

## 3. Plano de Contingência e Rollback
Em caso de anomalia durante o cutover:
1. Interromper imediatamente o processo v10 do Cockpit GTI.
2. Restaurar o último snapshot válido de `data/sessao_sei.json`.
3. Notificar o Gestor de TIC (SA-GTI) para revalidação do ambiente antes de qualquer reativação.
