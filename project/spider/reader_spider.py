import glob
import json
import os
import pickle
import random
import re
import shutil
import string
import time

from lxml import etree
from easydict import EasyDict

import requests

is_delay = False
base_dir = os.path.dirname(os.path.abspath(__file__))
json_dir = os.path.join(base_dir, "json")
data_dir = os.path.join(base_dir, "data")
jsons_dir = os.path.join(base_dir, "jsons")


def download(url: str, is_json=False):
    if is_delay:
        time.sleep(random.randint(1, 3))
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) "
                      "Chrome/58.0.3029.110 Safari/537.3"
    }
    print(url)
    response = requests.get(url, headers=headers)
    status_code = response.status_code
    if status_code == 200:
        if is_json:
            html = response.json()
        else:
            html = response.text
    else:
        html = None
    return html


def pipe(html: str):
    root = etree.HTML(html)
    data_list = []
    # main_element = root.find(".//*[@class='layui-container']")
    ylist_nodes = root.findall('.//div[@class="ylist"]')
    for node in ylist_nodes:
        try:
            data = EasyDict()
            href_tag = node.find(".//a")
            href_attrib = href_tag.attrib['href']
            href_text = href_tag.text
            p_tag = node.findall(".//p")
            time_text = p_tag[-1].text
            span_tag = node.findall(".//span")
            down_times = span_tag[-1].text
            head, _ = str(href_attrib).split(".")
            data.href = head + ".json"
            data.webname = href_text
            data.time = time_text
            data.downloads = down_times
            data_list.append(data)
        except Exception as e:
            print(e)
    return data_list


def dump(filepath: str, pickle_path: pickle, is_clean=False):
    with open(pickle_path, 'rb') as f:
        index_data = pickle.load(f)
    if not os.path.exists(json_dir):
        print(f"create json dir:{json_dir}")
        os.mkdir(json_dir)
    pickle_jsonpath = []
    for info in index_data:
        json_url = info.href
        _, name = os.path.split(json_url)
        json_save_path = os.path.join(json_dir, name)
        pickle_jsonpath.append(json_save_path)
        if os.path.exists(json_save_path):
            # 尽可能不要给服务器压力，已经保存过的数据不再重复请求
            # print(f"file has exist {json_save_path}, pass.")
            continue
        html = download(json_url, is_json=True)
        with open(os.path.join(json_dir, name), 'w', encoding='utf-8') as f:
            json.dump(html, f, ensure_ascii=False, indent=4)
    # files = [os.path.join(json_dir, file) for file in os.listdir(json_dir) if file.endswith(".json")]
    # 考虑到 pickle 可能过滤的情况，根据 pickle 数据的 json 来取比较好
    files = pickle_jsonpath
    all_data = []
    for file in files:
        with open(file, 'r', encoding='utf8') as f:
            all_data.extend(json.load(f))
    with open(filepath, 'w', encoding='utf8') as f:
        json.dump(all_data, f, ensure_ascii=False, indent=4)
    if is_clean:
        # 源数据还是保留比较好，不建议清理
        shutil.rmtree(json_dir)
        print(f"remove temp dir:{json_dir}")


def save_index(index_pickle: pickle, new_data: list):
    if os.path.exists(index_pickle):
        with open(index_pickle, 'rb') as f:
            current_data = pickle.load(f)
        new_data.extend(current_data)
    # 去重
    old_length = len(new_data)
    temp_dict = {item["href"]: item for item in new_data}
    new_data = list(temp_dict.values())
    now_length = len(new_data)
    with open(index_pickle, 'wb') as f:
        pickle.dump(new_data, f)
    # 存在重复数据交给上一级停止抓取
    if old_length != now_length:
        return True
    return None


def filter_data(origin: pickle, download_low=10 ** 4, download_high=10 ** 6) -> str:
    # 按照下载次数过滤，返回过滤后的pickle相对路径
    with open(origin, 'rb') as f:
        data = pickle.load(f)
    new_pickle = os.path.join(data_dir, "filter.pickle")
    new_data = []
    for i in data:
        info = i.downloads
        downtimes = ''.join(filter(str.isdigit, info))
        downtimes = float(downtimes)
        if download_low <= downtimes < download_high:
            new_data.append(i)
    with open(new_pickle, 'wb') as f:
        pickle.dump(new_data, f)
    return new_pickle


def source_merge():
    website = "https://www.yckceo.com/yuedu/shuyuans/index.html"
    webroot = "https://www.yckceo.com"
    if not os.path.exists(json_dir):
        os.mkdir(json_dir)
    index_pickle = os.path.join(data_dir, "index_merge.pickle")
    for i in range(1, 4):
        url = f"{website}?page={i}"
        page = download(url)
        new_data = pipe(page)
        for one_data in new_data:
            temp = one_data.href
            temp = str(temp).replace("content", "json")
            one_data.href = f"{webroot}{temp}"
        is_true = save_index(index_pickle, new_data)
        if is_true:
            print("存在重复数据，停止抓取")
            break
    with open(index_pickle, 'rb') as f:
        index_data = pickle.load(f)
    if not os.path.exists(jsons_dir):
        os.mkdir(jsons_dir)
    pickle_jsonpath = []
    for index, info in enumerate(index_data):
        json_url = info.href
        _, name = os.path.split(json_url)
        json_save_path = os.path.join(jsons_dir, name)
        pickle_jsonpath.append(json_save_path)
        if os.path.exists(json_save_path):
            continue
        html = download(json_url, is_json=True)
        with open(os.path.join(jsons_dir, name), 'w', encoding='utf-8') as f:
            json.dump(html, f, ensure_ascii=False, indent=4)
    
    # 合成的json太大了
    def merge_json_files(filenames, output_filename):
        with open(output_filename, 'w') as output_file:
            output_file.write('[')  # 开始写入 JSON 数组
            for j, filename in enumerate(filenames):
                with open(filename, 'r') as input_file:
                    # 除了第一个文件，其他文件之前都需要添加一个逗号，
                    # 这是因为我们正在创建一个 JSON 数组。
                    if j != 0:
                        output_file.write(',')
                    output_file.write(input_file.read().strip())  # 写入文件的 JSON 内容
            output_file.write(']')  # 结束 JSON 数组
    
    # 使用 glob 模块找到所有的 JSON 文件
    files = os.listdir(jsons_dir)
    filepaths = [os.path.join(jsons_dir, filepath) for filepath in files if filepath.endswith(".json")]
    jsonpath = os.path.join(data_dir, 'merged.json')
    merge_json_files(filepaths, jsonpath)
    json_format(src=jsonpath, dst=jsonpath)


def schedule(has_data=False):
    website = "https://www.yckceo.com/yuedu/shuyuan/index.html"
    webroot = "https://www.yckceo.com"
    if not os.path.exists(data_dir):
        os.mkdir(data_dir)
    index_pickle = os.path.join(data_dir, "index.pickle")
    json_filepath = os.path.join(data_dir, "all.json")
    if not has_data:
        for i in range(1, 40):
            url = f"{website}?page={i}"
            page = download(url)
            new_data = pipe(page)
            for one_data in new_data:
                # 构造json的url请求地址
                temp = one_data.href
                temp = str(temp).replace("content", "json")
                one_data.href = f"{webroot}{temp}"
            is_true = save_index(index_pickle, new_data)
            if is_true:
                print("存在重复数据，停止抓取")
                break
    # 过滤生成新的pickle，只取精华书源。
    new_pickle = filter_data(origin=index_pickle, download_low=10 ** 4, download_high=10 ** 6)
    _ = new_pickle
    dump(filepath=json_filepath, pickle_path=index_pickle)


def generate_18(datas, dst_path=""):
    def check(check_str, check_list, ignore_list):
        has_include = False
        for keyword in check_list:
            if str(keyword) in str(check_str):
                has_include = True
                break
        for keyword in ignore_list:
            if str(keyword) in str(check_str):
                has_include = False
                break
        return has_include
    
    keywords = ["🔞", "18", "R18", "r18", "辣", "涩", "肉"]
    ignore_keywords = ["修复", "自写"]
    new_data = []
    for data in datas:
        data = EasyDict(data)
        book_comment = data.get("bookSourceComment")
        book_kind = data.get("bookSourceGroup")
        book_name = data.get("bookSourceName")
        status_comment = False
        status_kind = False
        status_name = False
        if book_comment:
            status_comment = check(book_comment, keywords, ignore_keywords)
        if book_comment:
            status_kind = check(book_kind, keywords, ignore_keywords)
        if book_comment:
            status_name = check(book_name, keywords, ignore_keywords)
        if status_comment or status_kind or status_name:
            data.bookSourceGroup = "18"
            new_data.append(data)
    print(f"18:{len(new_data)}")
    if dst_path:
        output = dst_path
    else:
        output = '18.json'
    with open(output, 'w', encoding='utf8') as f:
        json.dump(new_data, f, ensure_ascii=False, indent=4)


def generate_json():
    index_pickle = os.path.join(data_dir, "index.pickle")
    os.chdir(data_dir)
    d_range = [(0, 10 ** 4),
               (10 ** 4, 10 ** 4 * 2),
               (10 ** 4 * 2, 10 ** 4 * 3),
               (10 ** 4 * 3, 10 ** 4 * 4),
               (10 ** 4 * 4, 10 ** 4 * 5),
               (10 ** 4 * 5, 10 ** 6)]
    for i in d_range:
        temp = filter_data(origin=index_pickle, download_low=i[0], download_high=i[1])
        name = f"{i[0]}_{i[1]}.json"
        dump(filepath=name, pickle_path=temp)
        with open(name, 'r', encoding='utf8') as f:
            datas = json.load(f)
        new_datas = []
        for data in datas:
            data = EasyDict(data)
            if i[1] == 10 ** 6:
                data.bookSourceGroup = "5w+"
            else:
                data.bookSourceGroup = str(i[0])
            new_datas.append(data)
        print(f"{i[0]}_{i[1]}:{len(datas)}")
        with open(name, 'w', encoding='utf8') as f:
            json.dump(new_datas, f, ensure_ascii=False, indent=4)
    # 18特别设置
    temp = filter_data(origin=index_pickle, download_low=0, download_high=10 ** 6)
    name = "all.json"
    dump(filepath=name, pickle_path=temp)
    with open(name, 'r', encoding='utf8') as f:
        datas = json.load(f)
    generate_18(datas)


def json_format(src, dst):
    with open(src, 'r', encoding='utf8') as f:
        datas = json.load(f)
    with open(dst, 'w', encoding='utf8') as f:
        json.dump(datas, f, ensure_ascii=False, indent=4)


def clear_text(src, dst):
    with open(src, 'r', encoding='utf8') as f:
        lines = f.readlines()
    #  常见中文字符 '，。“”‘’！？【】《》；：·'
    reg = rf'[\w\s\u3400-\u4DBF\u4E00-\u9FFF\uF900-\uFAFF{re.escape(string.punctuation)}，。“”‘’！？【】《》；：·]+'
    new_lines = []
    for line in lines:
        result = re.findall(reg, line, re.UNICODE)
        if result:
            new_lines.append("".join(result))
        else:
            new_lines.append(line)
    with open(dst, 'w', encoding='utf8') as f:
        for line in new_lines:
            f.write(line)


if __name__ == '__main__':
    schedule()