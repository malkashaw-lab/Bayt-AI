from fastapi import FastAPI, Request, Form
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates

app = FastAPI()

templates = Jinja2Templates(directory="templates")


@app.get("/", response_class=HTMLResponse)
async def home(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})


@app.post("/generate", response_class=HTMLResponse)
async def generate(
    request: Request,
    poem: str = Form(...),
    output_type: str = Form(...),
):

    # تحليل بسيط للقصيدة
    theme = "الفخر والبطولة"

    if "حبيب" in poem or "نبك" in poem:
        theme = "الحنين والوجد"

    if "ليل" in poem:
        theme = "التأمل والرمزية"

    # سيناريو فيديو مقترح
    video_script = f"""
    يبدأ الفيديو بمشهد بصري مستوحى من القصيدة:
    {poem.splitlines()[0]}

    يتم تقديم الأبيات بصوت عربي ملحمي مع مشاهد
    مستوحاة من البيئة التاريخية للقصيدة.
    """

    result = {
        "poem": poem,
        "theme": theme,
        "output": output_type,
        "script": video_script
    }

    return templates.TemplateResponse(
        "index.html",
        {
            "request": request,
            "result": result
        }
    )
