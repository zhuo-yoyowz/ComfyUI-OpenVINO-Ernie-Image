from __future__ import annotations

import csv
from dataclasses import dataclass
from pathlib import Path

from PIL import Image, ImageDraw, ImageFilter, ImageFont, ImageOps


ROOT = Path(__file__).resolve().parents[1]
WORKSPACE_ROOT = ROOT.parent
CSV_PATH = WORKSPACE_ROOT / "xinghe-prompts-new-100cases.csv"
SOURCE_IMAGE_DIR = WORKSPACE_ROOT / "ComfyUI" / "output" / "ernie_base_int8_no_pe_exact_20260427_152601"
OUTPUT_PATH = ROOT / "assets" / "base_int8_long_prompt_showcase.png"
SELECTED_SOURCE_ROWS = [2, 7, 21, 28, 40, 53, 59, 73, 81, 93]

PAGE_BG = "#f3f5fb"
CARD_BG = "#ffffff"
CARD_BORDER = "#e6e9f2"
CARD_SHADOW = (29, 44, 87, 24)
TITLE_COLOR = "#1f2937"
TEXT_COLOR = "#4b5563"
MUTED_TEXT = "#6b7280"
CHIP_BG = "#eef2ff"
CHIP_TEXT = "#4f46e5"
ACCENT = "#2563eb"


@dataclass
class Case:
    source_row: int
    title: str
    source_size: str
    prompt: str
    image_path: Path


def load_font(size: int, bold: bool = False) -> ImageFont.FreeTypeFont | ImageFont.ImageFont:
    candidates = [
        r"C:\Windows\Fonts\msyhbd.ttc" if bold else r"C:\Windows\Fonts\msyh.ttc",
        r"C:\Windows\Fonts\segoeuib.ttf" if bold else r"C:\Windows\Fonts\segoeui.ttf",
        r"C:\Windows\Fonts\arialbd.ttf" if bold else r"C:\Windows\Fonts\arial.ttf",
    ]
    for candidate in candidates:
        path = Path(candidate)
        if path.exists():
            return ImageFont.truetype(str(path), size=size)
    return ImageFont.load_default()


def read_cases() -> list[Case]:
    with CSV_PATH.open("r", encoding="utf-8-sig", newline="") as f:
        rows = list(csv.reader(f))

    cases: list[Case] = []
    for source_row in SELECTED_SOURCE_ROWS:
        row = rows[source_row]
        image_name = f"base_int8_no_pe_exact_{source_row:03d}_00001_.png"
        cases.append(
            Case(
                source_row=source_row,
                title=row[2].strip(),
                source_size=row[3].strip(),
                prompt=row[6].strip(),
                image_path=SOURCE_IMAGE_DIR / image_name,
            )
        )
    return cases


def measure_text(draw: ImageDraw.ImageDraw, text: str, font: ImageFont.ImageFont) -> tuple[int, int]:
    left, top, right, bottom = draw.textbbox((0, 0), text, font=font)
    return right - left, bottom - top


def wrap_text(draw: ImageDraw.ImageDraw, text: str, font: ImageFont.ImageFont, max_width: int, max_lines: int) -> list[str]:
    if not text:
        return []
    lines: list[str] = []
    current = ""
    for char in text:
        trial = current + char
        width, _ = measure_text(draw, trial, font)
        if width <= max_width:
            current = trial
            continue
        if current:
            lines.append(current)
        current = char
        if len(lines) == max_lines:
            break
    if len(lines) < max_lines and current:
        lines.append(current)

    remaining = "".join(lines[max_lines:]) if len(lines) > max_lines else ""
    if remaining or len(text) > sum(len(line) for line in lines):
        if lines:
            trimmed = lines[max_lines - 1]
            ellipsis = "..."
            while trimmed:
                width, _ = measure_text(draw, trimmed + ellipsis, font)
                if width <= max_width:
                    lines[max_lines - 1] = trimmed + ellipsis
                    break
                trimmed = trimmed[:-1]
            else:
                lines[max_lines - 1] = ellipsis
    return lines[:max_lines]


def rounded_mask(size: tuple[int, int], radius: int) -> Image.Image:
    mask = Image.new("L", size, 0)
    draw = ImageDraw.Draw(mask)
    draw.rounded_rectangle((0, 0, size[0], size[1]), radius=radius, fill=255)
    return mask


def paste_with_mask(base: Image.Image, image: Image.Image, xy: tuple[int, int], radius: int) -> None:
    mask = rounded_mask(image.size, radius)
    base.paste(image, xy, mask)


def draw_chip(draw: ImageDraw.ImageDraw, x: int, y: int, text: str, font: ImageFont.ImageFont) -> int:
    padding_x = 14
    padding_y = 8
    text_w, text_h = measure_text(draw, text, font)
    chip_w = text_w + padding_x * 2
    chip_h = text_h + padding_y * 2
    draw.rounded_rectangle((x, y, x + chip_w, y + chip_h), radius=14, fill=CHIP_BG)
    draw.text((x + padding_x, y + padding_y - 1), text, font=font, fill=CHIP_TEXT)
    return chip_w


def build_card(draw: ImageDraw.ImageDraw, canvas: Image.Image, case: Case, box: tuple[int, int, int, int], fonts: dict[str, ImageFont.ImageFont]) -> None:
    x0, y0, x1, y1 = box
    shadow = Image.new("RGBA", (x1 - x0 + 24, y1 - y0 + 24), (0, 0, 0, 0))
    shadow_draw = ImageDraw.Draw(shadow)
    shadow_draw.rounded_rectangle((12, 12, shadow.size[0] - 12, shadow.size[1] - 12), radius=26, fill=CARD_SHADOW)
    shadow = shadow.filter(ImageFilter.GaussianBlur(12))
    canvas.alpha_composite(shadow, (x0 - 12, y0 - 8))

    draw.rounded_rectangle((x0, y0, x1, y1), radius=26, fill=CARD_BG, outline=CARD_BORDER, width=2)

    card_w = x1 - x0
    image_x = x0 + 18
    image_y = y0 + 18
    image_w = card_w - 36
    image_h = 250
    image_bg = Image.new("RGBA", (image_w, image_h), "#eef1f8")
    source = Image.open(case.image_path).convert("RGB")
    fitted = ImageOps.contain(source, (image_w, image_h))
    px = (image_w - fitted.width) // 2
    py = (image_h - fitted.height) // 2
    image_bg.paste(fitted, (px, py))
    paste_with_mask(canvas, image_bg, (image_x, image_y), radius=18)

    inner_x = x0 + 24
    chip_y = image_y + image_h + 16
    chip_x = inner_x
    chip_x += draw_chip(draw, chip_x, chip_y, f"Row #{case.source_row}", fonts["chip"]) + 10
    chip_x += draw_chip(draw, chip_x, chip_y, case.source_size, fonts["chip"])

    title_y = chip_y + 46
    title_lines = wrap_text(draw, case.title, fonts["title"], card_w - 48, 2)
    for idx, line in enumerate(title_lines):
        draw.text((inner_x, title_y + idx * 32), line, font=fonts["title"], fill=TITLE_COLOR)

    author_y = title_y + len(title_lines) * 32 + 2
    draw.text((inner_x, author_y), "Base INT8 · OpenVINO GPU · use_pe=false", font=fonts["meta"], fill=MUTED_TEXT)

    prompt_y = author_y + 34
    prompt_lines = wrap_text(draw, case.prompt, fonts["prompt"], card_w - 48, 6)
    for idx, line in enumerate(prompt_lines):
        draw.text((inner_x, prompt_y + idx * 25), line, font=fonts["prompt"], fill=TEXT_COLOR)


def build_gallery(cases: list[Case]) -> Image.Image:
    width = 2600
    margin = 54
    header_h = 180
    gap = 28
    cols = 5
    card_w = (width - margin * 2 - gap * (cols - 1)) // cols
    card_h = 520
    rows = (len(cases) + cols - 1) // cols
    height = margin + header_h + rows * card_h + (rows - 1) * gap + margin

    canvas = Image.new("RGBA", (width, height), PAGE_BG)
    draw = ImageDraw.Draw(canvas)

    fonts = {
        "hero": load_font(48, bold=True),
        "sub": load_font(24, bold=False),
        "title": load_font(24, bold=True),
        "meta": load_font(17, bold=False),
        "prompt": load_font(16, bold=False),
        "chip": load_font(15, bold=True),
    }

    draw.text((margin, margin), "Long Prompt Showcase", font=fonts["hero"], fill=TITLE_COLOR)
    draw.text((margin, margin + 64), "ERNIE-Image Base INT8 in ComfyUI with OpenVINO GPU", font=fonts["sub"], fill=TEXT_COLOR)
    draw.text(
        (margin, margin + 102),
        "10 real cases from the Xinghe prompt set. These samples keep the original prompt path with Prompt Enhancer disabled.",
        font=fonts["sub"],
        fill=MUTED_TEXT,
    )

    for index, case in enumerate(cases):
        row = index // cols
        col = index % cols
        x0 = margin + col * (card_w + gap)
        y0 = margin + header_h + row * (card_h + gap)
        x1 = x0 + card_w
        y1 = y0 + card_h
        build_card(draw, canvas, case, (x0, y0, x1, y1), fonts)

    return canvas


def main() -> int:
    cases = read_cases()
    missing = [case.image_path for case in cases if not case.image_path.exists()]
    if missing:
        raise FileNotFoundError(f"Missing generated images: {missing}")
    gallery = build_gallery(cases)
    OUTPUT_PATH.parent.mkdir(parents=True, exist_ok=True)
    gallery.convert("RGB").save(OUTPUT_PATH, format="PNG", optimize=True)
    print(OUTPUT_PATH)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
