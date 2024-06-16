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
import sys
from pathlib import Path
from typing import List


def transcode_wav(directory: Path, target_format: str, options: List[str] = []):
    for dirpath, _, filenames in os.walk(directory):
        for filename in filenames:
            if not filename.endswith(".wav"):
                continue

            source_file = Path(dirpath) / filename
            target_file = source_file.with_suffix(f".{target_format}")

            if target_file.exists():
                logging.warning(f"{target_file.name} already exists.")
                continue

            logging.info(f"Start transcoding {filename} to {target_format}")

            result = subprocess.run(
                ["ffmpeg", "-vn", "-i", str(source_file), *options, str(target_file)],
                stderr=subprocess.PIPE,
            )

            if result.returncode == 0:
                logging.info(f"Transcoded {filename} successfully, deleting the source file")
                source_file.unlink()
            else:
                logging.error(f"Failed to transcode {source_file} to {target_format}. Error: {result.stderr.decode()}")
                if target_file.exists():
                    target_file.unlink()
                sys.exit(1)


def wav_to_flac(directory: Path):
    transcode_wav(directory, "flac")


def wav_to_mp3(directory: Path):
    transcode_wav(directory, "mp3", ["-b:a", "320k"])
