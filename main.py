import argparse
from pathlib import Path

from dvtag import get_rjid, tag
from utils import wav_to_flac, wav_to_mp3


def start(dir_path: Path, w2f: bool, w2m: bool):
    if get_rjid(dir_path.name):
        if w2f:
            wav_to_flac(dir_path)
        if w2m:
            wav_to_mp3(dir_path)
        tag(dir_path)
        return

    for dir in dir_path.iterdir():
        if not dir_path.is_dir():
            continue
        start(dir, w2f, w2m)


def main():
    parser = argparse.ArgumentParser(description='Doujin Voice Tagging Tool')
    parser.add_argument('dir_path', type=str, help='a required directory path')
    parser.add_argument('--w2f',
                        default=False,
                        action=argparse.BooleanOptionalAction,
                        help='transcode wav file to flac [LOSELESS]')
    parser.add_argument('--w2m',
                        default=False,
                        action=argparse.BooleanOptionalAction,
                        help='transcode wav file to mp3')

    args = parser.parse_args()
    path = Path(args.dir_path).absolute()

    start(path, args.w2f, args.w2m)


if __name__ == '__main__':
    main()
