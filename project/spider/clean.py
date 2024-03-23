import os
import threading
from concurrent.futures import ThreadPoolExecutor

import requests
from easydict import EasyDict

import json

from reader_spider import generate_18, clear_text

base_dir = os.path.dirname(os.path.abspath(__file__))


def merge_json_files(filenames, output_filename):
    with open(output_filename, 'w', encoding='utf8') as output_file:
        output_file.write('[')  # 开始写入 JSON 数组
        for j, filename in enumerate(filenames):
            with open(filename, 'r', encoding='utf8') as input_file:
                # 除了第一个文件，其他文件之前都需要添加一个逗号，
                # 这是因为我们正在创建一个 JSON 数组。
                if j != 0:
                    output_file.write(',')
                output_file.write(input_file.read().strip())  # 写入文件的 JSON 内容
        output_file.write(']')  # 结束 JSON 数组


def merge():
    json_path = os.path.join(base_dir, "ignore")
    output = os.path.join(base_dir, "data")
    files = os.listdir(json_path)
    filepaths = [os.path.join(json_path, filepath) for filepath in files if filepath.endswith(".json")]
    out = os.path.join(output, 'merged.json')
    merge_json_files(filepaths, out)


def pick():
    huge_json = os.path.join(base_dir, "data", "merged.json")
    merged_filter = os.path.join(base_dir, "data", "merged_filter.json")
    with open(huge_json, 'r', encoding='utf8') as f:
        datas = json.load(f)
    new_data = []
    for data in datas:
        if data is None:
            continue
        for d in data:
            my_dict = EasyDict(d)
            url = my_dict.bookSourceUrl
            if "http" in url:
                new_data.append(d)
    temp_dict = {item["bookSourceUrl"]: item for item in new_data}
    new_data = list(temp_dict.values())
    with open(merged_filter, 'w', encoding='utf8') as f:
        json.dump(new_data, f, ensure_ascii=False, indent=4)
    print("okay")


def pick_again():
    filepath = os.path.join(base_dir, "data", "merged_filter.json")
    filter_result = os.path.join(base_dir, "data", "filter.json")
    with open(filepath, 'r', encoding='utf8') as f:
        data = json.load(f)
    print(f"origin {len(data)}")
    first_filter = []
    for d in data:
        my_dict = EasyDict(d)
        if my_dict.get("searchUrl"):
            has_search = True
        else:
            has_search = False
        if has_search:
            first_filter.append(d)
    print(f"first {len(first_filter)}")
    second_filter = []
    for d in first_filter:
        my_dict = EasyDict(d)
        url = my_dict.bookSourceUrl
        if "https" in url:
            second_filter.append(d)
    print(f"second {len(second_filter)}")
    third_filter = []
    filter_keyword = ["听", "有声", "漫画", "图片", "音乐", "仅发现", "搜索无效", "搜索失效"]
    for d in second_filter:
        my_dict = EasyDict(d)
        has_kind = False
        has_name = False
        book_comment = my_dict.get("bookSourceComment")
        book_kind = my_dict.get("bookSourceGroup")
        book_name = my_dict.get("bookSourceName")
        if book_kind:
            has_kind = True
        if book_name:
            has_name = True
        if has_kind:
            for keyword in filter_keyword:
                if keyword in book_kind:
                    has_kind = False
                    break
        if has_name:
            for keyword in filter_keyword:
                if keyword in book_name:
                    has_name = False
                    break
        if book_comment:
            for keyword in filter_keyword:
                if keyword in book_name:
                    has_name = False
                    has_kind = False
                    break
        if has_name and has_kind:
            third_filter.append(d)
    print(f"third {len(third_filter)}")
    dst_18 = os.path.join(base_dir, "data", "filter_18.json")
    generate_18(third_filter, dst_path=dst_18)
    with open(filter_result, 'w', encoding='utf8') as f:
        json.dump(third_filter, f, ensure_ascii=False, indent=4)


def check(data, valid_data, lock, timeout=5):
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) "
                      "Chrome/58.0.3029.110 Safari/537.3"
    }
    my_dict = EasyDict(data)
    url = my_dict.bookSourceUrl
    group = my_dict.bookSourceGroup
    status = "request error"
    try:
        response = requests.get(url, headers=headers, timeout=timeout)
        status = response.status_code
    except Exception as e:
        print(f"error url:{url}\nerror info:{e}")
    if status == 200:
        with lock:
            valid_data.append(data)
        print(f"okay url:{url}  status:{status}  group:{group}")


def multi_threading(tasks, count=10):
    lock = threading.Lock()
    valid_data = []
    pool = ThreadPoolExecutor(max_workers=count)
    timeout = 5
    for task in tasks:
        sub_thread = pool.submit(check, task, valid_data, lock, timeout)
        sub_thread.exception(timeout=None)
    pool.shutdown()
    return valid_data


def valid_url():
    path_all = os.path.join(base_dir, "data", "filter.json")
    path_18 = os.path.join(base_dir, "data", "filter_18.json")
    output = os.path.join(base_dir, "data", "clean.json")
    with open(path_all, 'r', encoding='utf8') as f:
        data_all = json.load(f)
    with open(path_18, 'r', encoding='utf8') as f:
        data_18 = json.load(f)
    data_all.extend(data_18)
    valid_data = multi_threading(data_all, count=20)
    print(f"datas:{len(valid_data)}")
    with open(output, 'w', encoding='utf8') as f:
        json.dump(valid_data, f, ensure_ascii=False, indent=4)
    clear_text(src=output, dst=output)


def valid_url_again():
    clean_json = os.path.join(base_dir, "data", "clean.json")
    with open(clean_json, 'r', encoding='utf8') as f:
        datas = json.load(f)
    new_data = []
    for data in datas:
        my_dict = EasyDict(data)
        url = my_dict.bookSourceUrl
        group = my_dict.bookSourceGroup
        if group == "18":
            continue
        if ".com" in url:
            if "m." in url:
                my_dict.bookSourceGroup = "m.com"
            else:
                my_dict.bookSourceGroup = "www.com"
        else:
            my_dict.bookSourceGroup = "other"
        new_data.append(my_dict)
    with open(clean_json, 'w', encoding='utf8') as f:
        json.dump(new_data, f, ensure_ascii=False, indent=4)


if __name__ == '__main__':
    # merge()
    # pick()
    # pick_again()
    # valid_url()
    # valid_url_again()
    ...