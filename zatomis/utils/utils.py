from typing import Dict
import json
import re

from zatomis.const import PAGE_SIZE, ARG_SEP_SYMBOL, DATA_SEP_SYMBOL, LISTEN_PORTNUM, METHOD_ALIASES, RID_REGEX, \
    BANNED_SYMBOLS


def is_json_valid(json_string):
    try:
        json.loads(json_string)
        return True
    except json.JSONDecodeError as e:
        return False


def check_format(packet: Dict):
    r = "decoded" in packet and "portnum" in packet['decoded'] and "payload" in packet['decoded'] and "from" in packet
    if not r:
        return False

    data: list[str] = packet['decoded']['payload'].decode('utf-8').split(ARG_SEP_SYMBOL)
    if len(data) != 4 or not check_rid_regex(data[0]) or not data[1].isdigit() or not data[2].isdigit():
        return False

    return int(data[2]) >= int(data[1]) > 0 and int(data[2]) > 0


def check_portnum(packet: Dict):
    return "decoded" in packet and "portnum" in packet['decoded'] and packet['decoded']['portnum'] == LISTEN_PORTNUM


def check_rid_regex(r_id: str):
    return re.match(RID_REGEX, r_id)


def parse_packet(data: str):
    #if "decoded" not in packet or "portnum" not in packet['decoded'] or "text" not in packet['decoded']:
    #    raise Exception("Пакет не содержит необходимых ключей")

    data = data.split(DATA_SEP_SYMBOL)
    if len(data) != 4:
        raise Exception("Число аргументов пакета не соответствует ожидаемому")

    method_id, res_id, route, req_body = data
    method_id = int(method_id)
    method = METHOD_ALIASES[method_id]
    link = f"{res_id}/{route}"
    req_body = json.loads(req_body) if is_json_valid(req_body) else req_body

    return method_id, method, link, req_body


def parse_sender(packet: Dict):
    if "from" not in packet:
        raise Exception("Пакет не содержит отправителя")

    return packet["from"]


def form_response(status: int, data: str):
    return f"{status}{DATA_SEP_SYMBOL}{data}"


def inject_rid(r_id, data):
    if isinstance(data, str):
        return f"{r_id}{ARG_SEP_SYMBOL}{data}"
    elif isinstance(data, list):
        rid_pages = []
        for page in data:
            rid_pages.append(f"{r_id}{ARG_SEP_SYMBOL}{page}")
        return rid_pages
    else:
        raise Exception("Неверный тип ввода для включения rid")
