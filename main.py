import argparse
import logging
from pathlib import Path
import itertools
from functools import partial
import multiprocessing

from dvtag import get_rjid, tag
from utils import wav_to_flac, wav_to_mp3

logging.basicConfig(level=logging.INFO,
                    format='%(asctime)s - %(levelname)s - %(message)s',
                    datefmt='%Y-%m-%d %a %H:%M:%S')


def start(w2f: bool, w2m: bool, dirpath: Path):
    if w2f:
        wav_to_flac(dirpath)
    if w2m:
        wav_to_mp3(dirpath)
    tag(dirpath)

def get_rj_paths(dirpath: Path, paths: [Path]):
    if get_rjid(dirpath.name):
        paths.append(dirpath)
        # don't add any child paths due to data races
        return

    for file in dirpath.iterdir():
        if not file.is_dir():
            continue
        get_rj_paths(file, paths)


def main():
    parser = argparse.ArgumentParser(
        description='Doujin Voice Tagging Tool (tagging in place)')
    parser.add_argument('dirpath', type=str, help='a required directory path')
    parser.add_argument('-w2f',
                        default=False,
                        action=argparse.BooleanOptionalAction,
                        help='transcode all wav files to flac [LOSELESS]')
    parser.add_argument('-w2m',
                        default=False,
                        action=argparse.BooleanOptionalAction,
                        help='transcode all wav files to mp3')
    parser.add_argument('-t',
                        type=int,
                        default=8,
                        help='number of threads')

    args = parser.parse_args()
    path = Path(args.dirpath).absolute()

    rjpaths = []
    get_rj_paths(path, rjpaths)
    rjpaths = list(set(rjpaths))

    fn = partial(start, args.w2f, args.w2m)
    with multiprocessing.Pool(args.t) as pool:
        pool.map(fn, rjpaths)

if __name__ == '__main__':
    main()
