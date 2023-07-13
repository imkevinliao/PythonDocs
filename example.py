import csv
import hashlib
import hmac
import inspect
import json
import multiprocessing
import os
import pickle
import platform
import random
import struct
import threading
import time
from collections import namedtuple
from concurrent.futures import ThreadPoolExecutor
from os import getpid
from typing import Union, Iterable, TypeVar

from lxml import etree

import numpy as np

# 如何安全使用pickle, Python文档中指出应该只对可信的pickle数据进行解析，使用hmac保证数据安全性。
# pickle 安全使用方式
secret_key = b"encrypt data"
obj = ["demo", (1, 2), ["a", "b"]]
data = pickle.dumps(obj)
digest = hmac.new(secret_key, data, hashlib.sha256).hexdigest()

expected_digest = hmac.new(secret_key, data, hashlib.sha256).hexdigest()
if not hmac.compare_digest(digest, expected_digest):
    print("Data integrity violated")
else:
    unpickle = pickle.loads(data)
    print(unpickle)


# 具名元组的使用，namedtuple是tuple的一个子类，namedtuple 和 tuple 一样无法修改成员值
def func(data: namedtuple):
    print(data.x)
    print(data.y)


Point = namedtuple("UserPoint", ["x", "y"])
p = Point(1, 2)
print(f"直接使用{p.x},{p.y}")
func(p)

ImageType = namedtuple("ImageType", ['jpg', 'png', 'jpeg', 'bmp', 'tif', 'tiff'])
IT = ImageType(".jpg", ".pnm", ".jpeg", ".bmp", ".tif", ".tiff")
print(IT.jpg)

# 读取二进制文件 尽量不要使用python的struct去处理，因为我发现numpy效率比struct高了好几个数量级
path = "bin file path"
with open(path, mode="rb") as f:
    origin_data = f.readlines()
    data = []
    for d in origin_data:
        data.append(np.frombuffer(d, dtype=np.uint8))
    print(data)

with open(path, mode='rb') as f:
    content = f.read(1)
    var = struct.unpack('B', content)[0]
    print(var)
    content = f.read(2)
    var = struct.unpack('h', content)[0]
    print(var)


# 多进程
def func_division(x, y):
    pid = getpid()
    print(f"current pid is:{pid}. x is {x}, y is {y}.")
    time.sleep(random.randint(0, 2))
    return x / y


def func_result(value):
    """value 是 func_add 返回的值"""
    pid = getpid()
    print(f"current pid is {pid}. x+y={value}")


def func_error(e):
    # ZeroDivisionError
    print(f"run error is {e}")


def multi_process():
    max_processes = multiprocessing.cpu_count()
    pool = multiprocessing.Pool(processes=int(max_processes * 0.8))
    for task in range(100):
        pool.apply_async(func=func_division, args=(random.randint(1, 10), random.randint(0, 3),), callback=func_result,
                         error_callback=func_error)
    pool.close()
    pool.join()  # 阻塞主线程


# 多线程
count = 0


def func_thread(task_id, task_lock, other_data):
    print(f"current task id is {task_id}")
    if other_data:
        ...
    global count
    with task_lock:
        count = count + 1
    return count


def func_done(result):
    print(f"task done: task_count is: {result.result()}")


def multi_threading():
    lock = threading.Lock()
    pool = ThreadPoolExecutor(max_workers=3)
    for task in range(10):
        sub_thread = pool.submit(func_thread, task, lock, "other data")
        sub_thread.add_done_callback(func_done)
        sub_thread.exception(timeout=None)
    pool.shutdown()


# lxml 基础的使用方法
path = r"xml文件路径"
tree = etree.parse(path)
root = tree.getroot()
for ele in root.iter():
    if len(ele) == 0:
        print(f"{ele.tag} 没有子节点")
    print(f"tag is {ele.tag}, text is:{ele.text},xpath is :{tree.getpath(ele)}")
    find_ele = root.find('..//title')
    find_elements = root.findall('.//component/name')
    if find_ele:
        find_ele.text = "my text 001"
    if find_elements:
        find_elements[0].text = "my text 002"
span = etree.SubElement(root, "img_prop")
root.insert(root.index(span), etree.Element("hello"))
tree.write("output_xml_path")

# json 使用 indent是缩进，可以让json可读性更好，ensure_ascii是为了保证中文能正常显示
json_filepath = ""


def gen_json(code_dict: dict):
    with open(json_filepath, "w", encoding="utf-8") as jsonfile:
        json_str = json.dumps(code_dict, indent=4, ensure_ascii=False)
        jsonfile.write(json_str)


# 关于代理
os.environ['no_proxy'] = '*'


# python 单例模式
class SingleDemo(object):
    __is_first_init = False
    
    def __new__(cls, *args, **kwargs):
        if not hasattr(cls, '_instance'):
            cls._instance = object.__new__(cls)
        return cls._instance
    
    def __init__(self, name, age, sex):
        if self.__is_first_init:
            return
        self.name = name
        self.age = age
        self.sex = sex
        self.__is_first_init = True


# 参数类型检查 参数类型检查需要考虑到很多中情况，例如不指定类型的情况，类型为None的情况，以及类型为可迭代对象的特殊情况，还需要考虑返回值检查
def func_check(x: int, y: (int, str), z: [int, float, list]) -> str:
    print(f"{x},{y},{z}")
    return "Hello World."


parameters = inspect.signature(func_check).parameters
args_name = list(parameters.keys())
"""
args_value =  [inspect.getcallargs(function, *args, **kwargs)[argument] for argument in inspect.getfullargspec(function).args]
"""
args_annotation = [parameters[argument].annotation for argument in args_name]
inspect._empty  # 注解为空
args_annotation[0] is None  # 注解为 None 的情况
"""
检查返回值的情况
result = function(*args, **kwargs)
annotation = inspect.signature(function).return_annotation
"""


# 事实上 normalize_id 与 normalize_id2 对于类型的描述是一致的，都是表达 user_id 可以接受int或者str两种类型的数据
def normalize_id(user_id: Union[int, str]) -> str:
    if isinstance(user_id, int):
        return f'user-{100_000 + user_id}'
    else:
        return user_id


def normalize_id2(user_id: int | str) -> str:
    if isinstance(user_id, int):
        return f'user-{100_000 + user_id}'
    else:
        return user_id


# func_iterable 和 func_iterable2 不同的地方在于，对于可迭代对象，我们其实并不在乎它是list还是tuple，抑或是其他类型，可以使用Iterable
def func_iterable(names: Iterable[str]) -> None:
    for name in names:
        print(f"hello {name}")


def func_iterable2(names: list[str]) -> None:
    for name in names:
        print(f"hello {name}")


"""
Python3.9 内置集合类型对象支持
list[str] 对象为str
tuple[int,int] 两个对象元组
tuple[()] 空元组
tuple[int, ...] 任意数量的元组
dict[str, int] 字典的键和值
Iterable[int] 包含整数的可迭代对象
Sequence[bool] 布尔值序列（只读）
Mapping[str,int] 从键到值的映射（只读）

类型检查器无法推断列表或者字典
l=[] 这种方式无法推断
l:list[int] = []
d:dict[str,int] = {}

特殊的部分：Any 任意类型，可以自由将任何类型分配给 Any

使用注解表明不检查该类，方法或函数
@typing.no_type_check

cli 运行 mypy + 文件名，检查类型问题
"""

# csv 可以直接写数据，也可以使用DictWriter写字典，encoding需要注意，保证excel可以正常读取中文，不会乱码
with open("csv filepath", 'w+', encoding='utf_8_sig', newline='') as csvfile:
    fieldnames = ['column1', 'column2', 'column3']
    # writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
    # writer.writeheader()
    # writer.writerow({'column1': "a", 'column2': "aa", 'column3': "aaa"})
    writer = csv.writer(csvfile)
    writer.writerow(fieldnames)
    data = [...]
    writer.writerows(data)


# 泛型 如果我想表达入参和返回值是同一个类型，使用 func_generics 这种并不能很好表达，相反使用泛型 func_generics_clear 表意清晰
# 自定义泛型，例如我希望整数和浮点数复数作为一个类型 B = TypeVar('B', int, float, complex)
def func_generics(value: int | float) -> int | float:
    return value


T = TypeVar('T')


def func_generics_clear(value: T) -> T:
    return value


B = TypeVar('B', int, float, complex)


def func_b(value: B) -> B:
    return value


func_b(complex(1, 2))
func_b(12)
func_b(1.2)

# 检查python是64位还是32位 通常配合dll
platform.architecture()

""" visual studio 创建dll工程会自动生成下面四个文件，修改为下面内容即可，注意需要根据python位数生成的对应的dll（32，64）
--------------------------------------------------
framework.h
#pragma once

#define WIN32_LEAN_AND_MEAN             // 从 Windows 头文件中排除极少使用的内容
// Windows 头文件
#include <windows.h>
--------------------------------------------------
pch.h
// pch.h: 这是预编译标头文件。
// 下方列出的文件仅编译一次，提高了将来生成的生成性能。
// 这还将影响 IntelliSense 性能，包括代码完成和许多代码浏览功能。
// 但是，如果此处列出的文件中的任何一个在生成之间有更新，它们全部都将被重新编译。
// 请勿在此处添加要频繁更新的文件，这将使得性能优势无效。

#ifndef PCH_H
#define PCH_H

// 添加要在此处预编译的标头
#include "framework.h"

#endif //PCH_H

//定义宏
#ifdef IMPORT_DLL
#else
#define IMPORT_DLL extern "C" _declspec(dllimport) //指的是允许将其给外部调用
#endif

IMPORT_DLL int add(int a, int b);
--------------------------------------------------
dllmain.cpp
// dllmain.cpp : 定义 DLL 应用程序的入口点。
#include "pch.h"

int add(int a, int b)
{
    return a + b;
}
--------------------------------------------------
pch.cpp
// pch.cpp: 与预编译标头对应的源文件

#include "pch.h"

// 当使用预编译的头时，需要使用此源文件，编译才能成功。
--------------------------------------------------
"""

configparser 是 python 提供用来处理配置文件类
