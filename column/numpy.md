# 快速上手
```
import numpy as np

# 读取数据
data = np.fromfile(filepath, dtype=np.uint16)
data = np.frombuffer(binary_data, np.int)

# 改变矩阵形状
matrix_2d = data.reshape((4096,4608))

# 三维零矩阵
matrix_3d = np.zeros((z,x,y), np.float32)

# 我们可以对矩阵求均值，方差，标准差（在求值的时候如果是三维或多维，
# 还可以指定是在哪一个维度上进行求取的axis=0，这里是对z轴求取，（z,x,y））：
# np.mean(matrix_3d, axis=0),np.std(),np.var(),np.sqrt()

# 二维矩阵保存为 raw 数据
matrix_2d.astype(np.uint16).tofile("user_data.raw")
```
# 进阶
```
# 去掉冗余维度，有些时候明明是一个一维的数据，偏偏嵌套成了三维度，就可以用这个去除冗余的维度
data = np.squeeze(data)

# 维度顺序调换
a = np.empty((2, 3, 4, 5))
b = np.transpose(a, (2, 3, 0, 1))
print(b.shape)
# result: (4, 5, 2, 3)
```
