from imports import *
import pyautogui as pg 
import time
import os
from datetime import datetime, date, timedelta
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException
from selenium.common.exceptions import InvalidElementStateException
from selenium.webdriver.common.keys import Keys
#iniciar ambiente (homologação ou principal)
def iniciar_ambiente(inicio, driver): 

    if inicio: 
        None
        # link_site = "https://192.168.254.243:1235/webapp"
        # driver.get(link_site)
        # driver.find_element(By.XPATH, '//*[@id="details-button"]').click()
        # time.sleep(0.5)
        # driver.find_element(By.XPATH, '//*[@id="proceed-link"]').click()
        # pg.keyDown("ctrl")
        # pg.press("l")
        # pg.keyUp("ctrl")        
        # pg.press("left")
        # pg.write("https://")
        # pg.press("return")
    else: 
        link_site = "https://protheus.dalba.com.br:1239/webapp/index.html"
        driver.get(link_site)
        
#função para entrar nos shadow ( open )
def expand_shadow(driver, element ):
    return driver.execute_script("return arguments[0].shadowRoot", element)

#funcão para confirmar a entrada do banco de dados 
def confirmaBase(driver, wait): 
    time.sleep(5)
    dialogs = wait.until(EC.presence_of_all_elements_located((By.CSS_SELECTOR, 'wa-dialog')))
    wa_dialog = dialogs[1]
    shadow = expand_shadow(driver, wa_dialog)

    footer = shadow.find_element(By.CSS_SELECTOR, 'footer')
    buttons = footer.find_elements(By.CSS_SELECTOR, 'wa-button')

    shadow_btn = expand_shadow(driver,buttons[1])
    btn = shadow_btn.find_element(By.CSS_SELECTOR, 'button')
    btn.click()
    #wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, "wa-webview")))
    time.sleep(1)

#função de Login ( usuário )
def login(driver, wait, credenciais):

    # Aguarda o webview ficar visível
    wa_webview = wait.until(
        EC.visibility_of_element_located((By.CSS_SELECTOR, "wa-webview"))
    )

    # Entra no Shadow DOM
    shadow = driver.execute_script("return arguments[0].shadowRoot", wa_webview)

    # Aguarda o iframe dentro do shadow estar visível e renderizado
    iframe = None
    for _ in range(15):  # retry por até 15 segundos
        try:
            iframe = shadow.find_element(By.CSS_SELECTOR, "iframe")
            if iframe.is_displayed() and iframe.size['height'] > 0:
                break
        except:
            time.sleep(1)
    else:
        raise Exception("Iframe dentro do Shadow DOM não carregou ou não está visível.")

    driver.switch_to.frame(iframe)

    # Aguarda inputs ficarem visíveis
    campos = wait.until(
        EC.visibility_of_all_elements_located((By.CLASS_NAME, "po-input"))
    )

    if len(campos) < 2:
        raise Exception(f"Erro: Esperava 2 campos de login, mas encontrou {len(campos)}")

    campo_usuario, campo_senha = campos[0], campos[1]

    campo_usuario.clear()
    campo_usuario.send_keys(credenciais[0])

    campo_senha.clear()
    campo_senha.send_keys(credenciais[1])

    # Aguarda botão "Entrar" clicável e clica
    entrar = wait.until(
        EC.element_to_be_clickable((By.CLASS_NAME, "po-button"))
    )
    entrar.click()

    # Retorna ao conteúdo principal
    driver.switch_to.default_content()

#função de seleção do ambiente 
def sel_ambiente(driver, wait, amb,homologacao):
    time.sleep(10)
    try:
        # Espera o shadow DOM
        wa_webview = wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, "wa-webview")))
        shadow = driver.execute_script("return arguments[0].shadowRoot", wa_webview)

        # Espera o iframe dentro do shadow DOM
        iframe = shadow.find_element(By.CSS_SELECTOR, "iframe")
        driver.switch_to.frame(iframe)

        # Espera inputs e botões estarem presentes
        inputs = WebDriverWait(driver, 10).until(
            EC.presence_of_all_elements_located((By.CLASS_NAME, "po-lookup-input"))
        )
        inputs_button = WebDriverWait(driver, 10).until(
            EC.presence_of_all_elements_located((By.CLASS_NAME, "po-lookup-button"))
        )

        input_amb = inputs[2]

        # Espera o input ficar clicável antes de interagir
        WebDriverWait(driver, 10).until(EC.element_to_be_clickable((By.CLASS_NAME, "po-lookup-input")))
        input_amb.clear()
        input_amb.send_keys(amb)

        # Espera o botão ficar clicável
        WebDriverWait(driver, 10).until(EC.element_to_be_clickable((By.CLASS_NAME, "po-lookup-button")))
        inputs_button[2].click()
        # Submeter
        time.sleep(5)
        entrar = WebDriverWait(driver, 10).until(
            EC.element_to_be_clickable((By.NAME, "submmit"))
        )
        entrar.click()
        if homologacao: 
            # Opcional: esperar um pouco até a próxima tela carregar
            time.sleep(5)
            pg.moveTo(1215,690)
            pg.click()
    except TimeoutException:
        print("Elemento não ficou interagível no tempo esperado.")
        
    except InvalidElementStateException:
        print("Elemento não está interagível no momento.")

################################################################################
################################################################################ def Scriptfind(driver, item):
def Scriptfind(driver, item, retorno=False):
    script = """
        const selector = arguments[0];

        function findAllDeep(root, selector, results = []) {
            if (!root) return results;

            // procura nesse nível
            const found = root.querySelectorAll(selector);
            found.forEach(el => results.push(el));

            // percorre todos os nós para entrar em shadow roots aninhados
            const all = root.querySelectorAll('*');
            for (const node of all) {
                if (node.shadowRoot) {
                    findAllDeep(node.shadowRoot, selector, results);
                }
            }

            return results;
        }

        const elements = findAllDeep(document, selector);

        return elements.map(el => {
            return {
                tag: el.tagName.toLowerCase(),
                id: el.id || "",
                class: el.className || "",
                caption: (
                    el.getAttribute("caption") ||
                    (el.shadowRoot && el.shadowRoot.innerText) ||
                    el.innerText ||
                    el.textContent ||
                    ""
                ).trim(),
                value: el.value || ""
            };
        });
    """

    elementos = driver.execute_script(script, item)

    if not elementos:
        print(f"Nenhum elemento encontrado para: {item}")
        return None if retorno else []

    for i, s in enumerate(elementos):
        print(
            f"[{i}] tag: {s['tag']}, id: {s['id']}, class: {s['class']}, "
            f"caption: {s['caption']}, value: {s['value']}"
        )

    # Se pediu retorno, devolve o dado mais útil do primeiro elemento
    if retorno:
        primeiro = elementos[0]

        # prioridade: value -> caption -> dicionário completo
        if primeiro["value"]:
            return primeiro["value"]
        elif primeiro["caption"] and primeiro["caption"] != "?":
            return primeiro["caption"]
        else:
            return primeiro  # fallback se quiser inspecionar

    return elementos

def pegar_valor_shadow(driver, host_id, target_id):
    script = """
        const hostId = arguments[0];
        const targetId = arguments[1];

        const host = document.getElementById(hostId);
        if (!host || !host.shadowRoot) return null;

        function findFirstDeep(root, targetId) {
            if (!root) return null;

            const el = root.querySelector('#' + targetId);
            if (el) return el;

            const all = root.querySelectorAll('*');
            for (const node of all) {
                if (node.shadowRoot) {
                    const found = findFirstDeep(node.shadowRoot, targetId);
                    if (found) return found;
                }
            }
            return null;
        }

        const el = findFirstDeep(host.shadowRoot, targetId);
        if (!el) return null;

        // 1) tenta value direto do componente
        if (el.value !== undefined && el.value !== null && String(el.value).trim() !== '') {
            return el.value;
        }

        // 2) tenta atributo value
        const attrValue = el.getAttribute('value');
        if (attrValue !== null && String(attrValue).trim() !== '') {
            return attrValue;
        }

        // 3) se for web component com shadow interno, tenta input interno
        if (el.shadowRoot) {
            const innerInput = el.shadowRoot.querySelector('input, textarea');
            if (innerInput) {
                if (innerInput.value !== undefined && innerInput.value !== null && String(innerInput.value).trim() !== '') {
                    return innerInput.value;
                }

                const innerAttr = innerInput.getAttribute('value');
                if (innerAttr !== null && String(innerAttr).trim() !== '') {
                    return innerAttr;
                }
            }
        }

        // 4) fallback texto
        const txt = (el.innerText || el.textContent || '').trim();
        if (txt !== '') return txt;

        return null;
    """

    return driver.execute_script(script, host_id, target_id)

def encontrarId(driver, item):
    dicionario = {} 
    script = """
        const selector = arguments[0];
        const elements = Array.from(document.querySelectorAll(selector));
        const shadowHosts = elements.filter(el => el.shadowRoot);
        return shadowHosts.map(el => {
            let caption = "";
            try {
                caption = el.shadowRoot.textContent.trim();
            } catch(e) {}
            return {
                tag: el.tagName.toLowerCase(),
                id: el.id,
                class: el.className,
                caption: caption
            };
        });
    """
    
    shadows = driver.execute_script(script, item)  

    for i, s in enumerate(shadows):
        #print(f"[{i}] tag: {s['tag']}, id: {s['id']}, class: {s['class']}, caption: {s['caption']}")
        dicionario[s['caption']] = s['id'] 

    #print(dicionario)
    return dicionario

#encontar o nome dos botões de acordo com as ids ( ou o contrario )
def encontrar_BTN(ids, nome, qnt):
    for id in ids: 
        if (nome in id) and (qnt > 0): 
            qnt = qnt - 1 
        elif (nome in id): 
            x = id
           
            return x 
            break
        else:
            None 
    
#clicar nos botões
def clicar_BTN(driver, id): 

    seletor = f"#{id}"
    # pega o elemento via JS
    botao = driver.execute_script("return document.querySelector(arguments[0]);", seletor)    
    botao.click()

#junção das 3 funções a cima
def funcao_tres_e_demais(driver, item, nome, qnt):
    nome_normalizado = nome.replace("\xa0", " ")

    time.sleep(5)
    ids = encontrarId(driver, item)
    x = encontrar_BTN(ids, nome_normalizado, qnt)

    #SE ERRO NO X QUER DIZER BOTÂO NÃO ENCONTRADO
    elemento = driver.find_element(By.ID, ids[x])  # pega o WebElement real
    driver.execute_script("arguments[0].scrollIntoView({behavior: 'smooth', block: 'center'});", elemento)
    time.sleep(0.5)
    try:
        # Tenta clicar normalmente
        clicar_BTN(driver, ids[x])
    except Exception as e:
        try:
            seletor = f"#{ids[x]}"
            botao = driver.execute_script("return document.querySelector(arguments[0])", seletor)

            # Função JS para buscar o botão pelo texto dentro de shadow DOMs recursivamente
            script_click_shadow = """
            function clickDeep(root, text){
                if(!root) return false;
                let nodes = root.querySelectorAll('*');
                for(let node of nodes){
                    if(node.shadowRoot){
                        if(clickDeep(node.shadowRoot, text)) return true;
                    }
                    if(node.innerText && node.innerText.trim() === text){
                        node.scrollIntoView(true);
                        node.click();
                        return true;
                    }
                }
                return false;
            }
            return clickDeep(arguments[0], arguments[1]);
            """

            success = driver.execute_script(script_click_shadow, botao, nome_normalizado)
            
        except Exception as e2:
            print("ERRO FINAL: Não foi possível clicar no botão.", e2)

def clicar_aba(driver, nome, timeout=10):

    wait = WebDriverWait(driver, timeout)

    # espera até existir pelo menos uma wa-tab-button
    wait.until(lambda d: d.execute_script(
        "return document.querySelectorAll('wa-tab-button').length > 0;"
    ))

    script = """
        const nomeAba = arguments[0];
        const tabs = document.querySelectorAll("wa-tab-button");

        for (const tab of tabs) {
            if (tab.textContent.trim().includes(nomeAba)) {

                tab.scrollIntoView({ block: "center" });

                tab.dispatchEvent(new PointerEvent('pointerdown', { bubbles: true }));
                tab.dispatchEvent(new PointerEvent('pointerup', { bubbles: true }));
                tab.dispatchEvent(new MouseEvent('click', { bubbles: true }));

                return true;
            }
        }

        return false;
    """

    return driver.execute_script(script, nome)
#inserir texto
def inserir_texto(driver, id, texto, shadow=False, enter=False, quantidade=1):
    # espera elemento estar visível
    campo = WebDriverWait(driver, 20).until(
        EC.visibility_of_element_located((By.ID, id))
    )

    if shadow:
        shadow_root = driver.execute_script(
            "return arguments[0].shadowRoot", campo
        )

        input_real = shadow_root.find_element(By.CSS_SELECTOR, "input, textarea")

        driver.execute_script("""
            arguments[0].focus();
            arguments[0].value = arguments[1];
            arguments[0].dispatchEvent(new Event('input', { bubbles: true }));
            arguments[0].dispatchEvent(new Event('change', { bubbles: true }));
            arguments[0].dispatchEvent(new Event('blur', { bubbles: true }));
        """, input_real, texto)

        elemento_envio = input_real

    else:
        driver.execute_script("""
            arguments[0].focus();
            arguments[0].value = arguments[1];
            arguments[0].dispatchEvent(new Event('input', { bubbles: true }));
            arguments[0].dispatchEvent(new Event('change', { bubbles: true }));
            arguments[0].dispatchEvent(new Event('blur', { bubbles: true }));
        """, campo, texto)
        if enter and quantidade == 1:
            elemento_envio = campo
            elemento_envio.send_keys(Keys.ENTER)
        if enter and quantidade > 1: 
            x = 0
            while x < quantidade: 
                time.sleep(1)
                elemento_envio = campo
                elemento_envio.send_keys(Keys.ENTER)
                x = x + 1

def inserir_na_tabela_shadow(driver, id_tabela, coluna_index, valor, linha_index=0, enter=False):
    print("entrou para TES")
    script = """
    const callback = arguments[arguments.length - 1];
    const idGrid = arguments[0];
    const rowId = arguments[1];
    const colId = arguments[2];
    const valor = String(arguments[3]);

    const esperar = (ms) => new Promise(r => setTimeout(r, ms));

    (async () => {
        try {
            const grid = document.querySelector(`#${idGrid}`);
            if (!grid || !grid.shadowRoot) {
                callback({ ok: false, erro: 'Grid não encontrado ou sem shadowRoot' });
                return;
            }

            const s = grid.shadowRoot;
            const cell = s.querySelector(`tr[id="${rowId}"] td[id="${colId}"]`);
            if (!cell) {
                callback({ ok: false, erro: `Célula não encontrada (${rowId}, ${colId})` });
                return;
            }

            // 1) Clica na célula alvo
            cell.dispatchEvent(new MouseEvent('mousedown', { bubbles: true, composed: true }));
            cell.dispatchEvent(new MouseEvent('mouseup', { bubbles: true, composed: true }));
            cell.dispatchEvent(new MouseEvent('click', { bubbles: true, composed: true }));

            await esperar(500);

            // 2) Enter para abrir o editor
            cell.dispatchEvent(new KeyboardEvent('keydown', {
                key: 'Enter', code: 'Enter', keyCode: 13, which: 13, bubbles: true, composed: true
            }));
            cell.dispatchEvent(new KeyboardEvent('keyup', {
                key: 'Enter', code: 'Enter', keyCode: 13, which: 13, bubbles: true, composed: true
            }));

            await esperar(400);

            // 3) Pega posição da célula
            const cellRect = cell.getBoundingClientRect();

            // 4) Procura o editor mais próximo da célula
            const editores = [...document.querySelectorAll('wa-text-input.dict-tget, wa-text-input[data-advpl="tget"]')]
                .filter(el => {
                    const st = getComputedStyle(el);
                    return st.display !== 'none' && st.visibility !== 'hidden' && el.offsetParent !== null;
                });

            if (!editores.length) {
                callback({ ok: false, erro: 'Nenhum editor visível' });
                return;
            }

            let editor = null;
            let menorDist = Infinity;

            for (const el of editores) {
                const r = el.getBoundingClientRect();
                const dx = Math.abs(r.left - cellRect.left);
                const dy = Math.abs(r.top - cellRect.top);
                const dist = dx + dy;

                if (dist < menorDist) {
                    menorDist = dist;
                    editor = el;
                }
            }

            if (!editor) {
                callback({ ok: false, erro: 'Editor da célula não encontrado' });
                return;
            }

            const input = editor.shadowRoot?.querySelector('input');
            if (!input) {
                callback({ ok: false, erro: 'Input interno não encontrado' });
                return;
            }

            // 5) Foco real
            input.focus();
            await esperar(80);

            // 6) Limpa e posiciona cursor
            input.value = '';
            input.setSelectionRange(0, 0);

            input.dispatchEvent(new InputEvent('input', {
                data: null,
                inputType: 'deleteContentBackward',
                bubbles: true,
                composed: true
            }));

            await esperar(60);

            // 7) Digita corretamente no cursor
            for (const ch of valor) {
                const keyCode = ch.charCodeAt(0);
                const code = ch >= '0' && ch <= '9' ? `Digit${ch}` : '';

                const start = input.selectionStart ?? input.value.length;
                const end = input.selectionEnd ?? input.value.length;

                input.dispatchEvent(new KeyboardEvent('keydown', {
                    key: ch, code, keyCode, which: keyCode, bubbles: true, composed: true
                }));

                input.dispatchEvent(new InputEvent('beforeinput', {
                    data: ch,
                    inputType: 'insertText',
                    bubbles: true,
                    composed: true,
                    cancelable: true
                }));

                // insere no cursor
                input.setRangeText(ch, start, end, 'end');

                input.dispatchEvent(new InputEvent('input', {
                    data: ch,
                    inputType: 'insertText',
                    bubbles: true,
                    composed: true
                }));

                input.dispatchEvent(new KeyboardEvent('keyup', {
                    key: ch, code, keyCode, which: keyCode, bubbles: true, composed: true
                }));

                await esperar(100);
            }

            callback({
                ok: true,
                linha: rowId,
                coluna: colId,
                valor: valor
            });

        } catch (e) {
            callback({ ok: false, erro: e.message || String(e) });
        }
    })();
    """

    resultado = driver.execute_async_script(script, id_tabela, linha_index, coluna_index, str(valor))

    if not resultado or not resultado.get("ok"):
        raise Exception(f"Erro ao inserir na tabela: {resultado}")

    return resultado

def esperar_existir(driver, item, nome, tempo=60):
    nome_normalizado = nome.replace("\xa0", " ")

    def condicao(driver):
        ids = encontrarId(driver, item,)
        x = encontrar_BTN(ids, nome_normalizado, 0)
        return x is not None

    try:
        WebDriverWait(driver, tempo).until(condicao)
        #print(f"Botão '{nome}' disponível.")
        return True
    except TimeoutException:
        #print(f"Botão '{nome}' não apareceu no tempo esperado.")
        return False

def esperar_sumir_panel(driver, caption, tempo=60):
    time.sleep(10)
    try:
        WebDriverWait(driver, tempo).until(
            EC.invisibility_of_element_located(
                (By.CSS_SELECTOR, f'wa-panel[caption="{caption}"]')
            )
        )
        return True
    except TimeoutException:
        return False

def clicar_aba(driver, id_botao, timeout=10):
    wait = WebDriverWait(driver, timeout)


    driver.execute_script("""
        const el = arguments[0];

        el.dispatchEvent(new PointerEvent('pointerdown', {bubbles:true}));
        el.dispatchEvent(new MouseEvent('mousedown', {bubbles:true}));
        el.dispatchEvent(new PointerEvent('pointerup', {bubbles:true}));
        el.dispatchEvent(new MouseEvent('mouseup', {bubbles:true}));
        el.dispatchEvent(new MouseEvent('click', {bubbles:true}));
    """, id_botao)


def marcar_filtro(driver, filtros):

    botao = driver.find_element(By.CSS_SELECTOR, 'wa-button[caption="Filtrar"]')

    # abre o painel
    driver.execute_script("""
        const host = arguments[0];
        const btn = host.shadowRoot?.querySelector('button');
        if (btn) btn.click();
    """, botao)

    esperar_existir(driver, "wa-button", "Aplicar")
    time.sleep(1)

    # desmarca todos via clique real no label
    driver.execute_script("""
        document.querySelectorAll('wa-checkbox').forEach(host => {
            const input = host.shadowRoot?.querySelector('input[type="checkbox"]');
            const label = host.shadowRoot?.querySelector('label');

            if (input && input.checked && label) {
                label.click();
            }
        });
    """)

    time.sleep(1)

    # marca os filtros desejados via clique real no label
    for filtro in filtros:
        checkbox = driver.find_element(
            By.CSS_SELECTOR,
            f'wa-checkbox[caption="{filtro}"]'
        )

        driver.execute_script("""
            const host = arguments[0];
            const input = host.shadowRoot?.querySelector('input[type="checkbox"]');
            const label = host.shadowRoot?.querySelector('label');

            if (input && !input.checked && label) {
                label.click();
            }
        """, checkbox)

        time.sleep(0.5)

        # debug: confirma se realmente ficou marcado
        marcado = driver.execute_script("""
            const host = arguments[0];
            const input = host.shadowRoot?.querySelector('input[type="checkbox"]');
            return input ? input.checked : null;
        """, checkbox)

        print(f"Filtro '{filtro}' marcado? {marcado}")

    time.sleep(1)

    # aplicar
    funcao_tres_e_demais(driver, "wa-button", "Aplicar", 0)

def pegar_texto_input(driver, id): 
    element = driver.find_element(By.ID, id)
    shadow_root = driver.execute_script("return arguments[0].shadowRoot", element)
    input_field = shadow_root.find_element(By.CSS_SELECTOR, "input")
    valor = input_field.get_attribute("value")
    return valor

def cancelar_lancamento_de_nota(driver):
    print("Cancelando para não lançar...")
    funcao_tres_e_demais(driver, "wa-button", "Cancelar", 0)
    time.sleep(1)
    funcao_tres_e_demais(driver, "wa-button", "Não", 0)

    print("========================================")
    print("FIM LANCAMENTO")

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

def encerrar_sistema(driver): 
    log("Encerrando o sistema....")
    funcao_tres_e_demais(driver,"wa-button","Log Off",0 )
    funcao_tres_e_demais(driver,"wa-button","Finalizar",0 )

# =====================================================
# FUNÇÃO DE LOG
# =====================================================

import os
from datetime import datetime

logfile_atual = None  # guarda o arquivo desta execução

def log(msg):
    global logfile_atual

    try: 
        pasta_relatorio = r'C:\Users\gustavo.elicker\Desktop\REGISTROS\LOG'
    except:
        pasta_relatorio = r"C:\Users\DALBAPY\Desktop\Nova pasta\REGISTRO\LOG"

    # Define o arquivo apenas uma vez por execução
    if logfile_atual is None:
        data_hoje = datetime.now().strftime('%Y-%m-%d')
        nome_base = f"log_{data_hoje}.txt"
        logfile = os.path.join(pasta_relatorio, nome_base)

        # Se já existir, cria log_YYYY-MM-DD_2.txt, _3, _4...
        if os.path.exists(logfile):
            contador = 2
            while True:
                nome_novo = f"log_{data_hoje}_{contador}.txt"
                novo_logfile = os.path.join(pasta_relatorio, nome_novo)

                if not os.path.exists(novo_logfile):
                    logfile = novo_logfile
                    break

                contador += 1

        logfile_atual = logfile  # salva para reutilizar durante toda a execução

    timestamp = datetime.now().strftime("[%H:%M:%S]")
    msg_formatado = f"{timestamp} {msg}"
    print(msg_formatado)

    with open(logfile_atual, "a", encoding="utf-8") as f:
        f.write(msg_formatado + "\n")

# variável global para reutilizar o mesmo arquivo durante a execução
arquivo_relatorio_atual = None


def relatorio_consolidado(lista_notas_lancadas, lista_notas_nao_lancadas, filial_atual):
    """
    Gera relatório consolidado para o cliente:
    - 1 arquivo por execução
    - Se já existir relatório do dia, cria _2, _3, etc.
    - Durante a mesma execução, reutiliza o mesmo arquivo
    """

    global arquivo_relatorio_atual

    try:
        pasta_relatorio = r'C:\Users\gustavo.elicker\Desktop\REGISTROS\RELATORIO'
    except:
        pasta_relatorio = r"C:\Users\DALBAPY\Desktop\Nova pasta\REGISTRO\RELATORIO"

    # cria a pasta se não existir
    os.makedirs(pasta_relatorio, exist_ok=True)

    # Define o arquivo apenas uma vez por execução
    if arquivo_relatorio_atual is None:
        data_hoje = datetime.now().strftime('%d-%m-%y')
        nome_base = f"relatorio_{data_hoje}.txt"
        arquivo_relatorio = os.path.join(pasta_relatorio, nome_base)

        # Se já existir, cria relatorio_dd-mm-aa_2.txt, _3, _4...
        if os.path.exists(arquivo_relatorio):
            contador = 2
            while True:
                nome_novo = f"relatorio_{data_hoje}_{contador}.txt"
                novo_arquivo = os.path.join(pasta_relatorio, nome_novo)

                if not os.path.exists(novo_arquivo):
                    arquivo_relatorio = novo_arquivo
                    break

                contador += 1

        arquivo_relatorio_atual = arquivo_relatorio  # salva para reutilizar

    # Limite de largura para centralização
    largura = 60

    def extrair_campo(nota, campo, padrao="N/I"):
        """
        Extrai valor de um campo de uma lista de strings no formato 'CAMPO: valor'
        Exemplo: 'FORNECEDOR: EMPRESA XYZ'
        """
        return next(
            (x.split(": ", 1)[1] for x in nota if x.startswith(campo)),
            padrao
        )

    # Define a filial do título com base na primeira nota disponível
    if lista_notas_lancadas:
        filial_titulo = extrair_campo(lista_notas_lancadas[0], "FILIAL")
    elif lista_notas_nao_lancadas:
        filial_titulo = extrair_campo(lista_notas_nao_lancadas[0], "FILIAL")
    else:
        filial_titulo = filial_atual

    with open(arquivo_relatorio_atual, "a", encoding="utf-8") as f:
        # Título centralizado
        titulo = f"RELATÓRIO DE NOTAS FISCAIS - FILIAL {filial_titulo}"
        print(titulo.center(largura))
        f.write(titulo.center(largura) + "\n\n")

        # LANÇADAS
        titulo_lancadas = "LANÇADAS"
        print(titulo_lancadas.center(largura))
        f.write(titulo_lancadas.center(largura) + "\n")

        if lista_notas_lancadas:
            for nota in lista_notas_lancadas:
                filial = extrair_campo(nota, "FILIAL")
                fornecedor = extrair_campo(nota, "FORNECEDOR", None)
                numero_nota = extrair_campo(nota, "NOTA")

                if fornecedor:
                    linha = f"{filial} - {numero_nota} - {fornecedor}"
                else:
                    linha = f"{filial} - {numero_nota}"

                print(linha)
                f.write(linha + "\n")
        else:
            print("Nenhuma nota lançada")
            f.write("Nenhuma nota lançada\n")

        f.write("\n")

        # NÃO LANÇADAS
        titulo_nao_lancadas = "NÃO LANÇADAS"
        print(titulo_nao_lancadas.center(largura))
        f.write(titulo_nao_lancadas.center(largura) + "\n")

        if lista_notas_nao_lancadas:
            for nota in lista_notas_nao_lancadas:
                filial = extrair_campo(nota, "FILIAL")
                fornecedor = extrair_campo(nota, "FORNECEDOR", None)
                numero_nota = extrair_campo(nota, "NOTA")
                motivo = extrair_campo(nota, "MOTIVO", "Motivo não informado")

                if fornecedor:
                    linha = f"{filial} - FORNECEDOR: {fornecedor} - NOTA: {numero_nota} - {motivo}"
                else:
                    linha = f"{filial} - {numero_nota} - {motivo}"

                print(linha)
                f.write(linha + "\n")
        else:
            print("Nenhuma nota não lançada")
            f.write("Nenhuma nota não lançada\n")

        f.write("\n" + "=" * largura + "\n\n")

    print("\nRelatório salvo em:", arquivo_relatorio_atual)
