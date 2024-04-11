import io
from PIL import Image, ImageDraw, ImageFont


def contains_non_english(text):
    for char in text:
        if not (0x20 <= ord(char) <= 0x7E):
            return True
    return False


def split_list_in_two(lst):
    midpoint = len(lst) // 2
    return lst[:midpoint], lst[midpoint:]


async def shitpost(text: str, image_data, size : int):
    if contains_non_english(text):
        return await shitpost_impact(text, image_data)
    else:
        return await shitpost_pinterst(text, image_data, size)


async def shitpost_impact(text: str, image_data):
    # img = Image.open(file_path)
    img = Image.open(image_data)
    width, height = img.size
    text_width = width * 0.9
    text_max_height = height * 0.2
    draw = ImageDraw.Draw(img)
    font_path = "fonts/ofont.ru_Impact.ttf"
    size = 20
    text = text.upper()
    while True:
        font = ImageFont.truetype(font_path, size)
        lines = []
        line = ""
        for word in text.split():
            proposed_line = line
            if line:
                proposed_line += " "
            proposed_line += word
            if font.getlength(proposed_line) <= text_width:
                line = proposed_line
            else:
                lines.append(line)
                line = word
        if line:
            lines.append(line)
        quote = "\n".join(lines)
        x1, y1, x2, y2 = draw.multiline_textbbox((0, 0), quote, font, stroke_width=2)
        w, h = x2 - x1, y2 - y1
        if w >= text_width or h >= text_max_height:
            break
        else:
            size += 1
    if quote.count("\n"):
        a, b = split_list_in_two(lines)
        a = "\n".join(a)
        b = "\n".join(b)
        x1, y1, x2, y2 = draw.multiline_textbbox((0, 0), a, font, stroke_width=2)
        w, h = x2 - x1, y2 - y1
        draw.multiline_text((width / 2 - w / 2 - x1, height * 0.01 + h - y2), a, font=font, align="center",
                            stroke_width=3, stroke_fill="#000")
        x1, y1, x2, y2 = draw.multiline_textbbox((0, 0), b, font, stroke_width=2)
        w, h = x2 - x1, y2 - y1
        draw.multiline_text((width / 2 - w / 2 - x1, height * 0.99 - h - y1), b, font=font, align="center",
                            stroke_width=3, stroke_fill="#000")
    else:
        draw.multiline_text((width / 2 - w / 2 - x1, height * 0.99 - h - y1), quote, font=font, align="center",
                            stroke_width=3, stroke_fill="#000")
    # img.save(file_path, format="PNG")

    img_buffer = io.BytesIO()
    img.save(img_buffer, format="PNG")
    img_buffer.seek(0)
    return img_buffer


async def shitpost_pinterst(text, image_data, size: int):
    # img = Image.open(file_path)
    img = Image.open(image_data)
    width, height = img.size
    text_width = width * 0.8
    text_max_height = height * 0.8
    draw = ImageDraw.Draw(img)
    font_path = "fonts/Upright.ttf"
    while size > 9:
        font = ImageFont.truetype(font_path, size)
        lines = []
        line = ""
        for word in text.split():
            proposed_line = line
            if line:
                proposed_line += " "
            proposed_line += word
            if font.getlength(proposed_line) <= text_width:
                line = proposed_line
            else:
                lines.append(line)
                line = word
        if line:
            lines.append(line)
        quote = "\n".join(lines)
        x1, y1, x2, y2 = draw.multiline_textbbox((0, 0), quote, font, stroke_width=2)
        w, h = x2 - x1, y2 - y1
        if h <= text_max_height:
            break
        else:
            size -= 5
    draw.multiline_text((width / 2 - w / 2 - x1, height / 2 - h / 2 - y1), quote, font=font, align="center",
                        stroke_width=3, stroke_fill="#000")
    # img.save(file_path, format="PNG")

    img_buffer = io.BytesIO()
    img.save(img_buffer, format="PNG")
    img_buffer.seek(0)
    return img_buffer
