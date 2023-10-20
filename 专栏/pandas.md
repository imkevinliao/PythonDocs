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

日期转换:`df["日期"] = pd.to_datetime(df["日期"])`

定位数据：<https://zhuanlan.zhihu.com/p/129898162>
```
loc,iloc,ix
loc:通过标签来进行定位，这意味着必须有标签
iloc:通过索引值来定位，即定位列表采用的方式
（ix是综合loc和iloc最先产生的，但是后面被loc，iloc取代，被弃用了）

df.loc[行索引范围,列索引范围]
df.iloc[行索引范围,列索引范围]
df.loc[行索引范围,列索引范围]
```
以 df.iloc 举例：
```
如果想选取所有行，选取部分列，应该是 
df.iloc[:,[2,4]]
df.iloc[:,0:3]
```

