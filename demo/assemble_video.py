#!/usr/bin/env python3
"""
Assemble master 1080p demo video for Uncluster.
Combines Playwright screen recording (with native in-DOM subtitle badges) with neural voiceover.
"""

import os
import sys
import glob
import subprocess

DEMO_DIR = os.path.dirname(__file__)
RAW_VIDEO_DIR = os.path.join(DEMO_DIR, "raw_video")
MASTER_AUDIO = os.path.join(DEMO_DIR, "master_audio.mp3")
OUTPUT_VIDEO = os.path.join(DEMO_DIR, "uncluster_demo.mp4")

def get_duration(file_path):
    cmd = [
        "ffprobe", "-v", "error",
        "-show_entries", "format=duration",
        "-of", "default=noprint_wrappers=1:nokey=1",
        file_path
    ]
    return float(subprocess.check_output(cmd).decode().strip())

def main():
    webm_files = glob.glob(os.path.join(RAW_VIDEO_DIR, "*.webm"))
    if not webm_files:
        print("❌ Error: No .webm video found in raw_video/")
        sys.exit(1)

    raw_video = max(webm_files, key=os.path.getmtime)
    print(f"📹 Found raw video: {raw_video}")

    video_dur = get_duration(raw_video)
    audio_dur = get_duration(MASTER_AUDIO)
    print(f"Raw Video Duration: {video_dur:.2f}s | Audio Duration: {audio_dur:.2f}s")

    cmd = [
        "ffmpeg", "-y",
        "-i", raw_video,
        "-i", MASTER_AUDIO,
        "-c:v", "libx264",
        "-preset", "medium",
        "-crf", "18",
        "-pix_fmt", "yuv420p",
        "-c:a", "aac",
        "-b:a", "192k",
        "-shortest",
        OUTPUT_VIDEO
    ]

    print("⚙️ Running ffmpeg command...")
    subprocess.run(cmd, check=True)

    final_dur = get_duration(OUTPUT_VIDEO)
    file_size_mb = os.path.getsize(OUTPUT_VIDEO) / (1024 * 1024)
    print(f"🎉 Final master video assembled successfully!")
    print(f"📁 Path: {OUTPUT_VIDEO}")
    print(f"⏱️ Duration: {final_dur:.2f}s ({final_dur/60:.2f} mins)")
    print(f"📦 Size: {file_size_mb:.2f} MB")

if __name__ == "__main__":
    main()
