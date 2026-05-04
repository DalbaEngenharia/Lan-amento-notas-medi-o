import os
import time
import google.genai as genai
from Protheus_Biblioteca import log

def consulta_LLM(texto):
    api_key = os.getenv("GEMINI_API_KEY")

    if not api_key:
        log("[LLM] ERRO: variável de ambiente GEMINI_API_KEY não encontrada.")
        return None

    client = genai.Client(api_key=api_key)

    tentativa = 0

    while True:
        tentativa += 1

        try:
            log(f"[LLM] Tentativa {tentativa}...")

            # response = client.models.generate_content(
            #     model="gemini-2.5-flash",
            #     contents=texto
            # )

            # if response is None:
            #     log("[LLM] Resposta do modelo veio None.")
            #     raise Exception("Resposta None do modelo")

            # resposta_texto = getattr(response, "text", None)
            resposta_texto = '{"erro":"True","motivo":"Tipo de documento enviado diferente do tipo real identificado no documento. Cancelar lançamento."}'
            if not resposta_texto or not resposta_texto.strip():
                log("[LLM] response.text veio vazio.")
                raise Exception("response.text vazio")

            log("[LLM] Resposta recebida com sucesso.")
            log(f"[LLM] Tamanho da resposta: {len(resposta_texto)} chars")
            log(f"[LLM] Prévia: {resposta_texto[:200]}...")

            return resposta_texto

        except Exception as e:
            erro_str = str(e)

            erro_transitorio = any(x in erro_str for x in [
                "503",
                "UNAVAILABLE",
                "429",
                "RESOURCE_EXHAUSTED",
                "DeadlineExceeded",
                "timeout",
                "timed out",
                "Connection reset",
                "ServiceUnavailable",
                "InternalServerError"
            ])

            log(f"[LLM] Erro na tentativa {tentativa}: {erro_str}")

            if not erro_transitorio:
                log("[LLM] Erro não transitório. Abortando sem retry.")
                return None
            espera = 10
            log(f"[LLM] Erro transitório. Aguardando {espera}s para retry...")
            time.sleep(espera)