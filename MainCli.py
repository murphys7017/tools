import os
import sys
from PyQt5.QtCore import Qt, QTimer
from PyQt5.QtGui import QFont
from PyQt5.QtWidgets import QApplication, QMainWindow,QLineEdit, QVBoxLayout, QWidget
from PyQt5.QtGui import QKeySequence
from PyQt5.QtWidgets import QShortcut
from PyQt5.QtCore import QThread, pyqtSignal


from Config import GlobalVarManager
from MiraiSingleAdapter import MiraiSingleAdapter
from ScriptsManagement import ScriptManager
from loguru import logger
import Config

class WsListenerThread(QThread):
    new_message_signal = pyqtSignal(dict)  # 用于传递消息的信号

    def __init__(self,qqAdapter):
        super().__init__()
        self.qqAdapter=qqAdapter

    def run(self):
        while True:
            message = self.qqAdapter.base_message_receiver()
            self.new_message_signal.emit(message)

class CLIWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        
        self.user_name = GlobalVarManager.get('UserName')
        self.bot_name = GlobalVarManager.get('BotName')
        
        
        self.scriptManager = ScriptManager(os.path.join('scripts'))
        
        self.split_char = '>'
        self.placeholder_text = f"{self.user_name} {self.split_char} "
        
        self.setWindowTitle(f"{self.bot_name}的小窗")
        self.setGeometry(10, 800, 800, 200)
        self.setWindowFlags(Qt.FramelessWindowHint | Qt.WindowStaysOnTopHint)  # 设置无边框并且始终置顶
        self.setAttribute(Qt.WA_TranslucentBackground)  # 设置透明背景
        self.setStyleSheet("background-color: transparent;")  # 设置背景透明
        
        self.lines = []
        
        for _ in range(7):
            tempLine = QLineEdit(self)
            tempLine.setStyleSheet("""QLineEdit {
                background-color: transparent; 
                color: #619B5F; 
                font-family: 'Microsoft YaHei Light';
                font-size: 14px;
                border: none;
                padding: 0px;
                }
            """)
            tempLine.setAlignment(Qt.AlignLeft)  # 设置文本左对齐
            tempLine.setReadOnly(True)  # 文本只读
            tempLine.setContentsMargins(0, 0, 0, 0)
            self.lines.insert(0,tempLine)

        
        # 初始化显示文本
        self.line_history = [f"{self.bot_name}: 欢迎回来，{self.user_name}"]
        self.text_lines = self.line_history[-6:] 
        for line, text in zip(self.lines, self.text_lines):
            line.setText(text)  # 更新文本行
        self.lines[len(self.line_history)].setReadOnly(False)  # 文本可编辑
        self.lines[len(self.line_history)].setText(self.placeholder_text)  # >文本
        self.lines[len(self.line_history)].setFocus()
        self.lines[len(self.line_history)].setCursorPosition(len(self.placeholder_text))

        # 布局设置
        layout = QVBoxLayout()
        layout.setSpacing(-30) 
        for line in self.lines:
            layout.addWidget(line)

        container = QWidget(self)
        container.setLayout(layout)
        self.setCentralWidget(container)

        
        # 允许拖动窗口
        self.old_pos = None
        self.setMouseTracking(True)
        
        # 监听快捷键 Ctrl+Q
        self.shortcut_ctrl_q = QShortcut(QKeySequence("Ctrl+Q"), self)
        self.shortcut_ctrl_q.activated.connect(self.ctrl_q_pressed)

        self.qqAdapter = MiraiSingleAdapter()
        
        self.ws_thread = WsListenerThread(self.qqAdapter)
        self.ws_thread.new_message_signal.connect(self.on_new_message)  # 连接信号到槽
        self.ws_thread.start()  # 启动线程
    def on_new_message(self,response):
        logger.info(f"on_new_message: {response}")
                
        # choose type
        if flattened_message := self.qqAdapter.message_flattener(response):
            self.update_text_show(flattened_message)

    def ctrl_q_pressed(self):
        """Ctrl+Q 被按下时触发的操作"""
        if len(self.line_history) > 7 : 
            self.lines[6].setFocus()
            self.lines[6].setCursorPosition(len(self.placeholder_text))
        else:

            self.lines[len(self.text_lines)].setFocus()
            self.lines[len(self.text_lines)].setCursorPosition(len(self.placeholder_text))

    def keyPressEvent_bk(self, event):
        """处理回车事件"""
        if event.key() != Qt.Key_Return: 
            return
        edit_line = self.lines[len(self.text_lines)].text()
        self.line_history.append(edit_line)  # 记录用户输入
        self.line_history.append("...") 
        self.text_lines = self.line_history[-6:] 
        user_input = edit_line.split(self.split_char)[-1].strip()  # 获取用户输入
        # 获取当前输入的文本
        logger.info(f"User input: {user_input}")
        if user_input.lower() == "exit":  # 输入 "exit" 退出程序
            self.close()
            return
        
        if len(self.line_history) > 7 : 
            for line, text in zip(self.lines, self.text_lines):
                line.setText(text)  # 更新文本行
            self.lines[6].setReadOnly(False)  # 文本可编辑
            # self.lines[6].setPlaceholderText()  # 显示输入提示符
            self.lines[6].setText(self.placeholder_text)  # >文本
            self.lines[6].setFocus()
            self.lines[6].setCursorPosition(len(self.placeholder_text))
        else:
            for line, text in zip(self.lines, self.text_lines):
                line.setText(text)  # 更新文本行
            self.lines[len(self.text_lines)].setReadOnly(False)  # 文本可编辑
            # self.lines[len(self.text_lines)].setPlaceholderText("> ")  # 显示输入提示符
            self.lines[len(self.text_lines)].setText(self.placeholder_text)  # >文本
            self.lines[len(self.text_lines)].setFocus()
            self.lines[len(self.text_lines)].setCursorPosition(len(self.placeholder_text))
        
        message = {'category':'message','content':user_input}
        if user_input.startswith('/'):
            message['category'] = 'command'
        # # 显示响应
        if responses := self.scriptManager.message_handler(message):
            for response in responses:
                logger.info(f"Get chat Response: {response}")
                self.display_response(f"{self.bot_name}: {response}")
        
    def keyPressEvent(self, event):
        """处理回车事件"""
        if event.key() != Qt.Key_Return: 
            return
        edit_line = self.lines[len(self.text_lines)].text()
        self.line_history.append(edit_line)  # 记录用户输入
        self.line_history.append("...")
        self.text_lines = self.line_history[-6:]
        user_input = edit_line.split(self.split_char)[-1].strip()  # 获取用户输入
        # 获取当前输入的文本
        logger.info(f"User input: {user_input}")
        if user_input.lower() == "exit":  # 输入 "exit" 退出程序
            self.close()
            return
        
        message = {'category':'message','content':user_input}
        if user_input.startswith('/'):
            message['category'] = 'command'
        # # 显示响应
        if responses := self.scriptManager.message_handler(message):
            for response in responses:
                logger.info(f"Get chat Response: {response}")
                self.update_text_show(f"{self.bot_name}: {response}")
        # # 清空输入框
        # self.text_display.clear()
    
    def update_text_show(self,message):
        message = message.strip() 
        self.line_history.append(message)  # 记录用户输入
        self.text_lines = self.line_history[-6:]

        if len(self.line_history) > 7 : 
            for line, text in zip(self.lines, self.text_lines):
                line.setText(text)  # 更新文本行
            self.lines[6].setReadOnly(False)  # 文本可编辑
            # self.lines[6].setPlaceholderText()  # 显示输入提示符
            self.lines[6].setText(self.placeholder_text)  # >文本
            self.lines[6].setFocus()
            self.lines[6].setCursorPosition(len(self.placeholder_text))
        else:
            for line, text in zip(self.lines, self.text_lines):
                line.setText(text)  # 更新文本行
            self.lines[len(self.text_lines)].setReadOnly(False)  # 文本可编辑
            # self.lines[len(self.text_lines)].setPlaceholderText("> ")  # 显示输入提示符
            self.lines[len(self.text_lines)].setText(self.placeholder_text)  # >文本
            self.lines[len(self.text_lines)].setFocus()
            self.lines[len(self.text_lines)].setCursorPosition(len(self.placeholder_text))
        # # 显示响应
        self.display_response(message)
        
    def display_response(self, response):
        """逐字符流式显示响应"""
        self.line_history[-1] = response
        self.text_lines[-1] = ""
        def add_char(i):
            """逐个字符添加到响应文本"""
            if i < len(response):
                self.text_lines[-1] += response[i]  # 将字符追加到响应行
                if len(self.line_history) > 7 : 
                    self.lines[5].setText(self.text_lines[-1])  # 更新显示文本
                else:
                    self.lines[len(self.text_lines)-1].setText(self.text_lines[-1]) 
                QTimer.singleShot(80, lambda: add_char(i + 1))  # 每隔100ms显示下一个字符

        add_char(0)  # 从第一个字符开始

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
