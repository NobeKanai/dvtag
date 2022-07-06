import logging
import re
from html import unescape
from urllib.parse import quote

from dvtag.utils import create_request_session

session = create_request_session()


class DoujinVoice():
    def __init__(self, rjid: str) -> None:
        self.rjid = rjid

        self.dl_count = 0
        self.url = ""
        self.work_name = ""
        self.work_image = ""
        self.seiyus = []
        self.illustrators = []
        self.circle = ""
        self.sale_date = ""
        self.genres = []
        self.age_restriction = ""

        self._init_metadata()
        self._add_metadata()
        self._get_cover()

    def _add_metadata(self):
        html = session.get(self.url).text

        try:
            pattern = r'<th>声優</th>[\s\S]*?<td>[\s\S]*?(<a[\s\S]*?>[\s\S]*?)</td>'
            seiyu_list_html = re.search(pattern, html).group(1)

            pattern = r'<a[\s\S]*?>(.*?)<'
            for seiyu_html in re.finditer(pattern, seiyu_list_html):
                self.seiyus.append(unescape(seiyu_html.group(1)))
        except AttributeError as e:
            logging.error("Cannot get artists from {}: {}".format(
                self.rjid, e))

        try:
            pattern = r'<th>イラスト</th>[\s\S]*?<td>[\s\S]*?(<a[\s\S]*?>[\s\S]*?)</td>'
            illustrator_list_html = re.search(pattern, html).group(1)

            pattern = r'<a[\s\S]*?>(.*?)<'
            for illustrator_html in re.finditer(pattern, illustrator_list_html):
                self.illustrators.append(unescape(illustrator_html.group(1)))
        except AttributeError as e:
            logging.error("Cannot get illustrators from {}: {}".format(
                self.rjid, e))

        try:
            pattern = r'<th>ジャンル</th>[\s\S]*?<td>[\s\S]*?(<a[\s\S]*?>[\s\S]*?)</td>'
            genre_list_html = re.search(pattern, html).group(1)

            pattern = r'<a[\s\S]*?>(.*?)<'
            for genre_html in re.finditer(pattern, genre_list_html):
                self.genres.append(unescape(genre_html.group(1)))
        except AttributeError as e:
            logging.error("Cannot get genres from {}: {}".format(
                self.rjid, e))

        try:
            pattern = r"<th>サークル名</th>[\s\S]*?<a[\s\S]*?>(.*?)<"
            circle = re.search(pattern, html).group(1)
            self.circle = unescape(circle)

        except AttributeError as e:
            logging.error("Cannot get circle from {}: {}".format(self.rjid, e))

        try:
            pattern = r"<div class=\"work_genre\">[\s\S]*?<span class=\"icon_[\s\S+]*?\"[\s\S]*?>(.*?)<"
            age_restriction = re.search(pattern, html).group(1)
            self.age_restriction = unescape(age_restriction)

        except AttributeError as e:
            logging.error("Cannot get rating from {}: {}".format(self.rjid, e))

        # get sale date
        pattern = r'www\.dlsite\.com/maniax/new/=/year/([0-9]{4})/mon/([0-9]{2})/day/([0-9]{2})/'
        match = re.search(pattern, html)
        if match:
            self.sale_date = "{}-{}-{}".format(match.group(1), match.group(2),
                                               match.group(3))

    def _init_metadata(self):
        rsp = session.get(
            "https://www.dlsite.com/maniax/product/info/ajax?product_id=" +
            self.rjid)

        try:
            json_data = rsp.json()[self.rjid]

            self.dl_count = int(json_data["dl_count"])
            self.url = json_data["down_url"].replace("download/split",
                                                     "work").replace(
                                                         "download", "work")
            self.work_name = json_data["work_name"]
            self.work_image = "https:" + json_data["work_image"]

        except ValueError as e:
            logging.error(
                f"Cannot convert a response to json or convert dl_count to int with RJ-ID {self.rjid}: {e}",
            )
        except KeyError as e:
            logging.error(e)

    def _get_cover(self):
        """
        Tries to fetch a better cover
        """
        try:
            search_url = "https://chobit.cc/s/?f_category=vo&q_keyword=" + quote(
                self.work_name)

            headers = {'cookie': 'showr18=1'}
            search_result = session.get(search_url, headers=headers).text

            href = re.search(r'work-work-name.*?<a.*href=\"(.*?)\"',
                             search_result).group(1)

            detail_url = "https://chobit.cc" + href

            detail = session.get(detail_url, headers=headers).text

            self.work_image = re.search(r'albumart="(.*?)"', detail).group(1)
        except Exception as e:
            logging.warning(
                f"Cannot fetch cover from chobit for {self.rjid}: {e}")
