__all__ = [
    "tag",
]


import logging
from io import BytesIO
from pathlib import Path
from typing import List, Optional

from mutagen.flac import FLAC
from mutagen.id3 import APIC, ID3, TALB, TCON, TDRC, TIT2, TPE1, TPE2, TPOS, TRCK, ID3NoHeaderError
from mutagen.mp4 import MP4, MP4Cover
from natsort import os_sorted
from PIL.Image import Image

from ._doujin_voice import DoujinVoice
from ._scrape import ParsingError, scrape
from ._utils import extract_titles, get_audio_paths_list, get_image, get_picture, get_png_byte_arr


def tag_mp3s(mp3_paths: List[Path], dv: DoujinVoice, png_bytes_arr: BytesIO, disc_number: Optional[int]):
    tags = ID3()

    tags.add(TALB(text=[dv.name]))
    tags.add(TPE2(text=[dv.circle]))
    tags.add(TDRC(text=[dv.sale_date]))
    if dv.genres:
        tags.add(TCON(text=[";".join(dv.genres)]))
    if disc_number:
        tags.add(TPOS(text=[str(disc_number)]))
    if dv.seiyus:
        tags.add(TPE1(text=dv.seiyus))
    tags.add(APIC(mime="image/png", desc="Front Cover", data=png_bytes_arr.getvalue()))

    sorted = list(os_sorted(mp3_paths))
    titles = extract_titles(sorted_stems=[f.stem for f in sorted])

    for trck, title, p in zip(range(1, len(sorted) + 1), titles, sorted):
        tags.add(TIT2(text=[title]))
        tags.add(TRCK(text=[str(trck)]))

        try:
            if ID3(p) != tags:
                tags.save(p, v1=0)
                logging.info(f"Tagged <track: {trck}, disc: {disc_number}, title: '{title}'> to '{p.name}'")
        except ID3NoHeaderError:
            tags.save(p, v1=0)
            logging.info(f"Tagged <track: {trck}, disc: {disc_number}, title: '{title}'> to '{p.name}'")


def tag_mp4s(files: List[Path], dv: DoujinVoice, png_bytes_arr: BytesIO, disc: Optional[int]):
    cover = MP4Cover(png_bytes_arr.getvalue(), MP4Cover.FORMAT_PNG)

    sorted = list(os_sorted(files))
    titles = extract_titles(sorted_stems=[f.stem for f in sorted])

    for trck, title, p in zip(range(1, len(sorted) + 1), titles, sorted):
        tags = MP4(p)
        tags.clear()

        tags["\xa9alb"] = [dv.name]
        tags["\xa9day"] = [dv.sale_date]
        tags["\xa9nam"] = [title]
        tags["aART"] = [dv.circle]
        tags["covr"] = [cover]
        tags["\xa9ART"] = [";".join(dv.seiyus)]
        tags["\xa9gen"] = [";".join(dv.genres)]
        tags["trkn"] = [(trck, 0)]
        if disc:
            tags["disk"] = [(disc, 0)]

        if tags != MP4(p):
            tags.save(p)
            logging.info(f"Tagged <track: {trck}, disc: {disc}, title: '{title}'> to '{p.name}'")


def tag_flacs(files: List[Path], dv: DoujinVoice, image: Image, png_bytes_arr: BytesIO, disc: Optional[int]):
    picture = get_picture(png_bytes_arr, image.width, image.height, image.mode)

    sorted = list(os_sorted(files))
    titles = extract_titles(sorted_stems=[f.stem for f in sorted])

    for trck, title, p in zip(range(1, len(sorted) + 1), titles, sorted):
        tags = FLAC(p)
        tags.clear()
        tags.clear_pictures()

        tags.add_picture(picture)
        tags["album"] = [dv.name]
        tags["albumartist"] = [dv.circle]
        tags["date"] = [dv.sale_date]
        tags["title"] = [title]
        tags["tracknumber"] = [str(trck)]
        if dv.genres:
            tags["genre"] = dv.genres
        if dv.seiyus:
            tags["artist"] = dv.seiyus
        if disc:
            tags["discnumber"] = [str(disc)]

        if tags != FLAC(p):
            tags.save(p)
            logging.info(f"Tagged <track: {trck}, disc: {disc}>, title: '{title}'>  to '{p.name}'")


def tag(basepath: Path, workno: str):
    flac_paths_list, m4a_paths_list, mp3_paths_list = get_audio_paths_list(basepath)
    if not flac_paths_list and not m4a_paths_list and not mp3_paths_list:
        return

    try:
        dv = scrape(workno)
    except ParsingError:
        raise
    except Exception as e:
        logging.exception(f"An error occurred during scraping metadata for {workno}: {e}.")
        return

    logging.info(f"[{workno}] Ready to tag...")
    logging.info(f" Circle: {dv.circle}")
    logging.info(f" Album:  {dv.name}")
    logging.info(f" Seiyu:  {','.join(dv.seiyus)}")
    logging.info(f" Genre:  {','.join(dv.genres)}")
    logging.info(f" Date:   {dv.sale_date}")

    image = get_image(dv.image_url)
    png_bytes_arr = get_png_byte_arr(image)

    disc = None
    if len(flac_paths_list) + len(m4a_paths_list) + len(mp3_paths_list) > 1:
        disc = 1

    for flac_files in flac_paths_list:
        tag_flacs(flac_files, dv, image, png_bytes_arr, disc)
        if disc:
            disc += 1

    for m4a_files in m4a_paths_list:
        tag_mp4s(m4a_files, dv, png_bytes_arr, disc)
        if disc:
            disc += 1

    for mp3_files in mp3_paths_list:
        tag_mp3s(mp3_files, dv, png_bytes_arr, disc)
        if disc:
            disc += 1

    logging.info(f"[{workno}] Done.")
