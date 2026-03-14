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

os.makedirs("templates", exist_ok=True)
os.makedirs("static", exist_ok=True)
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
    if "حبيب" in poem or "نبك" in poem or "دمع" in poem:
        return "الحنين والوجد"
    if "ليل" in poem or "نجوم" in poem:
        return "التأمل والرمزية"
    if "الخيل" in poem or "السيف" in poem or "رمح" in poem:
        return "الفخر والبطولة"
    return "شعر عربي كلاسيكي"


def create_background_image(text: str, out_path: str, style="desert"):
    img = Image.new("RGB", (1280, 720), color=(15, 23, 42))
    draw = ImageDraw.Draw(img)

    if style == "desert":
        draw.rectangle([0, 0, 1280, 720], fill=(194, 144, 75))
        draw.rectangle([0, 420, 1280, 720], fill=(120, 78, 40))
        draw.ellipse([950, 70, 1110, 230], fill=(255, 220, 140))
    elif style == "night":
        draw.rectangle([0, 0, 1280, 720], fill=(20, 30, 70))
        draw.ellipse([1000, 80, 1100, 180], fill=(240, 240, 210))
        for x, y in [(150, 120), (240, 80), (330, 150), (900, 110), (760, 70), (1110, 130)]:
            draw.ellipse([x, y, x + 5, y + 5], fill=(255, 255, 255))
    else:
        draw.rectangle([0, 0, 1280, 720], fill=(70, 50, 90))
        draw.rectangle([0, 440, 1280, 720], fill=(40, 30, 60))

    draw.rounded_rectangle(
        [(60, 480), (1220, 660)],
        radius=22,
        fill=(0, 0, 0)
    )

    font = None
    for font_path in [
        "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf",
        "/usr/share/fonts/truetype/freefont/FreeSans.ttf",
    ]:
        if os.path.exists(font_path):
            font = ImageFont.truetype(font_path, 42)
            break

    if font is None:
        font = ImageFont.load_default()

    wrapped = textwrap.fill(text, width=26)

    draw.multiline_text(
        (100, 525),
        wrapped,
        font=font,
        fill=(255, 255, 255),
        spacing=16,
        align="right"
    )

    img.save(out_path)


def generate_audio(poem: str, audio_path: str):
    tts = gTTS(text=poem, lang="ar")
    tts.save(audio_path)


def generate_video(poem: str, video_path: str):
    theme = detect_theme(poem)

    lines = [x.strip() for x in poem.splitlines() if x.strip()]
    if not lines:
        lines = ["قصيدة عربية", "إبداع عربي", "BaytAI"]

    while len(lines) < 3:
        lines.append(lines[-1])

    uid = str(uuid.uuid4())
    image_paths = []
    styles = ["desert", "night", "classic"]

    for i in range(3):
        img_path = f"static/generated/{uid}_scene_{i}.jpg"
        create_background_image(lines[i], img_path, styles[i % len(styles)])
        image_paths.append(img_path)

    audio_path = f"static/generated/{uid}_audio.mp3"
    generate_audio(poem, audio_path)

    audio = AudioFileClip(audio_path)
    total_duration = max(audio.duration, 9)
    scene_duration = total_duration / 3

    clips = []
    for path in image_paths:
        clip = ImageClip(path).set_duration(scene_duration).resize((1280, 720))
        clips.append(clip)

    final_video = concatenate_videoclips(clips, method="compose").set_audio(audio)

    final_video.write_videofile(
        video_path,
        fps=24,
        codec="libx264",
        audio_codec="aac"
    )

    return theme


@app.post("/generate", response_class=HTMLResponse)
async def generate(
    request: Request,
    poem: str = Form(...),
    output_type: str = Form(...)
):
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
        {
            "request": request,
            "result": result
        }
    )
