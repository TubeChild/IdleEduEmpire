#!/usr/bin/env python3
"""Generate icon.png and icon.ico for Idle Edu Empire."""
from PIL import Image, ImageDraw


def _draw_icon(size: int) -> Image.Image:
    s = size
    img = Image.new("RGBA", (s, s), (0, 0, 0, 0))
    draw = ImageDraw.Draw(img)

    NAVY  = (18, 48, 96, 255)
    GOLD  = (235, 178, 32, 255)
    DGOLD = (170, 120, 15, 255)

    # Background
    draw.rounded_rectangle([0, 0, s - 1, s - 1], radius=s // 7, fill=NAVY)

    cx = s // 2
    by = int(s * 0.40)   # vertical centre of the board diamond

    # ── Board (wide rhombus) ─────────────────────────────────────────────
    bw = int(s * 0.42)
    bh = int(s * 0.13)
    board = [
        (cx,      by - bh),
        (cx + bw, by),
        (cx,      by + bh),
        (cx - bw, by),
    ]
    draw.polygon(board, fill=GOLD, outline=DGOLD)

    # ── Cap body (trapezoid) ─────────────────────────────────────────────
    cap_top = by + int(bh * 0.4)
    cap_bot = by + int(s * 0.27)
    cw_t = int(s * 0.21)
    cw_b = int(s * 0.17)
    cap = [
        (cx - cw_t, cap_top),
        (cx + cw_t, cap_top),
        (cx + cw_b, cap_bot),
        (cx - cw_b, cap_bot),
    ]
    draw.polygon(cap, fill=GOLD)

    # Brim ellipse at bottom of cap
    bw2 = int(s * 0.22)
    bh2 = int(s * 0.05)
    draw.ellipse([cx - bw2, cap_bot - bh2, cx + bw2, cap_bot + bh2], fill=GOLD)

    # ── Tassel ────────────────────────────────────────────────────────────
    lw = max(2, s // 56)
    tx, ty = cx + bw - int(s * 0.05), by
    tdx, tdy = -int(s * 0.05), int(s * 0.19)
    draw.line([(tx, ty), (tx + tdx, ty + tdy)], fill=DGOLD, width=lw)
    br = max(3, s // 30)
    bx, ball_y = tx + tdx, ty + tdy
    draw.ellipse([bx - br, ball_y - br, bx + br, ball_y + br], fill=DGOLD)

    return img


if __name__ == "__main__":
    img256 = _draw_icon(256)
    img256.save("icon.png")
    print("Saved icon.png")

    # Multi-resolution ICO (Windows wants 16/32/48/64/128/256)
    sizes = [16, 32, 48, 64, 128, 256]
    img256.save(
        "icon.ico",
        format="ICO",
        sizes=[(s, s) for s in sizes],
    )
    print("Saved icon.ico")
