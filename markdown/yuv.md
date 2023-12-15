```
Y  = a * R + b * G + c * B
Cb = (B - Y) / d
Cr = (R - Y) / e
```

|   |BT.601|BT.709|BT.2020|
|:-:|-----:|-----:|------:|
| a | 0.299|0.2126| 0.2627|
| b | 0.587|0.7152| 0.6780|
| c | 0.114|0.0722| 0.0593|
| d | 1.772|1.8556| 1.8814|
| e | 1.402|1.5748| 1.4746|

```
R = Y + e * Cr
G = Y - (a * e / b) * Cr - (c * d / b) * Cb
B = Y + d * Cb
```

* https://www.itu.int/rec/R-REC-BT.601
* https://www.itu.int/rec/R-REC-BT.709
* https://www.itu.int/rec/R-REC-BT.2020
