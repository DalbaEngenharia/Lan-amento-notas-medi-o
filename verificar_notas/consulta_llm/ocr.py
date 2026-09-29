import os
import base64
import requests
import fitz  # PyMuPDF


API_KEY = os.environ.get("GEMINI_API_KEY_2")

URL = (
    "https://vision.googleapis.com/v1/"
    f"images:annotate?key={API_KEY}"
)

MAX_LADO = 4000


def redimensionar_pixmap(pagina):
    """
    Converte uma página do PDF em imagem.
    Limita o maior lado a MAX_LADO pixels.
    """

    largura = pagina.rect.width
    altura = pagina.rect.height

    maior_lado = max(largura, altura)

    escala = (
        MAX_LADO / maior_lado
        if maior_lado > MAX_LADO
        else 1
    )

    matriz = fitz.Matrix(escala, escala)

    pixmap = pagina.get_pixmap(
        matrix=matriz,
        alpha=False
    )

    return pixmap


def ocr_imagem(pixmap):
    """
    Envia uma imagem para a Google Vision API
    e retorna o texto reconhecido.
    """

    imagem_bytes = pixmap.tobytes("png")

    imagem_base64 = base64.b64encode(
        imagem_bytes
    ).decode("utf-8")

    payload = {
        "requests": [
            {
                "image": {
                    "content": imagem_base64
                },
                "features": [
                    {
                        "type": "DOCUMENT_TEXT_DETECTION"
                    }
                ]
            }
        ]
    }

    resposta = requests.post(
        URL,
        json=payload,
        timeout=120
    )

    resposta.raise_for_status()

    dados = resposta.json()

    respostas = dados.get("responses", [])

    if not respostas:
        return ""

    resposta_ocr = respostas[0]

    if "error" in resposta_ocr:

        raise RuntimeError(
            resposta_ocr["error"].get(
                "message",
                "Erro desconhecido na API"
            )
        )

    texto = (
        resposta_ocr
        .get("fullTextAnnotation", {})
        .get("text", "")
    )

    return texto


def ler_pdf(caminho_pdf):
    """
    OCR de todas as páginas de um PDF.

    Retorna o texto reconhecido pelas imagens.
    """

    textos = []

    print(f"\n[OCR] Processando: {caminho_pdf}")

    documento = fitz.open(caminho_pdf)

    try:

        total_paginas = len(documento)

        for numero, pagina in enumerate(
            documento,
            start=1
        ):

            print(
                f"[OCR] Página "
                f"{numero}/{total_paginas}"
            )

            pixmap = redimensionar_pixmap(pagina)

            texto = ocr_imagem(pixmap)

            if texto:

                textos.append(
                    f"\n--- Página {numero} ---\n"
                )

                textos.append(texto)

    finally:

        documento.close()

    return "\n".join(textos)


def ler_todos_pdfs(caminho):
    """
    Recebe o caminho de uma pasta local,
    lê todos os PDFs usando OCR.
    """

    if not os.path.isdir(caminho):

        raise FileNotFoundError(
            f"A pasta não existe: {caminho}"
        )

    pdfs = [
        arquivo
        for arquivo in os.listdir(caminho)
        if arquivo.lower().endswith(".pdf")
    ]

    pdfs.sort()

    if not pdfs:
        return ""

    textos = []

    for nome_pdf in pdfs:

        caminho_pdf = os.path.join(
            caminho,
            nome_pdf
        )

        texto_pdf = ler_pdf(caminho_pdf)

        textos.append(
            f"\n\n{'=' * 80}\n"
            f"ARQUIVO: {nome_pdf}\n"
            f"{'=' * 80}\n\n"
        )

        textos.append(texto_pdf)

    return "\n".join(textos)