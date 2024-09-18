"""This module provides a minimal implementation of some functions for transcoding `.wav` files to other formats using `ffmpeg`.

If users need more flexible encoding options or advanced features(like parallel transcoding), we recommend directly using `ffmpeg` or a more feature-rich library.
"""

__all__ = [
    "wav_to_flac",
    "wav_to_mp3",
]

import logging
import os
import subprocess
from pathlib import Path
from typing import List


def transcode_wav(dir: Path, format: str, options: List[str] = []):
    for dirpath, _, filenames in os.walk(dir):
        for filename_wav in filenames:
            if not filename_wav.endswith(".wav"):
                continue
            filename_trans = filename_wav[:-3] + format

            file_wav = os.path.join(dirpath, filename_wav)
            file_trans = os.path.join(dirpath, filename_trans)
            if os.path.exists(file_trans):
                logging.warning(f"{filename_trans} already exists.")
                continue

            logging.info(f"Start transcoding {filename_wav} to {format}")

            returncode = subprocess.call(
                ["ffmpeg", "-i", file_wav, *options, file_trans], stdout=open(os.devnull, "w"), stderr=subprocess.STDOUT
            )
            if returncode == 0:
                logging.info(f"Transcoded {filename_wav} successfully, deleting this source file")
                os.remove(file_wav)
            else:
                logging.fatal(f"Failed to transcode {filename_wav} to {format}. Check your ffmpeg")


def wav_to_flac(dir: Path, compression_level: int):
    options = ["-compression_level", str(compression_level), "-bitexact", "-map", "0:a", "-map_metadata", "-1"]
    transcode_wav(dir, "flac", options)


def wav_to_mp3(dir: Path):
    options = ["-b:a", "320k", "-bitexact", "-map", "0:a", "-map_metadata", "-1"]
    transcode_wav(dir, "mp3", options)
