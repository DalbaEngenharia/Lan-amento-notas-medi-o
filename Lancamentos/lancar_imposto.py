from Protheus_Biblioteca import *
from verificar_notas.texto_notas import consultar_impostos_nota
from Listas.lista import lista_de_impostos
from tabelas.tabelas_protheus import *
from Lancamentos.mapeamento_impostos import mapa_impostos
import time


def normalizar_valor(valor):

    if valor is None:
        return ""

    return (
        str(valor)
        .replace(".", "")
        .replace(" ", "")
        .strip()
    )


def preencher_wa_numero(driver, componente_id, valor):

    return driver.execute_script("""
        const comp = document.querySelector(arguments[0]);

        if (!comp)
            throw new Error('Componente não encontrado: ' + arguments[0]);

        comp.resetBuffer();

        for (const c of arguments[1]) {
            comp.insertKey(c);
        }

        comp.focus();
        comp.blur();

        comp.dispatchEvent(
            new Event('input', { bubbles:true })
        );

        comp.dispatchEvent(
            new Event('change', { bubbles:true })
        );

        return {
            value: comp.value,
            inputValue: comp.inputValue,
            buffer: comp.bufferValues
        };
    """,
    f"#{componente_id}",
    str(valor)
    )


def lancar_imposto(driver, caminho_nota_servidor, filial):

    print("LANCAMENTO DE IMPOSTO")

    driver.find_element(
        By.ID,
        "BUTTON-COMP6029"
    ).click()

    impostos_llm = consultar_impostos_nota(caminho_nota_servidor,filial)

    print(impostos_llm)

    if not impostos_llm:
        raise Exception("Nenhum retorno recebido da consulta de impostos.")

    if not impostos_llm.get("impostos"):
        raise Exception("Nenhum imposto encontrado para lançamento.")

    body = driver.find_element(
        By.TAG_NAME,
        "body"
    )

    validacoes = []

    for i, imposto in enumerate(impostos_llm["impostos"]):

        tipo = imposto["tipo"]
        base = imposto["base"]
        valor_imposto = imposto["valor"]
        print(tipo, base, valor_imposto)

        # abre inclusão
        driver.execute_script("""
            const linha = document
                .querySelector('#COMP6105')
                .shadowRoot
                .querySelector('tbody tr');

            linha.focus();

            ['keydown','keypress','keyup'].forEach(evt => {

                linha.dispatchEvent(
                    new KeyboardEvent(evt,{
                        key:'Enter',
                        code:'Enter',
                        keyCode:13,
                        which:13,
                        bubbles:true
                    })
                );

            });
        """)

        time.sleep(2)

        # valida imposto
        if tipo not in lista_de_impostos:
            raise Exception(
                f"Imposto não encontrado na lista: {tipo}"
            )

        indice_imposto = lista_de_impostos.index(tipo)

        # seleciona imposto
        driver.execute_script(f"""
            const combo = document
                .querySelector('#COMP7502')
                .shadowRoot
                .querySelector('select');

            combo.value = '{indice_imposto}';

            combo.dispatchEvent(
                new Event('change', {{
                    bubbles: true
                }})
            );
        """)

        time.sleep(1)

        # BASE
        for tentativa in range(10):

            info = preencher_wa_numero(driver,"COMP7505",base)

            print("BASE:", info)

            body.send_keys(Keys.TAB)

            time.sleep(1)

            base_sistema = pegar_texto_input(driver,"COMP7505")

            print("base sistema:", base_sistema)

            if (
                normalizar_valor(base_sistema) == normalizar_valor(base) ):
                print("BASE OK")
                break

            else:
                raise Exception(
                    f"Não foi possível gravar a BASE do imposto {tipo}. "
                    f"Esperado: {base}"
                )

        # VALOR
        for tentativa in range(10):

            info = preencher_wa_numero(driver,"COMP7506",valor_imposto)

            print("VALOR:", info)

            body.send_keys(Keys.TAB)

            time.sleep(1)

            valor_sistema = pegar_texto_input(driver,"COMP7506")

            print("valor sistema:", valor_sistema)

            if ( normalizar_valor(valor_sistema) == normalizar_valor(valor_imposto) ):
                print("VALOR OK")
                break

            else:
                raise Exception(
                    f"Não foi possível gravar o VALOR do imposto {tipo}. "
                    f"Esperado: {valor_imposto}"
                )

        # conferência final da linha
        base_final = pegar_texto_input(driver,"COMP7505")

        valor_final = pegar_texto_input(driver,"COMP7506")

        print("BASE FINAL:", base_final)
        print("VALOR FINAL:", valor_final)

        if (normalizar_valor(base_final)!=normalizar_valor(base)):
            raise Exception(
                f"Base divergente para {tipo}. "
                f"Esperado: {base} | Sistema: {base_final}"
            )

        if (normalizar_valor(valor_final) != normalizar_valor(valor_imposto) ):
            raise Exception(
                f"Valor divergente para {tipo}. "
                f"Esperado: {valor_imposto} | Sistema: {valor_final}"
            )

        validacoes.append({
            "tipo": tipo,
            "base": base_final,
            "valor": valor_final
        })

        body.send_keys(Keys.ENTER)

        time.sleep(2)

        # conferência final antes de salvar
        esperado = len(impostos_llm["impostos"])
        realizado = len(validacoes)

        print(f"Esperado: {esperado}")
        print(f"Validado: {realizado}")

        if realizado != esperado:
            raise Exception(
                f"Quantidade de impostos divergente. "
                f"Esperado: {esperado} | Validado: {realizado}"
            )

        print("Resumo dos impostos lançados:")

        for item in validacoes:
            print(
                f"Tipo: {item['tipo']} | "
                f"Base: {item['base']} | "
                f"Valor: {item['valor']}"
            )

        print("Todas as validações concluídas com sucesso.")

        funcao_tres_e_demais(driver,"wa-button","Salvar")

        
        # verificar aliquota na tabela: 
            # se diferente da aliquita do imposto
                #coloca nos itens direto do produto
                #altera valor do imposto
            # else
                # coninue

        time.sleep(5)
        linhas = linhas_de_tabela(driver, "COMP6105")
        colunas = colunas_da_tabela(driver, linhas)
        imprimir_tabela_por_id(driver,"COMP6105")
        print("###########################")
        for j, linha in enumerate(colunas):

            if j == 0:
                continue
            if j == i+1: 
                codigo = linha[0].strip()
                descricao = linha[1].strip()
                base = linha[2].strip()
                aliquota = linha[3].strip()
                valor = linha[4].strip()

                print(
                    codigo,
                    descricao,
                    base,
                    aliquota,
                    valor
                )
                if aliquota != imposto['aliquota']:
                    print("Aliquitas diferentes, ajustar")
                    for coluna_mapeada in mapa_impostos: 
                        if codigo in coluna_mapeada : 
                            print("coluna_mapeada: ", coluna_mapeada,"--", mapa_impostos[coluna_mapeada])
                        if codigo in coluna_mapeada and "Aliq" in coluna_mapeada:
                            print("---->",mapa_impostos[coluna_mapeada],"<----")
                            
                            #autaliza a tabela
                            linhas_para_base = linhas_de_tabela(driver,"COMP6022")
                            colunas_para_base = colunas_da_tabela(driver,linhas_para_base)
                            
                            #loop para as linhas de produtos 
                            for index, linhas_local in enumerate(colunas_para_base):
                                for tentativas in range(5):
                                    if imposto['aliquota'][1] ==',': 
                                        alq_temp = "0" + imposto['aliquota']
                                        inserir_na_tabela_shadow(driver,"COMP6022",mapa_impostos[coluna_mapeada],alq_temp,index)
                                    else:                                 
                                        inserir_na_tabela_shadow(driver,"COMP6022",mapa_impostos[coluna_mapeada],imposto["aliquota"],index)

                                    linhas_para_base = linhas_de_tabela(driver,"COMP6022")
                                    colunas_para_base = colunas_da_tabela(driver,linhas_para_base) 
                                    if colunas_para_base[index][64] == imposto['aliquota']: 
                                        tentativa = 0 
                                        for tentativa in range(5):
                                            time.sleep(5)
                                            insercao_tabela_teste(driver,"COMP6105",4,"46,02",j)                                            
                                            imprimir_tabela_por_id(driver,"COMP6105")
                                            body.send_keys(Keys.ESCAPE)
                                        
                                        
                                        
                                        break
                                    else: 
                                        continue
                                        
                                #criar função para mudar aliquota aqui
                else: 
                    print("ALiquitas iguais")
                    continue
        print("###########################")
        print("###########################")
        print("###########################")
        print("###########################")
        imprimir_tabela_por_id(driver,"COMP6022")
        
        time.sleep(1)

    print("Fim do lançamento dos impostos")