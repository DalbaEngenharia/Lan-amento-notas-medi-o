import os
import time
import random
import google.genai as genai


def consulta_LLM(texto, max_tentativas=5):
    api_key = os.getenv("GEMINI_API_KEY")

    if not api_key:
        print("[LLM] ERRO: variável de ambiente GEMINI_API_KEY não encontrada.")
        return None

    client = genai.Client(api_key=api_key)

    for tentativa in range(1, max_tentativas + 1):
        try:
            print(f"[LLM] Tentativa {tentativa}/{max_tentativas}...")

            response = client.models.generate_content(
                model="gemini-2.5-flash",
                contents=texto
            )

            if response is None:
                print("[LLM] Resposta do modelo veio None.")
                raise Exception("Resposta None do modelo")

            resposta_texto = getattr(response, "text", None)

            if not resposta_texto or not resposta_texto.strip():
                print("[LLM] response.text veio vazio.")
                raise Exception("response.text vazio")

            print("[LLM] Resposta recebida com sucesso:")
            print(resposta_texto)

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

            print(f"[LLM] Erro na tentativa {tentativa}: {e}")

            if not erro_transitorio:
                print("[LLM] Erro não transitório. Abortando sem retry.")
                return None

            if tentativa == max_tentativas:
                print("[LLM] Máximo de tentativas atingido. Abortando.")
                return None

            espera = min((2 ** tentativa) + random.uniform(0, 1.5), 30)
            print(f"[LLM] Erro transitório detectado. Aguardando {espera:.1f}s antes de tentar novamente...")
            time.sleep(espera)

    return None