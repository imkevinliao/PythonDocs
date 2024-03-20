import json
import os
import pickle
import random
import shutil
import time

from lxml import etree
from easydict import EasyDict

import requests

is_delay = False


def download(url: str, is_json=False) -> str | list:
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
    temp_dir = "temp"
    if not os.path.exists(temp_dir):
        print(f"create temp dir:{temp_dir}")
        os.mkdir(temp_dir)
    pickle_jsonpath = []
    for info in index_data:
        json_url = info.href
        _, name = os.path.split(json_url)
        json_save_path = os.path.join(temp_dir, name)
        pickle_jsonpath.append(json_save_path)
        if os.path.exists(json_save_path):
            # 尽可能不要给服务器压力，已经保存过的数据不再重复请求
            # print(f"file has exist {json_save_path}, pass.")
            continue
        html = download(json_url, is_json=True)
        with open(os.path.join(temp_dir, name), 'w', encoding='utf-8') as f:
            json.dump(html, f, ensure_ascii=False, indent=4)
    # files = [os.path.join(temp_dir, file) for file in os.listdir(temp_dir) if file.endswith(".json")]
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
        shutil.rmtree(temp_dir)
        print(f"remove temp dir:{temp_dir}")


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
    new_pickle = "filter.pickle"
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


def schedule(has_data=False):
    website = "https://www.yckceo.com/yuedu/shuyuan/index.html"
    webroot = "https://www.yckceo.com"
    index_pickle = "index.pickle"
    json_filepath = "test.json"
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
    # 如果需要过滤，请改成 pickle_path=new_pickle，如果不需要请改成 pickle_path=index_pickl
    dump(filepath=json_filepath, pickle_path=index_pickle)


def generate_json():
    # result_dir = "./result"
    # os.mkdir(result_dir)
    # os.chdir(result_dir)
    d_range = [(0, 10 ** 4),
               (10 ** 4, 10 ** 4 * 2),
               (10 ** 4 * 2, 10 ** 4 * 3),
               (10 ** 4 * 3, 10 ** 4 * 4),
               (10 ** 4 * 4, 10 ** 4 * 5),
               (10 ** 4 * 5, 10 ** 6)]
    for i in d_range:
        temp = filter_data(origin="index.pickle", download_low=i[0], download_high=i[1])
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
    temp = filter_data(origin="index.pickle", download_low=0, download_high=10 ** 6)
    name = "all.json"
    dump(filepath=name, pickle_path=temp)
    with open(name, 'r', encoding='utf8') as f:
        datas = json.load(f)
    book_sort = ["🔞", "18", "R18", "r18", "辣"]
    comment = ["🔞", "涩", "肉"]
    generate_data = []
    for data in datas:
        data = EasyDict(data)
        group = data.get("bookSourceGroup")
        book_name = data.get("bookSourceName")
        is_18 = False
        for temp in book_sort:
            if str(group).find(str(temp)) != -1:
                if "修复" in str(group):
                    continue
                if "自写" in str(group):
                    continue
                is_18 = True
        for temp in comment:
            if str(book_name).find(str(temp)) != -1:
                is_18 = True
        if is_18:
            data.bookSourceGroup = "18"
            generate_data.append(data)
    print(f"18:{len(generate_data)}")
    with open('18.json', 'w', encoding='utf8') as f:
        json.dump(generate_data, f, ensure_ascii=False, indent=4)


if __name__ == '__main__':
    generate_json()