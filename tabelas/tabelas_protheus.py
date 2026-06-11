from Protheus_Biblioteca import * 
def linhas_de_tabela(driver,id_tabela):
    tabela = driver.find_element(By.ID, id_tabela)
    tabela_2 = expand_shadow(driver, tabela)
    linhas_tabela = tabela_2.find_elements(By.CSS_SELECTOR,"tbody tr")
    return linhas_tabela

def colunas_da_tabela(driver, linhas): 
    dados = []

    for linha in linhas:

        colunas = linha.find_elements(By.CSS_SELECTOR, "td")

        valores = []

        for coluna in colunas:

            texto = driver.execute_script("""
                return arguments[0].innerText;
            """, coluna)

            valores.append(texto.strip())

        dados.append(valores)

    return dados

def descer_para_proxima_na_tabela(driver, tabela_id):
    try:
        tabela = driver.find_element(By.ID, tabela_id)

        # força foco no grid
        driver.execute_script("arguments[0].focus();", tabela)
        time.sleep(0.2)

        # tenta send_keys nativo primeiro (mais confiável que JS em muitos casos)
        try:
            tabela.send_keys(Keys.ARROW_DOWN)
            print("ArrowDown enviado via send_keys no wa-tgrid")
            time.sleep(0.5)
            return True
        except Exception as e:
            print("Falhou send_keys no wa-tgrid, tentando JS:", e)

        # fallback via JS
        driver.execute_script("""
            const tabela = arguments[0];
            tabela.focus();

            const evento = new KeyboardEvent('keydown', {
                key: 'ArrowDown',
                code: 'ArrowDown',
                keyCode: 40,
                which: 40,
                bubbles: true,
                cancelable: true
            });

            tabela.dispatchEvent(evento);
        """, tabela)

        print("ArrowDown enviado via JS no wa-tgrid")
        time.sleep(0.5)
        return True

    except Exception as e:
        print("Erro ao descer para a próxima nota:", e)
        return False

def imprimir_tabela_por_id(driver, id_tabela): 

    linhas = linhas_de_tabela(driver,id_tabela)
    colunas = colunas_da_tabela(driver, linhas)
    
    for i, linha in enumerate(colunas):
                print(i, linha)


def insercao_tabela_teste(driver, id_tabela, coluna_index, valor, linha_index=0):
    js = """
    const browse = document.querySelector(arguments[0]);

    if (!browse || !browse.shadowRoot) {
        return false;
    }

    const cell = browse.shadowRoot.querySelector(
        `tbody tr[id="${arguments[1]}"] td[id="${arguments[2]}"] label`
    );

    if (!cell) {
        return false;
    }

    cell.textContent = arguments[3];
    return true;
    """

    return driver.execute_script(
        js,
        f"#{id_tabela}",
        str(linha_index),
        str(coluna_index),
        str(valor)
    )