from pathlib import Path

BASE_DIR = Path(__file__).parent.parent  # points to top_video_project/

DATA_DIR      = BASE_DIR / "data"
ASSETS_DIR    = BASE_DIR / "assets"
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
LAYOUT_TEMPLATE   = ASSETS_DIR / "layout_template.png"
FINAL_OUTPUT      = FINAL_DIR / "top.mp4"

# Video settings
FADE_DURATION  = 2    # seconds
TARGET_FPS     = 30
TARGET_RESOLUTION = "1920:1080"
PAD_COLOR = "black"
VIDEO_CODEC = "libx264"  # CPU (libx264) default, change to h264_nvenc / h264_amf / h264_qsv for GPU
