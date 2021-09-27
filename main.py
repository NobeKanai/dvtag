import argparse
from pathlib import Path

from dvtag import get_rjid, tag
from w2f import wav_to_flac


def start_tagging(dir_path: Path):
    if get_rjid(dir_path.name):
        tag(dir_path)
        return

    for dir in dir_path.iterdir():
        if not dir_path.is_dir():
            continue
        start_tagging(dir)


def main():
    parser = argparse.ArgumentParser(description='Doujin Voice Tagging Tool')
    parser.add_argument('dir_path', type=str, help='A required directory path')
    parser.add_argument('--w2f',
                        default=False,
                        action=argparse.BooleanOptionalAction,
                        help='Converting wav file to flac [LOSELESS]')

    args = parser.parse_args()
    path = Path(args.dir_path).absolute()

    if args.w2f:
        wav_to_flac(path)
    start_tagging(path)


if __name__ == '__main__':
    main()
