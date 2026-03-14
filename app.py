from fastapi import FastAPI, Request, Form
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from fastapi.staticfiles import StaticFiles

from gtts import gTTS
from moviepy.editor import ImageClip, AudioFileClip, CompositeVideoClip, concatenate_videoclips
from PIL import Image, ImageDraw, ImageFont
import requests
import os
import uuid
import textwrap

app = FastAPI()
templates = Jinja2Templates(directory="templates")

# إنشاء المجلدات إن لم تكن موجودة
os.makedirs("templates", exist_ok=True)
os.makedirs("static/generated", exist_ok=True)

app.mount("/static", StaticFiles(directory="static"), name="static")


@app.get("/", response_class=HTMLResponse)
async def home(request: Request):
    return templates.TemplateResponse("index.html", {"request": request, "result": None})


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


def build_prompts(poem: str, theme: str):
    lines = [x.strip() for x in poem.splitlines() if x.strip()]
    first = lines[0] if len(lines) > 0 else "قصيدة عربية"
    second = lines[1] if len(lines) > 1 else first

    return [
        f"cinematic arabic historical scene, inspired by Arabic poetry, {theme}, desert, warm lighting, artistic, high quality, scene 1, {first}",
        f"cinematic arabic poetic scene, emotional atmosphere, {theme}, classical arabic mood, high quality, scene 2, {second}",
        f"epic arabic calligraphy scene, historical ambiance, {theme}, cultural heritage, cinematic ending, high quality, scene 3",
    ]


def download_image(prompt: str, path: str):
    # خدمة صور مجانية
    url = f"https://image.pollinations.ai/prompt/{requests.utils.quote(prompt)}"
    r = requests.get(url, timeout=60)
    r.raise_for_status()
    with open(path, "wb") as f:
        f.write(r.content)


def create_text_overlay(base_path: str, text: str, out_path: str):
    img = Image.open(base_path).convert("RGB")
    img = img.resize((1280, 720))

    overlay = Image.new("RGBA", img.size, (0, 0, 0, 0))
    draw = ImageDraw.Draw(overlay)

    # خلفية شبه شفافة أسفل الصورة
    draw.rectangle([(40, 500), (1240, 680)], fill=(0, 0, 0, 150))

    wrapped = textwrap.fill(text, width=28)

    # جرّب خطوط شائعة، وإن لم توجد استخدم الافتراضي
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

    draw.multiline_text(
        (80, 540),
        wrapped,
        font=font,
        fill=(255, 255, 255, 255),
        spacing=12
    )

    combined = Image.alpha_composite(img.convert("RGBA"), overlay)
    combined.convert("RGB").save(out_path)


def generate_audio(poem: str, audio_path: str):
    tts = gTTS(text=poem, lang="ar")
    tts.save(audio_path)


def generate_video(poem: str, video_path: str):
    theme = detect_theme(poem)
    prompts = build_prompts(poem, theme)
    lines = [x.strip() for x in poem.splitlines() if x.strip()]
    while len(lines) < 3:
        lines.append(lines[-1] if lines else "قصيدة عربية")

    uid = str(uuid.uuid4())
    image_paths = []
    overlay_paths = []

    for i, prompt in enumerate(prompts):
        img_path = f"static/generated/{uid}_scene_{i}.jpg"
        out_img = f"static/generated/{uid}_scene_{i}_overlay.jpg"
        download_image(prompt, img_path)
        create_text_overlay(img_path, lines[i], out_img)
        image_paths.append(img_path)
        overlay_paths.append(out_img)

    audio_path = f"static/generated/{uid}_audio.mp3"
    generate_audio(poem, audio_path)

    audio = AudioFileClip(audio_path)
    total_duration = max(audio.duration, 9)
    scene_duration = total_duration / 3

    clips = []
    for path in overlay_paths:
        clip = ImageClip(path).set_duration(scene_duration).resize((1280, 720))
        clips.append(clip)

    final_video = concatenate_videoclips(clips, method="compose").set_audio(audio)
    final_video.write_videofile(
        video_path,
        fps=24,
        codec="libx264",
        audio_codec="aac"
    )

    return theme, audio_path, overlay_paths


@app.post("/generate", response_class=HTMLResponse)
async def generate(
    request: Request,
    poem: str = Form(...),
    output_type: str = Form(...)
):
    uid = str(uuid.uuid4())
    video_path = f"static/generated/{uid}.mp4"

    try:
        theme, audio_path, image_paths = generate_video(poem, video_path)
        result = {
            "poem": poem,
            "theme": theme,
            "output_type": output_type,
            "video_url": f"/static/generated/{uid}.mp4"
        }
    except Exception as e:
        result = {
            "poem": poem,
            "theme": "تعذر التوليد حاليًا",
            "output_type": output_type,
            "error": str(e),
            "video_url": None
        }

    return templates.TemplateResponse(
        "index.html",
        {
            "request": request,
            "result": result
        }
    )
