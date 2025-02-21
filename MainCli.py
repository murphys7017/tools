import os
import sys
from PyQt5.QtCore import Qt, QTimer, QThread, pyqtSignal , QMutex, QMutexLocker, QMetaObject
from PyQt5.QtGui import QFont, QKeySequence, QTextOption ,QTextCursor
from PyQt5.QtWidgets import QApplication, QMainWindow,QLineEdit, QVBoxLayout, QWidget ,QShortcut, QTextEdit,QSizePolicy

from Config import GlobalVarManager
from MiraiSingleAdapter import MiraiSingleAdapter
from ScriptsManagement import ScriptManager
from loguru import logger

class WsListenerThread(QThread):
    qq_message_signal = pyqtSignal(dict)  # 用于传递消息的信号

    def __init__(self,qqAdapter):
        super().__init__()
        self.qqAdapter=qqAdapter
        GlobalVarManager.set('qqAdapter',qqAdapter)

    def run(self):
        while True:
            message = self.qqAdapter.base_message_receiver()
            self.qq_message_signal.emit(message)

class ScriptManagerPressThread(QThread):
    script_manager_result_signal = pyqtSignal(str)
    def __init__(self, script_manager, message):
        super().__init__()
        self.script_manager = script_manager
        self.message = message

    def run(self):
        if responses := self.script_manager.message_handler(self.message):
            for res in responses:
                logger.info(f"Get chat Response: {res}")
                # 使用信号将处理结果返回到主线程
                self.script_manager_result_signal.emit(res)
                
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
        #background-color: transparent; 
        #   color: #619B5F; 
        for _ in range(7):
            tempLine = QTextEdit(self)
            tempLine.setStyleSheet("""QTextEdit {
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
            tempLine.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
            tempLine.setWordWrapMode(QTextOption.WrapAnywhere)
            tempLine.setVerticalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
            self.lines.insert(0,self.on_text_changed(target_line=0,textExit=tempLine))

        self.on_text_changed(0)
        # 初始化显示文本
        self.line_history = [f"{self.bot_name}: 欢迎回来，{self.user_name}"]
        self.text_lines = self.line_history[-6:] 
        for line, text in zip(self.lines, self.text_lines):
            line.setText(text)  # 更新文本行
        self.lines[len(self.line_history)].setReadOnly(False)  # 文本可编辑
        self.lines[len(self.line_history)].setText(self.placeholder_text)  # >文本
        self.lines[len(self.line_history)].setFocus()
        cursor = self.lines[len(self.line_history)].textCursor()
        cursor.movePosition(QTextCursor.End) # 还可以有别的位置
        self.lines[len(self.line_history)].setTextCursor(cursor)
        self.on_text_changed(len(self.line_history))

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
        self.ws_thread.qq_message_signal.connect(self.on_qq_message)  # 连接信号到槽
        self.ws_thread.start()  # 启动线程
        
        self.mutex = QMutex() 
        
        
        # 定时器，模拟加载文本
        self.loading_timer = QTimer(self)
        self.loading_timer.timeout.connect(self.update_loading_text)
        self.dots_count = 0  # 计数，控制文本变化
        
        
        # 连接键盘事件信号与槽函数
        # self.plaintextedit.keyPressEvent = self.handle_keypress
        
    def on_qq_message(self,response):
        logger.info(f"on_new_message: {response}")
                
        # choose type
        if flattened_message := self.qqAdapter.message_flattener(response):
            self.update_text_show(flattened_message)
    def on_script_manager_message(self,response):
        logger.info(f"script_manager_result_signal :{response}")
        if self.loading_timer.isActive():
            self.loading_timer.stop()
            self.lines[len(self.text_lines)].setText(self.placeholder_text)  # >文本
            self.lines[len(self.text_lines)].setReadOnly(True)  # 文本可编辑
        self.update_text_show(f"{self.bot_name}: {response}")
    def ctrl_q_pressed(self):
        """Ctrl+Q 被按下时触发的操作"""
        if len(self.line_history) > 7 : 
            self.lines[6].setFocus()
            cursor = self.lines[len(self.line_history)].textCursor()
            cursor.movePosition(QTextCursor.End) # 还可以有别的位置
            self.lines[len(self.line_history)].setTextCursor(cursor)
        else:

            self.lines[len(self.text_lines)].setFocus()
            cursor = self.lines[len(self.line_history)].textCursor()
            cursor.movePosition(QTextCursor.End) # 还可以有别的位置
            self.lines[len(self.line_history)].setTextCursor(cursor)


    def keyPressEvent(self, event):
        """处理回车事件"""
        logger.info(event)
        if event.key() == Qt.Key_Enter:
            print(111)
        if event.key() == Qt.Key_Return or event.key() == Qt.Key_Enter:
            pass
        else:
            super().keyPressEvent(event)
        edit_line = self.lines[len(self.text_lines)].toPlainText()
        user_input = edit_line.split(self.split_char)[-1].strip()  # 获取用户输入
        # 获取当前输入的文本
        logger.info(f"User input: {user_input}")
        if user_input.lower() == "exit":  # 输入 "exit" 退出程序
            self.close()
            return
        
        self.update_text_show(edit_line,need_stream_show=False)
        
        message = {'category':'message','content':user_input}
        if user_input.startswith('/'):
            message['category'] = 'command'
        # # 显示响应
        
        self.script_manager_thread = ScriptManagerPressThread(self.scriptManager,message)
        self.script_manager_thread.script_manager_result_signal.connect(self.on_script_manager_message)  # 连接信号到槽
        self.script_manager_thread.start()  # 启动线程
        # 开始显示 "..."（类似于loading效果）
        self.dots_count = 0  # 重置计数
        self.loading_timer.start(500)  # 每隔500ms更新一次文本，模拟加载效果
        self.lines[len(self.text_lines)].setReadOnly(False)  # 文本可编辑
        
    def update_loading_text(self):
        """更新加载文本"""
        # 根据计数更新文本
        if self.dots_count < 5:
            self.lines[len(self.text_lines)].setText(self.placeholder_text + '.' * self.dots_count)  # >文本
            self.dots_count += 1
        else:
            self.dots_count = 1


    def update_text_show(self,message, need_stream_show=True):
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
                cursor = self.lines[6].textCursor()
                cursor.movePosition(QTextCursor.End) # 还可以有别的位置
                self.lines[6].setTextCursor(cursor)
            else:
                for line, text in zip(self.lines, self.text_lines):
                    line.setText(text)  # 更新文本行
                self.lines[len(self.text_lines)].setReadOnly(False)  # 文本可编辑
                # self.lines[len(self.text_lines)].setPlaceholderText("> ")  # 显示输入提示符
                self.lines[len(self.text_lines)].setText(self.placeholder_text)  # >文本
                self.lines[len(self.text_lines)].setFocus()
                cursor = self.lines[len(self.line_history)].textCursor()
                cursor.movePosition(QTextCursor.End) # 还可以有别的位置
                self.lines[len(self.line_history)].setTextCursor(cursor)
            # # 显示响应
            if need_stream_show:
                self.display_response(message)
    def on_text_changed(self,target_line,textExit=None):
            """文本变化时自动调整大小"""
            if textExit:
                document = textExit.document()
            else:
                document = self.lines[target_line].document()
            
            # 获取文档中的总行数
            block_count = document.blockCount()

            # 计算每行的高度，依据字体大小进行推算
            line_height = document.documentLayout().blockBoundingRect(document.findBlockByNumber(0)).height()

            # 计算总高度
            total_height = block_count * line_height + 6
            
            # 设置最小和最大高度
            if textExit:
                textExit.setMinimumHeight(int(total_height))
                textExit.setMaximumHeight(int(total_height))
                return textExit
            else:
                self.lines[target_line].setMinimumHeight(int(total_height))  # 设置最小高度
                self.lines[target_line].setMaximumHeight(int(total_height))  # 设置最大高度
    def display_response(self, response, index=0):
        """逐字符显示"""
        if index >= len(response):
            return  # 递归终止条件
        with QMutexLocker(self.mutex):
            self.text_lines[-1] = response[:index+1]
        
            
            if len(self.line_history) > 7:
                target_line = 5
            else:
                target_line = len(self.text_lines) - 1
            
            if target_line < len(self.lines):
                self.on_text_changed(target_line)
                self.lines[target_line].setText(self.text_lines[-1])
        
        QTimer.singleShot(100, lambda: self.display_response(response, index + 1))
            
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
