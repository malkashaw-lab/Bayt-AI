def create_background_image(text: str, out_path: str, style="desert"):
    from PIL import Image, ImageDraw, ImageFont
    import textwrap

    img = Image.new("RGB", (1280, 720), color=(15, 23, 42))
    draw = ImageDraw.Draw(img)

    if style == "desert":
        draw.rectangle([0, 0, 1280, 720], fill=(194, 144, 75))
        draw.rectangle([0, 420, 1280, 720], fill=(120, 78, 40))
    elif style == "night":
        draw.rectangle([0, 0, 1280, 720], fill=(20, 30, 70))
        draw.ellipse([1000, 80, 1100, 180], fill=(240, 240, 210))
    else:
        draw.rectangle([0, 0, 1280, 720], fill=(70, 50, 90))

    draw.rectangle([(60, 480), (1220, 660)], fill=(0, 0, 0, 140))

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

    wrapped = textwrap.fill(text, width=28)
    draw.multiline_text(
        (100, 520),
        wrapped,
        font=font,
        fill=(255, 255, 255),
        spacing=14
    )

    img.save(out_path)
