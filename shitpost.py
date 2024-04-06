import io
from PIL import Image
from PIL import ImageDraw
from PIL import ImageFont

def contains_non_english(text):
    for char in text:
        if not (0x20 <= ord(char) <= 0x7E):
            return True
    return False
async def shitpost(text, image_data):
    #img = Image.open(file_path)

    img = Image.open(image_data)
    width, height = img.size
    text_width = width * 0.8
    text_max_height = height * 0.8
    size=45
    draw = ImageDraw.Draw(img)
    font_path = "fonts/Upright.ttf"
    if contains_non_english(text):
        font_path = "fonts/ofont.ru_Impact.ttf"
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
            size -= 1
    draw.multiline_text((width / 2 - w / 2 - x1, height / 2 - h / 2 - y1), quote, font=font, align="center", stroke_width=3, stroke_fill="#000")
    #img.save(file_path, format="PNG")

    img_buffer = io.BytesIO()
    img.save(img_buffer, format="PNG")
    img_buffer.seek(0)
    return img_buffer

