import argparse
from pathlib import Path

from dvtag import get_rjid, tag
from w2f import wav_to_flac


def start(dir_path: Path, w2f: bool):
    if get_rjid(dir_path.name):
        if w2f:
            wav_to_flac(dir_path)
        tag(dir_path)
        return

    for dir in dir_path.iterdir():
        if not dir_path.is_dir():
            continue
        start(dir, w2f)


def main():
    parser = argparse.ArgumentParser(description='Doujin Voice Tagging Tool')
    parser.add_argument('dir_path', type=str, help='a required directory path')
    parser.add_argument('--w2f',
                        default=False,
                        action=argparse.BooleanOptionalAction,
                        help='transcode wav file to flac [LOSELESS]')

    args = parser.parse_args()
    path = Path(args.dir_path).absolute()

    start(path, args.w2f)


if __name__ == '__main__':
    main()
