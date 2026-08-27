from decimal import Decimal
import time

from Protheus_Biblioteca import *
from tabelas.tabelas_protheus import *


# ============================================================
# CONVERSÃO DE VALORES
# ============================================================

def _decimal_br(valor):
    """
    Converte valores brasileiros para Decimal.

    Exemplos:
        "120,00"        -> Decimal("120.00")
        "1.200,00"      -> Decimal("1200.00")
        "120,0100000"   -> Decimal("120.0100000")
        "120.01"        -> Decimal("120.01")
    """

    valor = str(valor).strip()

    if not valor:
        return Decimal("0")

    if "," in valor:
        valor = valor.replace(".", "")
        valor = valor.replace(",", ".")

    return Decimal(valor)


def _decimal_para_br_7(valor):
    """
    Decimal -> formato brasileiro com 7 casas.

    Decimal("120.01")
        ->
    "120,0100000"
    """

    return f"{valor:.7f}".replace(".", ",")


# ============================================================
# INSERE DIRETAMENTE NO UNITÁRIO
# COMP6022 / LINHA 0 / COLUNA 5
# M->D1_VUNIT
# ============================================================

def inserir_na_tabela_shadow_teste_local(driver, valor):

    script = r"""
    const callback = arguments[arguments.length - 1];
    const valor = String(arguments[0]);

    const grid = document.querySelector("#COMP6022");

    const rowId = "0";
    const colId = "5";

    const sleep = ms => new Promise(r => setTimeout(r, ms));

    (async () => {

        try {

            // ==================================================
            // GRID
            // ==================================================

            if (!grid || !grid.shadowRoot) {
                callback({
                    ok: false,
                    erro: "Grid COMP6022 não encontrada"
                });
                return;
            }


            // ==================================================
            // CÉLULA EXATA
            // ==================================================

            const cell = grid.shadowRoot.querySelector(
                `tr[id="${rowId}"] td[id="${colId}"]`
            );

            if (!cell) {
                callback({
                    ok: false,
                    erro: "Célula COMP6022 / linha 0 / coluna 5 não encontrada"
                });
                return;
            }

            console.log("CÉLULA ALVO:", cell);


            // ==================================================
            // ABRE A CÉLULA
            // ==================================================

            cell.dispatchEvent(new MouseEvent("mousedown", {
                bubbles: true,
                composed: true
            }));

            await sleep(80);

            cell.dispatchEvent(new MouseEvent("mouseup", {
                bubbles: true,
                composed: true
            }));

            await sleep(80);

            cell.dispatchEvent(new MouseEvent("click", {
                bubbles: true,
                composed: true
            }));

            await sleep(300);


            cell.dispatchEvent(new KeyboardEvent("keydown", {
                key: "Enter",
                code: "Enter",
                keyCode: 13,
                which: 13,
                bubbles: true,
                composed: true
            }));

            await sleep(600);


            // ==================================================
            // PROCURA O EDITOR DO UNITÁRIO
            // ==================================================

            const editores = [
                ...document.querySelectorAll(
                    'wa-text-input.dict-tget, wa-text-input[data-advpl="tget"]'
                )
            ];

            const editor = editores.find(
                e => e.getAttribute("name") === "M->D1_VUNIT"
            );

            if (!editor) {

                callback({
                    ok: false,
                    erro: "Editor M->D1_VUNIT não encontrado"
                });

                return;
            }


            console.log("================================");
            console.log("EDITOR UNITÁRIO");
            console.log("ID:", editor.id);
            console.log("NAME:", editor.getAttribute("name"));
            console.log("OWNER:", editor.ownerId);
            console.log("================================");


            // ==================================================
            // SEGURANÇA
            // ==================================================

            if (editor.getAttribute("name") !== "M->D1_VUNIT") {

                callback({
                    ok: false,
                    erro:
                        "Editor incorreto: " +
                        editor.getAttribute("name")
                });

                return;
            }


            // ==================================================
            // LIMPA O BUFFER
            // ==================================================

            editor.resetBuffer();

            await sleep(100);


            // ==================================================
            // DIGITA PELO MECANISMO INTERNO
            // ==================================================

            for (const ch of valor) {
                editor.insertKey(ch);
            }

            await sleep(100);


            // ==================================================
            // ATUALIZA BUFFER / DISPLAY
            // ==================================================

            editor.writeBuffer();

            await sleep(200);


            console.log(
                "VALOR EDITOR:",
                JSON.stringify(editor.value)
            );

            console.log(
                "BUFFER:",
                JSON.stringify(editor.bufferValues)
            );


            // ==================================================
            // CHANGE
            // ==================================================

            editor.dispatchEvent(
                new Event("change", {
                    bubbles: true,
                    composed: true
                })
            );

            await sleep(150);


            // ==================================================
            // COMMIT
            // ==================================================

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


            // ==================================================
            // RETORNO
            // ==================================================

            callback({

                ok: true,

                grid: "COMP6022",

                linha: rowId,

                coluna: colId,

                editor: editor.id,

                name: editor.getAttribute("name"),

                valorSolicitado: valor,

                valorEditor: editor.value,

                buffer: editor.bufferValues,

                celula: cell.innerText

            });

        }

        catch (e) {

            callback({
                ok: false,
                erro: e.message || String(e)
            });

        }

    })();
    """

    resultado = driver.execute_async_script(
        script,
        str(valor)
    )

    if not resultado or not resultado.get("ok"):
        raise Exception(
            f"Erro ao inserir no unitário: {resultado}"
        )

    return resultado


# ============================================================
# AJUSTA CENTAVO
#
# coluna 5 = UNITÁRIO
# coluna 6 = TOTAL
#
# O cálculo é feito SEMPRE sobre a coluna 5.
# ============================================================

def ajusta_centavo(driver, sentido):

    print("================================")
    print("AJUSTE DE CENTAVO")
    print("================================")


    # ========================================================
    # LÊ UNITÁRIO ATUAL
    # ========================================================

    linhas = linhas_de_tabela(
        driver,
        "COMP6022"
    )

    colunas = colunas_da_tabela(
        driver,
        linhas
    )

    print("TABELA ATUAL:")

    for i, linha in enumerate(colunas):
        print(i, linha)


    # ========================================================
    # COLUNA 5 = UNITÁRIO
    # ========================================================

    valor_unitario_str = str(
        colunas[0][5]
    ).strip()

    valor_unitario_atual = _decimal_br(
        valor_unitario_str
    )


    # ========================================================
    # COLUNA 6 = TOTAL
    #
    # Apenas para diagnóstico.
    # NÃO usamos para calcular o unitário.
    # ========================================================

    valor_total_str = str(
        colunas[0][6]
    ).strip()

    valor_total_atual = _decimal_br(
        valor_total_str
    )


    print("================================")
    print("VALORES ATUAIS")
    print("================================")

    print(
        "UNITÁRIO:",
        valor_unitario_atual
    )

    print(
        "TOTAL:",
        valor_total_atual
    )


    # ========================================================
    # CALCULA NOVO UNITÁRIO
    # ========================================================

    if sentido == "abaixo":

        valor_unitario_novo = (
            valor_unitario_atual
            + Decimal("0.01")
        )

    elif sentido == "acima":

        valor_unitario_novo = (
            valor_unitario_atual
            - Decimal("0.01")
        )

    else:

        raise ValueError(
            "sentido deve ser 'acima' ou 'abaixo'"
        )


    valor_novo_str = _decimal_para_br_7(
        valor_unitario_novo
    )


    print("================================")
    print("NOVO UNITÁRIO")
    print("================================")

    print(
        "Atual:",
        valor_unitario_atual
    )

    print(
        "Novo:",
        valor_unitario_novo
    )

    print(
        "String:",
        valor_novo_str
    )


    # ========================================================
    # INSERE EXATAMENTE NO UNITÁRIO
    # COMP6022 / 0 / 5
    # ========================================================

    resultado = inserir_na_tabela_shadow_teste_local(
        driver,
        valor_novo_str
    )


    print("================================")
    print("INSERÇÃO")
    print("================================")

    print(resultado)


    # ========================================================
    # ESPERA O PROTHEUS RECALCULAR
    # ========================================================

    time.sleep(1)


    # ========================================================
    # LÊ NOVAMENTE A TABELA
    # ========================================================

    linhas = linhas_de_tabela(
        driver,
        "COMP6022"
    )

    colunas = colunas_da_tabela(
        driver,
        linhas
    )


    # ========================================================
    # NOVO UNITÁRIO
    # ========================================================

    novo_unitario_str = str(
        colunas[0][5]
    ).strip()

    novo_unitario = _decimal_br(
        novo_unitario_str
    )


    # ========================================================
    # NOVO TOTAL
    # ========================================================

    novo_total_str = str(
        colunas[0][6]
    ).strip()

    novo_total = _decimal_br(
        novo_total_str
    )


    print("================================")
    print("RESULTADO FINAL")
    print("================================")

    print(
        "UNITÁRIO ANTES:",
        valor_unitario_atual
    )

    print(
        "UNITÁRIO SOLICITADO:",
        valor_unitario_novo
    )

    print(
        "UNITÁRIO DEPOIS:",
        novo_unitario
    )

    print(
        "TOTAL DEPOIS:",
        novo_total
    )

    print("================================")


    # ========================================================
    # CONFIRMA QUE ALTEROU O UNITÁRIO
    # ========================================================

    if novo_unitario != valor_unitario_novo:

        raise Exception(
            "Protheus não aceitou o novo valor unitário. "
            f"Solicitado={valor_unitario_novo} "
            f"Atual={novo_unitario}"
        )


    print("CENTAVO AJUSTADO COM SUCESSO.")


    return {
        "ok": True,
        "unitario_anterior": str(valor_unitario_atual),
        "unitario_novo": str(novo_unitario),
        "total_anterior": str(valor_total_atual),
        "total_novo": str(novo_total),
        "resultado_insercao": resultado
    }