import logging
from io import BytesIO
from pathlib import Path
from typing import List, Optional

from mutagen.flac import FLAC
from mutagen.id3 import (APIC, ID3, TALB, TDRC, TPE1, TPE2, TPOS, TRCK, TIT2, TCON, TXXX,
                         ID3NoHeaderError)
from natsort import os_sorted
from PIL.Image import Image

from dvtag.utils import (get_audio_paths_list, get_image, get_picture,
                         get_png_byte_arr, get_rjid, get_track_title)

from .doujinvoice import DoujinVoice


def tag_mp3s(mp3_paths: List[Path], dv: DoujinVoice, png_bytes_arr: BytesIO,
             disc_number: Optional[int]):
    tags = ID3()

    tags.add(TALB(text=[dv.work_name]))
    tags.add(TPE2(text=[dv.circle]))
    tags.add(TDRC(text=[dv.sale_date]))
    tags.add(TCON(text=dv.genres))
    if disc_number:
        tags.add(TPOS(text=[str(disc_number)]))
    if dv.seiyus:
        tags.add(TPE1(text=["/".join(dv.seiyus)]))
    tags.add(TXXX(text=[dv.rjid], desc="DVTAG_RJID"))
    tags.add(TXXX(text=[dv.age_restriction], desc="DVTAG_AGE_RESTRICTION"))
    tags.add(TXXX(text=[str(dv.dl_count)], desc="DVTAG_DL_COUNT"))
    tags.add(TXXX(text=dv.illustrators, desc="DVTAG_ILLUSTRATORS"))
    tags.add(
        APIC(mime="image/png",
             desc="Front Cover",
             data=png_bytes_arr.getvalue()))

    for trck, p in enumerate(os_sorted(mp3_paths), start=1):
        track_title = get_track_title(p.name)
        tags.add(TIT2(text=track_title))
        tags.add(TRCK(text=[str(trck)]))

        try:
            if ID3(p) != tags:
                tags.save(p, v1=0)
                logging.info(
                    f"Tagged <track: {trck}, disc: {disc_number}, name: {track_title}> to '{p.name}'"
                )
        except ID3NoHeaderError:
            tags.save(p, v1=0)
            logging.info(
                f"Tagged <track: {trck}, disc: {disc_number}, name: {track_title}> to '{p.name}'")
        tags.delall("TIT2")
        tags.delall("TRCK")


def tag_flacs(files: List[Path], dv: DoujinVoice, image: Image,
              png_bytes_arr: BytesIO, disc: Optional[int]):
    picture = get_picture(png_bytes_arr, image.width, image.height, image.mode)

    for trck, file in enumerate(os_sorted(files), start=1):
        tags = FLAC(file)
        tags.clear()
        tags.clear_pictures()

        track_title = get_track_title(file.name)
        tags.add_picture(picture)
        tags["title"] = [track_title]
        tags["album"] = [dv.work_name]
        tags["tracknumber"] = [str(trck)]
        tags["artist"] = dv.seiyus
        tags["albumartist"] = [dv.circle]
        tags["date"] = [dv.sale_date]
        tags["dvtag_rjid"] = [dv.rjid]
        tags["dvtag_age_restriction"] = [dv.age_restriction]
        tags["dvtag_dl_count"] = [str(dv.dl_count)]
        tags["dvtag_illustrators"] = dv.illustrators
        if disc:
            tags["discnumber"] = [str(disc)]

        if tags != FLAC(file):
            tags.save(file)
            logging.info(
                f"Tagged <track: {trck}, disc: {disc}, name: {track_title}> to '{file.name}'")


def tag(basepath: Path):
    rjid = get_rjid(basepath.name)
    dv = DoujinVoice(rjid)
    logging.info(f"[{rjid}] Ready to tag...")
    logging.info(f"Circle:   {dv.circle}")
    logging.info(f"Album:    {dv.work_name}")
    logging.info(f"Seiyu:    {','.join(dv.seiyus)}")
    logging.info(f"Illust:   {','.join(dv.illustrators)}")
    logging.info(f"Rating:   {dv.age_restriction}")
    logging.info(f"Genres:   {','.join(dv.genres)}")
    logging.info(f"Date:     {dv.sale_date}")
    logging.info(f"DL Count: {dv.dl_count}")

    image = get_image(dv.work_image)
    png_bytes_arr = get_png_byte_arr(image)

    flac_paths_list, mp3_paths_list = get_audio_paths_list(basepath)

    set_disc = False
    disc = None
    if len(flac_paths_list) + len(mp3_paths_list) > 1:
        set_disc = True
        disc = 1

    for flac_files in flac_paths_list:
        tag_flacs(flac_files, dv, image, png_bytes_arr, disc)
        if set_disc:
            disc += 1

    for mp3_files in mp3_paths_list:
        tag_mp3s(mp3_files, dv, png_bytes_arr, disc)
        if set_disc:
            disc += 1

    logging.info(f"[{rjid}] Done.")
