import os
import sys
import zipfile

from qtpy.QtWidgets import *
from qtpy.QtGui import *
from qtpy.QtCore import *

import the_files
import the_variables
import ui_models

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


# toolbar ,search 
class Dialog_for_search_options(QDialog):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.setWindowTitle("搜索选项")

        self.new_init = False

        self.new_ignore_case = True
        self.new_search_columns = tuple()
        # 列号的数字

        # 手动调用 new_func_init()

    def new_func_init(self):
        # 数列还没有载入，ui_models.columns 内容为空
        # 需要时，再画 UI

        if self.new_init:
            return
        else:
            self.new_init = True

            # 一个都不选，表示 全选
            if not self.new_search_columns:
                self.new_search_columns = tuple(n for n in range(len(ui_models.columns)))

            # 大小写
            layout = QVBoxLayout()
            group_box_1 = QGroupBox("大小写")
            group_box_layout_2 = QVBoxLayout()
            self.new_check_box_for_ignore_case = QCheckBox("忽略大小写", self)
            self.new_check_box_for_ignore_case.setChecked(self.new_ignore_case)
            #self.new_check_box_for_ignore_case.clicked.connect(self.new_func_check_ignore_case)
            group_box_layout_2.addWidget(self.new_check_box_for_ignore_case)
            group_box_1.setLayout(group_box_layout_2)
            
            # 搜索范围，选择列
            group_box_2 = QGroupBox("搜索范围，选择列")
            group_box_layout_2 = QVBoxLayout()

            self.new_check_box_list = []
            for n in range( len(ui_models.columns) ):
                column_name = ui_models.columns[n]
                the_text = column_name
                if column_name in the_variables.columns_translation:
                    the_text = the_variables.columns_translation[column_name]
                a_check_box = QCheckBox(the_text, self)
                self.new_check_box_list.append(a_check_box)
                group_box_layout_2.addWidget(a_check_box)
                if n in self.new_search_columns:
                    a_check_box.setChecked(True)
                else:
                    a_check_box.setChecked(False)
            group_box_2.setLayout(group_box_layout_2)

            set_default_button = QPushButton("默认", self)
            set_default_button.clicked.connect(self.new_func_set_default)

            ok_button = QPushButton("确定", self)
            ok_button.setDefault(True)
            ok_button.clicked.connect(self.new_func_for_ok)
            ok_button.clicked.connect(self.accept)

            cancel_button = QPushButton("取消", self)
            cancel_button.clicked.connect(self.reject)

            layout.addWidget(group_box_1)
            layout.addWidget(group_box_2)
            layout.addWidget(set_default_button)
            layout.addWidget(ok_button)
            layout.addWidget(cancel_button)

            self.setLayout(layout)

    def new_func_for_ok(self):
        if self.new_check_box_for_ignore_case.isChecked():
            self.new_ignore_case = True
        else:
            self.new_ignore_case = False

        print("ignore_case:",self.new_ignore_case)

        temp_set = set()
        for n in range( len(self.new_check_box_list) ):
            widget = self.new_check_box_list[n]
            if widget.isChecked():
                temp_set.add(n)
            else:
                temp_set.discard(n)
        self.new_search_columns = tuple(sorted(temp_set))
        
        print("for ok button:",self.new_ignore_case,self.new_search_columns)
            
    def new_func_set_default(self):
        new_ignore_case = True
        new_columns = tuple(n for n in range(len(ui_models.columns)))
        self.new_func_set_value(new_ignore_case,new_columns)
    
    def new_func_set_value(self,ignore_case,new_columns):
        self.new_ignore_case = ignore_case

        # 一个都不选，表示 全选
        if not new_columns:
            new_columns = tuple(n for n in range(len(ui_models.columns)))

        self.new_search_columns = tuple(sorted(set(new_columns))) # 去重，排序

        self.new_check_box_for_ignore_case.setChecked(self.new_ignore_case)

        for n in range( len(self.new_check_box_list) ):
            widget = self.new_check_box_list[n]
            if n in self.new_search_columns:
                widget.setChecked(True)
            else:
                widget.setChecked(False)

    def new_func_get_value(self):
        return self.new_ignore_case,self.new_search_columns
#
class Line_editor_for_search(QLineEdit):
    new_signal_for_press_enter = Signal()
    new_signal_for_press_ctrl_enter = Signal()
    new_signal_for_press_escape = Signal()
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    def keyPressEvent(self, event):
        # Qt.Key_Escape
        if event.key() == Qt.Key_Enter or event.key() == Qt.Key_Return:
            if event.modifiers() & Qt.ControlModifier:
                self.new_signal_for_press_ctrl_enter.emit()
            else:
                self.new_signal_for_press_enter.emit()
        elif event.key() == Qt.Key_Escape:
            self.clear()
            self.new_signal_for_press_escape.emit()
        else:
            super().keyPressEvent(event)
#
class Toolbars_for_search(QToolBar):

    new_signal_for_search = Signal(str,bool,bool,tuple)
    new_signal_for_clear_search = Signal()
    # 搜索字符串
    # 是否正则
    # 是否忽略大小写
    # 搜索列 范围 tuple


    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.new_ignore_case = True
        self.new_search_columns = tuple()


        self.new_ui_line_edit = Line_editor_for_search()
        self.addWidget(self.new_ui_line_edit)
        self.new_ui_line_edit.setFixedWidth(200)
        self.new_ui_line_edit.setPlaceholderText("搜索游戏列表")
        #
        self.new_ui_line_edit.new_signal_for_press_enter.connect(self.new_func_for_search)        
        self.new_ui_line_edit.new_signal_for_press_ctrl_enter.connect(self.new_func_for_search_re)
        self.new_ui_line_edit.new_signal_for_press_escape.connect(self.new_signal_for_clear_search)

        
        self.new_action_search = QAction("搜索", self)
        self.new_action_search.triggered.connect(self.new_func_for_search)
        self.addAction(self.new_action_search)

        self.new_action_search_re = QAction("正则", self)
        self.new_action_search_re.triggered.connect(self.new_func_for_search_re)
        self.addAction(self.new_action_search_re)


        self.new_action_search_options = QAction("选项", self)
        self.new_action_search_options.triggered.connect(self.new_func_for_search_options)
        self.addAction(self.new_action_search_options)

        self.new_action_clear_search = QAction("清除", self)
        self.new_action_clear_search.triggered.connect(self.new_func_for_clear_search)
        self.addAction(self.new_action_clear_search)

        self.new_dialog_for_search_options = Dialog_for_search_options()

    def new_func_get_search_settings(self):
        # 暂时先不设置了

        return self.new_signal_for_clear_search, self.new_search_columns
    
    def new_func_for_search(self):
        print("test search")

        search_string = self.new_ui_line_edit.text()

        search_string=search_string.strip()

        if search_string == "":
            return

        use_re=False
        ignore_case, search_columns = self.new_func_get_search_settings()

        self.new_signal_for_search.emit(search_string,use_re,ignore_case,search_columns)

    def new_func_for_search_re(self):
        print("test search re")

        search_string = self.new_ui_line_edit.text()

        search_string=search_string.strip()

        if search_string == "":
            return

        use_re=True
        ignore_case, search_columns = self.new_func_get_search_settings()

        self.new_signal_for_search.emit(search_string,use_re,ignore_case,search_columns)

    def new_func_for_clear_search(self):
        print("test clear search")
        self.new_ui_line_edit.clear()
        self.new_signal_for_clear_search.emit()

    def new_func_for_search_options(self):
        # 显示选项小窗口
        print()
        print("search options")

        print("before:",self.new_ignore_case,self.new_search_columns)
        self.new_dialog_for_search_options.new_func_init()
        self.new_dialog_for_search_options.new_func_set_value(self.new_ignore_case,self.new_search_columns)
        if self.new_dialog_for_search_options.exec_():
            self.new_ignore_case,self.new_search_columns = self.new_dialog_for_search_options.new_func_get_value()
            print("after:",self.new_ignore_case,self.new_search_columns)
            
