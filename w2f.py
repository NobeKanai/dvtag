import os
from pathlib import Path

from pydub import AudioSegment


def wav_to_flac(dir: Path):
    for dirpath, _, filenames in os.walk(dir):
        for filename in filenames:
            if not filename.endswith(".wav"):
                continue

            file_wav = os.path.join(dirpath, filename)
            file_flac = file_wav[:-4] + ".flac"
            if os.path.exists(file_flac):
                # this should not happen
                print(f"{file_flac} already exists.")
                continue

            print(f"Start converting {filename}")

            song = AudioSegment.from_wav(file_wav)
            # FLAC is lossless. The bitrate doesn't matter
            song.export(file_flac, format="flac")
            del song

            os.remove(file_wav)
