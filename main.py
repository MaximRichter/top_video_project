import logging
from src.config import ALL_DIRS, LOG_FILE
from src.downloader import download_all
from src.video import trim_all
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
    download_all()
    trim_all()
