import os
import sys
import zipfile

from qtpy.QtWidgets import *
from qtpy.QtGui import *
from qtpy.QtCore import *

import the_files
import the_variables

class Dialog_to_choose_emulator_path(QDialog):  

    # signal
    # mame_path , mame_working_directory
    new_signal_for_emulator_path_and_working_directory = Signal(str,str)

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        # 不显示关闭按钮
        self.setWindowFlags(self.windowFlags() & ~Qt.WindowCloseButtonHint)

        parent = self.parentWidget()
        self.new_signal_for_emulator_path_and_working_directory.connect(parent.new_func_slot_to_receive_emulator_path_and_working_dir)

        self.setSizeGripEnabled(True)


        self.setWindowTitle("选择模拟器")

        self.setMinimumWidth(500)
        self.setMinimumHeight(300)

        # 垂直布局管理器
        layout = QVBoxLayout()

        # 第一行布局
        first_row_layout = QHBoxLayout()
        self.new_label_for_mame_path = QLabel("MAME 路径:")
        self.new_line_edit1 = QLineEdit()
        button1 = QPushButton("...")
        button1.clicked.connect(self.new_func_for_choose_mame_executable)
        first_row_layout.addWidget(self.new_label_for_mame_path)
        first_row_layout.addWidget(self.new_line_edit1)
        first_row_layout.addWidget(button1)
        layout.addLayout(first_row_layout)

        # 第二行布局
        second_row_layout = QHBoxLayout()
        label21 = QLabel("MAME 工作目录:")
        self.new_line_edit2 = QLineEdit()
        button2 = QPushButton("...")
        second_row_layout.addWidget(label21)
        second_row_layout.addWidget(self.new_line_edit2)
        second_row_layout.addWidget(button2)
        layout.addLayout(second_row_layout)

        # 添加一个按钮以演示如何关闭对话框（可选）
        button = QPushButton("确认")
        button.clicked.connect(self.new_func_for_close_this_dialog)
        layout.addWidget(button)

        button = QPushButton("放弃")
        button.clicked.connect(sys.exit)
        layout.addWidget(button)        

        self.setLayout(layout)

    def new_func_set_values(self,mame_path="", mame_working_directory=""):
        self.new_line_edit1.setText(mame_path)
        self.new_line_edit2.setText(mame_working_directory)
    def new_func_for_close_this_dialog(self,checked):

        mame_path = self.new_line_edit1.text()
        if mame_path :
            print("mame_path: ",mame_path)
        
        mame_working_directory = self.new_line_edit2.text()
        if mame_working_directory :
            if os.path.isdir(mame_working_directory):
                print("mame_working_directory: ",mame_working_directory)
                
        self.new_signal_for_emulator_path_and_working_directory.emit(mame_path,mame_working_directory)
        parent = self.parentWidget()
        
        self.close()
    
    def new_func_for_choose_mame_executable(self,checked):
        print("选择 MAME 可执行文件")
        file_path = QFileDialog.getOpenFileName(
            self,
            "选择一个可执行文件",
            "",  # 默认起始目录，空表示当前目录或上次使用的目录
            "可执行文件 (*.exe *.bat *.cmd *.com);;所有文件 (*.*)"  # Windows 常用可执行文件
            # 对于 macOS 可以改为 "应用程序 (*.app);;所有文件 (*)"
            # 对于 Linux 可以改为 "可执行文件 (*);;所有文件 (*)"
            )
        if file_path :
            print("file_path: ",file_path)
            self.new_line_edit1.setText(file_path[0])


class Search_Line(QLineEdit):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.setPlaceholderText("搜索")

        #self.returnPressed.connect(self.new_func_for_search)

class Image_dockwidget(QDockWidget):

        # closeEvent
        # showEvent
        # hideEvent    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.new_label_for_image = QLabel(self)
        self.setWidget(self.new_label_for_image)
        # 居中
        self.new_label_for_image.setAlignment(Qt.AlignCenter )
        #self.new_label_for_image.setScaledContents(True) 这个缩放不保持比例的
        
        # 窗口大小变化 ？？？
        self.new_label_for_image.setSizePolicy(QSizePolicy.Ignored, QSizePolicy.Ignored)        


        self.new_the_old_id = None
        self.new_zip_file_path = ""
        self.new_zip_opened_file = None

        self.new_pixmap_original = None

        self.new_visible = False
        self.visibilityChanged.connect(self.new_func_for_visibilityChanged)

    @Slot(str)
    def new_slot_for_id_change(self,game_id=""):

        #if not self.isVisible(): # 在签标页面 重叠时，不管用
        #    return

        if not self.new_visible:
            return

        #print()
        #print("slot for image :",self.objectName())
        if not game_id:
            return

        if game_id != the_variables.current_id:
            return
    
        if self.new_func_get_image_from_file(game_id):
            self.new_the_old_id = game_id
            return
    
        if self.new_func_get_image_from_zip(game_id):
            self.new_the_old_id = game_id
            return
        
        # 没有内容，但记录 id
        self.new_the_old_id = game_id

        # 没有内容,清空图片
        self.new_func_clear_image()
    
    def new_func_get_image_from_file(self,game_id=""):
        folder_path = the_variables.extra_image_folder_path["extra_image_folder_path/"+self.objectName()]
        
        if not folder_path:
            return
        
        file_path = os.path.join(folder_path,game_id+".png")
        if not os.path.isfile(file_path):
            return

        try:
            pixmap = QPixmap(file_path)
            scaled_pixmap = pixmap.scaled(
                self.new_label_for_image.size(),                  # 目标大小
                Qt.KeepAspectRatio,            # 保持宽高比[reference:5]
                Qt.SmoothTransformation        # 平滑变换[reference:6]
                )            
            self.new_label_for_image.setPixmap(scaled_pixmap)
            self.new_pixmap_original = pixmap
            return True
        except:
            pass

    def new_func_get_image_from_zip(self,game_id=""):
        zip_file_path = the_variables.extra_image_zip_path["extra_image_zip_path/"+self.objectName()]
        
        #print(zip_file_path)
        #print(self.new_zip_file_path)
        #print(self.new_zip_opened_file)

        if not zip_file_path:
            if self.new_zip_opened_file is not None:
                self.new_func_close_zip()
            return
        
        if not os.path.isfile(zip_file_path):
            if self.new_zip_opened_file is not None:
                self.new_func_close_zip()
            return
        
        # 文件变化，打开新文件
        if zip_file_path != self.new_zip_file_path:
            if self.new_zip_opened_file is not None:
                self.new_func_close_zip()
            self.new_func_open_zip(zip_file_path)

        # 从 zip 文件中读取图片
        if self.new_zip_opened_file is not None:
            image_file_path = game_id+".png"
            #print(image_file_path)
            try:
                with self.new_zip_opened_file.open(image_file_path, mode='r', ) as image_data:

                    pixmap=QPixmap()
                    pixmap.loadFromData(image_data.read()) 
                    scaled_pixmap = pixmap.scaled(
                        self.new_label_for_image.size(),                  # 目标大小
                        Qt.KeepAspectRatio,            # 保持宽高比[reference:5]
                        Qt.SmoothTransformation        # 平滑变换[reference:6]
                        )      
                    self.new_label_for_image.setPixmap(scaled_pixmap)
                    self.new_pixmap_original = pixmap
                    
                    #print(zip_file_path)
                    #print(image_file_path)
                    return True

            except:
                pass

    def new_func_open_zip(self,zip_file_path):
        try:
            self.new_zip_opened_file = zipfile.ZipFile(zip_file_path, mode='r',  allowZip64=True,)
            self.new_zip_file_path = zip_file_path
        except:
            self.new_zip_file_path = ""
            self.new_zip_opened_file = None
    
    def new_func_close_zip(self):
        if not self.new_zip_opened_file:
            try:
                self.new_zip_opened_file.close()
                self.new_zip_opened_file = None
                self.new_zip_file_path = ""
            except:
                pass

    def new_func_clear_image(self):
        self.new_label_for_image.clear()
        self.new_pixmap_original= None

    def closeEvent(self, event):
        self.new_func_close_zip()

        super().closeEvent(event)


    def resizeEvent(self, event):
        self.new_func_update_pixmap()
        super().resizeEvent(event)

    def new_func_update_pixmap(self):
        if self.new_pixmap_original :
            if not self.new_label_for_image.size().isEmpty():

                scaled_pixmap = self.new_pixmap_original.scaled(
                    self.new_label_for_image.size(),
                    Qt.KeepAspectRatio,
                    Qt.SmoothTransformation
                )

                self.new_label_for_image.setPixmap(scaled_pixmap)

    @Slot(bool)
    def new_func_for_visibilityChanged(self,visible):
        self.new_visible = visible