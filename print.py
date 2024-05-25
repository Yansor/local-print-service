import asyncio
import json
import socket
import sys
import PrintClass

import websockets
from PyQt5.QtCore import Qt, QObject, pyqtSignal, QSettings
from PyQt5.QtGui import QIcon
from PyQt5.QtWidgets import QApplication, QWidget, QVBoxLayout, QLabel, QComboBox, QHBoxLayout, QMessageBox, \
    QDesktopWidget, QPushButton, QSystemTrayIcon, QMenu
from PyQt5.QtPrintSupport import QPrinterInfo
from threading import Thread

port = 5000

# websocket server
class WebSocketServer(Thread):
    def __init__(self):
        super().__init__()
        self.daemon = True
        self.client_count = 0
        self.update_count_signal = UpdateCountSignal()

    def run(self):
        asyncio.set_event_loop(asyncio.new_event_loop())
        start_server = websockets.serve(self.handle_message, "localhost", port)
        asyncio.get_event_loop().run_until_complete(start_server)
        asyncio.get_event_loop().run_forever()

    # 接受消息处理
    async def handle_message(self, websocket, path):
        print("客户端个数:", self.client_count)
        self.client_count += 1
        self.update_count_signal.update_count.emit(self.client_count)

        try:
            async for message in websocket:
                print("Received data from client:", message)
                try:

                    # 读取本地文件 测试
                    # file = open("data.json", "r", encoding='utf-8')
                    # message = file.read()

                    # 获取客户端发送内容
                    data = json.loads(message)

                    # 以下可根据自己打印模板实际情况调整里面程序
                    painter = PrintClass.NewPrint()
                    painter.parse_data(data)
                    painter.handle_print()

                    resp = json.dumps({'code': 0, 'msg': '打印成功'})
                    await websocket.send(f"{resp}")
                except Exception as e:
                    resp = json.dumps({'code': 1, 'msg': str(e)})
                    await websocket.send(f"{resp}")

        except websockets.exceptions.ConnectionClosedError:
            pass
        finally:
            self.client_count -= 1
            self.update_count_signal.update_count.emit(self.client_count)

class UpdateCountSignal(QObject):
    update_count = pyqtSignal(int)

class PrintApp(QWidget):
    def __init__(self):
        super().__init__()
        self.initUI()

    def initUI(self):
        self.setWindowTitle('打印服务')
        self.setGeometry(0, 0, 400, 150)
        self.setMinimumSize(300, 150)
        self.setMaximumSize(500, 150)
        self.center()
        icon = QIcon('logo.ico')
        self.setWindowIcon(icon)

        layout = QVBoxLayout()

        printer_layout = QHBoxLayout()
        printer_label = QLabel("打印机:")
        printer_layout.addWidget(printer_label)
        self.printer_combo = QComboBox()
        self.printer_combo.addItems(self.get_printer_list())
        printer_layout.addWidget(self.printer_combo)

        # 加载设置的打印机
        self.load_saved_printer()

        # 保存按钮
        save_button = QPushButton("保存打印机")
        save_button.clicked.connect(self.save_printer)
        printer_layout.addWidget(save_button)
        layout.addLayout(printer_layout)

        self.client_count_label = QLabel()
        self.client_count_label.setText(f"当前客户端连接数: 0")
        layout.addWidget(self.client_count_label)

        self.tray_icon = QSystemTrayIcon(self)
        self.tray_icon.setIcon(icon)
        self.tray_icon.setToolTip('打印服务')
        self.tray_icon.show()
        self.tray_icon.activated.connect(self.on_tray_icon_activated)

        # 创建托盘菜单
        tray_menu = QMenu()
        restore_action = tray_menu.addAction("恢复")
        quit_action = tray_menu.addAction("退出")

        # 将槽函数与动作关联
        restore_action.triggered.connect(self.showNormal)
        quit_action.triggered.connect(self.exit_app)

        # 设置托盘菜单
        self.tray_icon.setContextMenu(tray_menu)

        self.setLayout(layout)

        if self.check_port_in_use(port):
            QMessageBox.critical(None, "错误", f"端口 {port} 已被占用，请先释放该端口！", QMessageBox.Ok)
            sys.exit(1)

        # 启动 WebSocket 服务器
        self.server_thread = WebSocketServer()
        self.server_thread.start()

        # 连接信号与槽
        self.server_thread.update_count_signal.update_count.connect(self.update_client_count)

    def update_client_count(self, count):
        self.client_count_label.setText(f"当前客户端连接数: {count}")

    # 打印机列表
    def get_printer_list(self):
        printer_list = []
        printers = QPrinterInfo.availablePrinters()
        for printer in printers:
            printer_list.append(printer.printerName())
        return printer_list

    # 窗口居中
    def center(self):
        # 获取屏幕的几何信息
        screen = QDesktopWidget().availableGeometry()
        # 获取窗口的几何信息
        window_rect = self.frameGeometry()
        # 将窗口移动到屏幕中心
        window_rect.moveCenter(screen.center())
        self.move(window_rect.topLeft())

    # 保存打印机
    def save_printer(self):
        selected_printer = self.printer_combo.currentText()
        settings = QSettings("MyCompany", "MyApp")
        settings.setValue("printer", selected_printer)
        QMessageBox.information(self, "保存成功", f"已保存选择的打印机为: {selected_printer}")

    # 读取打印机
    def load_saved_printer(self):
        settings = QSettings("MyCompany", "MyApp")
        saved_printer = settings.value("printer")
        if saved_printer is not None:
            index = self.printer_combo.findText(saved_printer)
            if index != -1:
                self.printer_combo.setCurrentIndex(index)

    # 最小化, 任务栏不显示
    def changeEvent(self, event):
        if event.type() == event.WindowStateChange:
            if self.windowState() & Qt.WindowMinimized:
                self.hide()
                event.ignore()

    # 关闭事件处理, 不关闭，只是隐藏，真正的关闭操作在托盘图标菜单里
    def closeEvent(self, event):
        if self.tray_icon.isVisible():
            QMessageBox.information(self, '系统托盘',
                                    '程序将继续在系统托盘中运行，要终止本程序，\n'
                                    '请在系统托盘入口的菜单中选择"退出"')
            self.hide()
            event.ignore()

    # 双击还原
    def on_tray_icon_activated(self, reason):
        if reason == QSystemTrayIcon.DoubleClick:
            self.showNormal()
            self.activateWindow()

    # 退出
    def exit_app(self):
        self.tray_icon.hide()
        QApplication.instance().quit()

    # 验证端口
    def check_port_in_use(self, port, host='127.0.0.1'):
        print(f"端口号: {port}")
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            try:
                s.bind((host, port))
                return False
            except OSError as e:
                print(f"Port check error: {e}")
                return True


if __name__ == '__main__':
    app = QApplication(sys.argv)
    window = PrintApp()
    window.show()
    sys.exit(app.exec_())
