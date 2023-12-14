# csv
```python
import csv
filepath = ""
with open(filepath, 'w', encoding='utf_8_sig', newline="") as f:
  writer = csv.writer(f)
  data = [1, 2, 3]
  writer.writerrow(data)
with open (filepath, 'r', newline="") as f:
  data = csv.reader(f)
  for row in data:
    print(row)
```

# json
```python
import json

filepath = ""

demo_dict = {"one":1,"two":{"three":['a','b']}}

json_str = json.dumps(demo_dict) # 将字典转成字符串
json_dict = json.loads(json_str) # 将字符串转成字典

with open(filepath,'w', encoding='utf8') as f:
  f.write(json.dumps(json_dict))

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
