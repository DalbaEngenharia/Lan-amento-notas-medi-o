from imports import *
from Protheus_Biblioteca import *
from LOOP import LoopLancamentos

import os
import time

from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait


# =========================
# CONFIG
# =========================
homologacao = False
teste = 1

chrome_options = Options()

# =========================
# PERFIL (SEGURO PARA .EXE)
# =========================
profile_path = os.path.join(os.getcwd(), "chrome_profile")
chrome_options.add_argument(f"--user-data-dir={profile_path}")

# =========================
# MODO EXECUÇÃO
# =========================
if not homologacao and teste == 0:
    chrome_options.add_argument("--headless=new")
    chrome_options.add_argument("--window-size=1920,1080")
    credenciais = ["robo", "robo2025"]

elif not homologacao and teste == 1:
    chrome_options.add_argument("--start-maximized")
    credenciais = ["robo", "robo2025"]

else:
    chrome_options.add_argument("--start-maximized")
    credenciais = ["gustavo.elicker", "123abc"]


# =========================
# ESTABILIDADE (ESSENCIAL)
# =========================
chrome_options.add_argument("--no-sandbox")
chrome_options.add_argument("--disable-dev-shm-usage")
chrome_options.add_argument("--disable-gpu")
chrome_options.add_argument("--remote-debugging-port=9222")

# =========================
# CONFIG EXTRA
# =========================
chrome_options.add_argument("--disable-notifications")
chrome_options.add_argument("--disable-popup-blocking")
chrome_options.add_argument("--disable-extensions")
chrome_options.add_argument("--disable-infobars")
chrome_options.add_argument("--ignore-certificate-errors")
chrome_options.add_argument("--allow-insecure-localhost")
chrome_options.add_argument("--use-fake-ui-for-media-stream")

chrome_options.add_argument(
    "--unsafely-treat-insecure-origin-as-secure=http://protheus.dalba.com.br:1239"
)

# =========================
# PREFS
# =========================
prefs = {
    "profile.default_content_setting_values.notifications": 2
}
chrome_options.add_experimental_option("prefs", prefs)


# =========================
# DRIVER (LOCAL!)
# =========================
# 👉 COLOQUE o chromedriver.exe na mesma pasta do .exe
service = Service("chromedriver.exe")

driver = webdriver.Chrome(service=service, options=chrome_options)
wait = WebDriverWait(driver, 20)


# =========================
# INÍCIO DO FLUXO
# =========================
iniciar_ambiente(homologacao, driver)
log("INICIANDO AMBIENTE")

confirmaBase(driver, wait)
log("CONFIRMANDO BASE")

login(driver, wait, credenciais)
log("REALIZANDO LOGIN")

sel_ambiente(driver, wait, "2", homologacao)
log("ENTRANDO EM ATUALIZAÇÕES")

funcao_tres_e_demais(driver, "wa-menu-item", "Atualizações", 0)
log("ENTRANDO EM MOVIMENTOS")

funcao_tres_e_demais(driver, "wa-menu-item", "Movimentos", 0)

LoopLancamentos(driver)
log("ENTRANDO EM LOOP LANÇAMENTOS")