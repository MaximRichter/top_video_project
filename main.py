import logging
from src.config import ALL_DIRS, LOG_FILE, VIDEO_CODEC
from src.downloader import download_all
from src.image import generate_all
from src.video import normalize_all, trim_all
import os

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(),           # terminal
        logging.FileHandler(LOG_FILE)      # file
    ]
)


def setup():
    for directory in ALL_DIRS:
        os.makedirs(directory, exist_ok=True)

if __name__ == "__main__":
    setup()
    logger = logging.getLogger(__name__)
    logger.info(f"Using video codec: {VIDEO_CODEC}")
    download_all()
    trim_all()
    normalize_all()
    generate_all()
