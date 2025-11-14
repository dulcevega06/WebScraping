# En este archivo vamos a corregir tu código para que SÍ guarde los ORCID y correos.
# Mantengo exactamente tu estilo de documentación: sencillo, línea por línea, sin tecnicismos.

import csv
import pandas as pd
import os
import selenium
from selenium import webdriver
from selenium.webdriver.common.by import By
import time
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
import re
import requests
import io
import fitz  # PyMuPDF
from urllib.parse import unquote, urlparse, parse_qs
import urllib3
from selenium.webdriver.chrome.options import Options
from selenium.common.exceptions import NoSuchElementException

# ---------------------------------------------------------------------------
# CONFIGURACIÓN DEL NAVEGADOR
# ---------------------------------------------------------------------------
chrome_options = Options()
chrome_options.add_argument("--headless=new")  # Navegador oculto
chrome_options.add_argument("--disable-gpu")
chrome_options.add_argument("--no-sandbox")
chrome_options.add_argument("--window-size=1920,1080")

# ---------------------------------------------------------------------------
# CARGAR CSV PRINCIPAL
# ---------------------------------------------------------------------------
df = pd.read_csv(r"C:\Users\122215\OneDrive\Documentos\UAdeO\SEMESTRE 3\PE\WebScraping_Revistas-main\PDFS_CORREOS2.csv", header=0)
pdfs = df['pdf']  # Aquí tomamos la columna que contiene los PDFs

# ---------------------------------------------------------------------------
# FUNCIÓN: get_orcids_from_page
# Busca ORCID y correos dentro del visor del PDF
# ---------------------------------------------------------------------------
def get_orcids_from_page(driver):
    """
    Esta función se mete al visor del PDF y busca:
    - Enlaces ORCID
    - Correos dentro de spans
    """
    orcids = set()
    correos = set()

    try:
        time.sleep(8)  # Esperamos a que cargue el PDF

        iframe = driver.find_element(By.TAG_NAME, "iframe")
        driver.switch_to.frame(iframe)

        scrollable_div = driver.find_element(By.ID, "viewerContainer")

        # Movimiento dentro del PDF
        step = 2000
        delay = 1
        scroll_height = driver.execute_script("return arguments[0].scrollHeight", scrollable_div)

        current_scroll = 0
        while current_scroll < scroll_height:
            current_scroll += step
            driver.execute_script("arguments[0].scrollTop = arguments[1]", scrollable_div, current_scroll)
            time.sleep(delay)

            # Buscar ORCID
            try:
                links = driver.find_elements(By.XPATH, "//a[contains(@href, 'orcid.org/')]")
                for link in links:
                    href = link.get_attribute("href")
                    if href:
                        orcids.add(href)
            except:
                pass

            # Buscar correos
            try:
                spans = driver.find_elements(By.XPATH, "//span[contains(text(), '@')]")
                for span in spans:
                    texto = span.text.strip()
                    encontrados = re.findall(r"[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}", texto)
                    for e in encontrados:
                        correos.add(e)
            except:
                pass

    except:
        pass

    return orcids, correos

# ---------------------------------------------------------------------------
# FUNCIÓN: get_emails_from_article
# Abre el artículo y detecta dónde está el PDF
# ---------------------------------------------------------------------------
def get_emails_from_article(url):
    """
    Abre la página del artículo y busca el PDF donde están los datos.
    """
    driver = webdriver.Chrome(options=chrome_options)
    driver.get(url)
    time.sleep(7)

    pdf_url = ""

    # Buscar PDF en IFRAME
    try:
        iframe = driver.find_element(By.TAG_NAME, "iframe")
        pdf_url = iframe.get_attribute("src")
    except NoSuchElementException:
        pass

    # Buscar PDF en OBJECT
    if not pdf_url:
        try:
            obj = driver.find_element(By.TAG_NAME, "object")
            pdf_url = obj.get_attribute("data")
        except NoSuchElementException:
            pass

    # Buscar PDF en visor PDF.js
    if not pdf_url:
        try:
            download_btn = driver.find_element(By.ID, "download")
            pdf_url = download_btn.get_attribute("href")
        except NoSuchElementException:
            pass

    # Extraer ORCID y correos dentro del visor
    orcids, correos = get_orcids_from_page(driver)

    driver.quit()
    return pdf_url, orcids, correos

# ---------------------------------------------------------------------------
# Ignorar problemas SSL en descargas
# ---------------------------------------------------------------------------
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)
headers = {"User-Agent": "Mozilla/5.0"}

# ---------------------------------------------------------------------------
# FUNCIÓN: get_pdf_url
# ---------------------------------------------------------------------------
def get_pdf_url(input_url):
    if isinstance(input_url, tuple):
        input_url = input_url[0]

    parsed = urlparse(input_url)
    params = parse_qs(parsed.query)

    if "file" in params:
        pdf_url_encoded = params["file"][0]
        pdf_url = unquote(pdf_url_encoded)
        return pdf_url
    return input_url

# ---------------------------------------------------------------------------
# FUNCIÓN: extract_text_from_pdf_url
# ---------------------------------------------------------------------------
def extract_text_from_pdf_url(pdf_url):
    if not pdf_url:
        return ""
    try:
        response = requests.get(pdf_url, headers=headers, verify=False)
        response.raise_for_status()
        doc = fitz.open(stream=io.BytesIO(response.content), filetype="pdf")
        texto = "".join([p.get_text() for p in doc])
        return texto
    except:
        return ""

# ---------------------------------------------------------------------------
# LISTAS FINALES
# ---------------------------------------------------------------------------
orcids_finales = []
correos_finales = []

# ---------------------------------------------------------------------------
# PROCESAR SOLO LOS 10 PRIMEROS
# ---------------------------------------------------------------------------
prueba1 = pdfs[0:10]

for i, enlace in enumerate(prueba1):
    viewer_url, orcids, correos = get_emails_from_article(enlace)

    pdf_url = get_pdf_url(viewer_url)
    texto_pdf = extract_text_from_pdf_url(pdf_url)

    # Correos encontrados dentro del PDF
    match = re.findall(r"[\w.+-]+@[\w-]+\.[\w.-]+", texto_pdf)

    # ORCID dentro del PDF
    orcid_pdf = re.findall(r"(?:https?://orcid\.org/)?\d{4}-\d{4}-\d{4}-\d{3}[0-9X]", texto_pdf)

    # Agregar ORCID y correos encontrados en visor
    orcids_finales.extend(list(orcids))
    correos_finales.extend(list(correos))

    # Agregar los del PDF
    correos_finales.extend(match)
    orcids_finales.extend(orcid_pdf)

# ---------------------------------------------------------------------------
# GUARDAR RESULTADOS
# ---------------------------------------------------------------------------
os.chdir(r"C:\Users\122215\OneDrive\Documentos\UAdeO\SEMESTRE 3\PE\WebScraping_Revistas-main")

# Guardar correos
pd.DataFrame(correos_finales, columns=["Correos"]).to_csv("CORREOS.csv", mode="a", header=False, index=False)

# Guardar ORCID
pd.DataFrame(orcids_finales, columns=["ClaveOrcid"]).to_csv("ClavesOrcid.csv", mode="a", header=False, index=False)