from fastapi import FastAPI, Request, Form
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from fastapi.staticfiles import StaticFiles

from gtts import gTTS
from moviepy.editor import ImageClip, AudioFileClip, concatenate_videoclips
from PIL import Image, ImageDraw, ImageFont

import os
import uuid
import textwrap

app = FastAPI()

templates = Jinja2Templates(directory="templates")

# إنشاء المجلدات إن لم تكن موجودة
os.makedirs("static/generated", exist_ok=True)

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


def detect_theme(poem: str):
    if "حبيب" in poem or "نبك" in poem:
        return "الحنين والوجد"
    if "الخيل" in poem or "السيف" in poem:
        return "الفخر والبطولة"
    if "ليل" in poem:
        return "التأمل والرمزية"
    return "شعر عربي كلاسيكي"


def create_scene(text, path, style="desert"):
    img = Image.new("RGB", (1280, 720), (20, 30, 50))
    draw = ImageDraw.Draw(img)

    if style == "desert":
        draw.rectangle([0, 400, 1280, 720], fill=(200, 150, 80))
        draw.ellipse([950, 60, 1100, 210], fill=(255, 220, 120))

    if style == "night":
        draw.rectangle([0, 0, 1280, 720], fill=(10, 20, 70))
        draw.ellipse([1000, 80, 1100, 180], fill=(240, 240, 200))

    draw.rectangle([60, 500, 1220, 650], fill=(0, 0, 0))

    font = None

    for f in [
        "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf",
        "/usr/share/fonts/truetype/freefont/FreeSans.ttf",
    ]:
        if os.path.exists(f):
            font = ImageFont.truetype(f, 42)
            break

    if font is None:
        font = ImageFont.load_default()

    wrapped = textwrap.fill(text, 25)

    draw.multiline_text(
        (120, 520),
        wrapped,
        fill=(255, 255, 255),
        font=font,
        spacing=10
    )

    img.save(path)


def generate_audio(poem, path):
    tts = gTTS(text=poem, lang="ar")
    tts.save(path)


def generate_video(poem, video_path):
    theme = detect_theme(poem)

    lines = [l.strip() for l in poem.splitlines() if l.strip()]

    if len(lines) == 0:
        lines = ["قصيدة عربية"]

    while len(lines) < 3:
        lines.append(lines[-1])

    uid = str(uuid.uuid4())

    scenes = []
    styles = ["desert", "night", "classic"]

    for i in range(3):
        img_path = f"static/generated/{uid}_{i}.jpg"
        create_scene(lines[i], img_path, styles[i % 3])
        scenes.append(img_path)

    audio_path = f"static/generated/{uid}.mp3"
    generate_audio(poem, audio_path)

    audio = AudioFileClip(audio_path)

    duration = max(audio.duration, 9)
    scene_duration = duration / 3

    clips = []

    for s in scenes:
        clip = ImageClip(s).set_duration(scene_duration)
        clip = clip.resize((1280, 720))
        clips.append(clip)

    final = concatenate_videoclips(clips).set_audio(audio)

    final.write_videofile(
        video_path,
        fps=24,
        codec="libx264",
        audio_codec="aac"
    )

    return theme


@app.post("/generate", response_class=HTMLResponse)
async def generate(request: Request, poem: str = Form(...), output_type: str = Form(...)):

    uid = str(uuid.uuid4())

    video_path = f"static/generated/{uid}.mp4"

    try:

        theme = generate_video(poem, video_path)

        result = {
            "poem": poem,
            "theme": theme,
            "output_type": output_type,
            "video_url": f"/static/generated/{uid}.mp4",
            "error": None
        }

    except Exception as e:

        result = {
            "poem": poem,
            "theme": "تعذر التوليد حاليًا",
            "output_type": output_type,
            "video_url": None,
            "error": str(e)
        }

    return templates.TemplateResponse(
        "index.html",
        {"request": request, "result": result}
    )
