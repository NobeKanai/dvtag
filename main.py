import argparse
from pathlib import Path

from dvtag import get_rjid, tag


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

    args = parser.parse_args()
    start_tagging(Path(args.dir_path).absolute())


if __name__ == '__main__':
    main()
