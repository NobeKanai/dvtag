__all__ = [
    "ParsingError",
    "scrape",
]


import json
import re
from datetime import date
from html.parser import HTMLParser
from urllib.parse import urljoin

from ._doujin_voice import DoujinVoice
from ._utils import create_request_session

_session = create_request_session()


class ParsingError(Exception):
    """Exception raised when the parsing metadata from web."""

    def __init__(self, message: str, workno: str):
        self.workno = workno
        super().__init__(f"{message} for {workno}")


# ---------------------------------------------------------------------------
# Minimal HTML DOM parser
# ---------------------------------------------------------------------------

_VOID_ELEMENTS = {
    "area",
    "base",
    "br",
    "col",
    "embed",
    "hr",
    "img",
    "input",
    "link",
    "meta",
    "param",
    "source",
    "track",
    "wbr",
}


class _Node:
    def __init__(self, tag: str, attrs=()):
        self.tag = tag
        self.attrs = dict(attrs)
        self.children = []

    @property
    def text(self) -> str:
        return "".join(child if isinstance(child, str) else child.text for child in self.children)

    def iter(self, tag=None):
        if tag is None or self.tag == tag:
            yield self

        for child in self.children:
            if isinstance(child, _Node):
                yield from child.iter(tag)


class _HTMLTreeParser(HTMLParser):
    def __init__(self):
        super().__init__(convert_charrefs=True)
        self.root = _Node("document")
        self.stack = [self.root]

    def handle_starttag(self, tag, attrs):
        if tag == "br":
            self.stack[-1].children.append(" ")
            return

        node = _Node(tag, attrs)
        self.stack[-1].children.append(node)

        if tag not in _VOID_ELEMENTS:
            self.stack.append(node)

    def handle_startendtag(self, tag, attrs):
        self.handle_starttag(tag, attrs)

        if tag not in _VOID_ELEMENTS and self.stack[-1].tag == tag:
            self.stack.pop()

    def handle_endtag(self, tag):
        for i in range(len(self.stack) - 1, 0, -1):
            if self.stack[i].tag == tag:
                del self.stack[i:]
                break

    def handle_data(self, data):
        if self.stack[-1].tag not in {"script", "style"}:
            self.stack[-1].children.append(data)


def _has_class(node, class_name: str) -> bool:
    return class_name in (node.attrs.get("class") or "").split()


def _find_all(root, *, tag=None, class_name=None):
    for node in root.iter(tag):
        if class_name is not None and not _has_class(node, class_name):
            continue

        yield node


def _find_first(root, *, tag=None, element_id=None, class_name=None):
    for node in _find_all(root, tag=tag, class_name=class_name):
        if element_id is not None and node.attrs.get("id") != element_id:
            continue

        return node

    return None


def _text(node) -> str:
    if node is None:
        return ""

    return re.sub(r"\s+", " ", node.text).strip()


def _link_texts(node) -> list[str]:
    if node is None:
        return []

    return [text for anchor in node.iter("a") if (text := _text(anchor))]


# ---------------------------------------------------------------------------
# DLsite metadata extraction
# ---------------------------------------------------------------------------


def _get_info_rows(root) -> dict:
    """Extract product information from c-productInfo__item elements."""

    rows = {}

    for item in _find_all(
        root,
        tag="div",
        class_name="c-productInfo__item",
    ):
        key = _find_first(item, tag="dt")
        value = _find_first(item, tag="dd")

        if key and value:
            rows[_text(key).rstrip(":：")] = value

    return rows


def _get_row(rows: dict, *labels):
    for label in labels:
        if label in rows:
            return rows[label]

    return None


def _parse_date(value: str):
    """Parse dates in Japanese, ISO, or legacy DLsite URL format."""

    m = re.search(
        r"(?<!\d)(\d{4})\s*(?:年|[./-])\s*" r"(\d{1,2})\s*(?:月|[./-])\s*(\d{1,2})\s*日?",
        value,
    )

    if not m:
        m = re.search(
            r"/year/(\d{4})/mon/(\d{1,2})/day/(\d{1,2})(?:/|$)",
            value,
        )

    if not m:
        return None

    try:
        return date(*(int(part) for part in m.groups())).isoformat()
    except ValueError:
        return None


def _get_200(url):
    rsp = _session.get(url)
    if rsp.status_code != 200:
        rsp.raise_for_status()
    return rsp


def scrape(workno: str) -> DoujinVoice:
    url = f"https://www.dlsite.com/maniax/work/=/product_id/{workno}.html"
    html = _get_200(url).text

    # Parse HTML once and reuse the resulting tree.
    parser = _HTMLTreeParser()
    parser.feed(html)
    parser.close()
    root = parser.root

    # -----------------------------------------------------------------------
    # Work metadata: GA4 event div
    # -----------------------------------------------------------------------

    work_meta = next(
        (
            node
            for node in _find_all(root, tag="div")
            if node.attrs.get("data-product_id") == workno and node.attrs.get("data-work_name")
        ),
        None,
    )

    if work_meta is None:
        error_box = next(
            (node for node in root.iter() if _has_class(node, "error_box_work")),
            None,
        )

        if error_box:
            error_title = _find_first(
                error_box,
                tag="p",
                class_name="title_text",
            )
            raise ParsingError(
                _text(error_title) or _text(error_box) or "work unavailable",
                workno,
            )

    # data-work_name is the primary source.
    name = work_meta.attrs.get("data-work_name", "").strip() if work_meta else ""

    # Fallback for pages without the GA4 metadata div.
    if not name:
        name = _text(_find_first(root, element_id="work_name"))

    if not name:
        raise ParsingError("no work name found", workno)

    # -----------------------------------------------------------------------
    # Circle name
    # -----------------------------------------------------------------------

    maker_id = work_meta.attrs.get("data-maker_id") if work_meta else None

    # Prefer the circle link matching data-maker_id.
    maker_link = next(
        (node for node in root.iter("a") if maker_id and f"maker_id/{maker_id}.html" in node.attrs.get("href", "")),
        None,
    )

    # Fallback to the current page's maker-name element.
    if maker_link is None:
        maker_link = _find_first(
            root,
            tag="a",
            class_name="c-productInfo__makerName",
        )

    circle = _text(maker_link)

    if not circle:
        circle = next(
            (node.attrs["data-maker-name"] for node in root.iter() if node.attrs.get("data-maker-name")),
            "",
        )

    if not circle:
        raise ParsingError("no maker name found", workno)

    # -----------------------------------------------------------------------
    # Cover image
    # -----------------------------------------------------------------------

    image_meta = next(
        (node for node in root.iter("meta") if node.attrs.get("property", "").lower() == "og:image"),
        None,
    )

    image_src = image_meta.attrs.get("content", "") if image_meta else ""

    if not image_src:
        raise ParsingError("no cover image url found", workno)

    image_url = urljoin(url, image_src)

    # -----------------------------------------------------------------------
    # Product information
    # -----------------------------------------------------------------------

    rows = _get_info_rows(root)

    # Voice actors
    seiyu_cell = _get_row(rows, "声優")
    seiyus = _link_texts(seiyu_cell)

    if not seiyus and (seiyu_text := _text(seiyu_cell)):
        seiyus = [seiyu_text]

    # Genres
    genre_cell = _get_row(rows, "ジャンル")
    genres = _link_texts(genre_cell)

    # Sale date
    sale_date_cell = _get_row(rows, "販売日")

    sale_date = _parse_date(_text(sale_date_cell))

    # If the date is only present in the link URL.
    if not sale_date and sale_date_cell:
        for anchor in sale_date_cell.iter("a"):
            sale_date = _parse_date(anchor.attrs.get("href", ""))
            if sale_date:
                break

    # Legacy fallback.
    if not sale_date:
        m = re.search(
            r"/new/=/year/(\d{4})/mon/(\d{2})/day/(\d{2})/",
            html,
        )
        if m:
            try:
                sale_date = date(*(int(part) for part in m.groups())).isoformat()
            except ValueError:
                pass

    if not sale_date:
        raise ParsingError("no sale date found", workno)

    # -----------------------------------------------------------------------
    # Chobit metadata
    # -----------------------------------------------------------------------

    chobit_api = f"https://chobit.cc/api/v1/dlsite/embed?workno={workno}"
    res = _get_200(chobit_api).text

    try:
        data = json.loads(res)
        if data["count"]:
            work = data["works"][0]
            if work["file_type"] == "audio":
                image_url = work["thumb"].replace("media.dlsite.com/chobit", "file.chobit.cc", 1)

            # We may get a shorter, yet more accurate article title (with no promotion)
            if work["work_name"] in name:
                name = work["work_name"]

    except Exception as e:
        raise ParsingError("unable to extract metadata from chobit", workno) from e

    return DoujinVoice(
        id=workno, name=name, image_url=image_url, seiyus=seiyus, circle=circle, genres=genres, sale_date=sale_date
    )
