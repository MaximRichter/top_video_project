import pandas as pd
from PIL import Image, ImageDraw, ImageFont
from src.config import (
    VIDEOS_CSV,
    IMAGES_DIR,
    FONT_BOLD,
    FONT_REGULAR,
    REVIEWERS,
)
import logging

logger = logging.getLogger(__name__)

# Colors
DARK_BG      = (30, 30, 30, 220)     # dark semi-transparent background
LIGHT_BG     = (200, 185, 155, 255)  # beige for song name bar
WHITE        = (255, 255, 255, 255)
BLACK        = (0, 0, 0, 255)
TRANSPARENT  = (0, 0, 0, 0)

# Dimensions
CORNER_RADIUS = 12


def rounded_rectangle(draw, xy, radius, fill):
    x1, y1, x2, y2 = xy
    draw.rectangle([x1 + radius, y1, x2 - radius, y2], fill=fill)
    draw.rectangle([x1, y1 + radius, x2, y2 - radius], fill=fill)
    draw.ellipse([x1, y1, x1 + radius * 2, y1 + radius * 2], fill=fill)
    draw.ellipse([x2 - radius * 2, y1, x2, y1 + radius * 2], fill=fill)
    draw.ellipse([x1, y2 - radius * 2, x1 + radius * 2, y2], fill=fill)
    draw.ellipse([x2 - radius * 2, y2 - radius * 2, x2, y2], fill=fill)


def draw_top_left(img, draw, rank, anime_name, song_name):
    font_rank    = ImageFont.truetype(str(FONT_BOLD), 72)
    font_anime   = ImageFont.truetype(str(FONT_BOLD), 36)
    font_song    = ImageFont.truetype(str(FONT_REGULAR), 28)

    # Rank box
    rounded_rectangle(draw, (20, 20, 160, 155), CORNER_RADIUS, DARK_BG)
    draw.text((90, 87), str(rank), font=font_rank, fill=WHITE, anchor="mm")

    # Anime name bar
    rounded_rectangle(draw, (175, 20, 1060, 85), CORNER_RADIUS, DARK_BG)
    draw.text((617, 52), anime_name, font=font_anime, fill=WHITE, anchor="mm")

    # Song name bar
    rounded_rectangle(draw, (175, 95, 1060, 155), CORNER_RADIUS, LIGHT_BG)
    draw.text((617, 125), song_name, font=font_song, fill=BLACK, anchor="mm")


def draw_bottom_right(img, draw, scores):
    font_name    = ImageFont.truetype(str(FONT_BOLD), 28)
    font_score   = ImageFont.truetype(str(FONT_BOLD), 36)
    font_avg_lbl = ImageFont.truetype(str(FONT_BOLD), 24)
    font_avg_val = ImageFont.truetype(str(FONT_BOLD), 48)

    card_w, card_h = 160, 170
    avatar_size    = 80
    padding        = 10
    start_x        = 1920 - (len(REVIEWERS) + 1) * (card_w + padding) - 20
    start_y        = 1080 - card_h - 20

    for i, reviewer in enumerate(REVIEWERS):
        x = start_x + i * (card_w + padding)
        y = start_y

        # Card background
        rounded_rectangle(draw, (x, y, x + card_w, y + card_h), CORNER_RADIUS, DARK_BG)

        # Name
        draw.text((x + card_w // 2, y + 18), reviewer["name"], font=font_name, fill=WHITE, anchor="mm")

        # Avatar
        avatar = Image.open(reviewer["avatar"]).convert("RGBA")
        avatar = avatar.resize((avatar_size, avatar_size))
        img.paste(avatar, (x + (card_w - avatar_size) // 2, y + 35), avatar)

        # Score box + score centered in lower portion
        score = scores[i]
        score_y = y + 35 + avatar_size + (card_h - 35 - avatar_size) // 2
        score_box_w, score_box_h = 90, 44
        score_box_x = x + (card_w - score_box_w) // 2
        score_box_y = score_y - score_box_h // 2
        rounded_rectangle(draw, (score_box_x, score_box_y, score_box_x + score_box_w, score_box_y + score_box_h), CORNER_RADIUS, LIGHT_BG)
        draw.text((x + card_w // 2, score_y), str(score), font=font_score, fill=BLACK, anchor="mm")

    # Average card - beige background with dark text
    avg = round(sum(scores) / len(scores), 2)
    ax = start_x + len(REVIEWERS) * (card_w + padding)
    ay = start_y

    rounded_rectangle(draw, (ax, ay, ax + card_w, ay + card_h), CORNER_RADIUS, LIGHT_BG)
    draw.text((ax + card_w // 2, ay + 40), "Average", font=font_avg_lbl, fill=BLACK, anchor="mm")

    # Average value in its own dark box
    avg_box_w, avg_box_h = 120, 60
    avg_box_x = ax + (card_w - avg_box_w) // 2
    avg_box_y = ay + card_h // 2
    rounded_rectangle(draw, (avg_box_x, avg_box_y, avg_box_x + avg_box_w, avg_box_y + avg_box_h), CORNER_RADIUS, DARK_BG)
    draw.text((ax + card_w // 2, avg_box_y + avg_box_h // 2), str(avg), font=font_avg_val, fill=WHITE, anchor="mm")



def generate_overlay(index: int, rank: int, anime_name: str, song_name: str, scores: list[float]) -> bool:
    output_path = IMAGES_DIR / f"{index}.png"

    if output_path.exists():
        logger.info(f"[{index}] Overlay image already exists, skipping.")
        return True

    try:
        img  = Image.new("RGBA", (1920, 1080), TRANSPARENT)
        draw = ImageDraw.Draw(img)

        draw_top_left(img, draw, rank, anime_name, song_name)
        draw_bottom_right(img, draw, scores)

        img.save(str(output_path))
        logger.info(f"[{index}] Overlay generated.")
        return True

    except Exception as e:
        logger.error(f"[{index}] Failed to generate overlay: {e}")
        return False


def generate_all() -> None:
    df = pd.read_csv(VIDEOS_CSV, delimiter=";")
    for i in range(len(df)):
        row = df.iloc[i]
        index = i + 1
        scores = [float(row[str(r["score_column"])]) for r in REVIEWERS]
        generate_overlay(
            index=index,
            rank=index,
            anime_name=str(row["anime_name"]),
            song_name=str(row["song_name"]),
            scores=scores,
        )
