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
```
fig, axs = plt.subplots(3, sharex=True, sharey=False)
fig.suptitle(f'title')
fig.supxlabel('xlabel')
fig.supylabel('ylabel')
x_ticks = 5
axs[0].hist(data,bins=int(len_max/x_ticks), range=x_range,color="red",label="first")
axs[0].hist(data,bins=int(len_max/x_ticks), range=x_range,color="red",label="second")
axs[0].hist(data,bins=int(len_max/x_ticks), range=x_range,color="red",label="third")
axs[0].legend(loc="best")
axs[1].legend(loc="best")
axs[2].legend(loc="best")

overlapping = 0.7
axs[0].scatter(x_data,y_data,alpha=overlapping,color='r',label="first")
axs[1].scatter(x_data,y_data,alpha=overlapping,color='y',label="second")
axs[2].scatter(x_data,y_data,alpha=overlapping,color='g',label="third")

plt.savefig(image_path,dpi=400)
plt.close()


plt.figure(figsize=(1920/100,1080/100))
plt.imshow(image)

# 设置时间刻度
ax = plt.subplot(212)
plt.title(title_text, color="k")
plt.plot(data_x,data_y, color="b")
ax.text(0.02, 0.9, c="b", s="string",transform=ax.transAxes)
user_data = data.tail(data_counts)
formatter = dates.DateFormatter("%d")
user_interval = dates.DayLocator(interval=1)
formatter = dates.DateFormatter("%m")
user_interval = dates.MonthLocator(interval=1)
ax.xaxis.set_major_formatter(formatter)
ax.xaxis.set_major_locator(user_interval)
```
