import argparse
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
    json_src: str = "none"
    json_dst: str = "none"
    json_comment: str = "none"


def random_string(length_of_string=16):
    random.seed(time.time())
    r_str = ''.join(random.choices(string.ascii_uppercase + string.digits, k=length_of_string))
    return r_str


def set_dict(src, dst, comment="none"):
    d = Dict()
    d.json_src = src
    d.json_dst = dst
    d.json_comment = comment
    return vars(d)


def download_json(url: str):
    print(f"download {url}")
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


def update_csv():
    my_path = Path()
    i_csv = my_path.index_csv
    j_dir = my_path.json_dir
    datas = read_dict_from_csv(i_csv)
    new_datas = []
    for data in datas:
        dict_data = dict(data)
        src = dict_data.get("json_src")
        dst = dict_data.get("json_dst")
        if dst == "" or dst is None or dst == "none":
            html = download_json(src)
            dst = os.path.join(j_dir, f"{random_string()}.json")
            save_json(dst, html)
            dict_data["json_dst"] = dst
        new_datas.append(dict_data)
    write_dicts_to_csv(i_csv, new_datas, mode="w")


def merge_json(filenames, output_filename):
    with open(output_filename, 'w', encoding='utf8') as output_file:
        output_file.write('[')  # 开始写入JSON 数组
        for j, filename in enumerate(filenames):
            with open(filename, 'r', encoding='utf8') as input_file:
                file_content = input_file.read().strip()
                # 移除文件内容开头的'[' 和结尾的 ']'
                if file_content.startswith('['):
                    file_content = file_content[1:]
                if file_content.endswith(']'):
                    file_content = file_content[:-1]
                # 如果不是第一个文件，在前面添加一个逗号
                if j != 0:
                    output_file.write(',')
                output_file.write(file_content)  # 写入文件的 JSON 内容
        output_file.write(']')  # 结束 JSON 数组


def generate_json():
    my_path = Path()
    j_dir = my_path.json_dir
    n_json = my_path.new_json
    files = list(os.listdir(j_dir))
    if files:
        filepaths = [os.path.join(j_dir, file) for file in files if file.endswith(".json")]
        merge_json(filepaths, n_json)


def run(json_url, comment="none"):
    my_path = Path()
    j_dir = my_path.json_dir
    i_csv = my_path.index_csv
    if not os.path.exists(j_dir):
        os.mkdir(j_dir)
    status = check_csv(i_csv, json_url)
    if status is True:
        print(f"{json_url} has exist")
        return
    html = download_json(json_url)
    dst = os.path.join(j_dir, f"{random_string()}.json")
    save_json(dst, html)
    user_dict = set_dict(src=json_url, dst=dst, comment=comment)
    write_dict_to_csv(i_csv, user_dict)
    generate_json()


class Path:
    json_dir = os.path.join("./", "ignore_json")
    index_csv = "ignore_index.csv"
    new_json = "ignore_merge.json"


class Clean(object):
    def __init__(self, src, dst):
        self.src_path = src
        self.dst_path = dst
        self._group = "group"
    
    @property
    def group(self):
        return self._group
    
    @group.setter
    def group(self, value):
        self._group = value
    
    def get(self):
        with open(self.src_path, 'r', encoding='utf8') as f:
            data = json.load(f)
        return data
    
    def save(self, data):
        with open(self.dst_path, 'w+', encoding='utf8') as f:
            json.dump(data, f, ensure_ascii=False, indent=4)
        return None
    
    def run(self):
        datas = self.get()
        new_datas = []
        for index, data in enumerate(datas):
            name = data.get("bookSourceName", "")
            # group = data.get("bookSourceGroup", "")
            name = str(name).strip()
            new_str = f"{self._group[0]}:{index}:{name}"
            # new_str = clear_text(new_str)
            data["bookSourceGroup"] = self._group
            data["bookSourceName"] = new_str
            new_datas.append(data)
        self.save(new_datas)


def core():
    parse = argparse.ArgumentParser("Easy BookSource Build / 简单 书源构建\n")
    parse.add_argument('-g', '--generate', type=bool, default=False, help="bool:合成 json 文件")
    parse.add_argument('-u', '--update', type=bool, default=False, help="bool:根据 csv 文件更新 json 数据")
    parse.add_argument('-c', '--clean', type=bool, default=False, help="bool:重新命名组名")
    
    parse.add_argument('-a', '--add', type=str, default="", help="str:书源地址")
    parse.add_argument('-f', '--full', type=str, default="", help="str:输入为http字符串则增加书源并格式化，若为其他字符则只格式化")
    parse.add_argument('-m', '--comment', type=str, default="", help="str:书源地址 注释")
    parse.add_argument('-d', '--download', type=str, default="", help="str:书源地址 仅下载")
    
    parse.add_argument('--group', '--regroup', nargs=2, type=str, help="str1:文件路径  str2:新的组名（空格分隔两个参数）")
    args = parse.parse_args()
    new_url = args.add
    is_generate = args.generate
    is_update = args.update
    is_clean = args.clean
    comment = args.comment
    full = args.full
    
    group = args.group
    download = args.download
    if full:
        if "http" in new_url:
            url = new_url
            run(url, comment)
        update_csv()
        generate_json()
        Clean(src=Path().new_json, dst=Path().new_json).run()
        return None
    if new_url:
        if comment:
            run(new_url, comment=comment)
        else:
            run(new_url)
        return None
    if is_update:
        update_csv()
        return None
    if is_generate:
        generate_json()
        return None
    if is_clean:
        Clean(src=Path().new_json, dst=Path().new_json).run()
        return None
    if group:
        inst = Clean(src=group[0], dst=group[0])
        inst.group = group[1]
        inst.run()
        return None
    if download:
        html = download_json(download)
        save_json("temp.json", html)
        return None


def debug():
    print("debug test")


if __name__ == '__main__':
    core()
