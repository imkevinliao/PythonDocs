import csv
import json
import os.path
import random
import re
import string
import time
from dataclasses import dataclass

import requests
import urllib3


@dataclass
class Dict:
    json_src: str = ""
    json_dst: str = ""


def random_string(length_of_string=16):
    random.seed(time.time())
    r_str = ''.join(random.choices(string.ascii_uppercase + string.digits, k=length_of_string))
    return r_str


def set_dict(src, dst):
    d = Dict()
    d.json_src = src
    d.json_dst = dst
    return vars(d)


def download_json(url: str):
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) "
                      "Chrome/58.0.3029.110 Safari/537.3"
    }
    html = {}
    try:
        urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)
        response = requests.get(url, headers=headers, verify=False, timeout=5)
        html = response.json()
    except Exception as e:
        print(f"download_json error {e}")
    return html


def save_json(dst, data):
    with open(dst, 'w+', encoding='utf8') as f:
        json.dump(data, f, ensure_ascii=False, indent=4)


def clear_text(str_in: str):
    #  常见中文字符 '，。“”‘’！？【】《》；：·'
    reg = rf'[\w\s\u3400-\u4DBF\u4E00-\u9FFF\uF900-\uFAFF{re.escape(string.punctuation)}，。“”‘’！？【】《》；：·]+'
    result = re.findall(reg, str_in, re.UNICODE)
    if result:
        str_out = "".join(result)
    else:
        str_out = str_in
    return str_out


def read_dict_from_csv(path):
    with open(path, 'r', encoding='utf_8_sig') as f:
        reader = csv.DictReader(f)
        dicts = list(reader)
    return dicts


def write_dicts_to_csv(path: str, data: list, mode='a+'):
    with open(path, mode, encoding='utf_8_sig', newline='') as f:
        fields = list(data[0].keys())
        writer = csv.DictWriter(f, fields)
        file_size = f.tell()
        if file_size == 0:
            writer.writeheader()
        writer.writerows(data)


def write_dict_to_csv(path: str, data: dict, mode='a+'):
    with open(path, mode, encoding='utf_8_sig', newline='') as f:
        fields = list(data.keys())
        writer = csv.DictWriter(f, fields)
        file_size = f.tell()
        if file_size == 0:
            writer.writeheader()
        writer.writerow(data)


def check_csv(path, url):
    if not os.path.exists(path):
        return False
    datas = read_dict_from_csv(path)
    check_urls = []
    check_status = False
    for data in datas:
        dict_data = dict(data)
        src = dict_data.get("json_src")
        check_urls.append(src)
    for check in check_urls:
        if check == url:
            check_status = True
            break
    return check_status


def run(json_url):
    json_dir = os.path.join("./", "json")
    index_csv = "index.csv"
    if not os.path.exists(json_dir):
        os.mkdir(json_dir)
    status = check_csv(index_csv, json_url)
    if status is True:
        print(f"{json_url} has exist")
        return
    html = download_json(json_url)
    dst = os.path.join(json_dir, f"{random_string()}.json")
    save_json(dst, html)
    user_dict = set_dict(src=json_url, dst=dst)
    write_dict_to_csv(index_csv, user_dict)


if __name__ == '__main__':
    json_src = r"https://jt12.de/SYV2_4/2024/03/20/12/34/49/171090928965fa6769796a5.json"
    run(json_src)