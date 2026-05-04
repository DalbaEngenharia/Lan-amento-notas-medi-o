import pyodbc
import csv
import sys
import os

sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(__file__))))
from Listas.lista import filiais

# pasta saída
pasta_saida = "resultados"
os.makedirs(pasta_saida, exist_ok=True)


def consultar_banco(filial):
    conn = None
    cursor = None

    try:
        # conexão
        conn = pyodbc.connect(
            "DRIVER={PostgreSQL ANSI(x64)};"
            "SERVER=192.168.254.212;"
            "PORT=5432;"
            "DATABASE=prd;"
            "UID=gustavo.elicker;"
            "PWD=ge9550;"
        )

        cursor = conn.cursor()

        print(f"Consultando filial {filial}...")

        sql = f"""
            select DISTINCT
                f1_filial,
                f1_doc,
                f1_serie,
                f1_fornece
            from vwsf1010 f1

            left join vwsd1010 d1
                on d1.d_e_l_e_t_ = ''
            and f1_filial = d1_filial
            and f1_doc = d1_doc
            and f1_serie = d1_serie
            and f1_fornece = d1_fornece
            and f1_loja = d1_loja

            left join vwsc7010 c7
                on c7.d_e_l_e_t_ = ''
            and d1_filial = c7_filial
            and d1_pedido = c7_num
            and d1_itempc = c7_item
            and d1_fornece = c7_fornece
            and d1_loja = c7_loja

            where f1.d_e_l_e_t_ = ''
            and f1_status = ''
            and c7_medicao <> ''
            and f1_filial = '{filial}'
        """

        cursor.execute(sql)

        resultados = cursor.fetchall()
        resultados = []

        # nome do arquivo csv
        arquivo = os.path.join(pasta_saida, "resultado.csv")

        with open(arquivo, mode="w", newline="", encoding="utf-8-sig") as file:
            writer = csv.writer(file, delimiter=";")

            # cabeçalho
            colunas = [col[0] for col in cursor.description]
            writer.writerow(colunas)

        #     # dados
            for linha in resultados:
                writer.writerow(linha)

        print(f"Filial {filial}: {len(resultados)} registros salvos")

        return len(resultados)
    except Exception as e:
        print("Erro:", e)

    finally:
        if cursor:
            cursor.close()
        if conn:
            conn.close()