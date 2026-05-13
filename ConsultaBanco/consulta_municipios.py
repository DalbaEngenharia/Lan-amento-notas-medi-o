import pyodbc
from openpyxl import Workbook

def consultar_codigo_do_municipio(uf ,municipio ):
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

    uf = uf.upper()
    municipio = municipio.upper()

    sql = f"""
    select cc2_est, cc2_codmun, cc2_mun
    from cc2010 
    where d_e_l_e_t_ = ''
    and cc2_est = '{uf}'
    and cc2_mun = '{municipio}'
    and cc2_codmun <> ''
    """

    # executa a consulta
    cursor.execute(sql)

    # busca os resultados
    resultados = cursor.fetchall()

    # imprime os resultados
    for linha in resultados:
        estado = linha[0].strip()
        codigo = linha[1].strip()
        municipio = linha[2].strip()

        print(estado, codigo, municipio)

    # fecha conexão
    cursor.close()
    conn.close()
    return codigo
