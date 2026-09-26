#!/usr/bin/env python3
"""
Concatenate all audio segments into a single master audio track and generate SRT/ASS subtitles.
Outputs precise timestamps and durations for the Playwright recorder.
"""

import os
import json
import subprocess

DEMO_DIR = os.path.dirname(__file__)
AUDIO_DIR = os.path.join(DEMO_DIR, "audio_segments")
SCRIPT_FILE = os.path.join(DEMO_DIR, "voiceover_script.json")
CONCAT_LIST = os.path.join(DEMO_DIR, "concat_list.txt")
MASTER_AUDIO = os.path.join(DEMO_DIR, "master_audio.mp3")
SRT_FILE = os.path.join(DEMO_DIR, "subtitles.srt")
ASS_FILE = os.path.join(DEMO_DIR, "subtitles.ass")

def get_duration(file_path):
    cmd = [
        "ffprobe", "-v", "error",
        "-show_entries", "format=duration",
        "-of", "default=noprint_wrappers=1:nokey=1",
        file_path
    ]
    return float(subprocess.check_output(cmd).decode().strip())

def format_timestamp_srt(seconds):
    hrs = int(seconds // 3600)
    mins = int((seconds % 3600) // 60)
    secs = int(seconds % 60)
    millis = int((seconds - int(seconds)) * 1000)
    return f"{hrs:02d}:{mins:02d}:{secs:02d},{millis:03d}"

def format_timestamp_ass(seconds):
    hrs = int(seconds // 3600)
    mins = int((seconds % 3600) // 60)
    secs = int(seconds % 60)
    cs = int((seconds - int(seconds)) * 100)
    return f"{hrs:d}:{mins:02d}:{secs:02d}.{cs:02d}"

def main():
    with open(SCRIPT_FILE, "r", encoding="utf-8") as f:
        segments = json.load(f)

    lines = []
    srt_entries = []
    ass_events = []
    durations_dict = {}
    current_time = 0.0

    print("--- AUDIO SEGMENT TIMINGS ---")
    for seg in segments:
        seg_id = seg["id"]
        audio_file = os.path.join(AUDIO_DIR, f"seg_{seg_id:02d}.mp3")
        lines.append(f"file '{audio_file}'\n")

        duration = get_duration(audio_file)
        durations_dict[seg_id] = round(duration, 2)
        start_time = current_time
        end_time = current_time + duration

        print(f"Seg {seg_id}: {duration:.2f}s [{format_timestamp_srt(start_time)} -> {format_timestamp_srt(end_time)}]")

        # SRT format
        srt_entries.append(f"{seg_id}\n{format_timestamp_srt(start_time)} --> {format_timestamp_srt(end_time)}\n{seg['subtitle']}\n")

        # ASS format (Cyberdeck Phosphor Badge)
        ass_events.append(f"Dialogue: 0,{format_timestamp_ass(start_time)},{format_timestamp_ass(end_time)},CyberdeckStyle,,0,0,0,,{seg['subtitle']}")

        current_time = end_time

    with open(CONCAT_LIST, "w", encoding="utf-8") as f:
        f.writelines(lines)

    # Concat audio via ffmpeg
    cmd = [
        "ffmpeg", "-y", "-f", "concat", "-safe", "0",
        "-i", CONCAT_LIST, "-c", "copy", MASTER_AUDIO
    ]
    subprocess.run(cmd, check=True)
    print(f"\n✅ Generated master audio: {MASTER_AUDIO} ({current_time:.2f}s)")

    # Write SRT
    with open(SRT_FILE, "w", encoding="utf-8") as f:
        f.write("\n".join(srt_entries))
    print(f"✅ Generated SRT subtitles: {SRT_FILE}")

    # Write ASS with cyberdeck phosphor badge styling
    ass_header = """[Script Info]
ScriptType: v4.00+
PlayResX: 1920
PlayResY: 1080
ScaledBorderAndShadow: yes

[V4+ Styles]
Format: Name, Fontname, Fontsize, PrimaryColour, SecondaryColour, OutlineColour, BackColour, Bold, Italic, Underline, StrikeOut, ScaleX, ScaleY, Spacing, Angle, BorderStyle, Outline, Shadow, Alignment, MarginL, MarginR, MarginV, Encoding
Style: CyberdeckStyle,Plus Jakarta Sans,32,&H00FFFFFF,&H00000000,&H80000000,&HB00F141C,-1,0,0,0,100,100,0,0,3,8,0,2,60,60,54,1

[Events]
Format: Layer, Start, End, Style, Name, MarginL, MarginR, MarginV, Effect, Text
"""
    with open(ASS_FILE, "w", encoding="utf-8") as f:
        f.write(ass_header + "\n".join(ass_events))
    print(f"✅ Generated ASS cyberdeck subtitle badges: {ASS_FILE}")

    print("\nDURATIONS_MAP = ", json.dumps(durations_dict, indent=2))

if __name__ == "__main__":
    main()
