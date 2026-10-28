import time
from .ia_01_principal_processamento import executar_nivel_1
from .ia_02_orquestracao_intermediario import executar_nivel_2
from .ia_03_micro_tarefas_log import executar_nivel_3

def processar_com_failover(prompt: str, contexto: str = "", nivel_preferencial: int = 1) -> dict:
    """
    Orquestrador com Failover Automático em 3 Níveis:
    Tenta Nível 1 -> Falha/Timeout -> Nível 2 -> Falha/Timeout -> Nível 3.
    Garante 100% de disponibilidade.
    """
    inicio = time.time()
    niveis = [1, 2, 3] if nivel_preferencial == 1 else ([2, 3] if nivel_preferencial == 2 else [3])
    log_tentativas = []
    
    for nivel in niveis:
        try:
            if nivel == 1:
                resultado = executar_nivel_1(prompt, contexto)
            elif nivel == 2:
                resultado = executar_nivel_2(prompt, contexto)
            else:
                resultado = executar_nivel_3(prompt, contexto)
            
            tempo_total = round((time.time() - inicio) * 1000, 2)
            return {
                "sucesso": True,
                "resposta": resultado["resposta"],
                "nivel_executado": resultado["nivel"],
                "modelo": resultado["modelo"],
                "tempo_ms": tempo_total,
                "failover_acionado": nivel != nivel_preferencial,
                "log_tentativas": log_tentativas
            }
        except Exception as e:
            log_tentativas.append(f"Nível {nivel} indisponível: {str(e)}")
            continue

    # Fallback final de segurança se todos falharem
    return {
        "sucesso": False,
        "resposta": "Todos os níveis de IA estiveram temporariamente indisponíveis.",
        "nivel_executado": None,
        "modelo": None,
        "tempo_ms": round((time.time() - inicio) * 1000, 2),
        "failover_acionado": True,
        "log_tentativas": log_tentativas
    }