from fastapi import FastAPI, Form, Request
from fastapi.responses import FileResponse, HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
import csv, os

app = FastAPI(title="Sistema de Informes de Rendimentos")

BASE_DIR = os.path.dirname(os.path.abspath(__file__))

STATIC_DIR = os.path.join(BASE_DIR, "static")
PDF_DIR = os.path.join(BASE_DIR, "pdfs")
TEMPLATE_DIR = os.path.join(BASE_DIR, "templates")
CSV_PATH = os.path.join(BASE_DIR, "dados2.csv")

app.mount("/static", StaticFiles(directory=STATIC_DIR), name="static")
templates = Jinja2Templates(directory=TEMPLATE_DIR)

# ---- CSV
dados = {}
with open(CSV_PATH, newline="", encoding="latin-1") as f:
    reader = csv.DictReader(f, delimiter=";")
    for row in reader:
        cpf = row["cpf"].strip()
        dados[cpf] = {
            "dado": row["dado_confirmacao"].strip(),
            "nome": row["nome"].strip()
        }

# ---- Home
@app.get("/", response_class=HTMLResponse)
def home(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})

# ---- Resultado
@app.post("/consultar", response_class=HTMLResponse)
def consultar(request: Request, cpf: str = Form(...), dado: str = Form(...)):
    cpf = cpf.replace(".", "").replace("-", "").strip()
    dado = dado.strip()

    if cpf not in dados or dados[cpf]["dado"] != dado:
        return HTMLResponse("<h3>Dados inválidos</h3>", status_code=403)

    return templates.TemplateResponse(
        "resultado.html",
        {
            "request": request,
            "nome": dados[cpf]["nome"],
            "download_url": f"/download/{cpf}"
        }
    )

# ---- Download
@app.get("/download/{cpf}")
def download(cpf: str):
    path = os.path.join(PDF_DIR, f"{cpf}.pdf")
    if not os.path.exists(path):
        return HTMLResponse("<h3>Arquivo não encontrado</h3>", status_code=404)

    return FileResponse(path, media_type="application/pdf", filename="informe_rendimentos.pdf")