from fastapi import FastAPI, Form, Request, Response
from fastapi.responses import FileResponse, HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
import csv
import os

app = FastAPI(title="Sistema de Informes de Rendimentos")

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
STATIC_DIR = os.path.join(BASE_DIR, "static")
PDF_DIR = os.path.join(BASE_DIR, "pdfs")
TEMPLATE_DIR = os.path.join(BASE_DIR, "templates")
CSV_PATH = os.path.join(BASE_DIR, "dados2.csv")

os.makedirs(STATIC_DIR, exist_ok=True)
os.makedirs(PDF_DIR, exist_ok=True)
os.makedirs(TEMPLATE_DIR, exist_ok=True)

app.mount("/static", StaticFiles(directory=STATIC_DIR), name="static")
templates = Jinja2Templates(directory=TEMPLATE_DIR)

dados = {}

try:
    with open(CSV_PATH, newline="", encoding="latin-1", errors="ignore") as f:
        reader = csv.DictReader(f, delimiter=";")
        for row in reader:
            cpf = row.get("cpf", "").strip()
            dado = row.get("dado_confirmacao", "").strip()
            nome = row.get("nome", "").strip()
            if cpf:
                dados[cpf] = {"dado": dado, "nome": nome}
except Exception as e:
    print(f"Erro ao carregar CSV: {e}")

@app.head("/")
def healthcheck():
    return Response(status_code=200)

@app.get("/", response_class=HTMLResponse)
def home(request: Request):
    return templates.TemplateResponse(
        request, "index.html", {"request": request}
    )

@app.post("/consultar", response_class=HTMLResponse)
def consultar(request: Request, cpf: str = Form(...), dado: str = Form(...)):
    cpf = cpf.replace(".", "").replace("-", "").strip()
    dado = dado.strip()

    if cpf not in dados or dados[cpf]["dado"] != dado:
        return HTMLResponse("<h3>Dados inválidos</h3>", status_code=403)

    return templates.TemplateResponse(
        request,
        "resultado.html",
        {
            "request": request,
            "nome": dados[cpf]["nome"],
            "download_url": f"/download/{cpf}",
        },
    )

@app.get("/download/{cpf}")
def download(cpf: str):
    pdf_path = os.path.join(PDF_DIR, f"{cpf}.pdf")
    if not os.path.exists(pdf_path):
        return HTMLResponse("<h3>Arquivo não encontrado</h3>", status_code=404)

    return FileResponse(pdf_path, media_type="application/pdf")