import pyodbc


def consultar_codigo_do_municipio(uf, municipio):

    conn = pyodbc.connect(
        "DRIVER={PostgreSQL ANSI(x64)};"
        "SERVER=192.168.254.212;"
        "PORT=5432;"
        "DATABASE=prd;"
        "UID=gustavo.elicker;"
        "PWD=ge9550;"
    )

    cursor = conn.cursor()

    uf = uf.strip().upper()
    municipio = municipio.strip().upper()

    sql = """
        SELECT cc2_est, cc2_codmun, cc2_mun
        FROM cc2010
        WHERE d_e_l_e_t_ = ''
          AND TRIM(cc2_est) = ?
          AND TRIM(cc2_mun) = ?
          AND TRIM(cc2_codmun) <> ''
    """

    cursor.execute(sql, (uf, municipio))

    resultados = cursor.fetchall()

    print(f"Consulta banco resultados: {resultados}")

    if not resultados:
        cursor.close()
        conn.close()

        print(
            f"Nenhum município encontrado: "
            f"UF={uf}, MUNICÍPIO={municipio}"
        )

        return None

    linha = resultados[0]

    estado = linha[0].strip()
    codigo = linha[1].strip()
    municipio_banco = linha[2].strip()

    print(
        f"Estado: {estado} | "
        f"Código: {codigo} | "
        f"Município: {municipio_banco}"
    )

    cursor.close()
    conn.close()

    return codigo