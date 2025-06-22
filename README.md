# YouTube Segment Downloader

Simple GUI tool to download specific segments from YouTube videos.

## Installation

```bash
git clone https://github.com/yourusername/youtube-segment-downloader.git
cd youtube-segment-downloader
pip install yt-dlp
```

**Also install FFmpeg:**
- Windows: Download from [ffmpeg.org](https://ffmpeg.org/download.html)
- Mac: `brew install ffmpeg`
- Linux: `sudo apt install ffmpeg`

## Usage

```bash
python main.py
```

**Input:**
- YouTube URL
- Start time (MM:SS or HH:MM:SS)
- End time (MM:SS or HH:MM:SS)
- Quality selection
- Output directory

**Output:**
- Video segment saved as MP4/MKV/WEBM file

## Example
- URL: `https://youtube.com/watch?v=example`
- Start: `1:30`, End: `3:45`
- Downloads 2min 15sec segment in selected quality
