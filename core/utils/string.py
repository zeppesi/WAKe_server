import random
import time
import urllib.parse as urlparse
from urllib.parse import urlencode


def generate_number_key(length=6):
    key = ''.join(str(random.randint(0, 9)) for _ in range(length))
    return key


def second_to_time(second, has_sign=True):
    sign = '+'
    if second < 0:
        second = second * -1
        sign = '-'
    if not has_sign:
        sign = ''
    converted = time.gmtime(second)
    if converted.tm_hour >= 1:
        return f"{sign}{time.strftime('%H시간 %M분', converted)}"
    else:
        return f"{sign}{time.strftime('%M분 %S초', converted)}"


def sign(num):
    sign = '+'
    if num < 0:
        sign = '-'
        num = num * -1
    return f"{sign}{num}"


def set_url_query_params(url: str, query_params: dict):
    url_parts = list(urlparse.urlparse(url))
    query = dict(urlparse.parse_qsl(url_parts[4]))
    query.update(query_params)
    url_parts[4] = urlencode(query)
    return urlparse.urlunparse(url_parts)


