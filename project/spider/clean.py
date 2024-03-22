import os

from easydict import EasyDict

import json

from reader_spider import generate_18

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


if __name__ == '__main__':
    # merge()
    # pick()
    # pick_again()
    ...
