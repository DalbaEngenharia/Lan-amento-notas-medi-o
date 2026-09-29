from smb.SMBConnection import SMBConnection

from Protheus_Biblioteca import log

import pdfplumber
import os
import time

# OCR / LLM2
from verificar_notas.consulta_llm.ocr import ler_pdf as ler_pdf_ocr


def extrair_pdf(caminho):
    """
    Primeira tentativa:
    tenta extrair texto diretamente do PDF.
    """

    texto_pdf = ""

    try:

        log(
            f"[PDF] Tentando leitura normal: "
            f"{caminho}"
        )

        with pdfplumber.open(caminho) as pdf:

            for i, pagina in enumerate(
                pdf.pages,
                start=1
            ):

                conteudo = pagina.extract_text()

                if conteudo:

                    texto_pdf += (
                        conteudo + "\n"
                    )

                else:

                    log(
                        f"[PDF] Página {i} "
                        f"sem texto"
                    )

    except Exception as e:

        log(
            f"[PDF] Erro ao abrir/extrair "
            f"{caminho}: {e}"
        )

    return texto_pdf


def baixar_arquivo_smb(
    conn,
    service_name,
    remote_path,
    local_path,
    timeout=20
):
    """
    Faz download do arquivo SMB.
    """

    try:

        log(
            f"[SMB] Iniciando download: "
            f"{remote_path}"
        )

        inicio = time.time()

        with open(local_path, "wb") as f:

            conn.retrieveFile(
                service_name,
                remote_path,
                f,
                timeout=timeout
            )

        fim = time.time()

        tamanho = (
            os.path.getsize(local_path)
            if os.path.exists(local_path)
            else 0
        )

        log(
            f"[SMB] Download concluído em "
            f"{fim - inicio:.2f}s | "
            f"{tamanho} bytes"
        )

        return True

    except Exception as e:

        log(
            f"[SMB] Erro no download de "
            f"{remote_path}: {e}"
        )

        return False


def consultar_notas_pdf_no_servidor(
    filial,
    dados
):

    username = "comp_dalba"
    password = "CYtBXO6w"

    conn = SMBConnection(
        username,
        password,
        "python_client",
        "10.40.58.4",
        use_ntlm_v2=True,
        is_direct_tcp=True
    )

    try:

        log("[SMB] Conectando...")

        conectado = conn.connect(
            "10.40.58.4",
            445,
            timeout=10
        )

        if not conectado:

            log(
                "[SMB] Não foi possível conectar."
            )

            return 0, ""

        log("[SMB] Conectado com sucesso.")

    except Exception as e:

        log(f"[SMB] Erro ao conectar: {e}")

        return 0, ""

    caminho = f"/sf1010_{filial}"

    caminho_nota = (
        f"{caminho}/{dados}"
    )

    log(
        f"[SMB] Caminho base: {caminho}"
    )

    log(
        f"[SMB] Caminho da nota: "
        f"{caminho_nota}"
    )

    try:

        arquivos_nota = conn.listPath(
            "custom",
            caminho_nota
        )

        log(
            f"[SMB] {len(arquivos_nota)} "
            f"itens encontrados."
        )

    except Exception as e:

        log(
            f"[SMB] Erro ao listar pasta: {e}"
        )

        conn.close()

        return 0, ""

    texto_final = ""

    pdfs_encontrados = 0

    for a in arquivos_nota:

        if a.filename in [".", ".."]:
            continue

        if not a.filename.lower().endswith(".pdf"):
            continue

        pdfs_encontrados += 1

        log(
            f"[PDF] Arquivo encontrado: "
            f"{a.filename}"
        )

        remote = (
            f"{caminho_nota}/{a.filename}"
        )

        os.makedirs(
            "temp",
            exist_ok=True
        )

        local = os.path.join(
            "temp",
            a.filename
        )

        try:

            # ==================================================
            # 1. BAIXAR PDF
            # ==================================================

            ok = baixar_arquivo_smb(
                conn,
                "custom",
                remote,
                local,
                timeout=20
            )

            if not ok:

                log(
                    f"[PDF] Falha no download: "
                    f"{a.filename}"
                )

                continue

            if (
                not os.path.exists(local)
                or os.path.getsize(local) == 0
            ):

                log(
                    f"[PDF] Arquivo vazio: "
                    f"{local}"
                )

                continue

            # ==================================================
            # 2. PRIMEIRA TENTATIVA
            #    LEITURA NORMAL DO PDF
            # ==================================================

            log(
                "[PDF] Tentando extrair "
                "texto normalmente..."
            )

            texto_nota = extrair_pdf(local)

            # ==================================================
            # 3. SE NÃO CONSEGUIU LER
            #    ATIVA OCR / LLM2
            # ==================================================

            if not texto_nota.strip():

                log(
                    "[PDF] Não foi possível "
                    "extrair texto."
                )

                log(
                    "[OCR] Ativando OCR / LLM2..."
                )

                try:

                    texto_nota = ler_pdf_ocr(
                        local
                    )

                except Exception as e:

                    log(
                        f"[OCR] Erro no OCR: {e}"
                    )

                    texto_nota = ""

            # ==================================================
            # 4. VERIFICA RESULTADO FINAL
            # ==================================================

            if texto_nota.strip():

                log(
                    f"[PDF] Texto obtido: "
                    f"{len(texto_nota)} caracteres"
                )

                texto_final += (
                    f"\n\n"
                    f"===== {a.filename} =====\n\n"
                    f"{texto_nota}\n"
                )

            else:

                log(
                    "[PDF/OCR] Não foi possível "
                    "extrair texto do documento."
                )

        except Exception as e:

            log(
                f"[PDF] Erro ao processar "
                f"{a.filename}: {e}"
            )

        finally:

            # ==================================================
            # 5. APAGA PDF TEMPORÁRIO
            # ==================================================

            if os.path.exists(local):

                try:

                    os.remove(local)

                    log(
                        f"[TEMP] Removido: {local}"
                    )

                except Exception as e:

                    log(
                        f"[TEMP] Erro ao remover "
                        f"{local}: {e}"
                    )

    conn.close()

    log("[SMB] Conexão encerrada.")

    return (
        pdfs_encontrados,
        texto_final
    )