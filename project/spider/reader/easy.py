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
        if dst == "" or dst is None:
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


def run(json_url):
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
    user_dict = set_dict(src=json_url, dst=dst)
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
        self._group = "myGroup"
    
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
            group = data.get("bookSourceGroup", "")
            name = str(name).strip()
            group = str(group).strip()
            new_str = f"my{index}:{name}:{group}"
            # new_str = clear_text(new_str)
            data["bookSourceGroup"] = self._group
            data["bookSourceName"] = new_str
            new_datas.append(data)
        self.save(new_datas)


def core():
    parse = argparse.ArgumentParser("Easy BookSource Build / 简单 书源构建\n")
    parse.add_argument('-a', '--add', type=str, default="", help="add a json_url path/ 添加一个json_url 地址")
    parse.add_argument('-g', '-m', '--merge', '--generate', type=bool, default=True,
                       help="merge json / 合成 json 文件")
    parse.add_argument('-u', '--update', type=bool, default=True, help="update json by csv file / 根据CSV文件更新json")
    parse.add_argument('-c', '--clean', '--clear', type=bool, default=True,
                       help="clear merge json file / 清理合成后的json文件")
    parse.add_argument('--regroup', '--change_group', nargs=2, type=str,
                       help="input two string use space to split: filepath group_name")
    
    args = parse.parse_args()
    new_url = args.add
    is_merge = args.merge
    is_update = args.update
    is_clean = args.clean
    regroup = args.regroup
    if new_url != "":
        run(new_url)
    if is_update:
        update_csv()
    if is_merge:
        generate_json()
    if is_clean:
        Clean(src=Path().new_json, dst=Path().new_json).run()
    if regroup:
        inst = Clean(src=regroup[0], dst=regroup[0])
        inst.group = regroup[1]
        inst.run()


def debug():
    print("debug test")


if __name__ == '__main__':
    core()
