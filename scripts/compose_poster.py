"""
FIFA World Cup 2026 海报合成脚本
===============================

把一张 3D 卡通人物图（白底）合成到主题色 "26" 海报背景上。

调用方式：
    python compose_poster.py \\
        --character <人物图片路径> \\
        --bg <背景模板路径> \\
        --dark "R,G,B" --light "R,G,B" \\
        --label "FIFA WORLD CUP 2026" \\
        --out <输出目录>

退出码：
    0  成功
    2  参数错误
    3  图片读取失败
"""

from __future__ import annotations

import argparse
import os
import sys
from collections import deque
from pathlib import Path

try:
    from PIL import Image, ImageDraw, ImageFont
except ImportError:
    print("缺少 Pillow 库。请先运行: pip install -r requirements.txt", file=sys.stderr)
    sys.exit(2)


def parse_rgb(s: str) -> tuple[int, int, int]:
    parts = [p.strip() for p in s.split(",")]
    if len(parts) != 3:
        raise argparse.ArgumentTypeError(f"颜色格式错误: {s!r}，应为 'R,G,B'")
    try:
        r, g, b = (int(p) for p in parts)
    except ValueError as e:
        raise argparse.ArgumentTypeError(f"颜色值不是整数: {s!r}") from e
    if not all(0 <= v <= 255 for v in (r, g, b)):
        raise argparse.ArgumentTypeError(f"颜色值超出 0-255: {s!r}")
    return (r, g, b)


def recolor_bg(
    bg: Image.Image, dark: tuple[int, int, int], light: tuple[int, int, int]
) -> Image.Image:
    """把 bg.png 的黑白二值图按 dark/light 重新着色。"""
    W, H = bg.size
    px = bg.load()
    out = Image.new("RGBA", (W, H), dark + (255,))
    out_px = out.load()
    for y in range(H):
        for x in range(W):
            r, g, b, a = px[x, y]
            if r < 128 and g < 128 and b < 128:
                out_px[x, y] = light + (a,)
            else:
                out_px[x, y] = dark + (a,)
    return out


def fit_backdrop(recolored: Image.Image, dark: tuple[int, int, int]) -> Image.Image:
    """把重新着色的 "26" 缩放到画布 85%，居中放在 dark 色画布上。"""
    W, H = recolored.size
    new_w = int(W * 0.85)
    new_h = int(H * 0.85)
    scaled = recolored.resize((new_w, new_h), Image.LANCZOS)
    canvas = Image.new("RGBA", (W, H), dark + (255,))
    canvas.paste(scaled, ((W - new_w) // 2, (H - new_h) // 2), scaled)
    return canvas


def floodfill_key(img: Image.Image, threshold: int = 240) -> Image.Image:
    """4 角泛洪：把连接到画布四角且 RGB >= threshold 的像素 alpha 设为 0。"""
    pixels = img.load()
    w, h = img.size
    visited = [[False] * h for _ in range(w)]
    q: deque = deque()
    for sx, sy in [(0, 0), (w - 1, 0), (0, h - 1), (w - 1, h - 1)]:
        r, g, b, _a = pixels[sx, sy]
        if r >= threshold and g >= threshold and b >= threshold:
            q.append((sx, sy))
            visited[sx][sy] = True
    while q:
        x, y = q.popleft()
        r, g, b, a = pixels[x, y]
        pixels[x, y] = (r, g, b, 0)
        for dx, dy in ((-1, 0), (1, 0), (0, -1), (0, 1)):
            nx, ny = x + dx, y + dy
            if 0 <= nx < w and 0 <= ny < h and not visited[nx][ny]:
                nr, ng, nb, _na = pixels[nx, ny]
                if nr >= threshold and ng >= threshold and nb >= threshold:
                    visited[nx][ny] = True
                    q.append((nx, ny))
    return img


def composite(canvas: Image.Image, character: Image.Image) -> Image.Image:
    """把人物合成到背景上。人物宽度 = 背景 85% 宽，水平居中，垂直居中。"""
    W, H = canvas.size
    cW, cH = character.size
    target_w = int(W * 0.85)
    ratio = target_w / cW
    target_h = int(cH * ratio)
    char_resized = character.resize((target_w, target_h), Image.LANCZOS)
    cx = (W - target_w) // 2
    cy = (H - target_h) // 2
    canvas.alpha_composite(char_resized, (cx, cy))
    return canvas


def add_label(img: Image.Image, text: str) -> Image.Image:
    """在底部 94.5% 高度处加 "FIFA WORLD CUP 2026"。深色填充，白色描边。"""
    W, H = img.size
    candidates = [
        "C:/Windows/Fonts/arialbd.ttf",
        "C:/Windows/Fonts/arial.ttf",
        "C:/Windows/Fonts/calibrib.ttf",
        "C:/Windows/Fonts/calibri.ttf",
        "/System/Library/Fonts/Helvetica.ttc",
        "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf",
    ]
    font = None
    for path in candidates:
        if not Path(path).exists():
            continue
        for sz in (110, 100, 90, 80, 70, 60, 50):
            f = ImageFont.truetype(path, sz)
            bbox = f.getbbox(text)
            tw = bbox[2] - bbox[0]
            if tw <= W * 0.85:
                font = f
                break
        if font:
            break
    if font is None:
        font = ImageFont.load_default()
    draw = ImageDraw.Draw(img)
    bbox = draw.textbbox((0, 0), text, font=font, stroke_width=4)
    tw = bbox[2] - bbox[0]
    th = bbox[3] - bbox[1]
    tx = (W - tw) // 2
    ty = int(H * 0.945) - th
    draw.text(
        (tx, ty),
        text,
        font=font,
        fill=(15, 15, 15, 255),
        stroke_width=4,
        stroke_fill=(255, 255, 255, 255),
    )
    return img


def main() -> int:
    ap = argparse.ArgumentParser(description="FIFA World Cup 2026 海报合成")
    ap.add_argument("--character", required=True, help="生成好的人物图片路径（白底）")
    ap.add_argument("--bg", required=True, help="背景模板 bg.png 路径")
    ap.add_argument(
        "--dark", required=True, type=parse_rgb, help="深色 (R,G,B)，背景底色"
    )
    ap.add_argument(
        "--light", required=True, type=parse_rgb, help="浅色 (R,G,B)，'26' 颜色"
    )
    ap.add_argument("--label", default="FIFA WORLD CUP 2026", help="底部文字")
    ap.add_argument("--out", required=True, help="输出目录")
    ap.add_argument("--name", default="poster.png", help="输出文件名")
    ap.add_argument("--no-label", action="store_true", help="不加底标")
    args = ap.parse_args()

    try:
        bg = Image.open(args.bg).convert("RGBA")
        character_raw = Image.open(args.character).convert("RGBA")
    except Exception as e:
        print(f"读取图片失败: {e}", file=sys.stderr)
        return 3

    recolored = recolor_bg(bg, args.dark, args.light)
    canvas = fit_backdrop(recolored, args.dark)

    character_keyed = floodfill_key(character_raw, threshold=240)
    composite(canvas, character_keyed)

    if not args.no_label:
        add_label(canvas, args.label)

    out_dir = Path(args.out).expanduser().resolve()
    # 警告：避免把海报直接写进系统根目录
    dangerous = {
        Path("C:/").resolve(),
        Path("C:\\").resolve(),
        Path("/").resolve(),
    }
    if out_dir.parent in dangerous:
        print(
            f"警告：输出目录 {out_dir} 处于系统根目录。\n"
            "建议改到项目根目录下的 .output/fifa-poster/，或 ~/Pictures/fifa-poster/。",
            file=sys.stderr,
        )
        return 4
    out_dir.mkdir(parents=True, exist_ok=True)
    out_path = out_dir / args.name
    canvas.save(out_path)
    print(f"已生成: {out_path}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
