# Pandas
pip install pandas

# 简易上手
df = pd.read_excel(io=filepath, header=0)

df = pd.read_csv(filepath)
```
参数解读：
header=None 无表头，纯数据
header=0 表示 Excel 第一行数据视为表头
header=1 表示将第二行数据视为表头，注意此时 Excel 第一行数据会被抛弃
```
关于遍历：

DataFrame.iterrows()	按行顺序优先，接着依次按列迭代
DataFrame.iteritems()	按列顺序优先，接着依次按行迭代
DataFrame.itertuples()	按行顺序优先，接着依次按列迭代

```python
for index, row in df.iterrows():
    data = row.tolist()
    ...
```
数据转换：Series -> List `row.tolist()`
