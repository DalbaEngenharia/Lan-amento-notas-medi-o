from Protheus_Biblioteca import *
from ConsultaBanco.consulta_municipios import consultar_codigo_do_municipio
from selenium.webdriver.common.by import By
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.support.ui import WebDriverWait
import time

def cadastro_informações_danfe(driver, json):

    # abrir tela
    driver.find_element(By.ID, "BUTTON-COMP6034").click()

    # aguardar carregamento básico
    WebDriverWait(driver, 10).until(
        lambda d: d.execute_script("return document.readyState") == "complete"
    )

    # validar chave
    chave_cadastrada = pegar_texto_input(driver, "COMP6148")
    chave_nota =  json['chave_nota_fiscal']
    if chave_cadastrada != chave_nota:
        print("|", chave_cadastrada, "|")
        print("|",chave_nota, "|")
        inserir_texto(driver, "COMP6148",chave_nota)
    else:
        log("Chave NOTA Ok.")
    time.sleep(1)
    # verificar CT-e
    driver.execute_script("""
    const root = document.querySelector('#COMP6164').shadowRoot;

    const select = root.querySelector('select');

    select.value = "1";

    select.dispatchEvent(new Event('input', { bubbles: true }));
    select.dispatchEvent(new Event('change', { bubbles: true }));
    """)

    if chave_cadastrada != chave_nota:
        print("|", chave_cadastrada, "|")
        print("|",chave_nota, "|")
        inserir_texto(driver, "COMP6164",chave_nota)
    else:
        log("Chave NOTA Ok.")

    texto_tipo_cte = pegar_texto_input(driver, "COMP6164")

    if texto_tipo_cte == "N - Normal":
        print(texto_tipo_cte)
        print("tipo CTE OK")
    time.sleep(5)
    funcao_tres_e_demais(driver,"wa-button","Fechar")
    script = """
    function deepQuery(selector, root = document) {
        const elements = [];

        function traverse(node) {
            if (!node) return;

            if (node.querySelectorAll) {
                node.querySelectorAll(selector).forEach(el => elements.push(el));
            }

            const children = node.querySelectorAll?.('*') || [];
            for (const child of children) {
                if (child.shadowRoot) {
                    traverse(child.shadowRoot);
                }
            }
        }

        traverse(root);
        return elements;
    }

    for (let i = 0; i < 3; i++) {

        const tabBars = deepQuery('wa-tab-bar');

        const visibleTabBars = tabBars.filter(el => {
            const rect = el.getBoundingClientRect();
            return rect.width > 0 && rect.height > 0;
        });

        const tabBar = visibleTabBars[1];

        if (!tabBar || !tabBar.shadowRoot) {
            console.log("TabBar inválido");
            break;
        }

        const buttons = tabBar.shadowRoot.querySelectorAll('wa-button');

        let clicked = false;

        for (const el of buttons) {
            const text = el.shadowRoot
                ?.querySelector('button span')
                ?.innerText
                ?.trim()
                ?.toLowerCase();

            if (text?.includes("next")) {
                el.shadowRoot.querySelector('button').click();
                console.log("NEXT clicado (" + (i+1) + "/3)");
                clicked = true;
                break;
            }
        }

        if (!clicked) {
            console.log("NEXT não encontrado");
            break;
        }
    }
    """
    try: 
        time.sleep(3)
        driver.execute_script(script)
        driver.find_element(By.ID, "BUTTON-COMP6036").click()
        uf_origem_site = pegar_texto_input(driver,"COMP6189") 
        uf_destino_site = pegar_texto_input(driver,"COMP6194") 
        mun_origem_site = pegar_texto_input(driver,"COMP6191") 
        mun_destino_site = pegar_texto_input(driver,"COMP6196") 
        print(uf_origem_site," - ",uf_destino_site," - ",mun_origem_site," - ",mun_destino_site) 
        
        codigo_origem = consultar_codigo_do_municipio(json['uf_origem'], json['municipio_origem'])
        codigo_destinho = consultar_codigo_do_municipio(json['uf_destino'], json['municipio_destino'])
        print("codigo_origem - ", codigo_origem, "codigo_destinho - ",codigo_destinho)
        
        if not uf_origem_site.strip():
            inserir_texto(driver, "COMP6189", json['uf_origem'],enter=True)
        time.sleep(1)
        if not mun_origem_site.strip():
            inserir_texto(driver, "COMP6191", codigo_origem)
        time.sleep(1)
        if not uf_destino_site.strip():
            inserir_texto(driver, "COMP6194", json['uf_destino'],enter=True)
        time.sleep(1)
        if not mun_destino_site.strip():
            inserir_texto(driver, "COMP6196", codigo_destinho)
        None

    except Exception as e:
        print("ERRO REAL:", e)