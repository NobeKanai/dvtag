from io import BytesIO
import logging
from pathlib import Path
from typing import List, Optional, Tuple

from PIL.Image import Image
import mutagen
from mutagen.flac import FLAC
from mutagen.id3 import APIC, ID3, ID3NoHeaderError, TALB, TDRC, TPE1, TPE2, TPOS, TRCK, TIT2
from mutagen.mp4 import MP4
from natsort import os_sorted

from dvtag.utils import (
    get_audio_paths_list,
    get_image,
    get_picture,
    get_png_byte_arr,
    get_rjid,
)

from .doujinvoice import DoujinVoice


def tag_mp3s(mp3_paths: List[Path], dv: DoujinVoice, png_bytes_arr: BytesIO, disc_number: Optional[int]):
    tags = ID3()

    tags.add(TALB(text=[dv.work_name]))
    tags.add(TPE2(text=[dv.circle]))
    tags.add(TDRC(text=[dv.sale_date]))
    if disc_number:
        tags.add(TPOS(text=[str(disc_number)]))
    if dv.seiyus:
        tags.add(TPE1(text=["/".join(dv.seiyus)]))
    tags.add(APIC(mime="image/png", desc="Front Cover", data=png_bytes_arr.getvalue()))

    for trck, p in enumerate(os_sorted(mp3_paths), start=1):
        tags.add(TRCK(text=[str(trck)]))
        tags.add(TIT2(text=[p.stem]))

        try:
            if ID3(p) != tags:
                tags.save(p, v1=0)
                logging.info(f"Tagged <track: {trck}, disc: {disc_number}> to '{p.name}'")
        except ID3NoHeaderError:
            tags.save(p, v1=0)
            logging.info(f"Tagged <track: {trck}, disc: {disc_number}> to '{p.name}'")
        tags.delall("TRCK")


def tag_flacs(files: List[Path], dv: DoujinVoice, image: Image, png_bytes_arr: BytesIO, disc: Optional[int]):
    picture = get_picture(png_bytes_arr, image.width, image.height, image.mode)

    for trck, file in enumerate(os_sorted(files), start=1):
        tags = FLAC(file)
        tags.clear()
        tags.clear_pictures()

        tags.add_picture(picture)
        tags["album"] = [dv.work_name]
        tags["tracknumber"] = [str(trck)]
        tags["title"] = [file.stem]
        tags["artist"] = dv.seiyus
        tags["albumartist"] = [dv.circle]
        tags["date"] = [dv.sale_date]
        if disc:
            tags["discnumber"] = [str(disc)]

        if tags != FLAC(file):
            tags.save(file)
            logging.info(f"Tagged <track: {trck}, disc: {disc}> to '{file.name}'")


def tag_mp4s(files: List[Path], dv: DoujinVoice, disc: Optional[int]):
    for trck, file in enumerate(os_sorted(files), start=1):
        tags = mutagen.File(file, easy=True)
        
        tags["album"] = [dv.work_name]
        tags["tracknumber"] = [str(trck)]
        tags["title"] = [file.stem]
        tags["artist"] = dv.seiyus
        tags["albumartist"] = [dv.circle]
        tags["date"] = [dv.sale_date]
        if disc:
            tags["discnumber"] = [str(disc)]

        if tags != mutagen.File(file, easy=True):
            tags.save(file)
            logging.info(f"Tagged <track: {trck}, disc: {disc}> to '{file.name}'")


def tag(basepath: Path):
    rjid = get_rjid(basepath.name)
    dv = DoujinVoice(rjid)
    logging.info(f"[{rjid}] Ready to tag...")
    logging.info(f"Circle: {dv.circle}")
    logging.info(f"Album:  {dv.work_name}")
    logging.info(f"Seiyu:  {','.join(dv.seiyus)}")
    logging.info(f"Date:   {dv.sale_date}")

    image = get_image(dv.work_image)
    png_bytes_arr = get_png_byte_arr(image)

    flac_paths_list, mp3_paths_list, mp4_paths_list = get_audio_paths_list(basepath)

    set_audioDisc = False
    set_videoDisc = False
    audioDisc = None
    videoDisc = None
    if len(flac_paths_list) + len(mp3_paths_list) > 1:
        set_audioDisc = True
        audioDisc = 1

    if len(mp4_paths_list) > 1:
        set_videoDisc = True
        videoDisc = 1

    for flac_files in flac_paths_list:
        tag_flacs(flac_files, dv, image, png_bytes_arr, audioDisc)
        if set_audioDisc:
            audioDisc += 1

    for mp3_files in mp3_paths_list:
        tag_mp3s(mp3_files, dv, png_bytes_arr, audioDisc)
        if set_audioDisc:
            audioDisc += 1

    for mp4_files in mp4_paths_list:
        tag_mp4s(mp4_files, dv, videoDisc)
        if set_videoDisc:
            videoDisc += 1

    logging.info(f"[{rjid}] Done.")
