from Listas.lista import filiais
from ConsultaBanco.consultaEmBanco.consultaGeral import consultar_banco
from Protheus_Biblioteca import *
from Lancamentos.relatorio import montar_retorno_nao_lancada
from selenium.webdriver.common.keys import Keys
from LancarNotas import lancamento
from selenium.webdriver.common.action_chains import ActionChains
from selenium.common.exceptions import StaleElementReferenceException
import limpeza
import time
import traceback
import csv
def LoopLancamentos(driver):

    ##Loop lancamentos inicia o loop de controle por filiais
    log("===== INICIOU LOOP DE LANÇAMENTOS =====")
    LoopFilial = 0


    # loop filial vai rodas sob a lista de filial garantindo todas as filials 
    while LoopFilial < len(filiais):
        Filtro_bruto = True
        filial_atual = filiais[LoopFilial]
        quantidade_notas = consultar_banco(filial_atual)
        if quantidade_notas == 0: 
            relatorio_consolidado(False,False,True, filial_atual)
            log(f"Sem notas para lançar na filial {filial_atual}")
            LoopFilial=LoopFilial+1
            continue
        
        #fazer leitura do CSV para verificar notas
        # caso 0, próxima filial
        # retorna notas, vai para lançar
        log(f"--- INICIANDO PROCESSAMENTO DA FILIAL [{LoopFilial + 1}/{len(filiais)}]: {filial_atual} ---")
        lista_notas_lançadas = []
        lista_notas_nao_lancadas = []
        #try para controle de erro
        try:
            while True: #gerencia mensagem licensa TOTVS
                log("Abrindo menu Documento...")
                funcao_tres_e_demais(driver, "wa-menu-item", "Documento", 0)

                log(f"Inserindo filial no campo COMP4512: {filial_atual}")
                inserir_texto(driver, "COMP4512", filial_atual)
                campo = driver.find_element(By.ID, "COMP4512")
                campo.send_keys(Keys.ENTER)

                log("Clicando em Confirmar para acessar financeiro...")
                funcao_tres_e_demais(driver, "wa-button", "Confirmar", 0)

                # TELA DE FINANCEIRO
                log("Aguardando tela de financeiro...")
                esperar_existir(driver, "wa-button", "Fechar")

                try:
                    log("Tentando fechar popup 1...")
                    funcao_tres_e_demais(driver, "wa-button", "Fechar", 0)
                except Exception as e:
                    log(f"Popup Fechar 1 não encontrado ou falhou: {e}")

            
                ##=============================================================================================VERIFICAR LIMITE DE LICENÇA
                time.sleep(10)
                print("#############################################################")
                
                retorno_teste = Scriptfind(driver, "wa-text-view", retorno=True)
                texto_tela = str(retorno_teste).lower()
                print("####################")
                print(texto_tela)
                if "excedeu numero de licenças" in texto_tela or "Moedas" in texto_tela:
                    
                    print("Excedeu licença, aguradando...")
                    log("Excedeu licença, aguradando...")
                    try: 
                        try: 
                            funcao_tres_e_demais(driver, "wa-button", "Cancelar", 0)
                            print("Clicou em fechar mensagem Moedas")
                            log("Clicou em fechar mensagem Moedas")
                            time.sleep(30)
                        except: 
                            try: 
                                funcao_tres_e_demais(driver, "wa-button", "Fechar", 0)
                                print("Clicou em fechar mensagem licenças")
                                log("Clicou em fechar mensagem licenças")
                                time.sleep(30)
                            except: 
                                print("Licenças OK")
                                break
                    except: 
                        print("Licenças OK")
                        break
                else: 
                    break
            
            time.sleep(5)
            try:
                print("verifica filtros ativos em tela")
                funcao_tres_e_demais(driver,"wa-button","Cancelar",0)
            except:
                None
            
            log("Aguardando botão Classificar...")
            esperar_existir(driver, "wa-button", "Classificar")
            time.sleep(5)
            # for 
            #realiza filtro do sistema do protheus, para aperecer apenas as notas por lançamento
                              
            with open("resultados/resultado.csv", newline="", encoding="utf-8") as arquivo:
                linhas = csv.DictReader(arquivo, delimiter=';')
                ## LOOP PRINCIPAL PARA NOTAS
                for linha in linhas:
                    if Filtro_bruto: 
                        filtros = ["FILTRO ROBO(MEDICOES)", "Filtro de Programa"]
                    
                        print("TESTANTO LISTAGEM DE CHECKBOX ")
                        log(f"Aplicando filtros: {filtros}")
                        marcar_filtro(driver, filtros)
                        Filtro_bruto = False
                    else: 
                        Scriptfind(driver, "wa-button")
                        funcao_tres_e_demais(driver, "wa-button", "Filtrar", 0)
                        funcao_tres_e_demais(driver, "wa-button", "Filtrar", 0)
                        funcao_tres_e_demais(driver, "wa-button", "Filtrar", 0)
                        time.sleep(3)
                        funcao_tres_e_demais(driver,"wa-button", "Aplicar", 0)
                        None
                    doc = linha["f1_doc"].strip()
                    serie = linha["f1_serie"].strip()
                    fornecedor = linha["f1_fornece"].strip()

                    print(f"doc={doc}, serie={serie}, fornece={fornecedor}")
                    lista_campos_filtros = ["COMP9003", "COMP9005", "COMP9007"]
                    for i, campo_id in enumerate(lista_campos_filtros):
                        time.sleep(5)
   
                        campo = driver.find_element(By.ID, campo_id)

                        if i == 0:
                            inserir_texto(driver, campo_id, doc )

                        elif i == 1:
                            inserir_texto(driver, campo_id, serie )

                        elif i == 2:
                            inserir_texto(driver, campo_id, fornecedor )
                    funcao_tres_e_demais(driver, "wa-button", "Confirmar",0)
                    esperar_sumir_panel(driver, "Aguarde", 60)
                    time.sleep(1)
                    try:
                        #encontra a tabela do protheus contendo as notas 
                        tabela = driver.find_element(By.ID, "COMP4513")
                        tabela_2 = expand_shadow(driver, tabela)
                        linhas = tabela_2.find_elements(By.CSS_SELECTOR, "tbody tr")

                        log(f"Total de linhas encontradas na tabela: {len(linhas)}")


                        for idx in range(len(linhas)):
                            try:
                                # rebusca tudo a cada linha para evitar stale
                                tabela = driver.find_element(By.ID, "COMP4513")
                                tabela_2 = expand_shadow(driver, tabela)
                                linhas = tabela_2.find_elements(By.CSS_SELECTOR, "tbody tr")

                                if idx >= len(linhas):
                                    log(f"Índice {idx} maior que quantidade atual de linhas ({len(linhas)}). Encerrando varredura atual.")
                                    break

                                linha = linhas[idx]
                                colunas = linha.find_elements(By.CSS_SELECTOR, "td label")
                                linha_dados = [col.text.strip() for col in colunas]

                                log(f"Linha {idx} lida com {len(linha_dados)} colunas.")

                                if len(linha_dados) < 14:
                                    log(f"Linha {idx} incompleta ({len(linha_dados)} colunas). Pulando...")
                                    continue

                                # chave única da nota
                                chave_nota = f"{linha_dados[1]}|{linha_dados[2]}|{linha_dados[7]}|{linha_dados[10]}"
                                log(f"Linha {idx} - chave da nota identificada: {chave_nota}")

                                # se já tratou essa nota, ignora
            

                                # encontrou uma nota nova
                                nota_nova_encontrada = True
                                log(f"Nova nota encontrada para processamento: {chave_nota}")

                                dados = []
                                dados.append(linha_dados[1])    # N° nota
                                dados.append(linha_dados[2])    # série
                                dados.append(linha_dados[3])    # fornecedor
                                dados.append(linha_dados[7])    # cnpj
                                dados.append(linha_dados[4])    # loja
                                dados.append(linha_dados[9])    # data emissão
                                dados.append(linha_dados[10])   # valor
                                dados.append(linha_dados[13])   # chave

                                log(f"Dados extraídos da nota: {dados}")

                                # marca ANTES de processar
                                # assim mesmo que dê erro/cancelamento ela não repete
                                log(f"Nota marcada como processada preventivamente: {chave_nota}")
                                #Realiza o clique 3x em calassificar garantindo o funcionamento
                                log("Clicando em Classificar (1)...")
                                funcao_tres_e_demais(driver, "wa-button", "Classificar", 0)

                                log("Clicando em Classificar (2)...")
                                funcao_tres_e_demais(driver, "wa-button", "Classificar", 0)

                                log("Clicando em Classificar (3)...")
                                funcao_tres_e_demais(driver, "wa-button", "Classificar", 0)

                                log("Aguardando popup de confirmação com botão 'Não'...")
                                esperar_existir(driver, "wa-button", "Não")

                                log("Clicando em 'Não'...")
                                funcao_tres_e_demais(driver, "wa-button", "Não", 0)

                                log("Aguardando botão 'Salvar' para iniciar lançamento...")
                                esperar_existir(driver, "wa-button", "Salvar")

                                #Inicia a função de lançamento (em LancarNotas.py )
                                log(f"Iniciando função de lançamento da nota: {chave_nota}")
                                resultado, dados_lancados = lancamento(driver, dados, filial_atual)
                                #se resultado for True (lancada) adiciona a lista_notas_lancadas para o relatorio
                                if resultado:
                                    log(f"Lançamento retornou TRUE para nota {chave_nota}. Aguardando estabilização de 60s...")
                                    lista_notas_lançadas.append(dados_lancados)
                                    print("NOTAS LANCADAS OK:", lista_notas_lançadas)
                                    time.sleep(60)
                                    log(f"Nota tratada com sucesso (salva/cancelada/etc): {chave_nota}")
                                #Caso false (não lancada) adiciona a lista_notas_não_lancadas para o relatorio
                                else:
                                    lista_notas_nao_lancadas.append(dados_lancados)
                                    log(f"Lançamento retornou FALSE para nota {chave_nota}. Descendo para próxima na tabela após 60s...")
                
                                    time.sleep(60)
                                    continue
                                    log("Movimentação para próxima nota na tabela executada.")

                                time.sleep(3)
                                log("Pausa de 3s após processamento da nota concluída.")

                                # processa UMA nota por ciclo e volta pro topo
                                # porque a tela pode ter mudado
                                log("Encerrando ciclo atual após processar uma nota. Reiniciando varredura da tabela...")
                                break

                            except StaleElementReferenceException:
                                log(f"Linha {idx} ficou stale. Tentando novamente na próxima varredura...")
                                continue
                            except Exception as e:
                                log("===== ERRO AO PROCESSAR LINHA =====")
                                log(f"Filial: {filial_atual}")
                                log(f"Linha: {idx}")
                                log(f"Tipo: {type(e).__name__}")
                                log(f"Mensagem: {str(e)}")
                                log(traceback.format_exc())
                                continue
                        #Verificação se tem nota nova a ser lançada
            
                    except Exception as e:
                        log("===== ERRO NO LOOP INTERNO =====")
                        log(f"Filial: {filial_atual}")
                        log(f"Tipo: {type(e).__name__}")
                        log(f"Mensagem: {str(e)}")
                        log(traceback.format_exc())

                        tentativas_sem_nota_nova += 1
                        time.sleep(2)

        except Exception as e:
            log("===== ERRO CRÍTICO NA FILIAL =====")
            log(f"Filial: {filial_atual}")
            log(f"Tipo do erro: {type(e).__name__}")
            log(f"Mensagem: {str(e)}")

            erro_completo = traceback.format_exc()
            log("Stacktrace completo:")
            log(erro_completo)

            try:
                screenshot_path = f"erro_filial_{filial_atual}.png"
                driver.save_screenshot(screenshot_path)
                log(f"Screenshot salva em: {screenshot_path}")
            except Exception as err:
                log(f"Falha ao salvar screenshot: {err}")

            try:
                html_path = f"erro_filial_{filial_atual}.html"
                with open(html_path, "w", encoding="utf-8") as f:
                    f.write(driver.page_source)
                log(f"HTML salvo em: {html_path}")
            except Exception as err:
                log(f"Falha ao salvar HTML: {err}")

        log(f"--- FINALIZANDO FILIAL: {filial_atual} ---")
        log("ATUALIZANDO RELATORIO....")
        relatorio_consolidado(lista_notas_lançadas, lista_notas_nao_lancadas, False, filial_atual)
        log("RELATORIO ATUALIZADO")
        driver.execute_script("document.getElementById('COMP4514').click();")
        time.sleep(10)
        log("Realizando limpeza de notas...")
        limpeza.limpeza()
        log("limpeza finalizada.")
        LoopFilial += 1

    log("===== FIM DO LOOP DE LANÇAMENTOS =====")
    encerrar_sistema(driver)

