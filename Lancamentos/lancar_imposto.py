from Protheus_Biblioteca import *
from verificar_notas.texto_notas import encontrar_nota
from verificar_notas.texto_notas import consultar_impostos_nota


def lancar_imposto(driver, caminho_nota_servidor, filial):

    print("LANCAMENTO DE IMPOSTO")

    driver.find_element(By.ID,"BUTTON-COMP6029").click()

    impostos = consultar_impostos_nota(caminho_nota_servidor,filial)

    print(impostos)

    if not impostos:
        return

    for imposto in impostos["impostos"]:

        tipo = imposto["tipo"]
        base = imposto["base"]
        aliquota = imposto["aliquota"]
        valor = imposto["valor"]

    print(tipo, base, aliquota, valor)
    #clica na celula para lançar impostos
    driver.execute_script("""
        const linha = document
            .querySelector('#COMP6105')
            .shadowRoot
            .querySelector('tbody tr');

        linha.focus();

        ['keydown', 'keypress', 'keyup'].forEach(tipo => {

            linha.dispatchEvent(new KeyboardEvent(tipo, {
                key: 'Enter',
                code: 'Enter',
                keyCode: 13,
                which: 13,
                bubbles: true
            }));

        });
    """)
    time.sleep(3)
    #seleciona o imposto na lista
    driver.execute_script("""
                        const combo = document
                            .querySelector('#COMP7502')
                            .shadowRoot
                            .querySelector('select');

                            combo.value = '1';

                            combo.dispatchEvent(new Event('change', {
                                bubbles: true
                            }));
                        """)
    for tentativa in range(0,10):
        
        base_sistema = pegar_texto_input(driver,"COMP7505")
        if base_sistema == base:
            break
        else:
            inserir_texto(driver,"COMP7505",base)

    inserir_texto(driver,"COMP7506",valor )
    
    # lançar selenium aqui