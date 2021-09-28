import os
import subprocess
import sys
from pathlib import Path


def wav_to_flac(dir: Path):
    for dirpath, _, filenames in os.walk(dir):
        for filename_wav in filenames:
            if not filename_wav.endswith(".wav"):
                continue
            filename_flac = filename_wav[:-4] + '.flac'

            file_wav = os.path.join(dirpath, filename_wav)
            file_flac = os.path.join(dirpath, filename_flac)
            if os.path.exists(file_flac):
                # this should not happen
                print(f"{filename_flac} already exists.")
                continue

            print(f"Start transcoding {filename_wav}")

            # FFmpeg uses multi-threading by default
            returncode = subprocess.call(["ffmpeg", "-i", file_wav, file_flac],
                                         stdout=open(os.devnull, "w"),
                                         stderr=subprocess.STDOUT)
            if returncode == 0:
                print(
                    f"Transcode {filename_wav} successfully, delete this source file"
                )
                os.remove(file_wav)
            else:
                print(f"Failed to transcode {filename_wav}")
                sys.exit(1)
