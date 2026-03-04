# Anime OST Top Video Pipeline

Automated pipeline for generating ranked anime opening/OST compilation videos with overlays, audio normalization, and fade effects.

## Prerequisites

- Python 3.11+
- [ffmpeg](https://ffmpeg.org/download.html)
- [yt-dlp](https://github.com/yt-dlp/yt-dlp)

## Installation
```bash
git clone <repo>
cd top_video_project
python -m venv .venv
source .venv/bin/activate  # Windows: .venv\Scripts\activate
pip install -r requirements.txt
```

## Configuration

Edit `src/config.py` before running:

- `VAAPI_DEVICE` — GPU render node (Linux only, e.g. `/dev/dri/renderD128`). Run `ls /dev/dri/` to find yours.
- `BROWSER_COOKIES` — Path to your browser profile for yt-dlp authentication (e.g. `firefox:~/.zen/your-profile/`)
- `REVIEWERS` — List of reviewers with names, avatar paths and CSV score column names.

## Assets

Place the following in the `assets/` folder:
```
assets/
├── fonts/
│   ├── Roboto-Bold.ttf
│   └── Roboto-Regular.ttf
└── avatars/
    ├── andy.png
    ├── alex.png
    └── astik.png
```

## CSV Format

`data/videos.csv` uses `;` as delimiter with the following columns:
```
anime_name;song_name;andy_score;alex_score;astik_score;trim_start;trim_duration;download_url
```

## Usage
```bash
python pipeline.py
```

The pipeline will run through all stages automatically:
1. Download
2. Trim
3. Normalize Audio
4. Generate Overlays
5. Overlay Video
6. Fade
7. Concatenate

Final output is saved to `output/final/top.mp4`.

## Utilities

Clean all output except downloads:
```bash
python clean.py
```
