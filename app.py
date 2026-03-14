from fastapi import FastAPI, Request, Form
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from fastapi.staticfiles import StaticFiles

import os

app = FastAPI()

templates = Jinja2Templates(directory="templates")

# إنشاء مجلد static إن لم يكن موجودًا
os.makedirs("static", exist_ok=True)

app.mount("/static", StaticFiles(directory="static"), name="static")


@app.get("/", response_class=HTMLResponse)
async def home(request: Request):
    return templates.TemplateResponse(
        "index.html",
        {"request": request, "result": None}
    )


@app.get("/healthz")
async def healthz():
    return {"status": "ok"}


def analyze_poem(poem: str):

    theme = "الشعر العربي الكلاسيكي"
    mood = "ملحمي"

    if "حبيب" in poem or "نبك" in poem or "دمع" in poem:
        theme = "الحنين والوجد"
        mood = "عاطفي"

    if "الخيل" in poem or "السيف" in poem or "رمح" in poem:
        theme = "الفخر والبطولة"
        mood = "ملحمي"

    if "ليل" in poem or "نجوم" in poem:
        theme = "التأمل والرمزية"
        mood = "هادئ"

    lines = [x.strip() for x in poem.splitlines() if x.strip()]

    if len(lines) == 0:
        lines = ["قصيدة عربية"]

    scene1 = f"مشهد افتتاحي بصري مستوحى من البيت: {lines[0]}"
    scene2 = "انتقال إلى مشهد تعبيري يعكس المشاعر المركزية في القصيدة"
    scene3 = "لقطة ختامية سينمائية تظهر النص الشعري مع موسيقى هادئة"

    video_script = f"""
    يبدأ الفيديو بمشهد بصري يعكس أجواء القصيدة.
    يظهر البيت الأول مع مؤثرات بصرية.
    ثم تنتقل الكاميرا إلى مشهد ثانٍ يعكس المعنى العاطفي للنص.
    وفي النهاية يظهر النص كاملاً مع صوت إلقاء عربي.
    """

    podcast_script = f"""
    مرحبًا بكم في بودكاست الشعر العربي.
    نستمع اليوم إلى أبيات تعبّر عن {theme}.
    دعونا نستكشف جمال هذا النص ومعانيه.
    """

    return {
        "theme": theme,
        "mood": mood,
        "scene1": scene1,
        "scene2": scene2,
        "scene3": scene3,
        "video_script": video_script,
        "podcast_script": podcast_script
    }


@app.post("/generate", response_class=HTMLResponse)
async def generate(
    request: Request,
    poem: str = Form(...),
    output_type: str = Form(...)
):

    analysis = analyze_poem(poem)

    result = {
        "poem": poem,
        "output_type": output_type,
        "theme": analysis["theme"],
        "mood": analysis["mood"],
        "scene1": analysis["scene1"],
        "scene2": analysis["scene2"],
        "scene3": analysis["scene3"],
        "video_script": analysis["video_script"],
        "podcast_script": analysis["podcast_script"],
        "video_demo": "https://www.youtube.com/embed/5qap5aO4i9A"
    }

    return templates.TemplateResponse(
        "index.html",
        {
            "request": request,
            "result": result
        }
    )
