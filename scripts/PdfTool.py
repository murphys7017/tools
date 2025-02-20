from PluginBase import PluginBase
class PdfTool(PluginBase):
    """所有脚本的抽象基类"""

    def __init__(
        self, 
        script_name: str ='pdftool', 
        author: str = 'alice',
        category: str= 'command', 
        route: str = 'startswith:/pdf',
        priority: int=10,
        need_thread=False,
        is_multi=False,
        multi_round=1
        ):
        super().__init__(script_name='pdftool',author='alice',category='command', route='startswith:/pdf')
        """初始化方法，必须调用 super
            script_name 
            author
            category = message|command|event
            route: str = path startswith:xxx,endswith:xxx,containswith:xxx
            priority = 1-> 999
        """
        
        
        self.script_name = script_name
        self.author = author
        self.category = category
        self.route = route
        self.priority = priority
        self.need_thread = need_thread
        self.is_multi = is_multi
        self.multi_round = multi_round
        self.thread = None
        
        
        self.multi_round_count = self.multi_round
        
        self._initialized = True  # 标记初始化完成
        if not hasattr(self, "_initialized"):  # 检查子类是否已经初始化
            raise RuntimeError(f"{self.__class__.__name__} must call super().__init__()")
    

    def check_message(self,message):
        """检查队列消息，判断是否启动脚本，同时移除使用的消息
        """
        return bool(message.startswith('/pdf '))

    
    def handle(self,message):
        commands = message.split('/pdf ')[1]
        if commands.startswith('unlock '):
            file_path = commands.split('unlock ')[1]
        
            from PyPDF2 import PdfReader #pdf的读取方法
            from PyPDF2 import PdfWriter #pdf的写入方法
            from Crypto.Cipher import AES #高加密的方法，要引入不然会报错
            """文件处理方法
            处理完成之后调用send_result返回处理结果
            status code: 200 完成, 400 此插件异常 201多步插件，等待下一轮对话
            return status code,result
            """
            
            def get_reader(filename, password): #读取pdf的方法（自定义函数）
                try:
                    old_file = open(filename, 'rb')
                    print('解密开始...')
                except Exception as err:
                    return print('文件打开失败！' + str(err))

                #如果是python2将PdfReader改为PdfFileReader
                pdf_reader = PdfReader(old_file, strict=False) #读取pdf文件

                # 如果是python2将is_encrypted改为isEncrypted
                if pdf_reader.is_encrypted: #解密操作（以下操作是自适应，不会展示在终端中）
                    if password is None:
                        return print('文件被加密，需要密码！--{}'.format(filename))
                    else:
                        if pdf_reader.decrypt(password) != 1:
                            return print('密码不正确！--{}'.format(filename))
                elif old_file in locals():
                    old_file.close() #如果pdf文件已经在本地了就关闭
                return pdf_reader #返回读出pdf的值
                
            def deception_pdf(filename, password, decrypted_filename=None): #生成新pdf的方法（自定义函数）
                print('正在生成解密...')
                pdf_reader = get_reader(filename, password) #得到传入的文件名，和密码（如果密码没有可以不填）
                if pdf_reader is None:
                    return print("无内容读取")

                # 如果是python2将is_encrypted改为isEncrypted
                elif not pdf_reader.is_encrypted:
                    return print('文件没有被加密，无需操作')

                # 如果是python2将PdfWriter改为PdfFileWriter
                pdf_writer = PdfWriter() #写pdf（记录pdf内容）

                #如果是python2将append_pages_from_reader改为appendPagesFromReader
                pdf_writer.append_pages_from_reader(pdf_reader)

                if decrypted_filename is None: #创建解密后的pdf文件和展示文件的路径
                    decrypted_filename = "".join(filename.split('.')[:-1]) + '_' + '已解密' + '.pdf'
                    print("解密文件已生成:{}".format(decrypted_filename))
                # 写入新文件
                pdf_writer.write(open(decrypted_filename, 'wb'))

            deception_pdf(file_path, '')
            return 200,['解密文件已生成']
        if commands.startswith('unlock '):
            file_path = commands.split('2docx ')[1]
            from pdf2docx import Converter

            def pdf_to_word_pdf2docx(pdf_path, word_path):
                cv = Converter(pdf_path)
                cv.convert(word_path, start=0, end=None)
                cv.close()
            pdf_to_word_pdf2docx(file_path,file_path.replace('pdf', 'docx'))
