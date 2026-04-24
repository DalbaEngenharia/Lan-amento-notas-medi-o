# ADICIONAR NO GERENCIADOR DO SISTEMA
from smb.SMBConnection import SMBConnection
from Protheus_Biblioteca import log
import pdfplumber
import os
import time


def extrair_pdf(caminho):
    texto_pdf = ""
    try:
        log(f"[PDF] Abrindo arquivo: {caminho}")
        with pdfplumber.open(caminho) as pdf:
            for i, pagina in enumerate(pdf.pages, start=1):
                conteudo = pagina.extract_text()
                if conteudo:
                    texto_pdf += conteudo + "\n"
                else:
                    log(f"[PDF] Página {i} sem texto (possível imagem)")
    except Exception as e:
        log(f"[PDF] Erro ao abrir/extrair {caminho}: {e}")
    return texto_pdf


def baixar_arquivo_smb(conn, service_name, remote_path, local_path, timeout=20):
    """
    Faz download do arquivo SMB com logs.
    """
    try:
        log(f"[SMB] Iniciando download: {remote_path}")
        inicio = time.time()

        with open(local_path, "wb") as f:
            conn.retrieveFile(service_name, remote_path, f, timeout=timeout)

        fim = time.time()
        tamanho = os.path.getsize(local_path) if os.path.exists(local_path) else 0

        log(f"[SMB] Download concluído em {fim - inicio:.2f}s | {tamanho} bytes")
        return True

    except Exception as e:
        log(f"[SMB] Erro no download de {remote_path}: {e}")
        return False


def consultar_notas_pdf_no_servidor(filial, dados):
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
        conectado = conn.connect("10.40.58.4", 445, timeout=10)

        if not conectado:
            log("[SMB] Não foi possível conectar ao SMB.")
            return 0, ""

        log("[SMB] Conectado com sucesso.")

    except Exception as e:
        log(f"[SMB] Erro ao conectar: {e}")
        return 0, ""

    caminho = f"/sf1010_{filial}"
    caminho_nota = f"{caminho}/{dados}"

    log(f"[SMB] Caminho base: {caminho}")
    log(f"[SMB] Caminho da nota: {caminho_nota}")

    try:
        arquivos_nota = conn.listPath("custom", caminho_nota)
        log(f"[SMB] {len(arquivos_nota)} itens encontrados na pasta.")
    except Exception as e:
        log(f"[SMB] Erro ao listar pasta SMB: {e}")
        conn.close()
        return 0, ""

    texto_final = ""
    pdfs_encontrados = 0

    for a in arquivos_nota:
        if a.filename in [".", ".."]:
            continue

        if a.filename.lower().endswith(".pdf"):
            pdfs_encontrados += 1

            log(f"[PDF] Arquivo encontrado: {a.filename}")
            log(f"[PDF] Tamanho SMB: {getattr(a, 'file_size', 'desconhecido')} bytes")

            remote = f"{caminho_nota}/{a.filename}"
            local = f"temp_{a.filename}"

            try:
                ok = baixar_arquivo_smb(conn, "custom", remote, local, timeout=20)

                if not ok:
                    log(f"[PDF] Falha no download: {a.filename}")
                    continue

                if not os.path.exists(local) or os.path.getsize(local) == 0:
                    log(f"[PDF] Arquivo vazio: {local}")
                    continue

                texto_nota = extrair_pdf(local)

                if texto_nota.strip():
                    log(f"[PDF] Texto extraído ({len(texto_nota)} chars)")
                    texto_final += texto_nota + "\n"
                else:
                    log(f"[PDF] Sem texto (provável imagem): {a.filename}")

            except Exception as e:
                log(f"[PDF] Erro ao processar {a.filename}: {e}")

            finally:
                if os.path.exists(local):
                    try:
                        os.remove(local)
                        log(f"[TEMP] Removido: {local}")
                    except Exception as e:
                        log(f"[TEMP] Erro ao remover {local}: {e}")

    conn.close()
    log("[SMB] Conexão encerrada.")

    return pdfs_encontrados, texto_final