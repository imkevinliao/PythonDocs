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
