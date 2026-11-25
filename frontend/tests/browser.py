"""Execute na pasta frontend. Inicia servidores locais com dados sintéticos."""
import os
from pathlib import Path
from subprocess import Popen
import sys
import time
from urllib.request import urlopen
from contextlib import contextmanager

from playwright.sync_api import expect, sync_playwright


@contextmanager
def server(args, env, url):
    process = Popen(args, env={**os.environ, **env})
    try:
        for _ in range(150):
            if process.poll() is not None:
                raise RuntimeError("Servidor encerrou antes do teste")
            try:
                with urlopen(url, timeout=1):
                    break
            except OSError:
                time.sleep(.2)
        else:
            raise RuntimeError("Servidor não respondeu")
        yield
    finally:
        process.terminate()
        process.wait()


api = "http://127.0.0.1:18001"
web = "http://127.0.0.1:13001"
with server([sys.executable, "-m", "uvicorn", "fixture:app", "--app-dir", "tests", "--port", "18001"],
            {"PYTHONPATH": str(Path("../backend").resolve())}, api + "/health"), server(
    ["node_modules/.bin/next", "start", "-H", "127.0.0.1", "-p", "13001"], {"API_ORIGIN": api}, web
), sync_playwright() as pw:
    browser = pw.chromium.launch(executable_path=os.getenv("CHROMIUM_PATH"))
    page = browser.new_page()
    page.goto(web)
    field = page.get_by_label("Tema de pesquisa")
    button = page.get_by_role("button", name="Pesquisar")
    field.fill("tema")
    button.click()
    expect(page.get_by_role("link", name="Estudo sintético")).to_have_attribute(
        "href", "https://pubmed.ncbi.nlm.nih.gov/1234/")
    expect(page.get_by_text("PMID 1234 · DOI 10.0000/teste")).to_be_visible()
    expect(page.get_by_text("Recuperado em", exact=False)).to_be_visible()
    button.click()
    expect(page.get_by_text("Resultado recuperado do cache.")).to_be_visible()
    field.fill("vazio")
    button.click()
    expect(page.get_by_text("Nenhuma publicação encontrada")).to_be_visible()
    field.fill("falha")
    button.click()
    expect(page.get_by_role("main").get_by_role("alert")).to_contain_text("O PubMed está temporariamente indisponível")
    browser.close()
