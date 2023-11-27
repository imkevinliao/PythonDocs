# matplotlib 快速上手 展示
```

```
pass
# 进阶
中文乱码问题：特别的 linux 如果没有设置的字体，那么这个也不会生效
```
plt.rcParams["font.sans-serif"] = ["SimHei"]  # 设置字体
plt.rcParams["axes.unicode_minus"] = False  # 该语句解决图像中的“-”负号的乱码问题
```
