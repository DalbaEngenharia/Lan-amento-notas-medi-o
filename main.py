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

if not homologacao and teste == 0: 
    chrome_options.add_argument("--headless")
    chrome_options.add_argument("--window-size=1920,1080")
    credenciais = ["robo", "robo2025"]
elif not homologacao and teste == 1: 
    credenciais = ["robo", "robo2025"]
    chrome_options.add_argument("--start-maximized")

else:
    credenciais = ["gustavo.elicker", "123abc"]

# estabilidade
chrome_options.add_argument("--disable-notifications")
chrome_options.add_argument("--disable-extensions")
chrome_options.add_argument("--disable-popup-blocking")
chrome_options.add_argument("--ignore-certificate-errors")
chrome_options.add_argument("--allow-insecure-localhost")

# cria o driver COM as options já configuradas
driver = webdriver.Chrome(
    service=Service(ChromeDriverManager().install()),
    options=chrome_options
)

wait = WebDriverWait(driver, 20)

# iniciar ambiente
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