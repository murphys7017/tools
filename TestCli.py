import sys
from PyQt5.QtCore import Qt, QTimer
from PyQt5.QtGui import QColor, QFont
from PyQt5.QtWidgets import QApplication, QMainWindow, QTextEdit, QLineEdit, QVBoxLayout, QWidget
from ollama_qw import OllamaQW
from loguru import logger

class CLIWindow(QMainWindow):
    def __init__(self):
        super().__init__()

        self.setWindowTitle("CLI 样式窗口")
        self.setGeometry(100, 100, 800, 200)
        self.setWindowFlags(Qt.FramelessWindowHint | Qt.WindowStaysOnTopHint)  # 设置无边框并且始终置顶
        self.setAttribute(Qt.WA_TranslucentBackground)  # 设置透明背景
        self.setStyleSheet("background-color: transparent;")  # 设置背景透明

        # 初始化 Ollama 模型
        # self.qwen_model = OllamaQW()
        # 设置窗口的样式以去掉边框和背景
        self.setStyleSheet("""
            background-color: transparent;  # 窗口背景透明
            border: none;  # 去除窗口边框
        """)

        # 创建显示区域：用于展示命令和响应
        self.text_display = QTextEdit(self)
        self.text_display.setReadOnly(True)
        
        self.text_display.setStyleSheet("""
            background-color: transparent;
            color: #619B5F;  # 科幻绿色
            font-family: 'Microsoft YaHei Light';
            font-size: 12px;
            border: none;
            padding: 10px;
        """)
        self.text_display.setCursorWidth(2)  # 设置光标宽度
        self.text_display.setTextInteractionFlags(Qt.TextEditorInteraction)  # 允许文本编辑器互动
        self.text_display.setAlignment(Qt.AlignLeft)  # 设置文本左对齐
        self.text_display.setVerticalScrollBarPolicy(Qt.ScrollBarAlwaysOff)  # 禁用滚动条

        # 创建输入框：用于接受用户输入
        self.input_box = QLineEdit(self)
        # 修改 QTextEdit 的样式，去掉边框和外边距
        self.text_display.setStyleSheet("""
            background-color: transparent;  # 设置透明背景
            color: #619B5F;  # 科幻绿色
            font-family: 'Microsoft YaHei Light';
            font-size: 12px;
            border: none;  # 去掉边框
            padding: 0px;  # 去掉内边距
            margin: 0px;  # 去掉外边距
        """)
        # self.input_box.setStyleSheet("""
        #     background-color: transparent;
        #     color: white;
        #     font-family: 'Microsoft YaHei Light';
        #     font-size: 12px;
        #     border: none;
        #     padding: 5px;
        # """)
        self.input_box.returnPressed.connect(self.handle_input)  # 回车触发输入处理

        # 布局设置
        layout = QVBoxLayout()
        layout.addWidget(self.text_display)
        layout.addWidget(self.input_box)

        container = QWidget(self)
        container.setLayout(layout)
        self.setCentralWidget(container)

        # 初始化显示文本
        self.text_lines = ["Alice: 欢迎回来，Yakumo", "> "]
        self.text_display.setText("\n".join(self.text_lines))

        # 允许拖动窗口
        self.old_pos = None
        self.setMouseTracking(True)

    def handle_input(self):
        """处理用户输入"""
        user_input = self.input_box.text().strip()
        logger.info(f"User input: {user_input}")

        if user_input.lower() == "exit":  # 输入 "exit" 退出程序
            self.close()
            return

        # 更新文本行：添加用户输入并准备新的提示符
        self.text_lines[-1] += user_input  # 在最后一行加入用户输入
        self.text_lines.append("")  # 响应占位
        self.text_lines.append("> ")  # 添加新的提示符
        self.update_display()

        # 显示响应
        # response = self.qwen_model.chat(user_input)
        response = {
            'content':"Alice:" + user_input
        }
        
        logger.info(f"Get chat Response: {response}")
        self.display_response("Alice: " + response['content'])

        # 清空输入框
        self.input_box.clear()

    def display_response(self, response):
        """逐字符流式显示响应"""
        # 确保响应占位符存在
        if len(self.text_lines) < 2 or self.text_lines[-2] != "":
            self.text_lines.insert(-1, "")  # 在提示符前插入空行作为响应

        def add_char(i):
            """逐个字符添加到响应文本"""
            if i < len(response):
                self.text_lines[-2] += response[i]  # 将字符追加到响应行
                self.update_display()
                QTimer.singleShot(100, lambda: add_char(i + 1))  # 每隔100ms显示下一个字符

        add_char(0)  # 从第一个字符开始

    def update_display(self):
        """更新文本显示区域"""
        self.text_display.setText("\n".join(self.text_lines))  # 更新显示文本

    def mousePressEvent(self, event):
        """允许窗口拖动"""
        if event.button() == Qt.LeftButton:
            self.old_pos = event.globalPos()

    def mouseMoveEvent(self, event):
        """拖动窗口"""
        if self.old_pos:
            delta = event.globalPos() - self.old_pos
            self.move(self.x() + delta.x(), self.y() + delta.y())
            self.old_pos = event.globalPos()

    def mouseReleaseEvent(self, event):
        """释放鼠标时重置位置"""
        self.old_pos = None

def main():
    app = QApplication(sys.argv)
    window = CLIWindow()
    window.show()
    sys.exit(app.exec_())

if __name__ == "__main__":
    main()
