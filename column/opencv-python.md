# 常见问题
问：opencv安装后Pycharm无法进行提示

安装低版本的opencv，具体原因不明，实测可行，具体低多少的版本，网上查看下。安装后注意重新启动项目。
尝试将 import cv2 改为 import import cv2.cv2 as cv2 

问：opencv无法读取图片以及无法写图

请确读取图片的绝对路径中不存在中文

# opencv-python 快速上手

```
cv2.imread(filepath)
img_yuv = cv2.cvtColor(img, cv2.COLOR_BGR2YUV_I420)
```

中文路径读取保存：
```
def opencv_save(filepath, image):
    _, ext = os.path.splitext(filepath)
    cv2.imencode(ext, image)[1].tofile(filepath)

# 注意这种方式读取的图片是 rgb 格式，opencv 默认是 bgr 格式
image = cv2.imdecode(np.fromfile(path, dtype=np.uint8), flags=cv2.IMREAD_COLOR)

# rgb2bgr
cv2.cvtColor(img, cv2.COLOR_RGB2BGR)
```
