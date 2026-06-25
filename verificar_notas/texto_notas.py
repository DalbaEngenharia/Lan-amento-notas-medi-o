from .consulta_llm.consulta_llm import consulta_LLM
from .consultar_notas.consultar_notas_pdf import consultar_notas_pdf_no_servidor
from Listas.lista import ESPEC, TES
import json


print("====================================")
print("INICIANDO ARQUIVO")
print("====================================")

with open("verificar_notas/consulta_llm/verificacao_tipo.txt", "r", encoding="utf-8") as arquivo_verifica:
    texto_verificação = arquivo_verifica.read()

print("Arquivo verificacao_tipo.txt carregado")


def setar_prompt(tipo_nota, dados_de_comparacao, modelo_llm):

    print("====================================")
    print("ENTROU NA FUNÇÃO setar_prompt")
    print("====================================")
    print("tipo_nota:", tipo_nota)
    print("modelo_llm:", modelo_llm)
    print("dados_de_comparacao:", dados_de_comparacao)

    if modelo_llm in ["NFS",  "CF", "SPED"]:
        print("Carregando prompt NFS/CF")

        with open("verificar_notas/consulta_llm/texto_llm_nfs_cf.txt", "r", encoding="utf-8") as arquivo:
            texto = arquivo.read()

    if modelo_llm == "CTE":
        print("Carregando prompt CTE")

        with open("verificar_notas/consulta_llm/texto_llm_cte.txt", "r", encoding="utf-8") as arquivo:
            texto = arquivo.read()
    

    prompt = texto

    print("TIPO DE NOTA:", tipo_nota)

    prompt += "\nNumero da nota para comparação: " + str(dados_de_comparacao[3]).strip()
    prompt += "\nTipo informado pelo sistema (NÃO VALIDAR, apenas contexto): " + str(dados_de_comparacao[0]).strip()
    prompt += "\nData de emissão para comparação: " + str(dados_de_comparacao[1]).strip()
    prompt += "\nValor bruto para comparação: " + str(dados_de_comparacao[2]).strip()
    prompt += "\n\nTEXTO DO DOCUMENTO:\n"

    print("Prompt montado com sucesso")
    print("Tamanho do prompt:", len(prompt))

    return prompt


def conferir_serie_e_especie(caminho):

    print("====================================")
    print("ENTROU NA FUNÇÃO conferir_serie_e_especie")
    print("====================================")
    print("Caminho recebido:", caminho)

    if ("CF" in caminho and "F" in caminho[10]) or ("NF" in caminho and caminho[10] != "F"):
        print("SERIE OU ESPECIE ERRADA")
        return False

    print("Série e espécie OK")
    return True


def encontrar_nota(caminho_nota_servidor, chave, filial, dados_de_comparacao, teste=False):

    print("====================================")
    print("INICIANDO encontrar_nota")
    print("====================================")

    tipo_nota = None

    print("Dados recebidos:")
    print("caminho_nota_servidor:", caminho_nota_servidor)
    print("chave:", chave)
    print("filial:", filial)
    print("dados_de_comparacao:", dados_de_comparacao)
    print("teste:", teste)

    print("Tamanho da chave:", len(chave))

    #######################################
    print("Validando série e espécie")

    if conferir_serie_e_especie(chave):
        print("Validação OK")
    else:
        print("Retornando erro de série")
        return "Serie errada"

    #######################################

    print("Dados finais para nota:", caminho_nota_servidor)

    print("Chamando consultar_notas_pdf_no_servidor")

    pdfs_encontrados, texto_final = consultar_notas_pdf_no_servidor(
        filial,
        caminho_nota_servidor
    )

    print("Quantidade de PDFs encontrados:", pdfs_encontrados)
    print("Tamanho texto extraído:", len(texto_final))

    if pdfs_encontrados == 0:
        print("Nenhum PDF encontrado dentro da pasta da nota.")

        return {
            "erro": "True",
            "motivo": "Não foi encontrado nem um PDF"
        }

    if not texto_final.strip():

        print("Nenhum texto foi extraído dos PDFs.")
        print("OBS: Isso geralmente significa que o PDF é escaneado (imagem) e não texto.")

        return {
            "erro": "True",
            "motivo": "Não foi possível ler o PDF"
        }

    print("####################################")
    print("PROMPT ENVIADO AO LLM")
    print("####################################")

    print("Tamanho texto verificação:", len(texto_verificação))
    print("Tamanho texto final:", len(texto_final))
    print(texto_verificação + texto_final)
    verificacao = consulta_LLM(texto_verificação + texto_final)

    print("====================================")
    print("RETORNO VERIFICAÇÃO LLM")
    print("====================================")
    #print(verificacao)
    print("Tipo esperado:", dados_de_comparacao[0].strip())
    print("Tipo identificado:", verificacao)

    if (dados_de_comparacao[0].strip() == verificacao) or (dados_de_comparacao[0].strip()=='CF' and verificacao=='CTE' or (dados_de_comparacao[0].strip()=='NFPS' and verificacao=='NFS') or (dados_de_comparacao[0].strip()=='NFS' and verificacao=='NFPS')
    ):

        print("TIPO CONFIRMADO PELO LLM")
        print("HELL YEAH")

        prompt = setar_prompt(tipo_nota,dados_de_comparacao,modelo_llm=verificacao)

        print("Tamanho prompt antes do texto:", len(prompt))

        prompt = prompt + texto_final

        print("Tamanho prompt final:", len(prompt))

        #################################

        print("Chamando consulta_LLM para JSON")

        dados_json = consulta_LLM(prompt)

        print("Retorno bruto do LLM:")
        print(dados_json)

    else:
        print("TIPO NÃO CONFERE")
        print("Esperado:", dados_de_comparacao[0].strip())
        print("Recebido:", verificacao)
        return {
                "erro": True,
                "motivo": "Espécie de documento divergente da nota para o sistema"
                }
    
    if dados_json is None:

        print("LLM retornou None.")
        return None

    try:

        print("Convertendo JSON")

        dados_json = json.loads(dados_json)

        print("JSON convertido com sucesso")

    except json.JSONDecodeError as e:

        print("====================================")
        print("ERRO AO CONVERTER JSON")
        print("====================================")
        print(e)

        return None

    print("====================================")
    print("JSON FINAL")
    print("====================================")

    print(dados_json)

    print("====================================")
    print("FINALIZANDO encontrar_nota")
    print("====================================")

    return dados_json

def consultar_impostos_nota(caminho_nota_servidor, filial):

    pdfs_encontrados, texto_final = consultar_notas_pdf_no_servidor(
        filial,
        caminho_nota_servidor
    )

    if pdfs_encontrados == 0:
        return None

    with open(
        "verificar_notas/consulta_llm/consulta_impostos.txt",
        "r",
        encoding="utf-8"
    ) as arquivo_verifica:
        prompt = arquivo_verifica.read()

    prompt += texto_final

    retorno = consulta_LLM(prompt)

    retorno = (
        retorno
        .replace("```json", "")
        .replace("```", "")
        .strip()
    )


    return json.loads(retorno)
