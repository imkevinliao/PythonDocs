# configparser
```
def example():
    filepath = None
    config = configparser.ConfigParser()
    config.read(filepath,encoding='utf8')
    if not config.has_section("user"):
        config.add_section("user")
    config.set("user", "kevin", "18")
    config.set("user","natalia","20")
    if not config.has_section("animal"):
        config.add_section("animal")
    config.set("animal","pig","lazy")
    config.set("animal","dog","loyalty")
    
    if not config.has_option("user","kevin"):
        print("None Section user, Option kevin")
    else:
        value = config.get('user', 'kevin')
        print(f"value is {value}.")
    # 转换成dict使用更方便
    user_dict = dict(config.items("user"))
    print(user_dict)
    config["user_new"] = user_dict
    with open(filepath, "w", encoding="utf8") as f:
        config.write(f)
--------------------------------------------
config = configparser.ConfigParser()
filepath = ""
config.read(filepath)

for section in config.sections():
    print(section)
    for key, value in config.items(section):
        print(key, value)

value1 = config.get('Section', 'Key')
print(value1)

config.set("Section","Key","new_value")
with open (filepath, 'w') as f:
    config.write(f)
# ---------------------------------------------
import configparser

# Create a ConfigParser object
config = configparser.ConfigParser()

# Add sections and keys with values
config['section_name'] = {'key_name': 'value'}

# Write to the INI file
with open('example.ini', 'w') as configfile:
    config.write(configfile)
```
# csv
```python
import csv
filepath = ""
with open(filepath, 'w', encoding='utf_8_sig', newline="") as f:
  writer = csv.writer(f)
  data = [1, 2, 3]
  writer.writerow(data)
with open (filepath, 'r', encoding='utf_8_sig', newline="") as f:
  data = csv.reader(f)
  for row in data:
    print(row)


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


def demo():
    test_dict = {'name': 'John Doe', 'age': '30', 'city': 'New York'}
    test_dict2 = [{'name': 'John 1', 'age': '30', 'city': 'New York'},
                  {'name': 'John 2', 'age': '30', 'city': 'New York'},
                  {'name': 'John 3', 'age': '30', 'city': 'New York'}]
    path = "data.csv"
    write_dict_to_csv(path, test_dict, "a+")
    write_dicts_to_csv(path, test_dict2)
    data = read_dict_from_csv(path)
    for i in data:
        print(i)
```
# decorator
```
import traceback
import time
import functools
import inspect
import collections


def timer(func):
    """
    calculates the time it takes to run the function.
    for example:
    @timer
    def show(name):
        print(name)
    show("kevin")
    """
    
    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        start = time.time()
        result = func(*args, **kwargs)
        end = time.time()
        print(f"Run function {func.__name__} takes {end - start} seconds")
        return result
    
    return wrapper


def delay(seconds: int = 1):
    """
    default delay one second, when function start.
    for example:
    @delay(3)
    def show(name):
        print(name)
    show("kevin")
    """
    
    def decorate(func):
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            time.sleep(seconds)
            result = func(*args, *kwargs)
            return result
        
        return wrapper
    
    return decorate


def error_handler(func):
    """
    If the function run fails, will return str "error", so you can judge by this if you need.
    for example:
    @error_handler
    def error_demo():
        return 1 / 0
    result = error_demo()
    if "error" == result:
        print("function run failed")
    """
    
    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        try:
            return func(*args, **kwargs)
        except Exception as e:
            print(f"{e}\n{traceback.format_exc()}")
            return "error"
    
    return wrapper


def func_hint(func):
    """
    prompt function start and end execution
    for example:
    @func_hint
    def show(name):
        print(name)
    show("kevin")
    """
    
    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        prompter = "*"
        length = 15
        hint_str = prompter * length
        print(f"{hint_str} {func.__name__} start {hint_str}")
        result = func(*args, **kwargs)
        print(f"{hint_str} {func.__name__}  end  {hint_str}")
        return result
    
    return wrapper


def param_check(func):
    """
    函数参数检查装饰器，需要配合函数注解表达式（Function Annotations）使用
    for example:
    @param_check
    def show(x: int, y: float, z: str):
        print(f"{x}:{type(x)}")
        print(f"{y}:{type(y)}")
        print(f"{z}:{type(z)}")
    show(1, 2, 3)
    ------
    result:
    func <show> argument y must be <class 'float'>,but got <class 'int'>,value 2
    func <show> argument z must be <class 'str'>,but got <class 'int'>,value 3
    """
    # 获取函数定义的参数
    sig = inspect.signature(func)
    parameters = sig.parameters  # 参数有序字典
    arg_keys = tuple(parameters.keys())  # 参数名称
    
    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        CheckItem = collections.namedtuple('CheckItem', ('anno', 'arg_name', 'value'))
        check_list = []
        
        # collect args   *args 传入的参数以及对应的函数参数注解
        for i, value in enumerate(args):
            arg_name = arg_keys[i]
            anno = parameters[arg_name].annotation
            check_list.append(CheckItem(anno, arg_name, value))
        
        # collect kwargs  **kwargs 传入的参数以及对应的函数参数注解
        for arg_name, value in kwargs.items():
            anno = parameters[arg_name].annotation
            check_list.append(CheckItem(anno, arg_name, value))
        
        # check type
        errors = []
        for item in check_list:
            if not isinstance(item.value, item.anno):
                error = f'func <{func.__name__}> argument {item.arg_name} must be {item.anno},' \
                        f'but got {type(item.value)},value {item.value} '
                errors.append(error)
        if errors:
            raise TypeError("\n" + "\n".join(errors))
        return func(*args, **kwargs)
    
    return wrapper
```

# json
```python
import json

filepath = ""

demo_dict = {"one":1,"two":{"three":['a','b']}}

json_str = json.dumps(demo_dict) # 将字典转成字符串
json_dict = json.loads(json_str) # 将字符串转成字典
# [dict,dict,...],list也可以直接这么使用
with open(filepath,'w', encoding='utf8') as f:
  f.write(json.dumps(json_dict,indent=4,ensure_ascii=False))

with open(filepath, 'r', encoding='utf8') as f:
  data_dict = json.load(f)
```
# argparse
```
import argparse
def get_args():
    parser = argparse.ArgumentParser("Genshin Auto Domain")
    parser.add_argument("--yolox_exp_file", type=str, default='yolox/exp/yolox_s_genshin.py')
    parser.add_argument("--lost_score", type=float, default=0.6)
    parser.add_argument("--lost_times", type=int, default=4)
    parser.add_argument("--track_timeout", type=float, default=4.5)
    parser.add_argument("--max_retry", type=int, default=200)
    return parser.parse_args()
args = get_args()
print(args.max_retry)
# ****************************main.py****************************************
import argparse
# 创建解析器
parser = argparse.ArgumentParser(description='这是一个用来演示argparse模块的示例')
# 添加参数
parser.add_argument('-arg1', type=int, help='应为整数类型')
parser.add_argument('--optional_arg', type=str, default='default_value', choices=['option1', 'option2'],help='一个可选的字符串参数，默认值为"default_value"，可选项为option1或option2')
parser.add_argument('--flag', action='store_true', help='一个标志参数，如果出现则为True，否则为False')
parser.add_argument('--number_list', nargs='+', type=int, help='接受多个整数的参数列表')
# 解析命令行参数
args = parser.parse_args()
# 使用参数
print('arg1 值:', args.arg1)
print('optional_arg 值:', args.optional_arg)
print('flag 值:', args.flag)
print('number_list 值:', args.number_list)
# python main.py -arg1 11 --number_list 11 22 33  --flag
# python main.py --help
```
# zipfile
```python
import zipfile
def zip_dir(src, dst):
    """
    压缩指定文件夹
    :param src:目标文件夹路径
    :param dst: 压缩后的保存路径(带上文件名及后缀):/home/ubuntu/test.zip
    :return:
    """
    # fold_name = os.path.dirname(src)
    zip_inst = zipfile.ZipFile(dst, 'w', zipfile.ZIP_DEFLATED)
    for root, dirs, files in os.walk(src):
        # fpath = root.replace(fold_name, "")
        fpath = root.replace(src,"")
        for file in files:
            temp_src = os.path.join(root, file)
            temp_dst = os.path.join(fpath, file)
            zip_inst.write(temp_src, temp_dst)
    zip_inst.close()

def unzip_dir(src, dst):
    """
    解压文件夹
    :param src: 压缩的zip文件
    :param dst: 解压后的文件夹路径
    :return:
    """
    with zipfile.ZipFile(src, 'r') as f:
        if not os.path.exists(dst):
            os.makedirs(dst)
        f.extractall(dst)
```
# log
```
import logging


class Log(logging.Logger):
    def __init__(self, log_filepath=None, level=logging.DEBUG, logfile_mode='a+'):
        super().__init__(name=log_filepath)
        self.logfile_mode = logfile_mode
        self.setLevel(level=level)
        self.config()
    
    def config(self):
        formatter = logging.Formatter(fmt="%(asctime)s %(levelname)s [line:%(lineno)d] %(message)s",
                                      datefmt="%Y-%m-%d %H:%M:%S(%p)")
        stdout_handler = logging.StreamHandler()
        stdout_handler.setFormatter(formatter)
        self.addHandler(stdout_handler)
        if self.name:
            file_handler = logging.FileHandler(filename=self.name, encoding='utf-8', mode=self.logfile_mode)
            file_handler.setFormatter(formatter)
            self.addHandler(file_handler)
"""
# 标准输出和文件输出
log = logging.getLogger("module name")
log.setLevel(logging.DEBUG)
formatter = logging.Formatter(fmt="%(asctime)s %(levelname)s [line:%(lineno)d] %(message)s", datefmt="%Y-%m-%d %H:%M:%S(%p)")

stdout_handler = logging.StreamHandler()
stdout_handler.setFormatter(formatter)
log.addHandler(stdout_handler)

file_handler = logging.FileHandler(filename="log.txt", encoding='utf-8', mode="a+")
file_handler.setFormatter(formatter)
log.addHandler(file_handler)

log.info("info")
log.debug("debug")
log.warning("warning")
log.critical("critical")
"""
```
