import os
import sys
import subprocess

# ============================================================
# CONFIGURAÇÃO
# ============================================================

ARQUIVO_ROBO = "main.py"

# ============================================================
# DIRETÓRIO
# ============================================================

if getattr(sys, "frozen", False):
    BASE_DIR = os.path.dirname(sys.executable)
else:
    BASE_DIR = os.path.dirname(os.path.abspath(__file__))

CAMINHO_ROBO = os.path.join(BASE_DIR, ARQUIVO_ROBO)

# ============================================================
# EXECUÇÃO CONTÍNUA
# ============================================================

print("=" * 60)
print("SUPERVISOR INICIADO")
print(f"Arquivo: {CAMINHO_ROBO}")
print("=" * 60)

while True:

    print()
    print("=" * 60)
    print("INICIANDO ROBÔ")
    print("=" * 60)

    try:

        resultado = subprocess.run(
            [sys.executable, CAMINHO_ROBO],
            cwd=BASE_DIR
        )

        print()
        print("ROBÔ FINALIZADO")
        print(f"Código de saída: {resultado.returncode}")
        print("INICIANDO NOVA EXECUÇÃO...")

    except Exception as erro:

        print()
        print("ERRO AO EXECUTAR O ROBÔ:")
        print(erro)
        print("TENTANDO NOVAMENTE...")


# Não existe sleep aqui.
# Quando o processo terminar, o while executa novamente.