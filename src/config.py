from pathlib import Path
from src.system import detect_codec

BASE_DIR = Path(__file__).parent.parent  # points to top_video_project/

DATA_DIR      = BASE_DIR / "data"
ASSETS_DIR    = BASE_DIR / "assets"
FONTS_DIR     = ASSETS_DIR / "fonts"
AVATARS_DIR   = ASSETS_DIR / "avatars"
OUTPUT_DIR    = BASE_DIR / "output"
LOG_FILE        = BASE_DIR / "pipeline.log"

DOWNLOADS_DIR   = OUTPUT_DIR / "downloads"
TRIMMED_DIR     = OUTPUT_DIR / "trimmed"
IMAGES_DIR      = OUTPUT_DIR / "images"
OVERLAYED_DIR   = OUTPUT_DIR / "overlayed"
NORMALISED_DIR  = OUTPUT_DIR / "normalised"
FADED_DIR       = OUTPUT_DIR / "faded"
FINAL_DIR       = OUTPUT_DIR / "final"

ALL_DIRS = [
    DOWNLOADS_DIR, TRIMMED_DIR, IMAGES_DIR,
    OVERLAYED_DIR, NORMALISED_DIR, FADED_DIR, FINAL_DIR
]

VIDEOS_CSV      = DATA_DIR / "videos.csv"
FINAL_OUTPUT      = FINAL_DIR / "top.mp4"

# Video settings
FADE_DURATION  = 2    # seconds
TARGET_FPS     = 30
TARGET_RESOLUTION = "1920:1080"
PAD_COLOR = "black"
VIDEO_CODEC = detect_codec()
VAAPI_DEVICE = "/dev/dri/renderD128"


# Overlay settings
FONT_BOLD = FONTS_DIR / "Roboto-Bold.ttf"
FONT_REGULAR = FONTS_DIR / "Roboto-Regular.ttf"
REVIEWERS = [
    {"name": "Andy", "avatar": AVATARS_DIR / "andy.png", "score_column": "andy_score"},
    {"name": "Alex", "avatar": AVATARS_DIR / "alex.png", "score_column": "alex_score"},
    {"name": "Astik", "avatar": AVATARS_DIR / "astik.png", "score_column": "astik_score"},
]

BROWSER_COOKIES = "firefox:~/.zen/0uz1xbvm.Default (release)/"
