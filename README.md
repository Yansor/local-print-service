# local-print-service
[README](/README.md "README") | [中文文档](/README_zh.md "中文文档")
## Introduction
A local printing service based on WebSocket, allowing for flexible data transfer.

## Features
    * Flexible selection of printer
    * Print directly without preview
    * Flexibly send data for printing

## Require
    * PYQT
    * Pyinstaller
    
## Installation
```shell
$ git clone https://github.com/Yansor/local-print-service.git
$ cd local-print-service
$ pyinstaller -i "logo.ico"  -w -F  print.py --onefile --noconsole --disable-windowed-traceback
```

## Preview
![效果预览](/screenshot.png)
