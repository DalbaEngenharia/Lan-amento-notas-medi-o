import pdfplumber
from teste import consulta_LLM
from smb.SMBConnection import SMBConnection
from lista import ESPEC, TES
import time
from datetime import datetime
import os
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

def extrair_pdf(caminho):
    texto_pdf = ""
    try:
        with pdfplumber.open(caminho) as pdf:
            for i, pagina in enumerate(pdf.pages, start=1):
                conteudo = pagina.extract_text()
                if conteudo:
                    texto_pdf += conteudo + "\n"
                else:
                    print(f"[PDF] Página {i} sem texto extraível (pode ser PDF escaneado/imagem).")
    except Exception as e:
        print(f"[PDF] Erro ao abrir/extrair {caminho}: {e}")
    return texto_pdf

def baixar_arquivo_smb(conn, service_name, remote_path, local_path, timeout=20):
    """
    Faz download do arquivo SMB com logs.
    """
    try:
        print(f"[SMB] Iniciando download: {remote_path}")
        inicio = time.time()

        with open(local_path, "wb") as f:
            # timeout aqui ajuda a não ficar pendurado eternamente
            conn.retrieveFile(service_name, remote_path, f, timeout=timeout)

        fim = time.time()
        tamanho = os.path.getsize(local_path) if os.path.exists(local_path) else 0
        print(f"[SMB] Download concluído em {fim - inicio:.2f}s | {tamanho} bytes")
        return True

    except Exception as e:
        print(f"[SMB] Erro no download de {remote_path}: {e}")
        return False

def encontrar_nota(dados, filial, dados_de_comparacao, teste=False):

    print("Dados de comparação recebidos:", dados_de_comparacao)

    inicio_total = time.time()
    prompt = texto

    # identifica se vai ser CTE
    if len(dados) > 30:
        print("CTE:", dados)
    if conferir_serie_e_especie(dados):    
        print("Dados para nota:", dados)
        print("====================")
        dados = dados.replace("|", "")
        print("Dados para nota ajustado:", dados)
        print("====================")
    else: 
        return "Serie errada"

    # pega o tipo de nota e a TES
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

    print("TIPO DE NOTA:", tipo_nota)
    prompt += "\nNumero da nota para comparação: " + str(dados_de_comparacao[3]).strip()
    prompt += "\nTipo de nota para comparação: " + str(dados_de_comparacao[0]).strip()
    prompt += "\nData de emissão para comparação: " + str(dados_de_comparacao[1]).strip()
    prompt += "\nValor bruto para comparação: " + str(dados_de_comparacao[2]).strip()

    if "NFS" in dados:
        dados = dados[:-3]
    else:
        dados = dados[:-2]

    print("Dados finais para nota:", dados)

    # TEMPORÁRIO (você pediu pra ignorar usuário/senha)
    username = "comp_dalba"
    password = "CYtBXO6w"

    conn = SMBConnection(
        username,
        password,
        "python_client",
        "10.40.58.4",
        use_ntlm_v2=True,
        is_direct_tcp=True
    )

    try:
        print("[SMB] Conectando...")
        conectado = conn.connect("10.40.58.4", 445, timeout=10)
        if not conectado:
            print("[SMB] Não foi possível conectar ao SMB.")
            return None
        print("[SMB] Conectado com sucesso.")
    except Exception as e:
        print(f"[SMB] Erro ao conectar: {e}")
        return None

    caminho = f"/sf1010_{filial}"
    caminho_nota = f"{caminho}/{dados}"

    print(f"[SMB] Caminho base: {caminho}")
    print(f"[SMB] Caminho da nota: {caminho_nota}")

    try:
        arquivos_nota = conn.listPath("custom", caminho_nota)
        print(f"[SMB] {len(arquivos_nota)} itens encontrados na pasta.")
    except Exception as e:
        print(f"[SMB] Erro ao listar pasta SMB: {e}")
        conn.close()
        return None

    texto_final = ""
    pdfs_encontrados = 0

    for a in arquivos_nota:
        # ignora . e ..
        if a.filename in [".", ".."]:
            continue

        if a.filename.lower().endswith(".pdf"):
            pdfs_encontrados += 1
            print(f"\n[PDF] Arquivo dentro da nota: {a.filename}")
            print(f"[PDF] Tamanho informado pelo SMB: {getattr(a, 'file_size', 'desconhecido')} bytes")

            remote = f"{caminho_nota}/{a.filename}"
            local = f"temp_{a.filename}"

            try:
                ok = baixar_arquivo_smb(conn, "custom", remote, local, timeout=20)
                if not ok:
                    print(f"[PDF] Pulando arquivo por falha no download: {a.filename}")
                    continue

                if not os.path.exists(local) or os.path.getsize(local) == 0:
                    print(f"[PDF] Arquivo local vazio ou inexistente: {local}")
                    continue

                texto_nota = extrair_pdf(local)

                if texto_nota.strip():
                    print(f"[PDF] Texto extraído com sucesso ({len(texto_nota)} chars)")
                    texto_final += texto_nota + "\n"
                else:
                    print(f"[PDF] Nenhum texto extraído de {a.filename} (provável PDF imagem).")

            except Exception as e:
                print(f"[PDF] Erro ao processar PDF {a.filename}: {e}")

            finally:
                if os.path.exists(local):
                    try:
                        os.remove(local)
                    except Exception as e:
                        print(f"[TEMP] Não foi possível remover {local}: {e}")

    conn.close()
    print("[SMB] Conexão encerrada.")

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
  
    inicio_llm = time.time()
    print("Início LLM:", datetime.now().strftime("%H:%M:%S"))

       
   
    #dados_json = input("ENTRADA MANUAL DO JSON: ")
   
    dados_json = consulta_LLM(prompt)

    fim_llm = time.time()
    print(f"Tempo de execução do LLM: {fim_llm - inicio_llm:.2f} segundos")

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

    fim_total = time.time()
    print(f"Tempo total do processo: {fim_total - inicio_total:.2f} segundos")

    return dados_json

# encontrar_nota('000131127|001|017154|01|NF', "030201", ['CF   ', '06/02/2026', '4500.00', '000001000'])

