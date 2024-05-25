# local-print-service
[README](/README.md "README") | [中文文档](/README_zh.md "中文文档")

## 简介
一个基于websocket的本地打印服务，允许数据灵活传输。

## 特性
    * 灵活选择打印机
    * 无需预览直接打印
    * 灵活发送数据打印

## 依赖
    * PYQT
    * Pyinstaller
    
## 安装
```shell
$ git clone https://github.com/Yansor/local-print-service.git
$ cd local-print-service
$ pyinstaller -i "logo.ico"  -w -F  print.py --onefile --noconsole --disable-windowed-traceback
```

## 效果预览

![效果预览](/screenshot.png)

