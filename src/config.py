from pathlib import Path

BASE_DIR = Path(__file__).parent.parent  # points to top_video_project/

DATA_DIR      = BASE_DIR / "data"
ASSETS_DIR    = BASE_DIR / "assets"
OUTPUT_DIR    = BASE_DIR / "output"

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

OPENINGS_CSV      = DATA_DIR / "openings.csv"
LAYOUT_TEMPLATE   = ASSETS_DIR / "layout_template.png"
FINAL_OUTPUT      = FINAL_DIR / "top.mp4"

# Video settings
TRIM_START     = 50   # seconds
TRIM_DURATION  = 35   # seconds
FADE_DURATION  = 2    # seconds
TARGET_FPS     = 30
TARGET_WIDTH   = 1920
TARGET_HEIGHT  = 1080
