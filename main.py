import argparse
import logging
from pathlib import Path

from dvtag import get_rjid, tag
from utils import wav_to_flac, wav_to_mp3

logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s", datefmt="%Y-%m-%d %a %H:%M:%S"
)


def start(dirpath: Path, w2f: bool, w2m: bool):
    if get_rjid(dirpath.name):
        if w2f:
            wav_to_flac(dirpath)
        if w2m:
            wav_to_mp3(dirpath)
        tag(dirpath)
        return

    for file in dirpath.iterdir():
        if not file.is_dir():
            continue
        start(file, w2f, w2m)


def main():
    parser = argparse.ArgumentParser(description="Doujin Voice Tagging Tool (tagging in place)")
    parser.add_argument("dirpath", type=str, help="a required directory path")
    parser.add_argument(
        "-w2f", default=False, action=argparse.BooleanOptionalAction, help="transcode all wav files to flac [LOSELESS]"
    )
    parser.add_argument(
        "-w2m", default=False, action=argparse.BooleanOptionalAction, help="transcode all wav files to mp3"
    )

    args = parser.parse_args()
    path = Path(args.dirpath).absolute()

    start(path, args.w2f, args.w2m)


if __name__ == "__main__":
    main()
