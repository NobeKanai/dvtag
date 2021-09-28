import io
import os
import re
from io import BytesIO
from pathlib import Path
from typing import List, Optional, Tuple

import requests
from mutagen.flac import Picture
from mutagen.id3 import PictureType
from PIL import Image

re_rjid = re.compile(r"RJ[0-9]{6}", flags=re.IGNORECASE)


def _split(audio_files: List[Path]) -> List[List[Path]]:
    regexes = [
        r'^omake_?.*[0-9]{1,2}.*$',
        r'^.*ex[0-9]{1,2}.*$',
        r'^ex_.+$',
        r'^後日談.*$',
        r'^おまけ_?[0-9]{0,2}.*$',
        r'^反転おまけ_?[0-9]{1,2}.*$',
        r'^反転_?[0-9]{1,2}.*$',
        r'^20..年?[0-9]{1,2}月配信.*$',
        r'^.*特典.*$',
        r'^追加[0-9]{1,2}.*$',
        r'^opt[0-9]?.*',
        r'^#[0-9]+(-|ー)B',
        r'^#[0-9]+(-|ー)C',
        r'^ASMR_.*',
        r'^.+Bパート',
        r'^番外編',
    ]  # regex expressions must keep no collision with each other

    results = {}
    paths = [[]]
    for audio_file in audio_files:
        matched = False
        for regex_expr in regexes:
            if re.match(regex_expr, audio_file.stem, re.IGNORECASE):
                matched = True
                if results.get(regex_expr):
                    results[regex_expr].append(audio_file)
                else:
                    results[regex_expr] = [audio_file]
                break

        if not matched:
            paths[0].append(audio_file)

    for _, v in results.items():
        paths.append(v)

    return paths


def get_audio_files(
        basepath: Path) -> Tuple[List[List[Path]], List[List[Path]]]:
    """get audio files(Path) from base_path recursively

    Args:
        base_path (Path): base path

    Returns:
        Tuple[List[List[Path]], List[List[Path]]]: flac_file_lists, mp3_file_lists
    """
    flac_file_lists = []
    mp3_file_lists = []

    for dirpath, _, filenames in os.walk(basepath):
        mp3_files = []
        flac_files = []
        for filename in filenames:
            if filename.endswith(".flac"):
                flac_files.append(Path(os.path.join(dirpath, filename)))
            elif filename.endswith(".mp3"):
                mp3_files.append(Path(os.path.join(dirpath, filename)))

        if len(flac_files):
            flac_file_lists.extend(_split(flac_files))
        if len(mp3_files):
            mp3_file_lists.extend(_split(mp3_files))

    return flac_file_lists, mp3_file_lists


def get_rjid(name: str) -> Optional[str]:
    """get rjid from name

    Args:
        name (str): a string

    Returns:
        Optional[str]: return a string(upper case, like RJ123123) if found, otherwise return None
    """
    m = re_rjid.search(name)
    if m:
        return m.group().upper()
    return None


def get_image(url: str) -> Image.Image:
    cover_path = requests.get(url, stream=True).raw
    return Image.open(cover_path)


def get_png_bytes_arr(im: Image.Image) -> BytesIO:
    img_byte_arr = io.BytesIO()
    im.save(img_byte_arr, "png")
    return img_byte_arr


mode_to_bpp = {
    '1': 1,
    'L': 8,
    'P': 8,
    'RGB': 24,
    'RGBA': 32,
    'CMYK': 32,
    'YCbCr': 24,
    'I': 32,
    'F': 32
}


def get_picture(img_byte_arr: BytesIO, width: int, height: int,
                mode: str) -> Picture:
    picture = Picture()
    picture.mime = "image/png"
    picture.width = width
    picture.height = height
    picture.type = PictureType.COVER_FRONT

    picture.depth = mode_to_bpp[mode]
    picture.data = img_byte_arr.getvalue()

    return picture
