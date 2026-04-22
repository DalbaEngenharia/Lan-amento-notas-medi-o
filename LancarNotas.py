from Protheus_Biblioteca import *
from lista import TES, ESPEC, natureza
from texto_notas import encontrar_nota
from Lancamentos import lancamentoSimples
import json
import ast
import traceback

def to_bool(valor):
    if isinstance(valor, bool):
        return valor
    if valor is None:
        return False
    return str(valor).strip().lower() in ["true", "1", "sim", "yes"]


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


def lancamento(driver, param, filial):
    dados_lancadas = []

    try:

        log("========================================")
        log("INÍCIO LANCAMENTO")
        log(f"param: {param}")
        print("========================================")
        print("INÍCIO LANCAMENTO")
        print("param:", param)

        time.sleep(10)
        log("Aguardou 10 segundos antes de iniciar interação.")
        #preciona ESC para garantir que nem uma caixa fique selecionada
        body = driver.find_element(By.TAG_NAME, "body")
        body.send_keys(Keys.ESCAPE)
        log("Enviado ESC para fechar possíveis modais/edições pendentes.")
        time.sleep(1)

        # ==========================================================
        # 1) LER DADOS DA NOTA DO COMPONENTE
        # ==========================================================
        log("Iniciando leitura do tipo de nota (COMP6019)...")
        # pega dados da tela do sistema para fazer comparações com a nota
        dados_a_comparar = []
        tipo_nota = pegar_texto_input(driver, "COMP6019")
        dados_a_comparar.append(tipo_nota)
        log(f"Tipo de nota bruto lido em COMP6019: {tipo_nota}")

        if tipo_nota and "NF" in tipo_nota:
            inserir_texto(driver, "COMP6019", "NFS", enter=True)
            log(f"Tipo de nota contém 'NF'. Ajustando para 'NFS'. Valor anterior: {tipo_nota}")
            tipo_nota = "NFS"

        tipo_nota = str(tipo_nota).strip()
        log(f"Tipo de nota final após tratamento: {tipo_nota}")

        data_emitida = pegar_texto_input(driver, "COMP6014")
        dados_a_comparar.append(data_emitida)
        log(f"Data emitida lida em COMP6014: {data_emitida}")

        resultado = Scriptfind(driver, "#COMP6051")
        if resultado:
            valor_bruto = resultado[0].get("value")
            log(f"Valor bruto encontrado em COMP6051: {valor_bruto}")
        else:
            valor_bruto = None
            log("Valor bruto não encontrado em COMP6051. Definido como None.")

        resultado = Scriptfind(driver, "#COMP6010")
        if resultado:
            numero_nota = resultado[0].get("value")
            log(f"Número da nota encontrado em COMP6010: {numero_nota}")
        else:
            numero_nota = None
            log("Número da nota não encontrado em COMP6010. Definido como None.")

        resultado = Scriptfind(driver, "#COMP6016")
        if resultado:
            fornecedor = resultado[0].get("value")
            log(f"Número do fornecedor encontrado em COMP6016: {fornecedor}")
        else:
            fornecedor = None
            log("Número do fornecedor não encontrado em COMP6016. Definido como None.")

        print("VALOR BRUTO:", valor_bruto)
        print("NUMERO NOTA:", numero_nota)
        print("NUMERO DO FORNECEDOR:", fornecedor)

        dados_a_comparar.append(valor_bruto)
        dados_a_comparar.append(numero_nota)
        dados_a_comparar.append(fornecedor)
        log(f"Dados montados para comparação: {dados_a_comparar}")
        print("Dados a comparar:", dados_a_comparar)

        # valida TES antes de seguir
        if tipo_nota not in TES:
            log(f"Tipo de nota inválido/não mapeado em TES: {tipo_nota}")
            cancelar_lancamento_de_nota(driver)
            return montar_retorno_nao_lancada(
                dados_lancadas, filial, fornecedor, numero_nota, "TIPO_NOTA_NAO_MAPEADO"
            )

        log(f"TES padrão a ser usada: {TES[tipo_nota]}")

        # ==========================================================
        # 2) BUSCAR DADOS DA NOTA / REGRA DE IMPOSTO
        # ==========================================================
        log("Buscando dados da nota via encontrar_nota(...)")
        
        #encontar nota busca a nota no servidor (texto_notas.py)
        dados_nota = encontrar_nota(param[6], filial, dados_a_comparar)

        log(f"Retorno bruto de encontrar_nota: {dados_nota}")

        #tratamento de notas que não foram encontradas ou não serão lançadas
        if dados_nota is None:
            log("Cancelando, erro ao consultar notas (retorno None)")
            cancelar_lancamento_de_nota(driver)
            return montar_retorno_nao_lancada(
                dados_lancadas, filial, fornecedor, dados_a_comparar[3], "ERRO AO CONSULTAR NOTA (retorno None)"
            )
        if dados_nota == "Serie errada": 
            log("Cancelando, serie errada")
            cancelar_lancamento_de_nota(driver)
            return montar_retorno_nao_lancada(
                dados_lancadas, filial, fornecedor, dados_a_comparar[3], "Serie errada"
            )
        print("Dados nota:", dados_nota)
        print("Tipo antes:", type(dados_nota))

        if isinstance(dados_nota, str):
            log("dados_nota veio como string. Tentando converter via json.loads / ast.literal_eval...")
            try:
                dados_nota = json.loads(dados_nota)
                log("Conversão de dados_nota via json.loads realizada com sucesso.")
            except json.JSONDecodeError:
                log("json.loads falhou. Tentando conversão com ast.literal_eval...")
                try:
                    dados_nota = ast.literal_eval(dados_nota)
                    log("Conversão de dados_nota via ast.literal_eval realizada com sucesso.")
                except Exception as e:
                    log(f"Falha ao converter dados_nota: {e}")
                    cancelar_lancamento_de_nota(driver)
                    return montar_retorno_nao_lancada(
                        dados_lancadas, filial, fornecedor, dados_a_comparar[3], "FALHA AO CONVERTER DADOS_NOTA"
                    )
        else:
            log("dados_nota já veio em formato estruturado (não string).")

        log(f"Tipo final de dados_nota: {type(dados_nota)}")
        print("Tipo depois:", type(dados_nota))

        if not isinstance(dados_nota, dict):
            log("dados_nota não é dict após conversão.")
            cancelar_lancamento_de_nota(driver)
            return montar_retorno_nao_lancada(
                dados_lancadas, filial, fornecedor, dados_a_comparar[3], "DADOS_NOTA_INVALIDO"
            )

        # ==========================================================
        # CANCELA LANÇAMENTO SE TER ERRO OU DIVERGÊNCIA
        # ==========================================================
        log("Validando campo de erro em dados_nota...")

        if to_bool(dados_nota.get("erro")):
            log(f"Erro identificado em dados_nota. Motivo: {dados_nota.get('motivo')}")
            print("Erro:", dados_nota.get("motivo"))

            log("Cancelando lançamento por erro retornado em dados_nota...")
            cancelar_lancamento_de_nota(driver)

            log("Lançamento cancelado por erro em dados_nota.")
            print("CANCELADO LANCAMENTO")

            return montar_retorno_nao_lancada(
                dados_lancadas,
                filial,
                fornecedor,
                dados_a_comparar[3],
                dados_nota.get("motivo", "ERRO RETORNADO EM DADOS_NOTA")
            )

        log("Validando campo contem_imposto...")
        if to_bool(dados_nota.get("contem_imposto")):
            log("Nota contém imposto. Cancelando lançamento.")
            print("Tem imposto")

            cancelar_lancamento_de_nota(driver)

            log("Lançamento cancelado porque a nota contém imposto.")
            print("CANCELADO, NOTA CONTÉM IMPOSTO")
            time.sleep(15)
            log("Aguardou 15 segundos após cancelamento por imposto.")

            return montar_retorno_nao_lancada(
                dados_lancadas, filial, fornecedor, dados_a_comparar[3], "NOTA CONTÉM IMPOSTO"
            )

        else:
            lancamentoSimples.lancamento_simples(driver, tipo_nota, dados_nota, dados_lancadas, filial, fornecedor, dados_a_comparar[3])

  
    except Exception as e:
        log("===== ERRO INESPERADO NO LANCAMENTO =====")
        log(f"Filial: {filial}")
        
        try:
            log(f"Parâmetro recebido (param): {param}")
        except:
            log("Falha ao logar param")

        log(f"Tipo do erro: {type(e).__name__}")
        log(f"Mensagem: {str(e)}")

        # stacktrace completo (ESSENCIAL)
        erro_completo = traceback.format_exc()
        log("Stacktrace completo:")
        log(erro_completo)

        print("===== ERRO INESPERADO NO LANCAMENTO =====")
        print(f"Tipo: {type(e).__name__}")
        print(f"Mensagem: {str(e)}")
        print(erro_completo)

        # tenta capturar estado atual da tela
        try:
            screenshot_path = f"erro_lancamento_{filial}.png"
            driver.save_screenshot(screenshot_path)
            log(f"Screenshot salva em: {screenshot_path}")
        except Exception as err:
            log(f"Falha ao salvar screenshot: {err}")

        try:
            html_path = f"erro_lancamento_{filial}.html"
            with open(html_path, "w", encoding="utf-8") as f:
                f.write(driver.page_source)
            log(f"HTML salvo em: {html_path}")
        except Exception as err:
            log(f"Falha ao salvar HTML: {err}")

        # tenta cancelar com segurança
        try:
            log("Tentando cancelar lançamento após erro...")
            cancelar_lancamento_de_nota(driver)
            log("Cancelamento executado com sucesso.")
        except Exception as e2:
            log(f"Falha ao cancelar lançamento: {type(e2).__name__} - {e2}")

        # fallback seguro dos dados
        nota_retorno = "N/A"
        fornecedor_retorno = "N/A"

        try:
            if 'dados_a_comparar' in locals() and len(dados_a_comparar) > 3:
                nota_retorno = dados_a_comparar[3]
        except Exception as err:
            log(f"Falha ao recuperar nota: {err}")

        try:
            if 'fornecedor' in locals():
                fornecedor_retorno = fornecedor
        except Exception as err:
            log(f"Falha ao recuperar fornecedor: {err}")

        return montar_retorno_nao_lancada(
            dados_lancadas,
            filial,
            fornecedor_retorno,
            nota_retorno,
            f"ERRO INESPERADO: {type(e).__name__} - {str(e)}"
        )