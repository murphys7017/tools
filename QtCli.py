import sys
from PyQt5.QtWidgets import QApplication, QWidget, QVBoxLayout, QLineEdit, QTextEdit, QLabel
from PyQt5.QtCore import Qt

class CLIApp(QWidget):
    def __init__(self):
        super().__init__()

        # 设置透明背景
        self.setWindowFlags(Qt.FramelessWindowHint)  # 去除窗口边框
        self.setAttribute(Qt.WA_TranslucentBackground)  # 设置透明背景
        self.setGeometry(100, 100, 800, 400)

        # 设置窗口背景颜色和透明度
        self.setStyleSheet("background-color: rgba(0, 0, 0, 180);")  # 设置透明黑色背景

        self.setWindowTitle("CLI 风格窗口")

        # 初始化布局和控件
        self.layout = QVBoxLayout()

        # 文本显示区域
        self.text_display = QTextEdit(self)
        self.text_display.setStyleSheet("color: #619B5F; font-size: 14px; font-family: Consolas; background-color: rgba(0, 0, 0, 180);")
        self.text_display.setReadOnly(True)  # 设置为只读
        self.text_display.setText("> CLI启动\n")  # 初始化显示

        self.layout.addWidget(self.text_display)

        # 用户输入框
        self.input_box = QLineEdit(self)
        self.input_box.setStyleSheet("color: #00FF00; font-size: 14px; font-family: Consolas; background-color: rgba(0, 0, 0, 180);")
        self.input_box.setPlaceholderText("请输入命令...")
        self.input_box.returnPressed.connect(self.handle_input)  # 绑定回车键事件

        self.layout.addWidget(self.input_box)

        self.setLayout(self.layout)

    def handle_input(self):
        """处理用户输入"""
        user_input = self.input_box.text().strip()
        if user_input.lower() == "exit":  # 输入 "exit" 退出程序
            self.close()
            return

        # 显示用户输入
        self.text_display.append(f"> {user_input}")  # 输出输入到文本框

        # 这里可以添加更复杂的处理逻辑
        response = f"你输入的命令是: {user_input}"

        # 显示响应
        self.text_display.append(response)

        # 清空输入框
        self.input_box.clear()

if __name__ == "__main__":
    app = QApplication(sys.argv)
    cli_app = CLIApp()
    cli_app.show()
    sys.exit(app.exec_())
