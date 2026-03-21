import math
from typing import Dict

from zatomis.const import PAGE_SIZE, ARG_SEP_SYMBOL, REQUEST_WAIT_TIME


def paginate(data: str):

    byte_c = 0
    pages_sep = [0]
    for symbol_i in range(len(data)):
        current_symbol_size = len(data[symbol_i].encode('utf-8'))

        if byte_c + current_symbol_size > PAGE_SIZE:
            pages_sep.append(symbol_i)
            byte_c = 0

        byte_c += current_symbol_size

    pages_num = len(pages_sep)

    result_pages = []
    for i in range(len(pages_sep)):
        start_idx = pages_sep[i]
        if i + 1 < len(pages_sep):
            end_idx = pages_sep[i + 1]
        else:
            end_idx = len(data)

        page_content = data[start_idx:end_idx]

        current_page_number = i + 1
        formatted_page = f"{current_page_number}{ARG_SEP_SYMBOL}{pages_num}{ARG_SEP_SYMBOL}{page_content}"
        result_pages.append(formatted_page)

    return result_pages


def parse_paged_request(packet: Dict):
    data = str(packet['decoded']['payload'], encoding='utf-8').split(ARG_SEP_SYMBOL)
    r_id, page, num_pages, data_page = data

    return r_id, int(page), int(num_pages), data_page


class PagedData:
    def __init__(self, num_pages: int):
        self.expecting_pages = list(range(1, num_pages + 1))
        self.data: list[str] = [None] * num_pages
        self.time_left = REQUEST_WAIT_TIME

    def insert_data(self, page, data):
        self.expecting_pages.remove(page)
        self.data[page-1] = data

    def get_request(self):
        if len(self.expecting_pages) != 0:
            return None

        return "".join(self.data)
