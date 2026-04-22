
def montar_retorno_nao_lancada(dados_lancadas, filial, fornecedor, nota, motivo):
    dados_lancadas.append("STATUS: NAO_LANCADA")
    dados_lancadas.append("FILIAL: " + str(filial))
    dados_lancadas.append("FORNECEDOR: " + str(fornecedor))
    dados_lancadas.append("NOTA: " + str(nota))
    dados_lancadas.append("MOTIVO: " + str(motivo))
    return False, dados_lancadas


def montar_retorno_lancada(dados_lancadas, filial, fornecedor, nota):
    dados_lancadas.append("STATUS: LANCADA")
    dados_lancadas.append("FILIAL: " + str(filial))
    dados_lancadas.append("FORNECEDOR: " + str(fornecedor))
    dados_lancadas.append("NOTA: " + str(nota))
    return True, dados_lancadas
