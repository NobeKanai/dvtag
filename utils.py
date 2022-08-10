import logging
import os
from pathlib import Path
import subprocess
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
                # this should not happen
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


def wav_to_flac(dir: Path):
    transcode_wav(dir, "flac")


def wav_to_mp3(dir: Path):
    transcode_wav(dir, "mp3", ["-b:a", "320k"])
