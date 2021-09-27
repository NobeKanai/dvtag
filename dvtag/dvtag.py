from io import BytesIO
from pathlib import Path
from typing import List, Optional

from mutagen.flac import FLAC
from mutagen.id3 import (APIC, ID3, TALB, TDRC, TPE1, TPE2, TPOS, TRCK,
                         ID3NoHeaderError)
from natsort import os_sorted
from PIL.Image import Image

from dvtag.utils import (get_audio_files, get_image, get_picture,
                         get_png_bytes_arr, get_rjid)

from .doujin_voice import DoujinVoice


def tag_mp3s(files: List[Path], dv: DoujinVoice, png_bytes_arr: BytesIO,
             disc: Optional[int]):
    tags = ID3()

    tags.add(TALB(text=[dv.work_name]))
    tags.add(TPE2(text=[dv.cicle]))
    tags.add(TDRC(text=[dv.sale_date]))
    if disc:
        tags.add(TPOS(text=[str(disc)]))
    if dv.seiyus:
        tags.add(TPE1(text=["/".join(dv.seiyus)]))
    tags.add(
        APIC(mime="image/png",
             desc="Front Cover",
             data=png_bytes_arr.getvalue()))

    for trck, file in enumerate(os_sorted(files), start=1):
        tags.add(TRCK(text=[str(trck)]))

        try:
            if ID3(file) != tags:
                tags.save(file, v1=0)
                print(f"tagged <track: {trck}, disc: {disc}> '{file.name}'")
        except ID3NoHeaderError:
            tags.save(file, v1=0)
            print(f"tagged <track: {trck}, disc: {disc}> to '{file.name}'")
        tags.delall("TRCK")


def tag_flacs(files: List[Path], dv: DoujinVoice, image: Image,
              png_bytes_arr: BytesIO, disc: Optional[int]):
    picture = get_picture(png_bytes_arr, image.width, image.height, image.mode)

    for trck, file in enumerate(os_sorted(files), start=1):
        tags = FLAC(file)
        tags.clear()
        tags.clear_pictures()

        tags.add_picture(picture)
        tags["album"] = [dv.work_name]
        tags["tracknumber"] = [str(trck)]
        tags["artist"] = dv.seiyus
        tags["albumartist"] = [dv.cicle]
        tags["date"] = [dv.sale_date]
        if disc:
            tags["discnumber"] = [str(disc)]

        if tags != FLAC(file):
            tags.save(file)
            print(f"tagged <track: {trck}, disc: {disc}> to '{file.name}'")


def tag(basepath: Path):
    rjid = get_rjid(basepath.name)
    dv = DoujinVoice(rjid)
    print(f"[{rjid}] Ready to tag")
    print(f"ALBUM:\t{dv.work_name}")
    print(f"SEIYU:\t{','.join(dv.seiyus)}")
    print(f"CICLE:\t{dv.cicle}")
    print(f"DATE:\t{dv.sale_date}")

    image = get_image(dv.work_image)
    img_bytes_arr = get_png_bytes_arr(image)

    flac_file_lists, mp3_file_lists = get_audio_files(basepath)

    set_disc = False
    disc = None
    if len(flac_file_lists) + len(mp3_file_lists) > 1:
        set_disc = True
        disc = 1

    for flac_files in flac_file_lists:
        tag_flacs(flac_files, dv, image, img_bytes_arr, disc)
        if set_disc:
            disc += 1

    for mp3_files in mp3_file_lists:
        tag_mp3s(mp3_files, dv, img_bytes_arr, disc)
        if set_disc:
            disc += 1

    print(f"[{rjid}] Done.")
