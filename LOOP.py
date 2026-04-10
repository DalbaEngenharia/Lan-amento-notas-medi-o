from lista import filiais
from Protheus_Biblioteca import *
from selenium.webdriver.common.keys import Keys
from LancarNotas import lancamento
from texto_notas import encontrar_nota
from selenium.webdriver.common.action_chains import ActionChains
from selenium.common.exceptions import StaleElementReferenceException
import limpeza
import time

def LoopLancamentos(driver):
    log("===== INICIOU LOOP DE LANÇAMENTOS =====")
    LoopFilial = 0
    realizar_filtro = True
    while LoopFilial < len(filiais):
        filial_atual = filiais[LoopFilial]
        log(f"--- INICIANDO PROCESSAMENTO DA FILIAL [{LoopFilial + 1}/{len(filiais)}]: {filial_atual} ---")
        lista_notas_lançadas = []
        lista_notas_nao_lancadas = []
        try:
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

            # try:
            #     log("Tentando confirmar popup intermediário...")
            #     funcao_tres_e_demais(driver, "wa-button", "Confirmar", 0)
            # except Exception as e:
            #     log(f"Popup Confirmar não encontrado ou falhou: {e}")

            # try:
            #     log("Tentando fechar popup 2...")
            #     funcao_tres_e_demais(driver, "wa-button", "Fechar", 0)
            # except Exception as e:
            #     log(f"Popup Fechar 2 não encontrado ou falhou: {e}")
            ##=============================================================================================VERIFICAR LIMITE DE LICENÇA
            time.sleep(5)
            print("#############################################################")
            retorno_teste = Scriptfind(driver, "wa-text-view", retorno=True)
            print(retorno_teste)
            print("#############################################################")

            log("Aguardando botão Classificar...")
            esperar_existir(driver, "wa-button", "Classificar")
            time.sleep(5)
            if realizar_filtro: 
                print("Filtro unico")
                filtros = ["ROBO NOTAS (MEDICOES)", "Filtro de Programa"]
                
                print("TESTANTO LISTAGEM DE CHECKBOX ")
                log(f"Aplicando filtros: {filtros}")
                marcar_filtro(driver, filtros)

                log("Aguardando painel 'Aguarde' desaparecer...")
                esperar_sumir_panel(driver, "Aguarde", 60)
                realizar_filtro = False


            try:
                tabela = driver.find_element(By.ID, "COMP4513")
                log("Tabela de lançamentos encontrada (COMP4513).")
            except Exception as e:
                log(f"Sem tabela de lançamento para a filial {filial_atual}. Erro: {e}")
                LoopFilial += 1
                continue

            notas_processadas = set()
            tentativas_sem_nota_nova = 0
            limite_tentativas_sem_nota_nova = 5  # evita loop infinito

            log(f"Iniciando varredura de notas da filial {filial_atual}...")

            while True:
                try:
                    tabela = driver.find_element(By.ID, "COMP4513")
                    tabela_2 = expand_shadow(driver, tabela)
                    linhas = tabela_2.find_elements(By.CSS_SELECTOR, "tbody tr")

                    log(f"Total de linhas encontradas na tabela: {len(linhas)}")

                    nota_nova_encontrada = False

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
                            if chave_nota in notas_processadas:
                                log(f"Nota já processada anteriormente. Ignorando: {chave_nota}")
                                continue

                            # encontrou uma nota nova
                            nota_nova_encontrada = True
                            log(f"Nova nota encontrada para processamento: {chave_nota}")

                            dados = []
                            dados.append(linha_dados[1])   # N° nota
                            dados.append(linha_dados[2])   # série
                            dados.append(linha_dados[3])   # fornecedor
                            dados.append(linha_dados[7])   # cnpj
                            dados.append(linha_dados[9])   # data emissão
                            dados.append(linha_dados[10])  # valor
                            dados.append(linha_dados[13])  # chave

                            log(f"Dados extraídos da nota: {dados}")

                            # marca ANTES de processar
                            # assim mesmo que dê erro/cancelamento ela não repete
                            notas_processadas.add(chave_nota)
                            log(f"Nota marcada como processada preventivamente: {chave_nota}")

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

                            log(f"Iniciando função de lançamento da nota: {chave_nota}")
                            resultado, dados_lancados = lancamento(driver, dados, filial_atual)
                            
                            if resultado:
                                log(f"Lançamento retornou TRUE para nota {chave_nota}. Aguardando estabilização de 60s...")
                                lista_notas_lançadas.append(dados_lancados)
                                print("NOTAS LANCADAS OK:", lista_notas_lançadas)
                                time.sleep(60)
                                log(f"Nota tratada com sucesso (salva/cancelada/etc): {chave_nota}")
                                
                            else:
                                lista_notas_nao_lancadas.append(dados_lancados)
                                log(f"Lançamento retornou FALSE para nota {chave_nota}. Descendo para próxima na tabela após 60s...")
            
                                time.sleep(60)
                                descer_para_proxima_na_tabela(driver, "COMP4513")
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
                            log(f"Erro ao processar linha {idx}: {e}")
                            continue

                    if not nota_nova_encontrada:
                        tentativas_sem_nota_nova += 1
                        log(f"Nenhuma nota nova encontrada. Tentativa {tentativas_sem_nota_nova}/{limite_tentativas_sem_nota_nova}")
                        time.sleep(2)

                        if tentativas_sem_nota_nova >= limite_tentativas_sem_nota_nova:
                            log(f"Sem novas notas para processar na filial {filial_atual}. Indo para próxima filial.")
                            break
                    else:
                        tentativas_sem_nota_nova = 0
                        log("Nota nova foi processada nesta varredura. Resetando contador de tentativas sem nota nova.")

                except Exception as e:
                    log(f"Erro geral no loop da filial {filial_atual}: {e}")
                    tentativas_sem_nota_nova += 1
                    time.sleep(2)

                    if tentativas_sem_nota_nova >= limite_tentativas_sem_nota_nova:
                        log(f"Muitas falhas seguidas na filial {filial_atual}. Indo para próxima filial.")
                        break

        except Exception as e:
            log(f"ERRO CRÍTICO AO PROCESSAR FILIAL {filial_atual}: {e}")

        log(f"--- FINALIZANDO FILIAL: {filial_atual} ---")
        log("ATUALIZANDO RELATORIO....")
        relatorio_consolidado(lista_notas_lançadas, lista_notas_nao_lancadas, filial_atual)
        log("RELATORIO ATUALIZADO")
        driver.execute_script("document.getElementById('COMP4514').click();")
        time.sleep(10)
        log("Realizando limpeza de notas...")
        limpeza.limpeza()
        log("limpeza finalizada.")
        LoopFilial += 1

    log("===== FIM DO LOOP DE LANÇAMENTOS =====")
    encerrar_sistema(driver)

