from .consulta_llm.consulta_llm import consulta_LLM
from .notas_cte import *
from .consultar_notas.consultar_notas_pdf import consultar_notas_pdf_no_servidor
from Listas.lista import ESPEC, TES  # esse fica absoluto porque está fora
import json

texto = """Você é um sistema de extração de dados de documentos fiscais brasileiros.

Antes de responder:

Analise com calma e atenção todo o conteúdo do documento.
Revise internamente todas as regras antes de gerar a resposta.
Priorize precisão, consistência e validação dos campos.
Não responda rapidamente: valide primeiro, responda depois.
Faça uma verificação final completa antes de responder.
Verifique novamente se os cálculos, comparações e regras obrigatórias estão corretos antes de retornar o JSON final.
Em caso de dúvida, use null em vez de inventar valores.

Sua resposta DEVE seguir estas regras obrigatórias:

Retorne apenas um objeto JSON válido.
Não use markdown, blocos de código, comentários ou explicações.
Retorne todos os campos em uma única linha.
Todos os valores monetários devem ter ponto decimal e 2 casas.
Campos ausentes devem ser null.

Identificação do tipo de documento:

Se o texto contiver "DACTE", o tipo é "CTE".
Se o texto contiver "NOTA FISCAL" ou "NFS-e" ou "DANFSe", o tipo é "NFS".
Se não contiver nenhum dos termos acima, o tipo é "CF".
Compare o tipo de documento enviado com o tipo real identificado no texto.
Se houver divergência, retorne:
{"erro":"True","motivo":"Tipo de documento enviado diferente do tipo real identificado no documento. Cancelar lançamento."}

Número da nota:

Extraia apenas o número principal do documento, removendo zeros à esquerda e ignorando série, DPS, RPS, chave de acesso, protocolo ou outros números.
Compare o número filtrado do documento diretamente com o número completo informado pelo sistema, se o numero da nota for "xx/yyyy" considerar apenas "xx"
Se "xx" filtrado não coincidir exatamente, retorne imediatamente:(ex: 27 e sistema 272026)
{"erro":"True","motivo":informe o motivo}

Impostos:

Considere que há imposto apenas quando valor_liquido for diferente de valor_total.
contem_imposto = "True" somente se valor_total != valor_liquido.
contem_imposto = "False" se valor_total == valor_liquido.
valor_impostos = valor_total - valor_liquido se houver imposto, caso contrário "0.00".

Ajuste de tipo e natureza:

Se houver imposto retido e o tipo for "NFS", ajuste Tipo_nota para "NFPS".
Se não houver imposto retido e o tipo for "NFS", Tipo_nota permanece "NFS".
Se o tipo identificado for "CTE", Tipo_nota = "CTE".
Se o tipo identificado for "CF", Tipo_nota = "CF".
natureza = "PXX003" se houver imposto, caso contrário "PXX001".

Campos a extrair:
{"Tipo_nota": null,"numero_nota": null,"data_emissao": null,"AC":"null","data_vencimento": null,"cnpj_emitente": null,"valor_total": null,"valor_liquido": null,"contem_imposto": null,"valor_impostos": null,"natureza": null}

Regras de consistência obrigatória:

Se valor_total == valor_liquido:
contem_imposto = "False", valor_impostos = "0.00", natureza = "PXX001".
Se valor_total != valor_liquido:
contem_imposto = "True", valor_impostos = valor_total - valor_liquido, natureza = "PXX003".
valor_impostos deve ser sempre formatado com 2 casas decimais.

Regras de validação com dados de comparação:

Compare todos os dados extraídos com os dados fornecidos pelo sistema (CNPJ, número da nota completo, data de emissão, valor total, tipo de documento).
Qualquer divergência relevante deve retornar:
{"erro":"True","motivo":"Divergencia entre os dados fornecidos pelo sistema e os dados da nota."}

Regras de prioridade na extração:

Sempre priorize campos explicitamente identificados no documento.
Para múltiplos valores, datas ou CNPJs, priorize:
valor_total final
data_emissao principal
CNPJ do emitente/prestador/remetente
Para data_vencimento, procure também em descrições, observações, fatura, boleto ou dados adicionais.
Se houver ambiguidade real, use null.

Formatação final obrigatória:

Retornar apenas o JSON final em uma linha.
Todos os campos obrigatórios devem estar presentes.
Use null se não for possível identificar um valor.
"""

def conferir_serie_e_especie(caminho):
    if ("CF" in caminho and "F" in caminho[10]) or ("NF" in caminho  and caminho[10] != "F"):
        print("SERIE OU ESPECIE ERRADA")
        return False
    return True

def encontrar_nota(dados, filial, dados_de_comparacao, teste=False):
    tipo_nota = None
    print("Dados de comparação recebidos:", dados_de_comparacao)

    prompt = texto

    # identifica se vai ser CTE
    print(len(dados))
    if len(dados) > 30:
        print("CTE:", dados)
        tipo_nota = ESPEC[3]
        #realizar desenvolvimento de lancar notas via CTE
        #montagem de caminho
        aaaaa = encontrar_notas_CTE()
        print(aaaaa)
        return aaaaa
    #######################################    
    if conferir_serie_e_especie(dados):    
        print("Dados para nota:", dados)
        print("====================")
        dados = dados.replace("|", "")
        print("Dados para nota ajustado:", dados)
        print("====================")
    else: 
        return "Serie errada"
    #######################################
    # pega o tipo de nota e a TES
    if tipo_nota != ESPEC[3]:
        tipo_nota = None
        for x in ESPEC:
            if x in dados:
                print("ESPEC:", x, "TES:", TES[x])
                tipo_nota = x
                break

    if tipo_nota is None:
        tipo_nota = ESPEC[4]

    if "NF" in dados:
        dados = dados.replace(" ", "")
        dados = dados.replace("F", "f__", 1)
    if "NFS" in dados:
        dados = dados[:-3]
    else:
        dados = dados[:-2]

    # ADICIONA DADOS DO SISTEMA PARA COMPARAR COM A NOTA
    #######################################
    #######################################
    print("TIPO DE NOTA:", tipo_nota)
    prompt += "\nNumero da nota para comparação: " + str(dados_de_comparacao[3]).strip()
    prompt += "\nTipo de nota para comparação: " + str(dados_de_comparacao[0]).strip()
    prompt += "\nData de emissão para comparação: " + str(dados_de_comparacao[1]).strip()
    prompt += "\nValor bruto para comparação: " + str(dados_de_comparacao[2]).strip()

    #DADOS FINAIS = CAMINHA DA NOTA NO SERVIDOR
    print("Dados finais para nota:", dados)

    pdfs_encontrados, texto_final = consultar_notas_pdf_no_servidor(filial, dados)

    if pdfs_encontrados == 0:
        print("Nenhum PDF encontrado dentro da pasta da nota.")
        return {"erro": "True", "motivo": "Não foi encontrado nem um PDF"}

    if not texto_final.strip():
        print("Nenhum texto foi extraído dos PDFs.")
        print("OBS: Isso geralmente significa que o PDF é escaneado (imagem) e não texto.")
        return {"erro": "True", "motivo": "Não foi possível ler o PDF"}

    prompt += "\n\nTEXTO DO DOCUMENTO:\n" + texto_final

    print("####################################")
    print("PROMPT ENVIADO AO LLM")
    print("####################################")
    print(prompt)
          
    dados_json = consulta_LLM(prompt)

    if dados_json is None:
        print("LLM retornou None.")
        return None

    try:
        dados_json = json.loads(dados_json)
    except json.JSONDecodeError as e:
        print("Erro ao converter JSON digitado:", e)
        return None

    print("JSON convertido:")
    print(dados_json)


    return dados_json
#                   chave da nota;                              filial   [          dados para comparação              ]
# encontrar_nota('41260410300672000176550010000009201727280014', "030201", ['CF   ', '06/02/2026', '4500.00', '000001000'])
encontrar_nota('000001071|F|037101|01|NFS', "030201", ['CF   ', '06/02/2026', '4500.00', '000001000'])

