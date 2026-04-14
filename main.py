from imports import *
from Protheus_Biblioteca import *
from LOOP import LoopLancamentos
import time
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from webdriver_manager.chrome import ChromeDriverManager


homologacao = False
teste = 0

chrome_options = Options()

# =========================
# PERFIL (REMOVE POPUPS DE VERDADE)
# =========================
chrome_options.add_argument(r"--user-data-dir=C:\selenium\perfil")

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
    credenciais = ["gustavo.elicker", "123abc"]

# =========================
# ESTABILIDADE
# =========================
chrome_options.add_argument("--disable-notifications")
chrome_options.add_argument("--disable-popup-blocking")
chrome_options.add_argument("--disable-extensions")
chrome_options.add_argument("--disable-infobars")
chrome_options.add_argument("--ignore-certificate-errors")
chrome_options.add_argument("--allow-insecure-localhost")

# IMPORTANTE (remove prompt de câmera/microfone)
chrome_options.add_argument("--use-fake-ui-for-media-stream")

# Seu sistema interno
chrome_options.add_argument(
    "--unsafely-treat-insecure-origin-as-secure=http://protheus.dalba.com.br:1239"
)

# =========================
# PREFS (só o essencial)
# =========================
prefs = {
    "profile.default_content_setting_values.notifications": 2
}

chrome_options.add_experimental_option("prefs", prefs)

# =========================
# DRIVER
# =========================
driver = webdriver.Chrome(
    service=Service(ChromeDriverManager().install()),
    options=chrome_options
)

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