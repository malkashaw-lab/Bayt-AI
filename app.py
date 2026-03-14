from fastapi import FastAPI, Request, Form
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates

app = FastAPI()
templates = Jinja2Templates(directory="templates")


@app.get("/", response_class=HTMLResponse)
async def home(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})


@app.get("/healthz")
async def healthz():
    return {"status": "ok"}


@app.post("/generate", response_class=HTMLResponse)
async def generate(
    request: Request,
    poem: str = Form(...),
    output_type: str = Form(...),
):
    result = {
        "poem": poem,
        "output_type": output_type,
        "voice": "ملحمي"
    }

    return templates.TemplateResponse(
        "index.html",
        {
            "request": request,
            "result": result
        }
    )
