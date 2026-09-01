from Protheus_Biblioteca import *
from verificar_notas.texto_notas import consultar_impostos_nota
from Listas.lista import lista_de_impostos, verificar_imposto, DicImpostos
from tabelas.tabelas_protheus import *
from Lancamentos.mapeamento_impostos import mapa_impostos
import time
import unicodedata

def normalizar_texto(texto):
    return ''.join(
        c for c in unicodedata.normalize('NFD', texto.lower())
        if unicodedata.category(c) != 'Mn'
    )

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
    cn_imposto = True
    while cn_imposto: 
        impostos_llm = consultar_impostos_nota(caminho_nota_servidor,filial)

        print(impostos_llm)

        if not impostos_llm:
            raise Exception("Nenhum retorno recebido da consulta de impostos.")

        elif not impostos_llm.get("impostos"):
            raise Exception("Nenhum imposto encontrado para lançamento.")
        else:
            cn_imposto = False

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
        print("tipo: ", tipo,"--- Indice: ", indice_imposto)
        

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
            teste_base_sistema = normalizar_valor(base_sistema)
            teste_base =  normalizar_valor(base) 
            if (teste_base_sistema == teste_base):
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
            teste_valor_sistema = normalizar_valor(valor_sistema)
            teste_valor_imposto =normalizar_valor(valor_imposto) 
            if ( teste_valor_sistema == teste_valor_imposto ):
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
        teste_base_sistema = normalizar_valor(base_final)
        teste_base = normalizar_valor(base)
        if (teste_base_sistema != teste_base):
            raise Exception(
                f"Base divergente para {tipo}. "
                f"Esperado: {base} | Sistema: {base_final}"
            )
        teste_valor_sistema = normalizar_valor(valor_final)
        teste_valor_imposto = normalizar_valor(valor_imposto)
        if teste_valor_sistema != teste_valor_imposto:
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


        print("Resumo dos impostos lançados:")

        for item in validacoes:
            print(
                f"Tipo: {item['tipo']} | "
                f"Base: {item['base']} | "
                f"Valor: {item['valor']}"
            )

        print("Todas as validações concluídas com sucesso.")

        funcao_tres_e_demais(driver,"wa-button","Salvar")


        time.sleep(5)
        linhas = linhas_de_tabela(driver, "COMP6105")
        colunas = colunas_da_tabela(driver, linhas)
        imprimir_tabela_por_id(driver,"COMP6105")
        print("###########################")
        for j, linha in enumerate(colunas):
            #ignora primeira linha que add imposta
            if j == 0:
                continue

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
            normal1 = normalizar_texto(codigo)
            normal2 = normalizar_texto(imposto['tipo'])
            if DicImpostos[imposto["tipo"]] != codigo:
                continue
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
                                valor_original_linha =  colunas_para_base[index][65]
                                print(valor_original_linha)
                                valor_original_linha = valor_original_linha.replace(".","")
                                if len(imposto['aliquota']) == 1: 
                                    alq_temp = "0"+imposto['aliquota']+",00"
                                    imposto['aliquota'] = imposto['aliquota']+",00"
                        
                                    inserir_na_tabela_shadow(driver,"COMP6022",mapa_impostos[coluna_mapeada],alq_temp,index)
                                    # inserir_na_tabela_shadow(driver,"COMP6022",mapa_impostos[coluna_mapeada]+1,valor_original_linha,index)
                                elif imposto['aliquota'][1] ==',': 
                                    alq_temp = "0" + imposto['aliquota']
                                    inserir_na_tabela_shadow(driver,"COMP6022",mapa_impostos[coluna_mapeada],alq_temp,index)
                                    # inserir_na_tabela_shadow(driver,"COMP6022",mapa_impostos[coluna_mapeada]+1,valor_original_linha,index)

                                else:                                 
                                    inserir_na_tabela_shadow(driver,"COMP6022",mapa_impostos[coluna_mapeada],imposto["aliquota"],index)
                                    # inserir_na_tabela_shadow(driver,"COMP6022",mapa_impostos[coluna_mapeada]+1,valor_original_linha,index,enter=True)
                                script = r"""
                                    const callback = arguments[arguments.length - 1];

                                    const valor = String(arguments[0]);
                                    const rowId = String(arguments[1]);
                                    const colId = String(arguments[2]);

                                    const sleep = ms => new Promise(resolve => setTimeout(resolve, ms));


                                    // ============================================================
                                    // PROCURA RECURSIVA NOS SHADOW DOMs
                                    // ============================================================

                                    function findDeep(root, predicate) {

                                        if (!root) {
                                            return null;
                                        }

                                        if (
                                            root.nodeType === Node.ELEMENT_NODE &&
                                            predicate(root)
                                        ) {
                                            return root;
                                        }

                                        for (const child of root.children || []) {

                                            const found = findDeep(child, predicate);

                                            if (found) {
                                                return found;
                                            }
                                        }

                                        if (root.shadowRoot) {

                                            const found = findDeep(root.shadowRoot, predicate);

                                            if (found) {
                                                return found;
                                            }
                                        }

                                        return null;
                                    }


                                    (async () => {

                                        try {

                                            // ========================================================
                                            // GRID
                                            // ========================================================

                                            const grid = document.querySelector("#COMP6022");

                                            if (!grid) {

                                                callback({
                                                    ok: false,
                                                    erro: "COMP6022 não encontrada"
                                                });

                                                return;
                                            }


                                            if (!grid.shadowRoot) {

                                                callback({
                                                    ok: false,
                                                    erro: "COMP6022 sem shadowRoot"
                                                });

                                                return;
                                            }


                                            // ========================================================
                                            // CÉLULA
                                            // ========================================================

                                            const selector =
                                                `tr[id="${rowId}"] td[id="${colId}"]`;

                                            const cell =
                                                grid.shadowRoot.querySelector(selector);


                                            if (!cell) {

                                                callback({
                                                    ok: false,
                                                    erro: "Célula não encontrada",

                                                    rowId: rowId,
                                                    colId: colId,
                                                    selector: selector
                                                });

                                                return;
                                            }


                                            console.log(
                                                "Célula:",
                                                cell.id,
                                                cell.innerText
                                            );


                                            // ========================================================
                                            // ABRE A CÉLULA
                                            // ========================================================

                                            cell.dispatchEvent(new MouseEvent("mousedown", {
                                                bubbles: true,
                                                composed: true
                                            }));

                                            await sleep(100);


                                            cell.dispatchEvent(new MouseEvent("mouseup", {
                                                bubbles: true,
                                                composed: true
                                            }));

                                            await sleep(100);


                                            cell.dispatchEvent(new MouseEvent("click", {
                                                bubbles: true,
                                                composed: true
                                            }));

                                            await sleep(400);


                                            // ========================================================
                                            // ENTER
                                            // ========================================================

                                            cell.dispatchEvent(new KeyboardEvent("keydown", {
                                                key: "Enter",
                                                code: "Enter",
                                                keyCode: 13,
                                                which: 13,
                                                bubbles: true,
                                                composed: true
                                            }));


                                            await sleep(1000);


                                            // ========================================================
                                            // PROCURA EDITOR COM FOCO
                                            // ========================================================

                                            let editor = null;


                                            for (let tentativa = 0; tentativa < 20; tentativa++) {

                                                editor = findDeep(
                                                    document.documentElement,
                                                    el => {

                                                        return (
                                                            el.tagName === "WA-TEXT-INPUT" &&
                                                            el.classList.contains("focus")
                                                        );
                                                    }
                                                );


                                                if (editor) {
                                                    break;
                                                }


                                                await sleep(250);
                                            }


                                            // ========================================================
                                            // EDITOR NÃO ENCONTRADO
                                            // ========================================================

                                            if (!editor) {

                                                callback({
                                                    ok: false,
                                                    erro: "WA-TEXT-INPUT com focus não encontrado",
                                                    rowId: rowId,
                                                    colId: colId
                                                });

                                                return;
                                            }


                                            console.log("EDITOR:", editor);
                                            console.log("NAME:", editor.getAttribute("name"));
                                            console.log("VALUE ANTES:", editor.value);
                                            console.log("BUFFER ANTES:", editor.bufferValues);


                                            // ========================================================
                                            // LIMPA BUFFER
                                            // ========================================================

                                            editor.resetBuffer();

                                            await sleep(100);


                                            // ========================================================
                                            // DIGITA O VALOR
                                            // ========================================================

                                            for (const ch of valor) {

                                                editor.insertKey(ch);

                                                await sleep(30);
                                            }


                                            await sleep(100);


                                            // ========================================================
                                            // ESCREVE BUFFER
                                            // ========================================================

                                            editor.writeBuffer();

                                            await sleep(200);


                                            console.log("VALUE DEPOIS:", editor.value);
                                            console.log("BUFFER DEPOIS:", editor.bufferValues);


                                            // ========================================================
                                            // CHANGE
                                            // ========================================================

                                            editor.dispatchEvent(
                                                new Event("change", {
                                                    bubbles: true,
                                                    composed: true
                                                })
                                            );


                                            await sleep(200);


                                            // ========================================================
                                            // COMMIT
                                            // ========================================================

                                            editor.dispatchEvent(
                                                new KeyboardEvent("keydown", {
                                                    key: "Enter",
                                                    code: "Enter",
                                                    keyCode: 13,
                                                    which: 13,
                                                    bubbles: true,
                                                    composed: true
                                                })
                                            );


                                            await sleep(100);


                                            editor.dispatchEvent(
                                                new KeyboardEvent("keyup", {
                                                    key: "Enter",
                                                    code: "Enter",
                                                    keyCode: 13,
                                                    which: 13,
                                                    bubbles: true,
                                                    composed: true
                                                })
                                            );


                                            await sleep(500);


                                            // ========================================================
                                            // RETORNO
                                            // ========================================================

                                            callback({

                                                ok: true,

                                                rowId: rowId,

                                                colId: colId,

                                                valorSolicitado: valor,

                                                celulaAntes: cell.innerText,

                                                editor: {

                                                    id: editor.id,

                                                    name: editor.getAttribute("name"),

                                                    ownerId: editor.ownerId,

                                                    value: editor.value,

                                                    bufferValues: editor.bufferValues,

                                                    className: editor.className
                                                }
                                            });


                                        }
                                        catch (e) {

                                            callback({
                                                ok: false,
                                                erro: e.stack || e.message || String(e)
                                            });
                                        }

                                    })();
                                    """


                                resultado = driver.execute_async_script(
                                    script,
                                    str(valor_original_linha),
                                    str(index),
                                    str(mapa_impostos[coluna_mapeada] + 1)
                                )

                                print(resultado)                               
                                linhas_para_base = linhas_de_tabela(driver,"COMP6022")
                                colunas_para_base = colunas_da_tabela(driver,linhas_para_base)
                                if colunas_para_base[index][64] == imposto['aliquota']: 
                                    for _ in range(0,5):
                                        time.sleep(0.3)
                                        insercao_tabela_teste(driver,"COMP6105",4,valor,j)                                            
                                        imprimir_tabela_por_id(driver,"COMP6105")
                                        body.send_keys(Keys.ESCAPE)
                                                
                                    
                                    
                                    
                                    break
                                else: 
                                    continue
                        break
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