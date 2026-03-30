from fastapi import FastAPI, Form
from fastapi.responses import FileResponse, HTMLResponse
from fastapi.staticfiles import StaticFiles
import csv
import os

app = FastAPI(title="Sistema de Informes de Rendimentos")

BASE_DIR = os.path.dirname(os.path.abspath(__file__))

STATIC_DIR = os.path.join(BASE_DIR, "static")
PDF_DIR = os.path.join(BASE_DIR, "pdfs")
TEMPLATE_DIR = os.path.join(BASE_DIR, "templates")
CSV_PATH = os.path.join(BASE_DIR, "dados2.csv")

app.mount("/static", StaticFiles(directory=STATIC_DIR), name="static")

# ==========================
# Carrega dados do CSV
# ==========================
dados = {}
with open(CSV_PATH, newline="", encoding="latin-1") as f:
    reader = csv.DictReader(f, delimiter=";")
    for row in reader:
        cpf = row["cpf"].strip()
        dados[cpf] = {
            "dado_confirmacao": row["dado_confirmacao"].strip(),
            "nome": row["nome"].strip()
        }

# ==========================
# Página inicial
# ==========================
@app.get("/", response_class=HTMLResponse)
def home():
    with open(os.path.join(TEMPLATE_DIR, "index.html"), encoding="utf-8") as f:
        return f.read()

# ==========================
# Consulta e resultado
# ==========================
@app.post("/consultar", response_class=HTMLResponse)
def consultar(cpf: str = Form(...), dado: str = Form(...)):
    cpf = cpf.replace(".", "").replace("-", "").strip()
    dado = dado.strip()

    if cpf not in dados or dados[cpf]["dado_confirmacao"] != dado:
        return HTMLResponse("<h3>Dados inválidos</h3>", status_code=403)

    nome = dados[cpf]["nome"]

    with open(os.path.join(TEMPLATE_DIR, "resultado.html"), encoding="utf-8") as f:
        html = f.read()

    # ✅ Cria o link HTML COMPLETO no backend (evita HTML quebrado)
    download_link = (
        f'<a href="/download/{cpf}" '
        f'class="button button-blue">Baixar informe (PDF)</a>'
    )

    html = html.replace("{{NOME}}", nome)
    html = html.replace("{{DOWNLOAD_LINK}}", download_link)

    return HTMLResponse(html)

# ==========================
# Download do PDF
# ==========================
@app.get("/download/{cpf}")
def download(cpf: str):
    pdf_path = os.path.join(PDF_DIR, f"{cpf}.pdf")

    if not os.path.exists(pdf_path):
        return HTMLResponse("<h3>Arquivo não encontrado</h3>", status_code=404)

    return FileResponse(
        pdf_path,
        media_type="application/pdf",
        filename="informe_rendimentos.pdf"
    )