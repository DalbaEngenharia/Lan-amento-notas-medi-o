from imports import *
from Protheus_Biblioteca import *
from LOOP import LoopLancamentos

import os
import sys

from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait

# NOVO (auto driver)
from webdriver_manager.chrome import ChromeDriverManager

# =========================
# CORREÇÃO CRÍTICA (AGENDADOR)
# =========================
if getattr(sys, 'frozen', False):
    base_dir = os.path.dirname(sys.executable)
else:
    base_dir = os.path.dirname(os.path.abspath(__file__))

os.chdir(base_dir)

# DEBUG (pode remover depois)
with open(os.path.join(base_dir, "debug_path.txt"), "w") as f:
    f.write(f"Rodando em: {os.getcwd()}")

# =========================
# CONFIG
# =========================
homologacao = False
teste = 1

chrome_options = Options()

# =========================
# PERFIL
# =========================
profile_path = os.path.join(base_dir, "chrome_profile")
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
# ESTABILIDADE
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
# DRIVER (AUTO + FALLBACK)
# =========================
try:
    # tenta baixar automaticamente
    service = Service(ChromeDriverManager().install())
except Exception as e:
    print("Erro ao baixar driver automático:", e)
    print("Usando driver local...")

    driver_path = os.path.join(base_dir, "chromedriver.exe")
    service = Service(driver_path)

driver = webdriver.Chrome(service=service, options=chrome_options)
wait = WebDriverWait(driver, 20)

# =========================
# INÍCIO DO FLUXO
# =========================
log("INICIANDO AMBIENTE")
iniciar_ambiente(homologacao, driver)

log("CONFIRMANDO BASE")
confirmaBase(driver, wait)

log("REALIZANDO LOGIN")
login(driver, wait, credenciais)

log("ENTRANDO EM ATUALIZAÇÕES")
sel_ambiente(driver, wait, "2", homologacao)

log("ENTRANDO EM MOVIMENTOS")
funcao_tres_e_demais(driver, "wa-menu-item", "Atualizações", 0)

funcao_tres_e_demais(driver, "wa-menu-item", "Movimentos", 0)

log("ENTRANDO EM LOOP LANÇAMENTOS")
LoopLancamentos(driver)

log("FINALIZANDO")
time.sleep(5)
driver.quit()
log("FINALIZADO")