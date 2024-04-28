import json
import re
from html import unescape

from .doujinvoice import DoujinVoice
from .utils import create_request_session

session = create_request_session()

__all__ = ["scrape", "ParsingError"]


class ParsingError(Exception):
    """Exception raised when the parsing metadata from web."""

    def __init__(self, message: str, workno: str):
        self.workno = workno
        super().__init__(f"{message} for {workno}")


def scrape(workno: str) -> DoujinVoice:
    url = f"https://www.dlsite.com/maniax/work/=/product_id/{workno}.html"
    html = session.get(url).text  # TODO check response code

    if m := re.search(r'data-product-name="(.+)"\s*data-maker-name="(.+)"', html):
        name = m.group(1)
        circle = m.group(2)
    else:
        raise ParsingError(f"no work name found", workno)

    if m := re.search(r"\"og:image\"[\s\S]*?content=\"(.+?)\"", html):
        image_url = m.group(1)
    else:
        raise ParsingError(f"no cover image url found", workno)

    seiyus: list[str] = []
    if m := re.search(r"<th>声優</th>[\s\S]*?<td>[\s\S]*?(<a[\s\S]*?>[\s\S]*?)</td>", html):
        seiyu_list_html = m.group(1)
        for seiyu_html in re.finditer(r"<a[\s\S]*?>(.+?)<", seiyu_list_html):
            seiyus.append(unescape(seiyu_html.group(1)))

    genres = [unescape(m[1]) for m in re.finditer(r'work\.genre">(.+)\</a>', html)]

    if m := re.search(r"www\.dlsite\.com/.*?/new/=/year/([0-9]{4})/mon/([0-9]{2})/day/([0-9]{2})/", html):
        sale_date = "{}-{}-{}".format(m.group(1), m.group(2), m.group(3))
    else:
        raise ParsingError(f"no sale date found", workno)

    # try extracting more accurate information from chobit
    chobit_api = f"https://chobit.cc/api/v1/dlsite/embed?workno={workno}"
    res = session.get(chobit_api).text

    try:
        data = json.loads(res[9:-1])
        if data["count"] and (work := data["works"][0])["file_type"] == "audio":
            image_url = work["thumb"].replace("media.dlsite.com/chobit", "file.chobit.cc", 1)
            # we may get a shorter, yet more accurate article title (with no promotion)
            if work["work_name"] in name:
                name = work["work_name"]

    except Exception as e:
        raise ParsingError("unable to extract metadata from chobit", workno) from e

    return DoujinVoice(
        id=workno, name=name, image_url=image_url, seiyus=seiyus, circle=circle, genres=genres, sale_date=sale_date
    )
