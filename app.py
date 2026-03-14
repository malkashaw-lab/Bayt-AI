from fastapi import FastAPI, Form, Request
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from pydantic import BaseModel
from typing import Optional
import os
import textwrap

app = FastAPI(title='BaytAI')
app.mount('/static', StaticFiles(directory='static'), name='static')
templates = Jinja2Templates(directory='templates')

class GenerateRequest(BaseModel):
    poem: str
    output_type: str = 'فيديو قصير'
    era: str = 'تلقائي'
    voice: str = 'ملحمي'


def analyze_poem(poem: str, era: str):
    theme = 'تحليل بلاغي وسياقي'
    if any(x in poem for x in ['الخيل', 'السيف', 'رمح']):
        theme = 'الفخر والبطولة'
    elif any(x in poem for x in ['حبيب', 'نبك', 'دمع']):
        theme = 'الحنين والوجد'
    detected_era = era if era != 'تلقائي' else ('العصر العباسي' if 'القرطاس' in poem or 'الخيل' in poem else 'العصر العربي الكلاسيكي')
    summary = f'يعرض هذا المخرج القصيدة ضمن قالب مرئي/صوتي يبرز ثيمتها الأساسية: {theme}، مع استحضار {detected_era} بصريًا وصوتيًا.'
    scenes = [
        'افتتاحية بمشهد تاريخي مناسب للعصر',
        'إظهار الصور البلاغية الأساسية للقصيدة',
        'إلقاء عربي احترافي مع موسيقى مناسبة',
        'شاشة ختامية باسم الشاعر والعصر والقيمة الثقافية',
    ]
    return {
        'theme': theme,
        'detected_era': detected_era,
        'summary': summary,
        'scenes': scenes,
    }


@app.get('/', response_class=HTMLResponse)
def home(request: Request):
    return templates.TemplateResponse('index.html', {'request': request, 'result': None})


@app.post('/generate', response_class=HTMLResponse)
def generate(request: Request, poem: str = Form(...), output_type: str = Form('فيديو قصير'), era: str = Form('تلقائي'), voice: str = Form('ملحمي')):
    result = analyze_poem(poem, era)
    result['poem_title'] = poem.splitlines()[0] if poem.strip() else 'قصيدة جديدة'
    result['output_type'] = output_type
    result['voice'] = voice
    result['poem'] = poem
    return templates.TemplateResponse('index.html', {'request': request, 'result': result})


@app.get('/healthz')
def healthz():
    return {"status": "ok", "app": "BaytAI"}
