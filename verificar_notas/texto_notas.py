from .consulta_llm.consulta_llm import consulta_LLM
from .notas_cte import *
from .consultar_notas.consultar_notas_pdf import consultar_notas_pdf_no_servidor
from Listas.lista import ESPEC, TES  # esse fica absoluto porque está fora
import json

with open("textoLLm.txt", "r", encoding="utf-8") as arquivo:
    texto = arquivo.read()

def conferir_serie_e_especie(caminho):
    if ("CF" in caminho and "F" in caminho[10]) or ("NF" in caminho  and caminho[10] != "F"):
        print("SERIE OU ESPECIE ERRADA")
        return False
    return True

def encontrar_nota(caminho_nota_servidor, chave, filial, dados_de_comparacao, teste=False):
    tipo_nota = None
    print("Dados de comparação recebidos:", dados_de_comparacao)

    prompt = texto

    # identifica se vai ser CTE
    print(len(chave))
    if len(chave) > 30:
        None
    #######################################    
    if conferir_serie_e_especie(chave):    
       None
    else: 
        return "Serie errada"
    #######################################
    # pega o tipo de nota e a TES

    # ADICIONA DADOS DO SISTEMA PARA COMPARAR COM A NOTA
    #######################################
    #######################################
    print("TIPO DE NOTA:", tipo_nota)
    prompt += "\nNumero da nota para comparação: " + str(dados_de_comparacao[3]).strip()
    prompt += "\nTipo de nota para comparação: " + str(dados_de_comparacao[0]).strip()
    prompt += "\nData de emissão para comparação: " + str(dados_de_comparacao[1]).strip()
    prompt += "\nValor bruto para comparação: " + str(dados_de_comparacao[2]).strip()

    #DADOS FINAIS = CAMINHA DA NOTA NO SERVIDOR
    print("Dados finais para nota:", caminho_nota_servidor)

    pdfs_encontrados, texto_final = consultar_notas_pdf_no_servidor(filial, caminho_nota_servidor)

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
