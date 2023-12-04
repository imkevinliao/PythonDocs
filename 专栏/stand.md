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
