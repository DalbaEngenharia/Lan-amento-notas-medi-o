from Protheus_Biblioteca import *
from Listas.lista import TES, ESPEC, natureza
from verificar_notas.texto_notas import encontrar_nota
import traceback
import json
import ast
from Lancamentos.relatorio import *

def lancamento_simples(driver, tipo_nota, dados_nota, dados_lancadas, filial, fornecedor, dados_a_comparar):
    try:
        #se der tudo certo, inicia o lançamento da nota
        log("Nota não contém imposto. Prosseguindo com lançamento.")
        print("Não tem imposto")

        tes = TES[tipo_nota]
        log(f"TES final definida para lançamento: {tes}")
        print("TES final:", tes)

        # ==========================================================
        # 3) PREENCHER TABELA 1 (COMP6022) -> COLUNA 7 = TES
        # ==========================================================
        log("Localizando tabela COMP6022...")
        tabela = driver.find_element(By.ID, "COMP6022")
        tabela_2 = expand_shadow(driver, tabela)
        linhas = tabela_2.find_elements(By.CSS_SELECTOR, "tbody tr")

        log(f"Tabela COMP6022 localizada com {len(linhas)} linha(s).")
        print("========================================")
        print("TABELA COMP6022")
        print("TOTAL LINHAS:", len(linhas))
        valores = []
        for i, linha in enumerate(linhas, start=1):
            colunas = linha.find_elements(By.CSS_SELECTOR, "td")
            
            try:
                valor_coluna_29 = colunas[29].text.strip()
            except:
                valor_coluna_29 = ""

            valores.append(valor_coluna_29)
            print(f"Linha {i} | Coluna 29: {valor_coluna_29}")
        #Verifica AF (pedido) da nota com com sistema
        # SE: iguais -> lancar nota
        # SE: nota não ter -> lançar nota
        # SE: nota ter, mas não for igual com a do sistema -> cancela o lançamento
        if dados_nota["AC"] == "null" or dados_nota["AC"] == None:
            None
        elif dados_nota["AC"] in valores: 
            None
        else:  
            log("Divergencia entre AFs")
            cancelar_lancamento_de_nota(driver)
            return montar_retorno_nao_lancada(
                dados_lancadas, filial, fornecedor, dados_a_comparar, "AF não compativel"
            )

        #INICIA O PREENCHIMENTO DA TES EM TODAS AS LINHAS
        x = 0
        while x < len(linhas):
            sucesso = False
            log(f"Iniciando preenchimento da linha {x} da COMP6022 com TES.")

            for tentativa in range(1, 6):
                log(f"Linha {x} | tentativa {tentativa}")
                print(f"Linha {x} | tentativa {tentativa}")

                time.sleep(1)

                try:
                    # coluna 7 = TES
                    log(f"Inserindo TES '{tes}' na linha {x}")
                    inserir_na_tabela_shadow(driver, "COMP6022", 7, tes, linha_index=x, enter=True)
                    log(f"Comando de inserção executado para linha {x}")
                except Exception as e:
                    log(f"Erro ao inserir TES na linha {x} da COMP6022: {e}")
                    print(f"Erro ao inserir TES na linha {x}: {e}")

                time.sleep(2)

                # recarrega a tabela após edição
                tabela = driver.find_element(By.ID, "COMP6022")
                tabela_2 = expand_shadow(driver, tabela)
                linhas = tabela_2.find_elements(By.CSS_SELECTOR, "tbody tr")

                if x >= len(linhas):
                    log(f"[COMP6022] Linha {x} não existe mais após recarregar tabela.")
                    continue

                linha_atual = linhas[x]
                colunas_atuais = linha_atual.find_elements(By.CSS_SELECTOR, "td")

                if len(colunas_atuais) <= 7:
                    log(f"[COMP6022] Linha {x} não possui coluna 7 após recarregar.")
                    continue

                valor_coluna_7 = driver.execute_script(
                    "return arguments[0].innerText || arguments[0].textContent || '';",
                    colunas_atuais[7]
                ).strip()

                print(f"[COMP6022] Linha {x}, Coluna 7 após inserir: '{valor_coluna_7}'")

                # ESC para fechar qualquer editor pendurado
                try:
                    body = driver.find_element(By.TAG_NAME, "body")
                    body.send_keys(Keys.ESCAPE)
                    log(f"[COMP6022] ESC enviado após tentativa {tentativa} da linha {x}.")
                except Exception as e:
                    log(f"[COMP6022] Falha ao enviar ESC após tentativa {tentativa} da linha {x}: {e}")

                time.sleep(1)

                # sucesso se a célula ficou preenchida
                if valor_coluna_7 != "":
                    sucesso = True
                    log(f"[COMP6022] Sucesso ao preencher TES na linha {x}.")
                    break

            if not sucesso:
                log(f"Falha definitiva ao preencher TES na linha {x} da COMP6022 após 5 tentativas.")
                cancelar_lancamento_de_nota(driver)
                return montar_retorno_nao_lancada(
                    dados_lancadas, filial, fornecedor, dados_a_comparar, f"FALHA AO PREENCHER TES LINHA {x}"
                )

            x += 1
            log(f"Linha {x - 1} da COMP6022 concluída. Próxima linha: {x}")

        # ==========================================================
        # 4) AVANÇAR PARA PRÓXIMA ETAPA
        # ==========================================================
        log("Clicando botão BUTTON-COMP6030 para avançar de etapa...")
        print("Clicando botão BUTTON-COMP6030...")
        driver.find_element(By.ID, "BUTTON-COMP6030").click()
        time.sleep(3)
        log("Aguardou 3 segundos após clicar em BUTTON-COMP6030.")

        # ==========================================================
        # 5) PREENCHER NATUREZA
        # ==========================================================
        log(f"Preenchendo natureza no campo COMP6087 com valor: {natureza[0]}")
        print("Natureza:", natureza[0])
        inserir_texto(driver, "COMP6087", natureza[0], enter=True, quantidade=3)
        time.sleep(2)
        log("Aguardou 2 segundos após preencher natureza.")

        # ==========================================================
        # 6) AGUARDAR TABELA 2 (COMP6092) CARREGAR
        # ==========================================================
        log("Localizando tabela COMP6092...")
        tabela = driver.find_element(By.ID, "COMP6092")

        log("Aguardando tabela COMP6092 carregar com valor diferente de 0,00 na 3ª coluna...")
        WebDriverWait(driver, 20).until(
            lambda d: d.execute_script("""
                let host = arguments[0];
                if (!host.shadowRoot) return false;

                let celula = host.shadowRoot.querySelector("tbody tr td:nth-child(3) label");
                if (!celula) return false;

                return celula.textContent.trim() !== "0,00";
            """, tabela)
        )

        time.sleep(1)
        log("Tabela COMP6092 carregada e validada.")

        # ==========================================================
        # 7) LER DADOS DA TABELA 2 (COMP6092)
        # ==========================================================
        log("Lendo dados da tabela COMP6092...")
        dados = driver.execute_script("""
            let host = arguments[0];
            let shadow = host.shadowRoot;
            let linhas = shadow.querySelectorAll("tbody tr");
            let resultado = [];

            linhas.forEach(tr => {
                let linha = [];
                tr.querySelectorAll("td label").forEach(td => {
                    linha.push(td.textContent.trim());
                });

                // Ignorar linha padrão vazia
                if (linha.length > 1 && linha[1] !== "/  /") {
                    resultado.push(linha);
                }
            });

            return resultado;
        """, tabela)

        log(f"Dados lidos da COMP6092: {dados}")
        print("========================================")
        print("TABELA COMP6092")
        print("Dados:", dados)

        if not dados or len(dados[0]) < 2:
            log("Dados da COMP6092 inválidos ou vazios.")
            cancelar_lancamento_de_nota(driver)
            return montar_retorno_nao_lancada(
                dados_lancadas, filial, fornecedor, dados_a_comparar, "DADOS_COMP6092_INVALIDOS"
            )

        # ==========================================================
        # 8) PREENCHER DATA NA TABELA 2 (COMP6092) -> COLUNA 1
        # ==========================================================
        data_sistema = dados[0][1]
        log(f"Data do sistema obtida da COMP6092: {data_sistema}")
        print("Data do sistema:", data_sistema)

        if dados_nota.get('data_vencimento') is None:
            log("Nota sem data de vencimento. Utilizando data do sistema / regra mínima.")
            print("Nota sem data de vencimento, utilizando data do sistema")
        else:
            log(f"Nota possui data de vencimento informada: {dados_nota.get('data_vencimento')}")
            print("Data de vencimento da nota")

        # converte a data do sistema
        try:
            data_sistema = datetime.strptime(data_sistema, "%d/%m/%Y")
        except Exception as e:
            log(f"Erro ao converter data do sistema '{data_sistema}': {e}")
            cancelar_lancamento_de_nota(driver)
            return montar_retorno_nao_lancada(
                dados_lancadas, filial, fornecedor, dados_a_comparar, "DATA_SISTEMA_INVALIDA"
            )

        # pega hoje + 8 dias
        data_minima = datetime.today() + timedelta(days=8)

        log(f"Data do sistema convertida: {data_sistema}")
        log(f"Data mínima calculada (hoje + 8 dias): {data_minima}")

        print("Data do sistema convertida:", data_sistema)
        print("Data mínima (hoje + 8 dias):", data_minima)

        # se a data mínima for menor que a data do sistema, usa a data do sistema
        if data_minima < data_sistema:
            log("Data mínima calculada é menor que a data do sistema. Ajustando para data do sistema.")
            print("DATA MENOR DO QUE OS 8 DIAS MÍNIMOS")
            data_minima = data_sistema

        # formata no final
        data_minima = data_minima.strftime("%d/%m/%Y")
        log(f"Data mínima final formatada para inserção: {data_minima}")
        print("Data mínima formatada:", data_minima)

        tentativa = 0
        print(f"[COMP6092] Inserindo data | tentativa {tentativa + 1}")
        log(f"[COMP6092] Iniciando tentativas para inserir data '{data_minima}' na linha 0, coluna 1.")

        while tentativa < 10:
            log(f"[COMP6092] Tentativa {tentativa + 1}/10 para inserir data.")
            try:
                # linha 0, coluna 1
                inserir_na_tabela_shadow(driver, "COMP6092", 1, data_minima, linha_index=0)
                log(f"[COMP6092] Comando de inserção executado com data {data_minima}.")
                body = driver.find_element(By.TAG_NAME, "body")
                body.send_keys(Keys.ESCAPE)
                log("[COMP6092] ESC enviado após tentativa de inserção da data.")
            except Exception as e:
                log(f"Erro ao inserir data na COMP6092: {e}")
                print(f"Erro ao inserir data na COMP6092: {e}")

            time.sleep(2)

            # valida se ficou preenchido
            tabela = driver.find_element(By.ID, "COMP6092")
            tabela_2 = expand_shadow(driver, tabela)
            linhas_2 = tabela_2.find_elements(By.CSS_SELECTOR, "tbody tr")

            log(f"[COMP6092] Total de linhas após tentativa de inserção: {len(linhas_2)}")

            if len(linhas_2) > 0:
                linha0 = linhas_2[0]
                colunas0 = linha0.find_elements(By.CSS_SELECTOR, "td")

                if len(colunas0) > 1:
                    valor_coluna_1 = driver.execute_script(
                        "return arguments[0].innerText || arguments[0].textContent || '';",
                        colunas0[1]
                    ).strip()

                    log(f"[COMP6092] Linha 0, coluna 1 após inserir: '{valor_coluna_1}'")
                    print(f"[COMP6092] Linha 0, Coluna 1 após inserir: '{valor_coluna_1}'")

                    if valor_coluna_1 == data_minima:
                        log("[COMP6092] Data confirmada com sucesso na tabela.")
                        break

            try:
                body = driver.find_element(By.TAG_NAME, "body")
                body.send_keys(Keys.ESCAPE)
                log("[COMP6092] ESC enviado ao final da tentativa.")
            except Exception as e:
                log(f"[COMP6092] Falha ao enviar ESC ao final da tentativa: {e}")

            time.sleep(1)
            tentativa += 1

        if tentativa >= 10:
            log("[COMP6092] Falha definitiva ao preencher data após 10 tentativas.")
            cancelar_lancamento_de_nota(driver)
            return montar_retorno_nao_lancada(
                dados_lancadas, filial, fornecedor, dados_a_comparar, "FALHA AO PREENCHER DATA COMP6092"
            )

        # ==========================================================
        # 9) SALVAR
        # ==========================================================
        log("Iniciando salvamento do lançamento...")

        # funcao_tres_e_demais(driver, "wa-button", "Salvar", 0)
        # esperar_existir(driver, "wa-dialog", "Título Contas a Pagar")
        # funcao_tres_e_demais(driver, "wa-button", "Salvar", 0)
        cancelar_lancamento_de_nota(driver)

        time.sleep(5)
        Scriptfind(driver, "wa-button")
        time.sleep(5)

        try:
            funcao_tres_e_demais(driver, "wa-button", "OK")
        except Exception:
            pass
        print("DADOS NOTA LANÇADA:", dados_lancadas)
        log("Lançamento finalizado com retorno TRUE.")
        return montar_retorno_lancada(
            dados_lancadas, filial, fornecedor, dados_a_comparar
        )        

    except Exception as e:
        log("===== ERRO NO LANCAMENTO SIMPLES =====")
        log(f"Filial: {filial}")
        log(f"Tipo nota: {tipo_nota}")

        try:
            log(f"dados_nota: {dados_nota}")
        except:
            log("Falha ao logar dados_nota")

        try:
            log(f"dados_a_comparar: {dados_a_comparar}")
        except:
            log("Falha ao logar dados_a_comparar")

        log(f"Tipo do erro: {type(e).__name__}")
        log(f"Mensagem: {str(e)}")

        erro_completo = traceback.format_exc()
        log("Stacktrace completo:")
        log(erro_completo)

        print("===== ERRO NO LANCAMENTO SIMPLES =====")
        print(f"Tipo: {type(e).__name__}")
        print(f"Mensagem: {str(e)}")
        print(erro_completo)

        # screenshot
        try:
            screenshot_path = f"erro_lancamento_simples_{filial}.png"
            driver.save_screenshot(screenshot_path)
            log(f"Screenshot salva em: {screenshot_path}")
        except Exception as err:
            log(f"Falha ao salvar screenshot: {err}")

        # html
        try:
            html_path = f"erro_lancamento_simples_{filial}.html"
            with open(html_path, "w", encoding="utf-8") as f:
                f.write(driver.page_source)
            log(f"HTML salvo em: {html_path}")
        except Exception as err:
            log(f"Falha ao salvar HTML: {err}")

        # tentativa de cancelar
        try:
            log("Tentando cancelar lançamento após erro...")
            cancelar_lancamento_de_nota(driver)
            log("Cancelamento executado.")
        except Exception as e2:
            log(f"Falha ao cancelar: {type(e2).__name__} - {e2}")

        return montar_retorno_nao_lancada(
            dados_lancadas,
            filial,
            fornecedor,
            dados_a_comparar,
            f"ERRO LANCAMENTO_SIMPLES: {type(e).__name__} - {str(e)}"
        )