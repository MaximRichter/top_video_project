import subprocess
import logging
import json
import pandas as pd

from src.config import VIDEOS_CSV, DOWNLOADS_DIR

logger = logging.getLogger(__name__)

URLS_RECORD = DOWNLOADS_DIR / "url_record.json"

def load_url_record() -> dict[str, str]:
    if URLS_RECORD.exists():
        return json.loads(URLS_RECORD.read_text())
    return {}

def save_url_record(record: dict[str, str]) -> None:
    URLS_RECORD.write_text(json.dumps(record, indent=2))



def download_video(index: int, url: str) -> bool:
    record = load_url_record()
    existing = list(DOWNLOADS_DIR.glob(f"{index}.*"))
    
    if existing:
        if record.get(str(index)) == url:
            logger.info(f"[{index}] Already exists with same URL, skipping.")
            return True
        else:
            logger.info(f"[{index}] URL changed, re-downloading.")
            existing[0].unlink()

    output_template = str(DOWNLOADS_DIR / f"{index}.%(ext)s")
    command = [
        "yt-dlp",
        "--no-overwrites",
        "-o", output_template,
        url
    ]

    try: 
        subprocess.run(command, check=True, stdout=subprocess.DEVNULL, stderr=subprocess.PIPE)
        logger.info(f"[{index}] Downloaded successfully.")
        record[str(index)] = url
        save_url_record(record)
        return True
    except subprocess.CalledProcessError as e:
        logger.error(f"[{index}] Download failed: {e.stderr.decode().strip()}")
        return False

def sync_downloads(valid_indices: set[int]) -> None:
    for file in DOWNLOADS_DIR.iterdir():
        if file.suffix == '.json':
            continue
        try:
            if int(file.stem) not in valid_indices:
                logger.info(f"[{file.stem}] No longer in CSV, deleting.")
                file.unlink()
        except ValueError:
            logger.warning(f"Unexpected file in downloads folder: {file.name}, skipping.")

def download_all() -> None:
    """
    Reads videos.csv, syncs the downloads folder, then downloads any missing videos.
    """
    df = pd.read_csv(VIDEOS_CSV, delimiter=';')
    valid_indices = set(range(1, len(df) + 1))
    sync_downloads(valid_indices)
    for i in range(len(df)):
        url = str(df['download_url'].iloc[i])
        download_video(i + 1, url)
