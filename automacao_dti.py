import os
import smtplib
import ssl
from datetime import datetime
from email.message import EmailMessage

from playwright.sync_api import sync_playwright
from reportlab.lib import colors
from reportlab.lib.pagesizes import A4
from reportlab.platypus import (
    SimpleDocTemplate,
    Paragraph,
    Spacer,
    Image,
    PageBreak,
)
from reportlab.lib.styles import getSampleStyleSheet

# ==========================
# CONFIGURAÇÕES
# ==========================

SEI_URL = "https://sei.defesa.gov.br/"
INTRANET_URL = "https://intranet.defesa.gov.br/"
OUTLOOK_URL = "https://outlook.office.com/mail/"
INTERNET_URL = "https://www.g1.globo.com"

# Email pessoal
PESSOAL_EMAIL = "email@gmail.com"
PESSOAL_SENHA = "senha-ou-app-password"

# Email institucional
INST_EMAIL = "usuario@empresa.com.br"
INST_SENHA = "senha"

SMTP_GMAIL = "smtp.gmail.com"
SMTP_GMAIL_PORT = 587

SMTP_OFFICE365 = "smtp.office365.com"
SMTP_OFFICE365_PORT = 587

ARQUIVO_ANEXO = "teste.txt"

PASTA_EVIDENCIAS = "evidencias"

os.makedirs(PASTA_EVIDENCIAS, exist_ok=True)

resultado = []


# ==========================
# SCREENSHOTS
# ==========================

def verificar_site(page, nome, url):
    try:
        page.goto(url, wait_until="networkidle", timeout=60000)

        screenshot = os.path.join(
            PASTA_EVIDENCIAS,
            f"{nome}.png"
        )

        page.screenshot(
            path=screenshot,
            full_page=True
        )

        resultado.append({
            "item": nome,
            "status": "OK",
            "imagem": screenshot
        })

        print(f"[OK] {nome}")

    except Exception as e:

        resultado.append({
            "item": nome,
            "status": f"FALHA - {str(e)}",
            "imagem": None
        })

        print(f"[FALHA] {nome}: {e}")


# ==========================
# EMAIL
# ==========================

def criar_anexo():

    with open(ARQUIVO_ANEXO, "w", encoding="utf-8") as f:
        f.write(
            f"Teste automático executado em "
            f"{datetime.now()}"
        )


def enviar_email(
        smtp_server,
        porta,
        usuario,
        senha,
        destino,
        assunto):

    try:

        msg = EmailMessage()

        msg["Subject"] = assunto
        msg["From"] = usuario
        msg["To"] = destino

        msg.set_content(
            "Teste automático de envio."
        )

        with open(
            ARQUIVO_ANEXO,
            "rb"
        ) as f:

            msg.add_attachment(
                f.read(),
                maintype="application",
                subtype="octet-stream",
                filename=ARQUIVO_ANEXO
            )

        context = ssl.create_default_context()

        with smtplib.SMTP(
                smtp_server,
                porta) as server:

            server.starttls(context=context)

            server.login(usuario, senha)

            server.send_message(msg)

        resultado.append({
            "item": assunto,
            "status": "OK",
            "imagem": None
        })

        print(f"[OK] {assunto}")

    except Exception as e:

        resultado.append({
            "item": assunto,
            "status": f"FALHA - {e}",
            "imagem": None
        })

        print(f"[FALHA] {assunto}: {e}")


# ==========================
# PDF
# ==========================

def gerar_pdf():

    pdf = SimpleDocTemplate(
        f"Relatorio_Disponibilidade-{datetime.now("%d-%m-%Y-%H:%M:%S")}.pdf",
        pagesize=A4
    )

    styles = getSampleStyleSheet()

    conteudo = []

    conteudo.append(
        Paragraph(
            "Relatório de Disponibilidade",
            styles["Title"]
        )
    )

    conteudo.append(
        Paragraph(
            datetime.now().strftime(
                "%d/%m/%Y %H:%M:%S"
            ),
            styles["Normal"]
        )
    )

    conteudo.append(Spacer(1, 20))

    for item in resultado:

        cor = "green"

        if "FALHA" in item["status"]:
            cor = "red"

        texto = (
            f"<b>{item['item']}</b> : "
            f"<font color='{cor}'>"
            f"{item['status']}</font>"
        )

        conteudo.append(
            Paragraph(
                texto,
                styles["Normal"]
            )
        )

        conteudo.append(
            Spacer(1, 10)
        )

        if item["imagem"]:

            conteudo.append(
                Image(
                    item["imagem"],
                    width=450,
                    height=250
                )
            )

            conteudo.append(
                Spacer(1, 10)
            )

        conteudo.append(
            PageBreak()
        )

    pdf.build(conteudo)

    print(
        "PDF gerado: "
        "Relatorio_Disponibilidade.pdf"
    )


# ==========================
# EXECUÇÃO
# ==========================

def main():

    criar_anexo()

    with sync_playwright() as p:

        browser = p.chromium.launch(
            channel="msedge",
            headless=False
        )

        page = browser.new_page()

        verificar_site(
            page,
            "SEI",
            SEI_URL
        )

        verificar_site(
            page,
            "INTRANET",
            INTRANET_URL
        )

        verificar_site(
            page,
            "Outlook",
            OUTLOOK_URL
        )

        verificar_site(
            page,
            "Internet",
            INTERNET_URL
        )

        browser.close()

    enviar_email(
        SMTP_GMAIL,
        SMTP_GMAIL_PORT,
        PESSOAL_EMAIL,
        PESSOAL_SENHA,
        INST_EMAIL,
        "Teste Pessoal -> Institucional"
    )

    enviar_email(
        SMTP_OFFICE365,
        SMTP_OFFICE365_PORT,
        INST_EMAIL,
        INST_SENHA,
        PESSOAL_EMAIL,
        "Teste Institucional -> Pessoal"
    )

    gerar_pdf()

    print("\n===== RESULTADO =====")

    for item in resultado:

        print(
            f"{item['item']} => "
            f"{item['status']}"
        )


if __name__ == "__main__":
    main()