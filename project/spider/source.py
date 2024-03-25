import json
import os.path
import threading
from collections import Counter
from concurrent.futures import ThreadPoolExecutor

import nltk
import requests
from nltk.corpus import stopwords


def merge_json_simple(src_paths, output):
    datas = []
    for path in src_paths:
        with open(path, 'r', encoding='utf8') as f:
            data = json.load(f)
            datas.extend(data)
    with open(output, 'w', encoding='utf8') as f:
        json.dump(datas, f, ensure_ascii=False, indent=4)


def check(data, valid_data, lock, timeout=4):
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) "
                      "Chrome/58.0.3029.110 Safari/537.3"
    }
    url = data.get("bookSourceUrl", "")
    status = 0
    try:
        response = requests.get(url, headers=headers, timeout=timeout)
        status = response.status_code
    except Exception as e:
        print(f"error url:{url}  error info:{e}")
    if status == 200:
        with lock:
            valid_data.append(data)
    print(f"url: {url} status_code:{status}")


def multi_threading(tasks, count=10):
    lock = threading.Lock()
    valid_data = []
    pool = ThreadPoolExecutor(max_workers=count)
    for task in tasks:
        sub_thread = pool.submit(check, task, valid_data, lock, timeout=3)
        sub_thread.exception(timeout=None)
    pool.shutdown()
    return valid_data


class Dict:
    bookSourceComment = ""
    bookSourceGroup = ""
    bookSourceName = ""
    bookSourceUrl = ""
    exploreUrl = ""
    searchUrl = ""


class Source(object):
    def __init__(self, src, dst):
        self.src_path = src
        self.dst_path = dst
    
    def info(self, index=0, sp=None):
        datas = self.get()
        if index > len(datas):
            index = -1
        data = datas[index]
        comment = data.get("bookSourceComment")
        name = data.get("bookSourceName")
        group = data.get("bookSourceGroup")
        url = data.get("bookSourceUrl")
        print(f"{data}\nindex:{index}\nnumbers:{len(datas)}\ncomment:{comment}\nname:{name}\ngroup:{group}\nurl:{url}")
        if sp:
            key_map = {
                'name': 'bookSourceName',
                'comment': 'bookSourceComment',
                'group': 'bookSourceGroup'
            }
            key = key_map.get(sp, "name")
            for i in datas:
                print(i.get(key))
    
    def get(self):
        with open(self.src_path, 'r', encoding='utf8') as f:
            data = json.load(f)
        return data
    
    def save(self, data):
        with open(self.dst_path, 'w', encoding='utf8') as f:
            json.dump(data, f, ensure_ascii=False, indent=4)
        return None
    
    def calculate_frequently(self):
        datas = self.get()
        book_comment = []
        book_name = []
        book_group = []
        for data in datas:
            book_comment.append(data.get("bookSourceComment")) if data.get("bookSourceComment") else None
            book_name.append(data.get("bookSourceName")) if data.get("bookSourceName") else None
            book_group.append(data.get("bookSourceGroup")) if data.get("bookSourceGroup") else None
        
        def calculate(text):
            words = nltk.word_tokenize(text)
            stop_words = set(stopwords.words('chinese'))
            filtered_words = [word for word in words if word not in stop_words]
            word_freq = Counter(filtered_words)
            return word_freq
        
        comment = calculate(" ".join(book_comment))
        name = calculate(" ".join(book_name))
        group = calculate(" ".join(book_group))
        
        print("comment:", comment.most_common(50))
        print("name:", name.most_common(50))
        print("group", group.most_common(50))
    
    def clear_invalid_book_sources(self, is_save=False):
        keywords = ['失效', '规则为空', '失-效', "搜索内容为空并且没有发现", "超时", "登录"]
        clean_data = []
        datas = self.get()
        for data in datas:
            comment = data.get("bookSourceComment", "")
            group = data.get("bookSourceGroup", "")
            comment = comment or ""
            group = group or ""
            if any(word in comment for word in keywords):
                continue
            if any(word in group for word in keywords):
                continue
            clean_data.append(data)
        print(f"clear invalid source:\ninput:{len(datas)}  output:{len(clean_data)}")
        if is_save:
            """清理无效书源，并保存回源路径"""
            temp = self.dst_path
            self.dst_path = self.src_path
            self.save(clean_data)
            self.dst_path = temp
        return clean_data
    
    def check_by_url(self, is_catch=True):
        datas = self.get()
        check_data = []
        api_data = []
        for data in datas:
            url = data.get("bookSourceUrl", "")
            if "api." in url:
                api_data.append(data)
            else:
                check_data.append(data)
        check_result = multi_threading(check_data, 20)
        new_data = api_data.extend(check_result)
        print(f"all data:{len(datas)}\ncheck_data:{len(check_data)}:check_result:{len(check_result)}\n")
        print(f"api data:{len(api_data)}, api url can't be checked, so pass check.")
        if is_catch:
            temp = self.dst_path
            self.dst_path = "temp" + os.path.basename(src_path)
            self.save(new_data)
            self.dst_path = temp
        return new_data
    
    @staticmethod
    def re_group_help(data: dict):
        categories = {
            '漫画': ["🎨", "漫画"],
            '有声': ["有声"],
            '图片': ["图片"],
            '仅发现': ["仅发现"],
            'api': ["api"],
            '18': ["🔞", "绅士"],
            '笔趣阁': ["笔趣"],
            '乐文': ["乐文"],
            '网页源': ["网页源"],
        }
        comment = data.get("bookSourceComment")
        group = data.get("bookSourceGroup")
        url = data.get("bookSourceUrl")
        name = data.get("bookSourceName")
        comment = comment or ""
        group = group or ""
        name = name or ""
        for category, keywords in categories.items():
            if any(word in comment for word in keywords) or any(word in group for word in keywords) or \
                    any(word in name for word in keywords) or (category == 'api' and 'api.' in url):
                data["bookSourceGroup"] = category
                return data
        data["bookSourceGroup"] = "未分类"
        return data
    
    def re_group(self, is_pick=False):
        datas = self.get()
        new_data = []
        for data in datas:
            after_group = self.re_group_help(data)
            if is_pick:
                pick = ['api', '18', '笔趣阁', '乐文', '网页源', '未分类']
                if any(word in after_group.get("bookSourceGroup") for word in pick):
                    new_data.append(after_group)
            else:
                new_data.append(after_group)
        return new_data
    
    def run(self):
        ...


if __name__ == "__main__":
    datadir = os.path.join(os.path.dirname(os.path.abspath(__file__)), "data")
    path1 = os.path.join(datadir, "source_single.json")
    path2 = os.path.join(datadir, "source_multi.json")
    path3 = os.path.join(datadir, "source_merge.json")
    path4 = os.path.join(datadir, "source_result.json")
    merge_json_simple([path1, path2], path3)
    source = Source(src=path3, dst=path4)
    results = source.re_group(is_pick=True)
    source.save(results)
