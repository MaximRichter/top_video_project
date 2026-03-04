import subprocess
import logging
import pandas as pd

from src.config import (
    VIDEOS_CSV,
    TRIMMED_DIR,
    OVERLAYED_DIR,
    NORMALISED_DIR,
    FADED_DIR,
    FINAL_DIR,
    TARGET_RESOLUTION,
    PAD_COLOR,
    TARGET_FPS,
    FADE_DURATION,
    DOWNLOADS_DIR,
    VIDEO_CODEC,
)


logger = logging.getLogger(__name__)

def trim_video(index: int, trim_start: int, trim_duration: int) -> bool:
    output_path = TRIMMED_DIR / f"{index}.mp4"

    if output_path.exists():
        logger.info(f"[{index}] Already trimmed, skipping.")
        return True

    input_files = list(DOWNLOADS_DIR.glob(f"{index}.*"))
    if not input_files:
        logger.error(f"[{index}] No downloaded file found, skipping trim.")
        return False

    input_path = input_files[0]

    video_filter: str = (
    f"scale={TARGET_RESOLUTION}:force_original_aspect_ratio=decrease," +
    f"pad={TARGET_RESOLUTION}:(ow-iw)/2:(oh-ih)/2:{PAD_COLOR}," +
    f"fps={TARGET_FPS}"
)

    command: list[str] = [
        "ffmpeg",
        "-ss", str(trim_start),
        "-i", str(input_path),
        "-t", str(trim_duration),
        "-vf", video_filter,
        "-c:v", VIDEO_CODEC,
        str(output_path)
    ]

    try:
        subprocess.run(command, check=True, stdout=subprocess.DEVNULL, stderr=subprocess.PIPE)
        logger.info(f"[{index}] Trimmed successfully.")
        return True
    except subprocess.CalledProcessError as e:
        logger.error(f"[{index}] Trim failed: {e.stderr.decode().strip()}")
        return False


def trim_all() -> None:
    """
    Reads videos.csv and trims all downloaded videos.
    """
    df = pd.read_csv(VIDEOS_CSV, delimiter=';')

    for i in range(len(df)):
        trim_video(
            index=i + 1,
            trim_start=int(df['trim_start'].iloc[i]),
            trim_duration=int(df['trim_duration'].iloc[i])
        )
