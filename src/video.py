import subprocess
import select
import logging
import json
import sys
import pandas as pd

from src.config import (
    VAAPI_DEVICE,
    VIDEOS_CSV,
    TRIMMED_DIR,
    OVERLAYED_DIR,
    NORMALISED_DIR,
    FADED_DIR,
    FINAL_DIR,
    FINAL_OUTPUT,
    TARGET_RESOLUTION,
    PAD_COLOR,
    TARGET_FPS,
    FADE_DURATION,
    DOWNLOADS_DIR,
    VIDEO_CODEC,
    IMAGES_DIR,
)


logger = logging.getLogger(__name__)

def trim_video(index: int, trim_start: float, trim_duration: float) -> bool:
    output_path = TRIMMED_DIR / f"{index}.mp4"

    if output_path.exists():
        logger.info(f"[{index}] Already trimmed, skipping.")
        return True

    input_files = list(DOWNLOADS_DIR.glob(f"{index}.*"))
    if not input_files:
        logger.error(f"[{index}] No downloaded file found, skipping trim.")
        return False

    input_path = input_files[0]

    hw_upload: str = ",format=nv12,hwupload" if VIDEO_CODEC == "h264_vaapi" else ""

    video_filter: str = (
    f"scale={TARGET_RESOLUTION}:force_original_aspect_ratio=decrease," +
    f"pad={TARGET_RESOLUTION}:(ow-iw)/2:(oh-ih)/2:{PAD_COLOR}," +
    f"fps={TARGET_FPS}" +
    f"{hw_upload}"
)

    vaapi_device: list[str] = ["-vaapi_device", VAAPI_DEVICE] if VIDEO_CODEC == "h264_vaapi" else []

    command: list[str] = [
        "ffmpeg", "-y",
        *vaapi_device,
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
            trim_start=float(df['trim_start'].iloc[i]),
            trim_duration=float(df['trim_duration'].iloc[i])
        )



def normalize_audio(index: int) -> bool:
    input_files = list(TRIMMED_DIR.glob(f"{index}.*"))
    if not input_files:
        logger.error(f"[{index}] No trimmed file found, skipping normalize.")
        return False

    input_path = input_files[0]
    output_path = NORMALISED_DIR / f"{index}.mp4"

    if output_path.exists():
        logger.info(f"[{index}] Already normalised, skipping.")
        return True

    pass1_filter = "loudnorm=I=-16:TP=-1.5:LRA=11:print_format=json"
    pass1_command = [
        "ffmpeg", "-y",
        "-i", str(input_path),
        "-af", pass1_filter,
        "-vn", "-f", "null", "/dev/null"
    ]

    try:
        result = subprocess.run(
            pass1_command,
            stdout=subprocess.DEVNULL,
            stderr=subprocess.PIPE,
            text=True,
            check=False
        )

        stderr = result.stderr
        json_start = stderr.rfind("{")
        json_end = stderr.rfind("}") + 1
        measurements = json.loads(stderr[json_start:json_end])

    except Exception as e:
        logger.error(f"[{index}] Normalize pass 1 failed: {e}")
        return False

    pass2_filter = (
        f"loudnorm=I=-16:TP=-1.5:LRA=11:linear=true:"
        f"measured_I={measurements['input_i']}:"
        f"measured_TP={measurements['input_tp']}:"
        f"measured_LRA={measurements['input_lra']}:"
        f"measured_thresh={measurements['input_thresh']}:"
        f"offset={measurements['target_offset']}:"
        f"print_format=summary"
    )
    pass2_command = [
        "ffmpeg", "-y",
        "-i", str(input_path),
        "-af", pass2_filter,
        "-c:v", "copy",
        "-c:a", "aac",
        str(output_path)
    ]

    try:
        subprocess.run(
            pass2_command,
            stdout=subprocess.DEVNULL,
            stderr=subprocess.PIPE,
            check=True
        )
        logger.info(f"[{index}] Normalised successfully.")
        return True

    except subprocess.CalledProcessError as e:
        logger.error(f"[{index}] Normalize pass 2 failed: {e.stderr.decode()}")
        return False


def normalize_all() -> None:
    df = pd.read_csv(VIDEOS_CSV, delimiter=";")
    for i in range(len(df)):
        index: int = i + 1
        normalize_audio(index)


def overlay_video(index: int) -> bool:
    input_files = list(NORMALISED_DIR.glob(f"{index}.*"))
    if not input_files:
        logger.error(f"[{index}] No normalised file found, skipping overlay.")
        return False

    input_path = input_files[0]
    overlay_path = IMAGES_DIR / f"{index}.png"
    output_path = OVERLAYED_DIR / f"{index}.mp4"

    if not overlay_path.exists():
        logger.error(f"[{index}] No overlay image found, skipping overlay.")
        return False

    if output_path.exists():
        logger.info(f"[{index}] Already overlayed, skipping.")
        return True

    command = [
        "ffmpeg", "-y",
        "-i", str(input_path),
        "-i", str(overlay_path),
        "-filter_complex", "[0:v][1:v]overlay=0:0",
        "-c:v", VIDEO_CODEC,
        "-c:a", "copy",
        str(output_path)
    ]

    if VIDEO_CODEC == "h264_vaapi":
        command = [
            "ffmpeg", "-y",
            "-vaapi_device", VAAPI_DEVICE,
            "-i", str(input_path),
            "-i", str(overlay_path),
            "-filter_complex", "[0:v]format=nv12[v];[v][1:v]overlay=0:0,format=nv12,hwupload[out]",
            "-map", "[out]",
            "-map", "0:a",
            "-c:v", VIDEO_CODEC,
            "-c:a", "copy",
            str(output_path)
        ]

    try:
        subprocess.run(
            command,
            stdout=subprocess.DEVNULL,
            stderr=subprocess.PIPE,
            check=True
        )
        logger.info(f"[{index}] Overlay applied successfully.")
        return True

    except subprocess.CalledProcessError as e:
        logger.error(f"[{index}] Overlay failed: {e.stderr.decode()}")
        return False


def overlay_all() -> None:
    df = pd.read_csv(VIDEOS_CSV, delimiter=";")
    for i in range(len(df)):
        overlay_video(i + 1)


def fade_video(index: int) -> bool:
    input_files = list(OVERLAYED_DIR.glob(f"{index}.*"))
    if not input_files:
        logger.error(f"[{index}] No overlayed file found, skipping fade.")
        return False

    input_path = input_files[0]
    output_path = FADED_DIR / f"{index}.mp4"

    if output_path.exists():
        logger.info(f"[{index}] Already faded, skipping.")
        return True

    # Get duration of the video
    probe_command = [
        "ffprobe", "-v", "error",
        "-show_entries", "format=duration",
        "-of", "default=noprint_wrappers=1:nokey=1",
        str(input_path)
    ]

    try:
        result = subprocess.run(
            probe_command,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
            check=True
        )
        duration = float(result.stdout.strip())
    except subprocess.CalledProcessError as e:
        logger.error(f"[{index}] ffprobe failed: {e.stderr}")
        return False

    fade_out_start = duration - FADE_DURATION

    vaapi_device = ["-vaapi_device", VAAPI_DEVICE] if VIDEO_CODEC == "h264_vaapi" else []

    if VIDEO_CODEC == "h264_vaapi":
        video_filter = (
            f"[0:v]format=yuv420p,"
            f"fade=t=in:st=0:d={FADE_DURATION},"
            f"fade=t=out:st={fade_out_start}:d={FADE_DURATION},"
            f"format=nv12,hwupload[out]"
        )
        filter_args = ["-filter_complex", video_filter, "-map", "[out]", "-map", "0:a"]

    else:
        video_filter = (
            f"fade=t=in:st=0:d={FADE_DURATION},"
            f"fade=t=out:st={fade_out_start}:d={FADE_DURATION}"
        )
        filter_args = ["-vf", video_filter]

    audio_filter = (
        f"afade=t=in:st=0:d={FADE_DURATION},"
        f"afade=t=out:st={fade_out_start}:d={FADE_DURATION}"
    )

    command = [
        "ffmpeg", "-y",
        *vaapi_device,
        "-i", str(input_path),
        *filter_args,
        "-af", audio_filter,
        "-c:v", VIDEO_CODEC,
        "-c:a", "aac",
        str(output_path)
    ]

    try:
        subprocess.run(
            command,
            stdout=subprocess.DEVNULL,
            stderr=subprocess.PIPE,
            check=True
        )
        logger.info(f"[{index}] Faded successfully.")
        return True

    except subprocess.CalledProcessError as e:
        logger.error(f"[{index}] Fade failed: {e.stderr.decode()}")
        return False


def fade_all() -> None:
    df = pd.read_csv(VIDEOS_CSV, delimiter=";")
    for i in range(len(df)):
        fade_video(i + 1)


def prompt_with_timeout(message: str, timeout: int, default: str) -> str:
    print(message, flush=True)
    for remaining in range(timeout, 0, -1):
        print(f"\rSelecting default ({default}) in {remaining}s... ", end="", flush=True)
        if sys.platform != "win32":
            ready, _, _ = select.select([sys.stdin], [], [], 1)
            if ready:
                choice = sys.stdin.readline().strip()
                print()
                return choice
        else:
            import msvcrt, time
            start = time.time()
            while time.time() - start < 1:
                if msvcrt.kbhit():
                    choice = input()
                    print()
                    return choice
    print(f"\nTimeout reached, using default: {default}")
    return default


def concatenate_all() -> bool:
    df = pd.read_csv(VIDEOS_CSV, delimiter=";")
    message = (
        "\nConcatenation mode:\n"
        "  [1] Only concatenate if all downloaded videos are present\n"
        "  [2] Skip missing files and concatenate available videos (default)\n"
        "Enter choice (1/2): "
    )
    choice = prompt_with_timeout(message, timeout=300, default="2")

    faded_files = []
    for i in range(len(df)):
        index = i + 1
        files = list(FADED_DIR.glob(f"{index}.*"))
        if not files:
            if choice == "2":
                logger.warning(f"[{index}] No faded file found, skipping.")
                continue
            else:
                download_files = list(DOWNLOADS_DIR.glob(f"{index}.*"))
                if not download_files:
                    logger.info(f"[{index}] No download found, skipping.")
                    continue
                logger.error(f"[{index}] No faded file found but download exists, aborting.")
                return False
        faded_files.append(files[0])
    
    faded_files.reverse()

    if not faded_files:
        logger.error("No faded files found at all, aborting.")
        return False

    inputs = []
    filter_parts = []
    for i, file in enumerate(faded_files):
        inputs += ["-i", str(file)]
        filter_parts.append(f"[{i}:v][{i}:a]")

    n = len(faded_files)
    vaapi_device = ["-vaapi_device", VAAPI_DEVICE] if VIDEO_CODEC == "h264_vaapi" else []

    if VIDEO_CODEC == "h264_vaapi":
        filter_complex = "".join(filter_parts) + f"concat=n={n}:v=1:a=1[vraw][a];[vraw]format=nv12,hwupload[v]"
        map_args = ["-map", "[v]", "-map", "[a]"]
    else:
        filter_complex = "".join(filter_parts) + f"concat=n={n}:v=1:a=1[v][a]"
        map_args = ["-map", "[v]", "-map", "[a]"]

    command = [
        "ffmpeg", "-y",
        *vaapi_device,
        *inputs,
        "-filter_complex", filter_complex,
        *map_args,
        "-c:v", VIDEO_CODEC,
        "-c:a", "aac",
        str(FINAL_OUTPUT)
    ]

    try:
        subprocess.run(
            command,
            stdout=subprocess.DEVNULL,
            stderr=subprocess.PIPE,
            check=True
        )
        logger.info("Concatenation complete. Final output: top.mp4")
        return True

    except subprocess.CalledProcessError as e:
        logger.error(f"Concatenation failed: {e.stderr.decode()}")
        return False

