from fastapi import FastAPI, Request, Form
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates

app = FastAPI()
templates = Jinja2Templates(directory="templates")


@app.get("/", response_class=HTMLResponse)
async def home(request: Request):
    return templates.TemplateResponse("index.html", {"request": request, "result": None})


@app.get("/healthz")
async def healthz():
    return {"status": "ok"}


@app.post("/generate", response_class=HTMLResponse)
async def generate(
    request: Request,
    poem: str = Form(...),
    output_type: str = Form(...)
):
    theme = "الفخر والبطولة"

    if "حبيب" in poem or "نبك" in poem:
        theme = "الحنين والوجد"
    elif "ليل" in poem:
        theme = "التأمل والرمزية"
    elif "دمع" in poem:
        theme = "الحزن والوجد"

    first_line = poem.splitlines()[0] if poem.strip() else "قصيدة عربية"

    video_script = f"يبدأ الفيديو بمشهد بصري مستوحى من البيت: {first_line}، مع إلقاء عربي مؤثر ومشاهد مرتبطة بالسياق التاريخي."

    result = {
        "poem": poem,
        "theme": theme,
        "output_type": output_type,
        "script": video_script
    }

    return templates.TemplateResponse(
        "index.html",
        {
            "request": request,
            "result": result
        }
    )
