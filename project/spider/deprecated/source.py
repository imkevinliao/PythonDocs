import json
import multiprocessing
import os.path
import re
import string
from collections import Counter
from datetime import datetime

import nltk
import requests
import urllib3
from multiprocessing_on_dill.dummy import Pool
from nltk.corpus import stopwords


def check_by_requests(data, index, check_result):
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) "
                      "Chrome/58.0.3029.110 Safari/537.3"
    }
    url = data.get("bookSourceUrl")
    try:
        urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)
        response = requests.get(url, headers=headers, verify=False, timeout=5)
        status = response.status_code
    except Exception as e:
        status = e
    if "api" in url:  # api 无法通过requests请求校验，较为复杂
        status = 200
    if str(status) == "200":
        check_result.append(data)
        print(f"okay:{index}  {url}  {status}")
    else:
        print(f"error:{index}  {url}  {status}")


def multi_process(datas):
    with multiprocessing.Manager() as manager:
        check_result = manager.list()
        core = int(multiprocessing.cpu_count())
        print(f"core number is {core}")
        p = Pool(processes=core)
        for index, task in enumerate(datas):
            p.apply_async(func=check_by_requests, args=(task, index, check_result))
        p.close()
        p.join()
        result = list(check_result)
    return result


def merge_json_simple(src_paths, output):
    datas = []
    for path in src_paths:
        with open(path, 'r', encoding='utf8') as f:
            data = json.load(f)
            datas.extend(data)
    with open(output, 'w', encoding='utf8') as f:
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
        print(
            f"{json.dumps(data, indent=4)}\nindex:{index}\nnumbers:{len(datas)}\ncomment:{comment}\nname:{name}\ngroup:{group}\nurl:{url}")
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
        with open(self.dst_path, 'w+', encoding='utf8') as f:
            json.dump(data, f, ensure_ascii=False, indent=4)
        return None
    
    def calculate_frequently(self, frequent=None):
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
        print("comment:", comment.most_common(frequent))
        print("name:", name.most_common(frequent))
        print("group", group.most_common(frequent))
    
    def clear_invalid_book_sources(self, is_save=False):
        keywords = ['失效', '规则为空', '失-效', "搜索内容为空并且没有发现", "超时", "登录", "验证码", "搜索有盾"]
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
        print(f"clear invalid source:input:{len(datas)},output:{len(clean_data)}")
        if is_save:
            """清理无效书源，并保存回源路径"""
            temp = self.dst_path
            self.dst_path = self.src_path
            self.save(clean_data)
            self.dst_path = temp
        return clean_data
    
    @staticmethod
    def re_group_help(data: dict):
        categories = {
            '漫画': ["🎨", "漫画"],
            '有声': ["有声", "FM", "听书"],
            '图片': ["图片"],
            '仅发现': ["仅发现", "发现"],
            '耽美': ["耽美"],
            'api': ["api"],
            '18': ["🔞", "绅士"],
            '女频': ["女频", "言情"],
            '笔趣阁': ["笔趣"],
            '番茄': ["番茄"],
            '小说网站': ["乐文", "顶点", "书包", "顶点", "御书", "笔下文学", "69书吧", "第一版主", "疯情", "燃文",
                         "海棠", "晋江", "八一", "奇书", "追书", "红袖", "九桃", "52书库", "掌阅", "香书", "第二书包",
                         "海岸线", "天域战歌", "烈火"],
            '优质': ["正版", "优质", "精品"],
            '自制': ["自制", "自写"],
            '大佬': ["破冰", "一程"],
            '网页源': ["网页源", "源仓库"],
            '其他': ["其他"],
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
        data["bookSourceGroup"] = "其他"
        return data
    
    def re_group(self, datas, is_pick=False):
        new_data = []
        for data in datas:
            after_group = self.re_group_help(data)
            if is_pick:
                pick = ['耽美', 'api', '18', '女频', '笔趣阁', '番茄', '小说网站1', '小说网站2', '优质', '自制', '大佬',
                        '网页源', '其他']
                if any(word in after_group.get("bookSourceGroup") for word in pick):
                    new_data.append(after_group)
            else:
                new_data.append(after_group)
        return new_data
    
    @staticmethod
    def filter_by_exist(datas: list):
        new_data = []
        for data in datas:
            ruleBookInfo = data.get("ruleBookInfo")
            ruleContent = data.get("ruleContent")
            ruleExplore = data.get("ruleExplore")
            ruleSearch = data.get("ruleSearch")
            ruleToc = data.get("ruleToc")
            explore = data.get("exploreUrl")
            search = data.get("searchUrl")
            if all([ruleBookInfo, ruleContent, ruleExplore, ruleSearch, ruleToc, explore, search]):
                new_data.append(data)
            else:
                pass
        print(f"filter source:input:{len(datas)},output:{len(new_data)}")
        return new_data
    
    @staticmethod
    def count(datas, key="bookSourceGroup"):
        count = Counter()
        for data in datas:
            count[data[key]] += 1
        print(count.most_common())
    
    def run(self):
        ...


def generate(src, dst):
    demo = Source(src=src, dst=dst)
    clear_data = demo.clear_invalid_book_sources()
    filter_data = demo.filter_by_exist(clear_data)
    new_data = demo.re_group(datas=filter_data, is_pick=True)
    demo.save(new_data)
    # clear_text(src=path4, dst=path4)


def requests_verify(src, dst):
    """src: need check url, dst: check result"""
    temp = Source(src=src, dst=dst)
    datas = temp.get()
    start = datetime.now()
    print(start)
    results = multi_process(datas)
    end = datetime.now()
    print(end)
    temp.save(results)
    print(f"input:{len(datas)},output:{len(results)}")


if __name__ == "__main__":
    datadir = os.path.join(os.path.dirname(os.path.abspath(__file__)), "data")
    path1 = os.path.join(datadir, "source_single.json")
    path2 = os.path.join(datadir, "source_multi.json")
    path3 = os.path.join(datadir, "source_merge.json")
    path4 = os.path.join(datadir, "source_result.json")