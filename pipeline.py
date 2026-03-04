import time
from datetime import timedelta
import pandas as pd
from tqdm import tqdm
from src.config import *
from src.downloader import download_video
from src.video import trim_video, normalize_audio, overlay_video, fade_video, concatenate_all
from src.image import generate_overlay
import logging

logger = logging.getLogger(__name__)


def setup():
    for directory in ALL_DIRS:
        directory.mkdir(parents=True, exist_ok=True)


def format_elapsed(seconds: float) -> str:
    return str(timedelta(seconds=round(seconds)))


def run_stage(name: str, indices: list[int], func) -> tuple[int, int, float]:
    success, failed = 0, 0
    start = time.time()

    with tqdm(indices, desc=f"{name:<20}", unit="video") as bar:
        for index in bar:
            result = func(index)
            if result:
                success += 1
            else:
                failed += 1
            bar.set_postfix(ok=success, fail=failed)

    return success, failed, time.time() - start


def main():
    setup()
    df = pd.read_csv(VIDEOS_CSV, delimiter=";")
    indices = list(range(1, len(df) + 1))
    rows = [df.iloc[i] for i in range(len(df))]

    print(f"\n{'='*50}")
    print(f"  Anime OST Pipeline — {len(indices)} videos")
    print(f"  Codec: {VIDEO_CODEC}")
    print(f"{'='*50}\n")

    total_start = time.time()
    summary = []

    stages = [
        ("Download",         lambda i: download_video(i, str(rows[i - 1]["download_url"]))),
        ("Trim", lambda i: trim_video(i, float(str(rows[i - 1]["trim_start"])), float(str(rows[i - 1]["trim_duration"])))),
        ("Normalize Audio",  normalize_audio),
        ("Generate Overlays", lambda i: generate_overlay(
            index=i,
            rank=i,
            anime_name=str(rows[i - 1]["anime_name"]),
            song_name=str(rows[i - 1]["song_name"]),
            scores=[float(rows[i - 1][str(r["score_column"])]) for r in REVIEWERS],
        )),
        ("Overlay Video",    overlay_video),
        ("Fade",             fade_video),
    ]

    for name, func in stages:
        success, failed, elapsed = run_stage(name, indices, func)
        summary.append((name, success, failed, elapsed))

    # Concatenation
    print("\nConcatenating...")
    start = time.time()
    concat_result = concatenate_all()
    concat_elapsed = time.time() - start
    summary.append(("Concatenate", 1 if concat_result else 0, 0 if concat_result else 1, concat_elapsed))

    total_elapsed = time.time() - total_start

    # Summary
    print(f"\n{'='*50}")
    print(f"  Pipeline Summary")
    print(f"{'='*50}")
    print(f"  {'Stage':<22} {'OK':>4} {'Fail':>4} {'Time':>10}")
    print(f"  {'-'*44}")
    for name, ok, fail, elapsed in summary:
        print(f"  {name:<22} {ok:>4} {fail:>4} {format_elapsed(elapsed):>10}")
    print(f"  {'-'*44}")
    print(f"  {'Total':<22} {'':>4} {'':>4} {format_elapsed(total_elapsed):>10}")
    print(f"{'='*50}\n")


if __name__ == "__main__":
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
        handlers=[logging.FileHandler(LOG_FILE)]
    )
    main()
