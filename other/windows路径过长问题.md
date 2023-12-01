# 路径过长
纸上得来终觉浅，绝知此事要躬行

<https://www.cnblogs.com/hexiaoqi/p/13040220.html>

总结：
1. win32api.GetShortPathName 实测没什么用处
2. 使用 os.chdir() + 操作文件名 实测没什么用处 
3. 绝对路径前加 `r'\\?\'`
4. 对于共享路径 ` r'\\share\www\demo' -> r'\\?\UNC\share\www\demo' `

给我放弃 windows 又增加了一个理由

windows 的兼容性好，既是优点，又是累赘。
