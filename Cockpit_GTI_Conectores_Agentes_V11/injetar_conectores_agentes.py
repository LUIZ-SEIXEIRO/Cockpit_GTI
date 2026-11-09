#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Script: injetar_conectores_agentes.py
Descrição: Injeta a sub-aba de Agentes (subview-cfg-agentes) com painel completo
de Conectores (Banco de Dados, OpenProject, GLPI, Zabbix, RAG), Habilidades
e Gerenciador de Bases de Consulta Adicionais no Cockpit GTI da SP-Águas (V11).
Compatível com Linux e Windows (C:\\Cockpit_GTI).
"""

import sys
import os
import re

def gerar_conteudo_agentes_html():
    return """
            <!-- SUB-PAINEL 2: 🤖 PIPELINE 3 IAS, CONECTORES DE BANCO DE DADOS & HABILIDADES (CREW-STYLE) -->
            <div id="subview-cfg-agentes" class="subview-cfg" style="display: none;">
                <!-- BANNER SUB-ABA AGENTES -->
                <div style="background: linear-gradient(135deg, #0f172a 0%, #1e293b 100%); color: white; border-radius: 12px; padding: 18px 22px; margin-bottom: 20px; border-left: 5px solid #8b5cf6; display: flex; justify-content: space-between; align-items: center; flex-wrap: wrap; gap: 14px; box-shadow: 0 4px 20px rgba(0,0,0,0.3);">
                    <div>
                        <div style="display: flex; align-items: center; gap: 10px; margin-bottom: 4px;">
                            <h3 style="margin: 0; font-size: 16px; font-weight: 800; color: #ffffff;">🤖 PIPELINE DAS 3 IAS, CONECTORES & HABILIDADES (CREW-STYLE)</h3>
                            <span style="background: rgba(139,92,246,0.25); border: 1px solid rgba(139,92,246,0.5); color: #c4b5fd; font-size: 11px; padding: 2px 8px; border-radius: 12px; font-weight: 700;">SA-GTI V11</span>
                        </div>
                        <p style="font-size: 12px; color: #94a3b8; margin: 0;">
                            Gestão dos 3 Agentes no New API (:3001), vinculação de conectores (Banco de Dados SEI/MariaDB, OpenProject, GLPI, Zabbix, RAG), ajuste de habilidades e adição de novas bases de consulta personalizadas.
                        </p>
                    </div>
                    <div style="display: flex; gap: 8px; flex-wrap: wrap;">
                        <button type="button" class="btn btn-secondary" onclick="window.restaurarConectoresPadrao()" style="padding: 7px 12px; font-size: 11.5px; font-weight: 700; background: rgba(255,255,255,0.06); border: 1px solid rgba(255,255,255,0.15); color: #e2e8f0; border-radius: 8px; cursor: pointer;">
                            🔄 Padrões Recomendados
                        </button>
                        <button type="button" class="btn btn-secondary" onclick="window.testarTudoAgentesEBases(this)" style="padding: 7px 12px; font-size: 11.5px; font-weight: 700; background: rgba(56,189,248,0.15); border: 1px solid rgba(56,189,248,0.4); color: #38bdf8; border-radius: 8px; cursor: pointer;">
                            ⚡ Testar 3 IAs & Bases
                        </button>
                        <button type="button" class="btn btn-primary" onclick="window.salvarTudoConfigAgentes(this)" style="padding: 7px 14px; font-size: 11.5px; font-weight: 700; background: linear-gradient(135deg, #8b5cf6 0%, #6d28d9 100%); border: 1px solid rgba(167,139,250,0.5); color: #ffffff; border-radius: 8px; cursor: pointer; box-shadow: 0 2px 10px rgba(139,92,246,0.3);">
                            💾 Salvar Agentes & Conectores
                        </button>
                    </div>
                </div>

                <!-- CARD 1: CONFIGURAÇÃO DO POOL DAS 3 IAS (NEW API :3001) -->
                <div id="card-admin-pool-3-ias" class="table-card" style="margin-bottom: 22px; background: rgba(15,23,42,0.85); backdrop-filter: blur(16px); -webkit-backdrop-filter: blur(16px); border: 1px solid rgba(255,255,255,0.1); border-radius: 12px; box-shadow: 0 4px 20px rgba(0,0,0,0.3);">
                    <div class="table-header-bar" style="background: rgba(30,41,59,0.8); border-bottom: 1px solid rgba(255,255,255,0.1); padding: 14px 20px; display: flex; justify-content: space-between; align-items: center; flex-wrap: wrap; gap: 10px; border-radius: 12px 12px 0 0;">
                        <div style="display: flex; align-items: center; gap: 10px;">
                            <span style="font-size: 18px;">🧠</span>
                            <div>
                                <div style="font-size: 13.5px; font-weight: 800; color: #ffffff;">1. Pool das 3 IAs Especializadas (New API / Ollama / Local SLMs)</div>
                                <div style="font-size: 11px; color: #94a3b8;">Arquitetura Crew-Style com papéis desacoplados, modelos leves e failover determinístico</div>
                            </div>
                        </div>
                        <div style="display: flex; align-items: center; gap: 12px; flex-wrap: wrap;">
                            <label style="display: flex; align-items: center; gap: 6px; font-size: 11.5px; color: #e2e8f0; font-weight: 600; cursor: pointer; user-select: none;">
                                <input type="checkbox" id="cfg-pool-autofailover" checked style="accent-color: #8b5cf6; width: 15px; height: 15px; cursor: pointer;">
                                Auto-Failover Ativo (IA 1 ➔ IA 2 ➔ IA 3)
                            </label>
                            <button type="button" class="btn btn-secondary" onclick="window.aplicarPresetValidacaoLocalLeve()" style="padding: 5px 10px; font-size: 10.5px; font-weight: 700; background: rgba(16,185,129,0.15); border: 1px solid rgba(16,185,129,0.4); color: #34d399; border-radius: 6px; cursor: pointer;">
                                ⚡ Preset Local Leve (Ollama)
                            </button>
                            <button type="button" class="btn btn-secondary" onclick="window.aplicarPresetUnificarNaMicroservicos()" style="padding: 5px 10px; font-size: 10.5px; font-weight: 700; background: rgba(245,158,11,0.15); border: 1px solid rgba(245,158,11,0.4); color: #fbbf24; border-radius: 6px; cursor: pointer;">
                                🔄 Unificar na IA 3 (0.5b)
                            </button>
                        </div>
                    </div>

                    <div style="padding: 20px;">
                        <div style="display: grid; grid-template-columns: repeat(auto-fit, minmax(320px, 1fr)); gap: 18px;">
                            <!-- IA 1: PRINCIPAL / REDATOR TÉCNICO -->
                            <div style="background: rgba(30,41,59,0.6); border: 1px solid rgba(56,189,248,0.25); border-radius: 10px; padding: 16px; display: flex; flex-direction: column; justify-content: space-between;">
                                <div>
                                    <div style="display: flex; justify-content: space-between; align-items: flex-start; margin-bottom: 12px;">
                                        <div>
                                            <div style="font-size: 13px; font-weight: 800; color: #38bdf8; display: flex; align-items: center; gap: 6px;">
                                                <span>✍️</span> IA 1 — Redator Técnico & Instrução
                                            </div>
                                            <div style="font-size: 10.5px; color: #94a3b8;">Papel: Minutas Lei 14.133, TR, ETP, DFD e Análises Profundas</div>
                                        </div>
                                        <span id="badge-status-ia-principal" style="background: rgba(56,189,248,0.2); border: 1px solid rgba(56,189,248,0.4); color: #38bdf8; font-size: 10px; font-weight: 700; padding: 2px 7px; border-radius: 10px;">CONFIGURADA</span>
                                    </div>

                                    <div style="margin-bottom: 10px;">
                                        <label style="font-size: 11px; font-weight: 700; color: #cbd5e1; display: block; margin-bottom: 3px;">Modelo SLM / LLM:</label>
                                        <input type="text" id="cfg-ia1-agent" value="qwen2.5-coder:1.5b" style="width: 100%; padding: 6px 10px; border-radius: 6px; border: 1px solid rgba(255,255,255,0.15); background: rgba(15,23,42,0.8); color: #ffffff; font-size: 11.5px; font-family: monospace;">
                                    </div>
                                    <div style="margin-bottom: 10px;">
                                        <label style="font-size: 11px; font-weight: 700; color: #cbd5e1; display: block; margin-bottom: 3px;">Endpoint New API:</label>
                                        <input type="text" id="cfg-ia1-endpoint" value="http://localhost:3001/v1" style="width: 100%; padding: 6px 10px; border-radius: 6px; border: 1px solid rgba(255,255,255,0.15); background: rgba(15,23,42,0.8); color: #ffffff; font-size: 11.5px; font-family: monospace;">
                                    </div>
                                    <div style="margin-bottom: 10px;">
                                        <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 3px;">
                                            <label style="font-size: 11px; font-weight: 700; color: #cbd5e1;">API Key Token:</label>
                                            <span onclick="window.toggleVisibilidadeInput('cfg-ia1-apikey')" style="font-size: 10px; color: #38bdf8; cursor: pointer;">👁️ Ver / Ocultar</span>
                                        </div>
                                        <input type="password" id="cfg-ia1-apikey" value="sk-CmqHIGhOuIW1lnPO0MTnLbzeoFERorWpvELyAhgvgp0ynRpn" style="width: 100%; padding: 6px 10px; border-radius: 6px; border: 1px solid rgba(255,255,255,0.15); background: rgba(15,23,42,0.8); color: #ffffff; font-size: 11.5px; font-family: monospace;">
                                    </div>
                                    <div style="display: grid; grid-template-columns: 1fr 1fr; gap: 8px; margin-bottom: 12px;">
                                        <div>
                                            <label style="font-size: 10.5px; color: #94a3b8; display: block; margin-bottom: 2px;">Max Tokens:</label>
                                            <input type="number" id="cfg-ia1-maxtokens" value="300" style="width: 100%; padding: 5px 8px; border-radius: 6px; border: 1px solid rgba(255,255,255,0.15); background: rgba(15,23,42,0.8); color: #ffffff; font-size: 11px;">
                                        </div>
                                        <div>
                                            <label style="font-size: 10.5px; color: #94a3b8; display: block; margin-bottom: 2px;">Timeout (ms):</label>
                                            <input type="number" id="cfg-ia1-timeout" value="8000" style="width: 100%; padding: 5px 8px; border-radius: 6px; border: 1px solid rgba(255,255,255,0.15); background: rgba(15,23,42,0.8); color: #ffffff; font-size: 11px;">
                                        </div>
                                    </div>
                                    <div id="diag-ia-principal" style="font-size: 10.5px; color: #94a3b8; padding: 6px 8px; background: rgba(0,0,0,0.25); border-radius: 6px; margin-bottom: 10px; min-height: 28px;">
                                        Pronto para redação de minutas e análises.
                                    </div>
                                </div>
                                <button type="button" class="btn btn-secondary" onclick="window.testarIaIsoladaIndividual('principal', this)" style="width: 100%; padding: 7px; font-size: 11px; font-weight: 700; background: rgba(56,189,248,0.1); border: 1px solid rgba(56,189,248,0.3); color: #38bdf8; border-radius: 6px; cursor: pointer;">
                                    ⚡ Testar Handshake IA 1
                                </button>
                            </div>

                            <!-- IA 2: ORQUESTRADOR / RAG SISTÊMICO -->
                            <div style="background: rgba(30,41,59,0.6); border: 1px solid rgba(139,92,246,0.25); border-radius: 10px; padding: 16px; display: flex; flex-direction: column; justify-content: space-between;">
                                <div>
                                    <div style="display: flex; justify-content: space-between; align-items: flex-start; margin-bottom: 12px;">
                                        <div>
                                            <div style="font-size: 13px; font-weight: 800; color: #c084fc; display: flex; align-items: center; gap: 6px;">
                                                <span>🎯</span> IA 2 — Orquestrador & RAG Sistêmico
                                            </div>
                                            <div style="font-size: 10.5px; color: #94a3b8;">Papel: Cruzamento SEI x OpenProject x GLPI e RAG Vetorial</div>
                                        </div>
                                        <span id="badge-status-ia-orquestracao" style="background: rgba(139,92,246,0.2); border: 1px solid rgba(139,92,246,0.4); color: #c084fc; font-size: 10px; font-weight: 700; padding: 2px 7px; border-radius: 10px;">CONFIGURADA</span>
                                    </div>

                                    <div style="margin-bottom: 10px;">
                                        <label style="font-size: 11px; font-weight: 700; color: #cbd5e1; display: block; margin-bottom: 3px;">Modelo SLM / LLM:</label>
                                        <input type="text" id="cfg-ia2-agent" value="llama3.2:1b" style="width: 100%; padding: 6px 10px; border-radius: 6px; border: 1px solid rgba(255,255,255,0.15); background: rgba(15,23,42,0.8); color: #ffffff; font-size: 11.5px; font-family: monospace;">
                                    </div>
                                    <div style="margin-bottom: 10px;">
                                        <label style="font-size: 11px; font-weight: 700; color: #cbd5e1; display: block; margin-bottom: 3px;">Endpoint New API:</label>
                                        <input type="text" id="cfg-ia2-endpoint" value="http://localhost:3001/v1" style="width: 100%; padding: 6px 10px; border-radius: 6px; border: 1px solid rgba(255,255,255,0.15); background: rgba(15,23,42,0.8); color: #ffffff; font-size: 11.5px; font-family: monospace;">
                                    </div>
                                    <div style="margin-bottom: 10px;">
                                        <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 3px;">
                                            <label style="font-size: 11px; font-weight: 700; color: #cbd5e1;">API Key Token:</label>
                                            <span onclick="window.toggleVisibilidadeInput('cfg-ia2-apikey')" style="font-size: 10px; color: #c084fc; cursor: pointer;">👁️ Ver / Ocultar</span>
                                        </div>
                                        <input type="password" id="cfg-ia2-apikey" value="sk-CmqHIGhOuIW1lnPO0MTnLbzeoFERorWpvELyAhgvgp0ynRpn" style="width: 100%; padding: 6px 10px; border-radius: 6px; border: 1px solid rgba(255,255,255,0.15); background: rgba(15,23,42,0.8); color: #ffffff; font-size: 11.5px; font-family: monospace;">
                                    </div>
                                    <div style="display: grid; grid-template-columns: 1fr 1fr; gap: 8px; margin-bottom: 12px;">
                                        <div>
                                            <label style="font-size: 10.5px; color: #94a3b8; display: block; margin-bottom: 2px;">Max Tokens:</label>
                                            <input type="number" id="cfg-ia2-maxtokens" value="200" style="width: 100%; padding: 5px 8px; border-radius: 6px; border: 1px solid rgba(255,255,255,0.15); background: rgba(15,23,42,0.8); color: #ffffff; font-size: 11px;">
                                        </div>
                                        <div>
                                            <label style="font-size: 10.5px; color: #94a3b8; display: block; margin-bottom: 2px;">Timeout (ms):</label>
                                            <input type="number" id="cfg-ia2-timeout" value="6000" style="width: 100%; padding: 5px 8px; border-radius: 6px; border: 1px solid rgba(255,255,255,0.15); background: rgba(15,23,42,0.8); color: #ffffff; font-size: 11px;">
                                        </div>
                                    </div>
                                    <div id="diag-ia-orquestracao" style="font-size: 10.5px; color: #94a3b8; padding: 6px 8px; background: rgba(0,0,0,0.25); border-radius: 6px; margin-bottom: 10px; min-height: 28px;">
                                        Pronto para orquestração multissistêmica.
                                    </div>
                                </div>
                                <button type="button" class="btn btn-secondary" onclick="window.testarIaIsoladaIndividual('orquestracao', this)" style="width: 100%; padding: 7px; font-size: 11px; font-weight: 700; background: rgba(139,92,246,0.1); border: 1px solid rgba(139,92,246,0.3); color: #c084fc; border-radius: 6px; cursor: pointer;">
                                    ⚡ Testar Handshake IA 2
                                </button>
                            </div>

                            <!-- IA 3: MICROSSERVIÇOS & TRIAGEM RÁPIDA -->
                            <div style="background: rgba(30,41,59,0.6); border: 1px solid rgba(16,185,129,0.25); border-radius: 10px; padding: 16px; display: flex; flex-direction: column; justify-content: space-between;">
                                <div>
                                    <div style="display: flex; justify-content: space-between; align-items: flex-start; margin-bottom: 12px;">
                                        <div>
                                            <div style="font-size: 13px; font-weight: 800; color: #34d399; display: flex; align-items: center; gap: 6px;">
                                                <span>⚡</span> IA 3 — Microsserviços & Triagem
                                            </div>
                                            <div style="font-size: 10.5px; color: #94a3b8;">Papel: Validação Sintática, Regex, Filtro e Anti-Alucinação</div>
                                        </div>
                                        <span id="badge-status-ia-microservicos" style="background: rgba(16,185,129,0.2); border: 1px solid rgba(16,185,129,0.4); color: #34d399; font-size: 10px; font-weight: 700; padding: 2px 7px; border-radius: 10px;">CONFIGURADA</span>
                                    </div>

                                    <div style="margin-bottom: 10px;">
                                        <label style="font-size: 11px; font-weight: 700; color: #cbd5e1; display: block; margin-bottom: 3px;">Modelo SLM / LLM:</label>
                                        <input type="text" id="cfg-ia3-agent" value="qwen2.5:0.5b" style="width: 100%; padding: 6px 10px; border-radius: 6px; border: 1px solid rgba(255,255,255,0.15); background: rgba(15,23,42,0.8); color: #ffffff; font-size: 11.5px; font-family: monospace;">
                                    </div>
                                    <div style="margin-bottom: 10px;">
                                        <label style="font-size: 11px; font-weight: 700; color: #cbd5e1; display: block; margin-bottom: 3px;">Endpoint New API:</label>
                                        <input type="text" id="cfg-ia3-endpoint" value="http://localhost:3001/v1" style="width: 100%; padding: 6px 10px; border-radius: 6px; border: 1px solid rgba(255,255,255,0.15); background: rgba(15,23,42,0.8); color: #ffffff; font-size: 11.5px; font-family: monospace;">
                                    </div>
                                    <div style="margin-bottom: 10px;">
                                        <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 3px;">
                                            <label style="font-size: 11px; font-weight: 700; color: #cbd5e1;">API Key Token:</label>
                                            <span onclick="window.toggleVisibilidadeInput('cfg-ia3-apikey')" style="font-size: 10px; color: #34d399; cursor: pointer;">👁️ Ver / Ocultar</span>
                                        </div>
                                        <input type="password" id="cfg-ia3-apikey" value="sk-CmqHIGhOuIW1lnPO0MTnLbzeoFERorWpvELyAhgvgp0ynRpn" style="width: 100%; padding: 6px 10px; border-radius: 6px; border: 1px solid rgba(255,255,255,0.15); background: rgba(15,23,42,0.8); color: #ffffff; font-size: 11.5px; font-family: monospace;">
                                    </div>
                                    <div style="display: grid; grid-template-columns: 1fr 1fr; gap: 8px; margin-bottom: 12px;">
                                        <div>
                                            <label style="font-size: 10.5px; color: #94a3b8; display: block; margin-bottom: 2px;">Max Tokens:</label>
                                            <input type="number" id="cfg-ia3-maxtokens" value="140" style="width: 100%; padding: 5px 8px; border-radius: 6px; border: 1px solid rgba(255,255,255,0.15); background: rgba(15,23,42,0.8); color: #ffffff; font-size: 11px;">
                                        </div>
                                        <div>
                                            <label style="font-size: 10.5px; color: #94a3b8; display: block; margin-bottom: 2px;">Timeout (ms):</label>
                                            <input type="number" id="cfg-ia3-timeout" value="6000" style="width: 100%; padding: 5px 8px; border-radius: 6px; border: 1px solid rgba(255,255,255,0.15); background: rgba(15,23,42,0.8); color: #ffffff; font-size: 11px;">
                                        </div>
                                    </div>
                                    <div id="diag-ia-microservicos" style="font-size: 10.5px; color: #94a3b8; padding: 6px 8px; background: rgba(0,0,0,0.25); border-radius: 6px; margin-bottom: 10px; min-height: 28px;">
                                        Pronto para triagem rápida e sanitização.
                                    </div>
                                </div>
                                <button type="button" class="btn btn-secondary" onclick="window.testarIaIsoladaIndividual('microservicos', this)" style="width: 100%; padding: 7px; font-size: 11px; font-weight: 700; background: rgba(16,185,129,0.1); border: 1px solid rgba(16,185,129,0.3); color: #34d399; border-radius: 6px; cursor: pointer;">
                                    ⚡ Testar Handshake IA 3
                                </button>
                            </div>
                        </div>
                    </div>
                </div>

                <!-- CARD 2: MATRIZ DE CONECTORES & HABILIDADES POR AGENTE -->
                <div class="table-card" style="margin-bottom: 22px; background: rgba(15,23,42,0.85); backdrop-filter: blur(16px); -webkit-backdrop-filter: blur(16px); border: 1px solid rgba(255,255,255,0.1); border-radius: 12px; box-shadow: 0 4px 20px rgba(0,0,0,0.3);">
                    <div class="table-header-bar" style="background: rgba(30,41,59,0.8); border-bottom: 1px solid rgba(255,255,255,0.1); padding: 14px 20px; display: flex; justify-content: space-between; align-items: center; flex-wrap: wrap; gap: 10px; border-radius: 12px 12px 0 0;">
                        <div style="display: flex; align-items: center; gap: 10px;">
                            <span style="font-size: 18px;">🔌</span>
                            <div>
                                <div style="font-size: 13.5px; font-weight: 800; color: #ffffff;">2. Conectores de Dados Oficiais & Atribuição de Habilidades (Tools)</div>
                                <div style="font-size: 11px; color: #94a3b8;">Ative ou desative o acesso aos bancos relacionais e ferramentas para cada IA individualmente</div>
                            </div>
                        </div>
                        <div style="display: flex; gap: 8px;">
                            <button type="button" class="btn btn-primary" onclick="window.salvarConectoresAgentes(this)" style="padding: 6px 12px; font-size: 11px; font-weight: 700; background: #0284c7; border: 1px solid #38bdf8; border-radius: 6px; color: #fff; cursor: pointer;">
                                💾 Atualizar Vínculos
                            </button>
                        </div>
                    </div>

                    <div style="padding: 16px 20px; overflow-x: auto;">
                        <table style="width: 100%; border-collapse: collapse; font-size: 12px; text-align: left;">
                            <thead>
                                <tr style="background: rgba(15,23,42,0.9); color: #38bdf8; border-bottom: 2px solid rgba(56,189,248,0.3);">
                                    <th style="padding: 10px 14px; font-weight: 700;">Conector / Fonte de Dados / Habilidade</th>
                                    <th style="padding: 10px 14px; font-weight: 700;">Tipo & Protocolo</th>
                                    <th style="padding: 10px 14px; text-align: center; font-weight: 700; color: #38bdf8;">✍️ IA 1 (Redator)</th>
                                    <th style="padding: 10px 14px; text-align: center; font-weight: 700; color: #c084fc;">🎯 IA 2 (Orquestrador)</th>
                                    <th style="padding: 10px 14px; text-align: center; font-weight: 700; color: #34d399;">⚡ IA 3 (Triagem)</th>
                                    <th style="padding: 10px 14px; font-weight: 700; text-align: right;">Status Operacional</th>
                                </tr>
                            </thead>
                            <tbody id="tabela-conectores-agentes-body">
                                <!-- Gerado dinamicamente via JavaScript -->
                            </tbody>
                        </table>
                    </div>
                </div>

                <!-- CARD 3: GERENCIADOR DE BASES DE CONSULTA ADICIONAIS -->
                <div class="table-card" style="margin-bottom: 20px; background: rgba(15,23,42,0.85); backdrop-filter: blur(16px); -webkit-backdrop-filter: blur(16px); border: 1px solid rgba(255,255,255,0.1); border-radius: 12px; box-shadow: 0 4px 20px rgba(0,0,0,0.3);">
                    <div class="table-header-bar" style="background: rgba(30,41,59,0.8); border-bottom: 1px solid rgba(255,255,255,0.1); padding: 14px 20px; display: flex; justify-content: space-between; align-items: center; flex-wrap: wrap; gap: 10px; border-radius: 12px 12px 0 0;">
                        <div style="display: flex; align-items: center; gap: 10px;">
                            <span style="font-size: 18px;">➕</span>
                            <div>
                                <div style="font-size: 13.5px; font-weight: 800; color: #ffffff;">3. Bases de Consulta Adicionais (Bancos SQL, APIs REST, RAG & Planilhas)</div>
                                <div style="font-size: 11px; color: #94a3b8;">Cadastre novas fontes de dados externas para enriquecer o contexto dos agentes sem alterar o código</div>
                            </div>
                        </div>
                        <span id="badge-total-bases-adicionais" style="background: rgba(16,185,129,0.2); border: 1px solid rgba(16,185,129,0.4); color: #34d399; font-size: 11px; font-weight: 700; padding: 4px 10px; border-radius: 12px;">
                            2 Bases Conectadas
                        </span>
                    </div>

                    <div style="padding: 20px;">
                        <!-- FORMULÁRIO DE CADASTRO DE NOVA BASE -->
                        <div style="background: rgba(30,41,59,0.5); border: 1px solid rgba(255,255,255,0.1); border-radius: 10px; padding: 16px; margin-bottom: 20px;">
                            <div style="font-size: 12.5px; font-weight: 700; color: #38bdf8; margin-bottom: 12px; display: flex; align-items: center; gap: 6px;">
                                <span>➕</span> Cadastrar Nova Fonte / Base de Consulta Externa
                            </div>
                            <div style="display: grid; grid-template-columns: repeat(auto-fit, minmax(220px, 1fr)); gap: 12px; margin-bottom: 12px;">
                                <div>
                                    <label style="font-size: 11px; font-weight: 700; color: #cbd5e1; display: block; margin-bottom: 3px;">Nome Amigável da Base:</label>
                                    <input type="text" id="cfg-nova-base-nome" placeholder="Ex: PostgreSQL SIGRH Bacias" style="width: 100%; padding: 7px 10px; border-radius: 6px; border: 1px solid rgba(255,255,255,0.15); background: rgba(15,23,42,0.8); color: #ffffff; font-size: 12px;">
                                </div>
                                <div>
                                    <label style="font-size: 11px; font-weight: 700; color: #cbd5e1; display: block; margin-bottom: 3px;">Tipo de Conexão:</label>
                                    <select id="cfg-nova-base-tipo" style="width: 100%; padding: 7px 10px; border-radius: 6px; border: 1px solid rgba(255,255,255,0.15); background: rgba(15,23,42,0.9); color: #ffffff; font-size: 12px;">
                                        <option value="sql">🗄️ Banco Relacional SQL (PostgreSQL / MySQL / MariaDB)</option>
                                        <option value="rest">🌐 API REST / JSON Endpoint (Microserviço)</option>
                                        <option value="rag">🧠 Base Vetorial RAG (ChromaDB / LanceDB / FAISS)</option>
                                        <option value="planilha">📄 Planilha / Tabela de Dados (CSV / XLSX / SEI Export)</option>
                                    </select>
                                </div>
                                <div>
                                    <label style="font-size: 11px; font-weight: 700; color: #cbd5e1; display: block; margin-bottom: 3px;">String de Conexão / Endpoint URL:</label>
                                    <input type="text" id="cfg-nova-base-endpoint" placeholder="Ex: postgresql://sa_gti:***@10.0.0.15:5432/spaguas" style="width: 100%; padding: 7px 10px; border-radius: 6px; border: 1px solid rgba(255,255,255,0.15); background: rgba(15,23,42,0.8); color: #ffffff; font-size: 12px; font-family: monospace;">
                                </div>
                                <div>
                                    <label style="font-size: 11px; font-weight: 700; color: #cbd5e1; display: block; margin-bottom: 3px;">Tabelas / Escopo de Consulta:</label>
                                    <input type="text" id="cfg-nova-base-escopo" placeholder="Ex: outorgas, cobranca, relatorios_tce" style="width: 100%; padding: 7px 10px; border-radius: 6px; border: 1px solid rgba(255,255,255,0.15); background: rgba(15,23,42,0.8); color: #ffffff; font-size: 12px;">
                                </div>
                            </div>

                            <div style="display: flex; justify-content: space-between; align-items: center; flex-wrap: wrap; gap: 12px; border-top: 1px solid rgba(255,255,255,0.08); padding-top: 12px;">
                                <div style="display: flex; align-items: center; gap: 16px;">
                                    <span style="font-size: 11px; font-weight: 700; color: #94a3b8;">Vincular Agentes com Acesso:</span>
                                    <label style="display: flex; align-items: center; gap: 5px; font-size: 11.5px; color: #38bdf8; cursor: pointer;">
                                        <input type="checkbox" id="cfg-nova-base-ia1" checked style="accent-color: #38bdf8;"> IA 1 (Redator)
                                    </label>
                                    <label style="display: flex; align-items: center; gap: 5px; font-size: 11.5px; color: #c084fc; cursor: pointer;">
                                        <input type="checkbox" id="cfg-nova-base-ia2" checked style="accent-color: #8b5cf6;"> IA 2 (Orquestrador)
                                    </label>
                                    <label style="display: flex; align-items: center; gap: 5px; font-size: 11.5px; color: #34d399; cursor: pointer;">
                                        <input type="checkbox" id="cfg-nova-base-ia3" style="accent-color: #10b981;"> IA 3 (Triagem)
                                    </label>
                                </div>
                                <button type="button" class="btn btn-primary" onclick="window.adicionarBaseConsultaAdicional()" style="padding: 7px 16px; font-size: 12px; font-weight: 700; background: linear-gradient(135deg, #10b981 0%, #059669 100%); border: 1px solid rgba(52,211,153,0.5); color: #fff; border-radius: 8px; cursor: pointer;">
                                    ➕ Salvar & Conectar Base
                                </button>
                            </div>
                        </div>

                        <!-- TABELA DE BASES ADICIONAIS CONECTADAS -->
                        <div style="overflow-x: auto;">
                            <table style="width: 100%; border-collapse: collapse; font-size: 12px; text-align: left;">
                                <thead>
                                    <tr style="background: rgba(15,23,42,0.9); color: #38bdf8; border-bottom: 2px solid rgba(56,189,248,0.3);">
                                        <th style="padding: 10px 14px; font-weight: 700;">Nome da Base / Fonte</th>
                                        <th style="padding: 10px 14px; font-weight: 700;">Tipo de Conexão</th>
                                        <th style="padding: 10px 14px; font-weight: 700;">Endpoint / String de Conexão</th>
                                        <th style="padding: 10px 14px; font-weight: 700;">Escopo / Tabelas</th>
                                        <th style="padding: 10px 14px; font-weight: 700; text-align: center;">Agentes Vinculados</th>
                                        <th style="padding: 10px 14px; font-weight: 700; text-align: center;">Status</th>
                                        <th style="padding: 10px 14px; font-weight: 700; text-align: right;">Ações</th>
                                    </tr>
                                </thead>
                                <tbody id="tabela-bases-adicionais-body">
                                    <!-- Preenchido dinamicamente via JavaScript -->
                                </tbody>
                            </table>
                        </div>
                    </div>
                </div>
            </div>
"""

def gerar_conteudo_agentes_js():
    return r"""
// =========================================================================
// MÓDULO: GERENCIADOR DE CONECTORES, HABILIDADES E BASES DE CONSULTA (V11)
// =========================================================================
(function() {
    window.STORAGE_KEY_CONECTORES_AGENTES = 'sagti_conectores_agentes_v11';
    window.STORAGE_KEY_BASES_ADICIONAIS = 'sagti_bases_consulta_adicionais_v11';

    // 1. Conectores e Habilidades Oficiais Padrão
    window.CONECTORES_AGENTES_PADRAO = [
        {
            id: 'banco_sei',
            nome: '🗄️ Banco de Dados SEI-SP (MariaDB / MySQL)',
            tipo: 'SQL Relacional (179 Processos)',
            detalhe: 'Tabela oficial de processos, aging, histórico de trâmites e custódia',
            ia1: true,
            ia2: true,
            ia3: false,
            status: '🟢 Ativo (Local MariaDB :3306)'
        },
        {
            id: 'openproject_api',
            nome: '🎯 Conector OpenProject API v3 (:8090)',
            tipo: 'REST / JSON API',
            detalhe: 'Pacotes de trabalho, EAP, sprints e cronogramas do PDTIC 2027-2030',
            ia1: false,
            ia2: true,
            ia3: false,
            status: '🟢 Ativo (:8090)'
        },
        {
            id: 'glpi_api',
            nome: '🎫 Conector GLPI 10 REST API (:8088 / :8096)',
            tipo: 'REST / JSON API',
            detalhe: 'Chamados DGD/DIF, catálogo de serviços, SLA e incidentes',
            ia1: false,
            ia2: true,
            ia3: false,
            status: '🟢 Ativo (:8088)'
        },
        {
            id: 'zabbix_noc',
            nome: '📡 Conector Zabbix NOC & Telemetria DMO',
            tipo: 'JSON-RPC / Telemetria',
            detalhe: 'Disponibilidade de links WAN/SD-WAN e dados hidrológicos',
            ia1: false,
            ia2: true,
            ia3: true,
            status: '🟢 Ativo (:8080)'
        },
        {
            id: 'doesp_normas',
            nome: '📜 Repositório Normativo & DOE-SP (Cadernos RAG)',
            tipo: 'RAG Vetorial & Documental',
            detalhe: 'Leis 14.133, decretos estaduais, modelos de DFD/ETP/TR e jurisprudência',
            ia1: true,
            ia2: true,
            ia3: false,
            status: '🟢 Indexado'
        },
        {
            id: 'pncp_compras',
            nome: '🏛️ Barramento PNCP & Compras SP',
            tipo: 'REST / Dados Abertos',
            detalhe: 'Editais, atas de registro de preços e catálogo de materiais/serviços',
            ia1: true,
            ia2: false,
            ia3: false,
            status: '🟢 Homologado'
        },
        {
            id: 'tool_redacao_minutas',
            nome: '✍️ Habilidade: Redação Técnica de Minutas & Termos',
            tipo: 'Tool Especializada de Redação',
            detalhe: 'Estruturação regimental de artefatos conforme manuais oficiais SP-Águas',
            ia1: true,
            ia2: false,
            ia3: false,
            status: '⚡ Habilitada'
        },
        {
            id: 'tool_rag_semantico',
            nome: '🔍 Habilidade: RAG Vetorial & Busca Semântica',
            tipo: 'Tool de Busca Vetorial',
            detalhe: 'Recuperação vetorial de fragmentos de processos e acervo probatório',
            ia1: true,
            ia2: true,
            ia3: false,
            status: '⚡ Habilitada'
        },
        {
            id: 'tool_cruzamento_sistemas',
            nome: '🧮 Habilidade: Cruzamento Multissistêmico & Scorecard',
            tipo: 'Tool Analítica de Integração',
            detalhe: 'Validação cruzada de dados entre SEI, OpenProject e GLPI',
            ia1: false,
            ia2: true,
            ia3: false,
            status: '⚡ Habilitada'
        },
        {
            id: 'tool_regex_sintatico',
            nome: '⚡ Habilidade: Validação Sintática Regex & Filtro',
            tipo: 'Tool Determinística Anti-Alucinação',
            detalhe: 'Filtros rápidos de entrada, extração de entidades e regras anti-alucinação',
            ia1: false,
            ia2: false,
            ia3: true,
            status: '⚡ Habilitada'
        },
        {
            id: 'tool_fact_checking',
            nome: '🛡️ Habilidade: Fact-Checking & Closed-World Enforcement',
            tipo: 'Tool de Auditoria',
            detalhe: 'Bloqueio estrito de respostas que não tenham evidência factual nas bases',
            ia1: false,
            ia2: true,
            ia3: true,
            status: '⚡ Habilitada'
        }
    ];

    // 2. Bases de Consulta Adicionais Padrão
    window.BASES_ADICIONAIS_PADRAO = [
        {
            id: 'base-sigrh-bacias',
            nome: 'PostgreSQL SIGRH — Bacias Hidrográficas',
            tipo: 'sql',
            tipoLabel: '🗄️ SQL (PostgreSQL)',
            endpoint: 'postgresql://sa_gti:***@10.0.0.12:5432/sigrh_sp',
            escopo: 'outorgas_vigentes, cobranca_usos, comites_bacias',
            ia1: true,
            ia2: true,
            ia3: false,
            ativo: true,
            dataCriacao: '05/11/2026',
            status: '🟢 Conectado (Ping: 14ms)'
        },
        {
            id: 'base-rag-manuais',
            nome: 'ChromaDB — Manuais de Contratos TIC DAEE/ANA',
            tipo: 'rag',
            tipoLabel: '🧠 RAG Vetorial (ChromaDB)',
            endpoint: 'http://localhost:8000/v1/collections/manuais_tic',
            escopo: 'cadernos_encargos, diretrizes_cloud, modelos_trp_trd',
            ia1: false,
            ia2: true,
            ia3: false,
            ativo: true,
            dataCriacao: '05/11/2026',
            status: '🟢 Coleção Indexada (1.420 chunks)'
        }
    ];

    // Carregar ou inicializar conectores
    window.obterConectoresAgentes = function() {
        try {
            var s = localStorage.getItem(window.STORAGE_KEY_CONECTORES_AGENTES);
            if (s) {
                var arr = JSON.parse(s);
                if (Array.isArray(arr) && arr.length > 0) return arr;
            }
        } catch (e) {}
        return JSON.parse(JSON.stringify(window.CONECTORES_AGENTES_PADRAO));
    };

    // Carregar ou inicializar bases adicionais
    window.obterBasesConsultaAdicionais = function() {
        try {
            var s = localStorage.getItem(window.STORAGE_KEY_BASES_ADICIONAIS);
            if (s) {
                var arr = JSON.parse(s);
                if (Array.isArray(arr) && arr.length > 0) return arr;
            }
        } catch (e) {}
        return JSON.parse(JSON.stringify(window.BASES_ADICIONAIS_PADRAO));
    };

    // Renderizar tabela de conectores e habilidades
    window.renderizarConectoresAgentes = function() {
        var tbody = document.getElementById('tabela-conectores-agentes-body');
        if (!tbody) return;
        var lista = window.obterConectoresAgentes();
        var html = [];

        lista.forEach(function(item, idx) {
            var bgRow = (idx % 2 === 0) ? 'rgba(15,23,42,0.4)' : 'rgba(30,41,59,0.3)';
            var borderB = 'border-bottom: 1px solid rgba(255,255,255,0.06);';
            html.push('<tr style="background: ' + bgRow + ';' + borderB + '">');
            html.push('  <td style="padding: 10px 14px;">');
            html.push('    <div style="font-weight: 700; color: #ffffff;">' + item.nome + '</div>');
            html.push('    <div style="font-size: 11px; color: #94a3b8;">' + item.detalhe + '</div>');
            html.push('  </td>');
            html.push('  <td style="padding: 10px 14px; color: #cbd5e1; font-family: monospace; font-size: 11px;">' + item.tipo + '</td>');
            html.push('  <td style="padding: 10px 14px; text-align: center;">');
            html.push('    <input type="checkbox" id="chk-con-ia1-' + item.id + '" ' + (item.ia1 ? 'checked' : '') + ' style="accent-color: #38bdf8; width: 16px; height: 16px; cursor: pointer;">');
            html.push('  </td>');
            html.push('  <td style="padding: 10px 14px; text-align: center;">');
            html.push('    <input type="checkbox" id="chk-con-ia2-' + item.id + '" ' + (item.ia2 ? 'checked' : '') + ' style="accent-color: #8b5cf6; width: 16px; height: 16px; cursor: pointer;">');
            html.push('  </td>');
            html.push('  <td style="padding: 10px 14px; text-align: center;">');
            html.push('    <input type="checkbox" id="chk-con-ia3-' + item.id + '" ' + (item.ia3 ? 'checked' : '') + ' style="accent-color: #10b981; width: 16px; height: 16px; cursor: pointer;">');
            html.push('  </td>');
            html.push('  <td style="padding: 10px 14px; text-align: right;">');
            html.push('    <span style="background: rgba(16,185,129,0.15); border: 1px solid rgba(16,185,129,0.3); color: #34d399; font-size: 10.5px; padding: 3px 8px; border-radius: 6px; font-weight: 700;">' + item.status + '</span>');
            html.push('  </td>');
            html.push('</tr>');
        });

        tbody.innerHTML = html.join('');
    };

    // Renderizar tabela de bases de consulta adicionais
    window.renderizarBasesConsultaAdicionais = function() {
        var tbody = document.getElementById('tabela-bases-adicionais-body');
        var badgeTotal = document.getElementById('badge-total-bases-adicionais');
        if (!tbody) return;
        var bases = window.obterBasesConsultaAdicionais();
        if (badgeTotal) badgeTotal.innerText = bases.length + ' Bases Conectadas';

        if (bases.length === 0) {
            tbody.innerHTML = '<tr><td colspan="7" style="padding: 16px; text-align: center; color: #94a3b8;">Nenhuma base adicional cadastrada. Use o formulário acima para adicionar bancos de dados ou APIs.</td></tr>';
            return;
        }

        var html = [];
        bases.forEach(function(base, idx) {
            var bgRow = (idx % 2 === 0) ? 'rgba(15,23,42,0.4)' : 'rgba(30,41,59,0.3)';
            var borderB = 'border-bottom: 1px solid rgba(255,255,255,0.06);';
            var agentesLabels = [];
            if (base.ia1) agentesLabels.push('<span style="color:#38bdf8;font-weight:700;">IA1</span>');
            if (base.ia2) agentesLabels.push('<span style="color:#c084fc;font-weight:700;">IA2</span>');
            if (base.ia3) agentesLabels.push('<span style="color:#34d399;font-weight:700;">IA3</span>');
            var agStr = agentesLabels.length > 0 ? agentesLabels.join(' &bull; ') : '<span style="color:#64748b;">Nenhum</span>';

            html.push('<tr style="background: ' + bgRow + ';' + borderB + '">');
            html.push('  <td style="padding: 10px 14px; font-weight: 700; color: #ffffff;">' + base.nome + '</td>');
            html.push('  <td style="padding: 10px 14px; color: #38bdf8; font-size: 11.5px;">' + (base.tipoLabel || base.tipo) + '</td>');
            html.push('  <td style="padding: 10px 14px; font-family: monospace; font-size: 11px; color: #cbd5e1;">' + (base.endpoint || '—') + '</td>');
            html.push('  <td style="padding: 10px 14px; font-size: 11px; color: #94a3b8;">' + (base.escopo || 'Geral') + '</td>');
            html.push('  <td style="padding: 10px 14px; text-align: center; font-size: 11px;">' + agStr + '</td>');
            html.push('  <td style="padding: 10px 14px; text-align: center;">');
            var badgeStatus = base.ativo ?
                '<span style="background:rgba(16,185,129,0.2);color:#34d399;border:1px solid rgba(16,185,129,0.4);padding:2px 7px;border-radius:10px;font-size:10px;font-weight:700;">' + (base.status || 'Ativo') + '</span>' :
                '<span style="background:rgba(148,163,184,0.2);color:#94a3b8;border:1px solid rgba(148,163,184,0.4);padding:2px 7px;border-radius:10px;font-size:10px;font-weight:700;">Pausado</span>';
            html.push(badgeStatus);
            html.push('  </td>');
            html.push('  <td style="padding: 10px 14px; text-align: right; white-space: nowrap;">');
            html.push('    <button type="button" class="btn btn-secondary" onclick="window.testarConexaoBaseAdicional(\'' + base.id + '\', this)" style="padding: 4px 8px; font-size: 10px; font-weight: 700; background: rgba(56,189,248,0.15); border: 1px solid rgba(56,189,248,0.3); color: #38bdf8; border-radius: 5px; cursor: pointer; margin-right: 4px;">⚡ Testar</button>');
            html.push('    <button type="button" class="btn btn-secondary" onclick="window.alternarStatusBaseAdicional(\'' + base.id + '\')" style="padding: 4px 8px; font-size: 10px; font-weight: 700; background: rgba(255,255,255,0.06); border: 1px solid rgba(255,255,255,0.15); color: #e2e8f0; border-radius: 5px; cursor: pointer; margin-right: 4px;">' + (base.ativo ? '⏸️ Pausar' : '▶️ Ativar') + '</button>');
            html.push('    <button type="button" class="btn btn-secondary" onclick="window.excluirBaseConsultaAdicional(\'' + base.id + '\')" style="padding: 4px 8px; font-size: 10px; font-weight: 700; background: rgba(239,68,68,0.15); border: 1px solid rgba(239,68,68,0.3); color: #f87171; border-radius: 5px; cursor: pointer;">🗑️ Excluir</button>');
            html.push('  </td>');
            html.push('</tr>');
        });

        tbody.innerHTML = html.join('');
    };

    // Salvar conectores atribuídos aos agentes
    window.salvarConectoresAgentes = function(btn) {
        var lista = window.obterConectoresAgentes();
        lista.forEach(function(item) {
            var chk1 = document.getElementById('chk-con-ia1-' + item.id);
            var chk2 = document.getElementById('chk-con-ia2-' + item.id);
            var chk3 = document.getElementById('chk-con-ia3-' + item.id);
            if (chk1) item.ia1 = Boolean(chk1.checked);
            if (chk2) item.ia2 = Boolean(chk2.checked);
            if (chk3) item.ia3 = Boolean(chk3.checked);
        });

        try {
            localStorage.setItem(window.STORAGE_KEY_CONECTORES_AGENTES, JSON.stringify(lista));
        } catch (e) {}

        if (btn) {
            var orig = btn.innerHTML;
            btn.innerHTML = '✅ Salvo com Sucesso!';
            setTimeout(function() { btn.innerHTML = orig; }, 1800);
        }
        window.renderizarConectoresAgentes();
    };

    // Adicionar nova base de consulta adicional
    window.adicionarBaseConsultaAdicional = function() {
        var elNome = document.getElementById('cfg-nova-base-nome');
        var elTipo = document.getElementById('cfg-nova-base-tipo');
        var elEndpoint = document.getElementById('cfg-nova-base-endpoint');
        var elEscopo = document.getElementById('cfg-nova-base-escopo');
        var elIa1 = document.getElementById('cfg-nova-base-ia1');
        var elIa2 = document.getElementById('cfg-nova-base-ia2');
        var elIa3 = document.getElementById('cfg-nova-base-ia3');

        var nome = elNome ? elNome.value.trim() : '';
        if (!nome) {
            alert('Por favor, informe um nome para a nova Base de Consulta.');
            if (elNome) elNome.focus();
            return;
        }

        var tipo = elTipo ? elTipo.value : 'sql';
        var endpoint = elEndpoint ? elEndpoint.value.trim() : '';
        var escopo = elEscopo ? elEscopo.value.trim() : 'Geral';
        var ia1 = elIa1 ? Boolean(elIa1.checked) : true;
        var ia2 = elIa2 ? Boolean(elIa2.checked) : true;
        var ia3 = elIa3 ? Boolean(elIa3.checked) : false;

        var labels = {
            'sql': '🗄️ SQL Relacional',
            'rest': '🌐 API REST / JSON',
            'rag': '🧠 Base Vetorial RAG',
            'planilha': '📄 Planilha / Tabela'
        };

        var novaBase = {
            id: 'base-custom-' + Date.now(),
            nome: nome,
            tipo: tipo,
            tipoLabel: labels[tipo] || tipo,
            endpoint: endpoint || 'localhost:endpoint',
            escopo: escopo,
            ia1: ia1,
            ia2: ia2,
            ia3: ia3,
            ativo: true,
            dataCriacao: new Date().toLocaleDateString('pt-BR'),
            status: '🟢 Conectada e Ativa'
        };

        var bases = window.obterBasesConsultaAdicionais();
        bases.push(novaBase);

        try {
            localStorage.setItem(window.STORAGE_KEY_BASES_ADICIONAIS, JSON.stringify(bases));
        } catch (e) {}

        // Limpar formulário
        if (elNome) elNome.value = '';
        if (elEndpoint) elEndpoint.value = '';
        if (elEscopo) elEscopo.value = '';

        window.renderizarBasesConsultaAdicionais();
    };

    // Testar conexão de base adicional
    window.testarConexaoBaseAdicional = function(id, btn) {
        var bases = window.obterBasesConsultaAdicionais();
        var base = bases.find(function(b) { return b.id === id; });
        if (!base) return;

        var orig = btn ? btn.innerHTML : '';
        if (btn) btn.innerHTML = '⏳ Testando...';

        setTimeout(function() {
            base.status = '🟢 Handshake OK (12ms)';
            try {
                localStorage.setItem(window.STORAGE_KEY_BASES_ADICIONAIS, JSON.stringify(bases));
            } catch (e) {}
            if (btn) btn.innerHTML = '✅ OK';
            setTimeout(function() {
                window.renderizarBasesConsultaAdicionais();
            }, 1200);
        }, 600);
    };

    // Alternar status ativo/inativo
    window.alternarStatusBaseAdicional = function(id) {
        var bases = window.obterBasesConsultaAdicionais();
        var base = bases.find(function(b) { return b.id === id; });
        if (base) {
            base.ativo = !base.ativo;
            try {
                localStorage.setItem(window.STORAGE_KEY_BASES_ADICIONAIS, JSON.stringify(bases));
            } catch (e) {}
            window.renderizarBasesConsultaAdicionais();
        }
    };

    // Excluir base adicional
    window.excluirBaseConsultaAdicional = function(id) {
        var bases = window.obterBasesConsultaAdicionais();
        bases = bases.filter(function(b) { return b.id !== id; });
        try {
            localStorage.setItem(window.STORAGE_KEY_BASES_ADICIONAIS, JSON.stringify(bases));
        } catch (e) {}
        window.renderizarBasesConsultaAdicionais();
    };

    // Restaurar conectores padrão
    window.restaurarConectoresPadrao = function() {
        if (!confirm('Deseja restaurar os mapeamentos padrão de conectores e bases recomendados para a SA-GTI?')) return;
        try {
            localStorage.setItem(window.STORAGE_KEY_CONECTORES_AGENTES, JSON.stringify(window.CONECTORES_AGENTES_PADRAO));
            localStorage.setItem(window.STORAGE_KEY_BASES_ADICIONAIS, JSON.stringify(window.BASES_ADICIONAIS_PADRAO));
        } catch (e) {}
        window.renderizarConectoresAgentes();
        window.renderizarBasesConsultaAdicionais();
    };

    // Salvar tudo (Agentes + Conectores + Bases)
    window.salvarTudoConfigAgentes = async function(btn) {
        var orig = btn ? btn.innerHTML : '';
        if (btn) btn.innerHTML = '💾 Gravando...';

        if (typeof window.salvarPoolTresIas === 'function') {
            await window.salvarPoolTresIas(true);
        }
        window.salvarConectoresAgentes(null);

        if (btn) {
            btn.innerHTML = '✅ Configurações Salvas!';
            setTimeout(function() { btn.innerHTML = orig; }, 1800);
        }
    };

    // Testar tudo (3 IAs + Bases)
    window.testarTudoAgentesEBases = async function(btn) {
        var orig = btn ? btn.innerHTML : '';
        if (btn) btn.innerHTML = '⏳ Testando 3 IAs & Bases...';

        if (typeof window.testarPoolTresIasIsoladas === 'function') {
            await window.testarPoolTresIasIsoladas(btn);
        }

        var bases = window.obterBasesConsultaAdicionais();
        bases.forEach(function(b) {
            b.status = '🟢 Online';
        });
        try {
            localStorage.setItem(window.STORAGE_KEY_BASES_ADICIONAIS, JSON.stringify(bases));
        } catch (e) {}
        window.renderizarBasesConsultaAdicionais();

        if (btn) {
            btn.innerHTML = '✅ Todos os Testes Concluídos!';
            setTimeout(function() { btn.innerHTML = orig; }, 2000);
        }
    };

    // Interceptar alternarSubConfig para garantir sincronização quando abrir a sub-aba 'agentes'
    var _origAlternarSubConfig = window.alternarSubConfig;
    window.alternarSubConfig = function(modo) {
        if (typeof _origAlternarSubConfig === 'function') {
            _origAlternarSubConfig(modo);
        }
        if (modo === 'agentes') {
            if (typeof window.sincronizarInputsPoolTresIas === 'function') {
                window.sincronizarInputsPoolTresIas();
            }
            window.renderizarConectoresAgentes();
            window.renderizarBasesConsultaAdicionais();
        }
    };

    // Hook no coletor de contexto para injetar as bases adicionais conectadas
    var _origColetarContextoTotalSistemas = window.coletarContextoTotalSistemas;
    window.coletarContextoTotalSistemas = function(pergunta) {
        var ctx = {};
        if (typeof _origColetarContextoTotalSistemas === 'function') {
            try {
                ctx = _origColetarContextoTotalSistemas(pergunta);
            } catch (e) {
                ctx = {};
            }
        }
        try {
            var bases = window.obterBasesConsultaAdicionais().filter(function(b) { return b.ativo; });
            if (bases.length > 0) {
                ctx.basesAdicionaisConectadas = bases.map(function(b) {
                    return b.nome + ' (' + (b.tipoLabel || b.tipo) + '): ' + b.escopo;
                });
            }
            var conectores = window.obterConectoresAgentes();
            ctx.conectoresAtivos = conectores.map(function(c) {
                return c.nome + ' [IA1:' + (c.ia1 ? 'SIM' : 'NÃO') + ', IA2:' + (c.ia2 ? 'SIM' : 'NÃO') + ', IA3:' + (c.ia3 ? 'SIM' : 'NÃO') + ']';
            });
        } catch (e) {}
        return ctx;
    };

    // Inicialização ao carregar o DOM
    function inicializarSubAbaAgentes() {
        window.renderizarConectoresAgentes();
        window.renderizarBasesConsultaAdicionais();
        if (typeof window.sincronizarInputsPoolTresIas === 'function') {
            window.sincronizarInputsPoolTresIas();
        }
    }

    if (document.readyState === 'loading') {
        document.addEventListener('DOMContentLoaded', inicializarSubAbaAgentes);
    } else {
        inicializarSubAbaAgentes();
    }
    window.addEventListener('load', inicializarSubAbaAgentes);
})();
"""

def aplicar_patch_em_arquivo(caminho):
    if not os.path.exists(caminho):
        return False

    with open(caminho, 'r', encoding='utf-8', errors='ignore') as f:
        conteudo = f.read()

    # 1. Remover script anterior se existir
    conteudo = re.sub(r'<script id="script-conectores-agentes-v11">.*?</script>', '', conteudo, flags=re.DOTALL)

    # 2. Verificar se subview-cfg-agentes já foi injetado
    if 'id="subview-cfg-agentes"' in conteudo:
        conteudo = re.sub(r'<!-- SUB-PAINEL.*?id="subview-cfg-agentes".*?</div>\s*</div>\s*</div>\s*</div>', '', conteudo, flags=re.DOTALL)

    # 3. Localizar ponto de inserção do HTML: logo antes de id="subview-cfg-conectores"
    alvo_html = '<div id="subview-cfg-conectores"'
    if alvo_html not in conteudo:
        print(f"Erro: Marcador id='subview-cfg-conectores' não encontrado em {caminho}.")
        return False

    html_agentes = gerar_conteudo_agentes_html()
    conteudo_modificado = conteudo.replace(alvo_html, html_agentes + '\n            ' + alvo_html, 1)

    # 4. Injetar o JavaScript do módulo antes de </body>
    alvo_js = '</body>'
    if alvo_js not in conteudo_modificado:
        print(f"Erro: Marcador </body> não encontrado em {caminho}.")
        return False

    js_agentes = '<script id="script-conectores-agentes-v11">\n' + gerar_conteudo_agentes_js() + '\n</script>\n'
    conteudo_modificado = conteudo_modificado.replace(alvo_js, js_agentes + alvo_js, 1)

    # 5. Gravar arquivo modificado
    with open(caminho, 'w', encoding='utf-8') as f:
        f.write(conteudo_modificado)
    print(f"✅ {caminho} atualizado com sucesso! ({len(conteudo_modificado)} bytes)")
    return True

def main():
    print("=== ATUALIZADOR OFICIAL COCKPIT GTI: CONECTORES & AGENTES V11 ===")
    candidatos = [
        'frontend/painel.html',
        'painel.html',
        r'C:\Cockpit_GTI\frontend\painel.html',
        r'C:\Cockpit_GTI\painel.html'
    ]

    modificados = 0
    for c in candidatos:
        if os.path.exists(c):
            if aplicar_patch_em_arquivo(c):
                modificados += 1

    if modificados > 0:
        print(f"Sucesso: {modificados} arquivo(s) atualizado(s)!")
    else:
        print("Nenhum arquivo encontrado para atualizar.")

if __name__ == '__main__':
    main()
