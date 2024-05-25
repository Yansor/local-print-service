from PyQt5.QtCore import QSizeF, QRectF, Qt, QSettings
from PyQt5.QtGui import QPainter, QTextOption, QFont, QFontMetrics
from PyQt5.QtPrintSupport import QPrinter
from PyQt5.QtWidgets import QDialog

# 解析json数据 打印
class NewPrint(QDialog):
    def __init__(self, parent=None):
        try:
            super().__init__(parent)
            self.printer = QPrinter()
            self.printer.setFullPage(True)
            self.printer.setPaperSize(QSizeF(210, 140), QPrinter.Millimeter)
            self.printer.setOutputFormat(QPrinter.NativeFormat)
            self.load_saved_printer()
        except Exception as e:
            print(f"Error occurred while initializing printer: {e}")

    # 读取打印机
    def load_saved_printer(self):
        settings = QSettings("MyCompany", "MyApp")
        saved_printer = settings.value("printer")
        print(f"打印机名称: {saved_printer}")
        if saved_printer is not None:
            self.printer.setPrinterName(saved_printer)

    def handle_print(self):
        try:
            painter = QPainter(self.printer)
            meter_width = self.printer.widthMM()
            meter_height = self.printer.heightMM()
            px_width = self.printer.width()
            px_height = self.printer.height()

            for header in self.h_info:
                self.draw_header(painter, meter_width, meter_height, header)

            line_height = self.t_height
            for row in self.l_info:
                self.draw_row(painter, meter_width, px_width, meter_height, px_height, line_height, row)

            return True

        except Exception as e:
            raise RuntimeError(f"Error occurred while printing: {e}")

    def parse_data(self, data):
        try:
            self.h_info = data.get('page_title', [])
            self.l_info = data.get('table_list', [])
            self.t_height = float(data.get('list_height', 0))

        except KeyError as e:
            raise RuntimeError(f"Data parsing error: Missing key {e}")

        except Exception as e:
            raise RuntimeError(f"Error occurred while parsing data: {e}")

    def draw_header(self, painter, meter_width, meter_height, header):
        option = QTextOption(Qt.AlignCenter)
        option.setWrapMode(QTextOption.WordWrap)
        font_size = header.get('font_size', 10)
        titleFont = QFont("宋体", int(font_size))
        painter.setFont(titleFont)
        painter.setPen(Qt.black)
        x = self.cal_px(meter_width, header['x'])
        y = self.cal_px(meter_height, header['y'])
        if header['type'] == "square":
            w = self.cal_px(meter_width, header['width'])
            h = self.t_height * 2
            painter.drawText(QRectF(x + 3, y + 3, w, h - 4), str(header['title']))
        else:
            painter.drawText(x, y, header['title'])

    def draw_row(self, painter, meter_width, px_width, meter_height, px_height, line_height, row):
        x = 0
        y = 0
        optionTitle = QTextOption(Qt.AlignCenter | Qt.AlignVCenter)
        for cell in row:
            font_size = cell.get('font_size', 11)
            titleFont = QFont("宋体", int(font_size))
            painter.setFont(titleFont)
            if x == 0:
                x = self.cal_px(meter_width, cell['x'])
            if y == 0:
                y = self.cal_px(meter_height, cell['y'])
            t = cell['title']
            w = self.cal_px(meter_width, cell['width'])
            painter.drawRect(x, y, w, line_height)
            qFontM = QFontMetrics(titleFont)
            painter.drawText(QRectF(x + 3, y + 3, w - 4, line_height - 4), qFontM.elidedText(str(t), Qt.ElideRight, w - 4), optionTitle)
            x += w
            y += line_height

    def cal_px(self, meter, x):
        return int(float(x) / float(meter) * self.printer.width())
