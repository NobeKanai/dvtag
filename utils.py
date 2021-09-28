import os
import subprocess
import sys
from pathlib import Path
from typing import List


def transcode_wav(dir: Path, format: str = "flac", options: List[str] = []):
    for dirpath, _, filenames in os.walk(dir):
        for filename_wav in filenames:
            if not filename_wav.endswith(".wav"):
                continue
            filename_trans = filename_wav[:-3] + format

            file_wav = os.path.join(dirpath, filename_wav)
            file_trans = os.path.join(dirpath, filename_trans)
            if os.path.exists(file_trans):
                # this should not happen
                print(f"{filename_trans} already exists.")
                continue

            print(f"Start transcoding {filename_wav} to {format}")

            # FFmpeg uses multi-threading by default
            returncode = subprocess.call(
                ["ffmpeg", "-i", file_wav, *options, file_trans],
                stdout=open(os.devnull, "w"),
                stderr=subprocess.STDOUT)
            if returncode == 0:
                print(
                    f"Transcode {filename_wav} successfully, delete this source file"
                )
                os.remove(file_wav)
            else:
                print(f"Failed to transcode {filename_wav} to {format}")
                sys.exit(1)


def wav_to_flac(dir: Path):
    transcode_wav(dir)


def wav_to_mp3(dir: Path):
    transcode_wav(dir, "mp3", ["-b:a", "320k"])
