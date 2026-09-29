import os
import smtplib
from email.message import EmailMessage


PASTA_RELATORIOS = r"C:\Users\DALBAPY\Desktop\Nova pasta\REGISTRO\RELATORIO"

EMAIL_REMETENTE = "robo.dalba@gmail.com"

EMAILS = [
    "gustavo.elicker@dalba.com.br",
    "rfh@dalba.com.br",
    "portal@dalba.com.br",
    "alexssander.matos@dalba.com.br",
    "francislene.amancio@dalba.com.br",
    "rafael.iglesias@dalba.com.br",
    "agner@dalba.com.br"
]


# Coloque aqui a senha da conta que fará o envio
senha = "jxrt cohu soik efhm"


def pegar_ultimo_relatorio():
    """
    Retorna o caminho do relatório .txt mais recente
    dentro da pasta de relatórios.
    """

    arquivos = [
        os.path.join(PASTA_RELATORIOS, arquivo)
        for arquivo in os.listdir(PASTA_RELATORIOS)
        if arquivo.lower().endswith(".txt")
        and arquivo.lower().startswith("relatorio_")
    ]

    if not arquivos:
        raise FileNotFoundError(
            f"Nenhum relatório encontrado em: {PASTA_RELATORIOS}"
        )

    # Pega o arquivo com a data de modificação mais recente
    ultimo = max(
        arquivos,
        key=os.path.getmtime
    )

    return ultimo


def enviar_ultimo_relatorio():
    """
    Envia somente o relatório mais recente.
    Os relatórios anteriores não são enviados novamente.
    """

    caminho_relatorio = pegar_ultimo_relatorio()

    nome_relatorio = os.path.basename(caminho_relatorio)

    print(f"Relatório encontrado: {nome_relatorio}")

    # Lê o conteúdo do relatório
    with open(
        caminho_relatorio,
        "r",
        encoding="utf-8"
    ) as arquivo:

        conteudo = arquivo.read()

    # Cria o e-mail
    mensagem = EmailMessage()

    mensagem["From"] = EMAIL_REMETENTE
    mensagem["To"] = ", ".join(EMAILS)

    mensagem["Subject"] = (
        f"Relatório automático - {nome_relatorio}"
    )

    mensagem.set_content(
        f"""Olá,

Segue o relatório gerado em periodo de medição:

{nome_relatorio}

O arquivo está anexado.

Atenciosamente,
Sistema de Relatórios
"""
    )

    # Anexa o relatório
    mensagem.add_attachment(
        conteudo.encode("utf-8"),
        maintype="text",
        subtype="plain",
        filename=nome_relatorio
    )

    # SMTP
    with smtplib.SMTP(
        "smtp.gmail.com",
        587
    ) as servidor:

        servidor.starttls()

        servidor.login(
            EMAIL_REMETENTE,
            senha
        )

        servidor.send_message(mensagem)

    print(
        f"Relatório enviado com sucesso: {nome_relatorio}"
    )
# enviar_ultimo_relatorio()