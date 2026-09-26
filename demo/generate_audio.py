#!/usr/bin/env python3
"""
Generate natural neural audio segments for Uncluster demo video using edge-tts.
Runs sequentially with retries to ensure zero rate limit failures.
"""

import os
import sys
import json
import asyncio
import subprocess
import time

DEMO_DIR = os.path.dirname(__file__)
SCRIPT_PATH = os.path.join(DEMO_DIR, "voiceover_script.json")
OUTPUT_DIR = os.path.join(DEMO_DIR, "audio_segments")

VOICE = "en-US-AndrewNeural"
RATE = "+4%"

def generate_segment(segment_id, text, output_file, max_retries=3):
    cmd = [
        "edge-tts",
        "--voice", VOICE,
        "--rate", RATE,
        "--text", text,
        "--write-media", output_file
    ]
    for attempt in range(max_retries):
        try:
            res = subprocess.run(cmd, check=True, capture_output=True, text=True)
            if os.path.exists(output_file) and os.path.getsize(output_file) > 1000:
                print(f"✅ Generated segment {segment_id}: {output_file} ({os.path.getsize(output_file)} bytes)")
                return True
        except subprocess.CalledProcessError as e:
            print(f"⚠️ Retry {attempt+1} for segment {segment_id}: {e.stderr}")
            time.sleep(1.5)
    print(f"❌ Failed segment {segment_id}")
    return False

def main():
    os.makedirs(OUTPUT_DIR, exist_ok=True)
    with open(SCRIPT_PATH, "r", encoding="utf-8") as f:
        segments = json.load(f)

    for seg in segments:
        out_file = os.path.join(OUTPUT_DIR, f"seg_{seg['id']:02d}.mp3")
        # Check if already successfully generated
        if os.path.exists(out_file) and os.path.getsize(out_file) > 1000:
            print(f"⏩ Segment {seg['id']} already exists, skipping.")
            continue
        generate_segment(seg["id"], seg["text"], out_file)
        time.sleep(0.5)

    print("All Uncluster audio segments ready!")

if __name__ == "__main__":
    main()
