import os
from pathlib import Path
def limpeza(): 

    # Caminho da pasta
    pasta = r"C:\Users\gustavo.elicker\Desktop\PROGRAMAS\AUTOMAÇÂO_NOTAS_CONTRATO"   # <- troque aqui

    # Converter para objeto Path
    p = Path(pasta)

    # Verificar se existe
    if not p.exists() or not p.is_dir():
        print("Pasta inválida!")
    else:
        apagados = 0

        for arquivo in p.iterdir():
            if arquivo.is_file() and arquivo.suffix.lower() == ".pdf":
                try:
                    arquivo.unlink()  # apaga o arquivo
                    print(f"Apagado: {arquivo.name}")
                    apagados += 1
                except Exception as e:
                    print(f"Erro ao apagar {arquivo.name}: {e}")

        print(f"\nTotal de PDFs apagados: {apagados}")
