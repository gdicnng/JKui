import os
import sys
import zipfile
import pickle
import functools

import qtpy
from qtpy.QtWidgets import *
from qtpy.QtGui import *
from qtpy.QtCore import *

import the_files
import the_variables
import ui_models
import extra_database
import misc_funcs

# 初始化时，设置 模拟器路径
class Dialog_to_choose_emulator_path(QDialog):  

    def __init__(self,qsettings, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.new_settings = qsettings

        # 不显示关闭按钮
        self.setWindowFlags(self.windowFlags() & ~Qt.WindowCloseButtonHint)

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
        #self.new_line_edit2.setPlaceholderText("大多数情况可以忽略；但不可以乱填")
        #self.new_line_edit2.setDisabled(True)
        button2 = QPushButton("...")
        button2.clicked.connect(lambda:self.new_func_for_choose_dir(self.new_line_edit2))
        #button2_2 = QPushButton("手动修改")
        #button2_2.clicked.connect(lambda:self.new_line_edit2.setDisabled(False))
        second_row_layout.addWidget(label21)
        second_row_layout.addWidget(self.new_line_edit2)
        second_row_layout.addWidget(button2)
        #second_row_layout.addWidget(button2_2)
        layout.addLayout(second_row_layout)

        layout.addWidget(QLabel(""))

        # groupbox
        groupbox = QGroupBox()
        vbox = QVBoxLayout()
        self.new_button_group = QButtonGroup()
        self.new_button_group.setExclusive(True)

        # -listxml -dtd
        self.new_button1 = QRadioButton("-listxml -dtd")
        self.new_button_group.addButton(self.new_button1)
        vbox.addWidget(self.new_button1)
        self.new_button1.setChecked(True)

        # -listxml
        self.new_button2 = QRadioButton("-listxml")
        self.new_button_group.addButton(self.new_button2)
        vbox.addWidget(self.new_button2)

        ## -listinfo
        #self.new_button3 = QRadioButton("-listinfo")
        #self.new_button_group.addButton(self.new_button3)
        #vbox.addWidget(self.new_button3)

        groupbox.setLayout(vbox)
        layout.addWidget(groupbox)

        layout.addWidget(QLabel(""),1)


        # 添加一个按钮以演示如何关闭对话框（可选）
        button = QPushButton("确认")
        button.clicked.connect(self.new_func_for_ok)
        layout.addWidget(button)

        button = QPushButton("放弃")
        button.clicked.connect(sys.exit)
        layout.addWidget(button)

        self.setLayout(layout)

    def new_func_set_values(self,):

        try:mame_path = self.new_settings.value("mame/path") 
        except:mame_path = ""
        if not isinstance(mame_path,str):
            mame_path = ""
        
        try:mame_working_directory = self.new_settings.value("mame/working_directory")
        except:mame_working_directory = ""
        if not isinstance(mame_working_directory,str):
            mame_working_directory = ""
        
        self.new_line_edit1.setText(mame_path)
        self.new_line_edit2.setText(mame_working_directory)
    
    def new_func_for_ok(self,checked):

        mame_path = self.new_line_edit1.text()
        self.new_settings.setValue("mame/path",mame_path)
        if mame_path :
            print("mame_path: ",mame_path)
        
        mame_working_directory = self.new_line_edit2.text()
        self.new_settings.setValue("mame/working_directory",mame_working_directory)
        if mame_working_directory :
            if os.path.isdir(mame_working_directory):
                print("mame_working_directory: ",mame_working_directory)

        text = self.new_button_group.checkedButton().text()
        print("text: ",text)

        if text == "-listxml -dtd":
            the_variables.command_line_options_for_emulator_to_export_data = ["-listxml", "-dtd"]
        elif text == "-listxml":
            the_variables.command_line_options_for_emulator_to_export_data = ["-listxml"]
        #elif text == "-listinfo":
        #    the_variables.command_line_options_for_emulator_to_export_data = ["-listinfo"]
        
        self.accept()
    
    def new_func_for_choose_mame_executable(self,checked):
        print("选择 MAME 可执行文件")
        file_path = QFileDialog.getOpenFileName(
            self,
            "选择一个可执行文件",
            "",  # 默认起始目录，空表示当前目录或上次使用的目录
            "可执行文件 (*.exe );;所有文件 (*.*)"  # Windows 常用可执行文件
            # 对于 macOS 可以改为 "应用程序 (*.app);;所有文件 (*)"
            # 对于 Linux 可以改为 "可执行文件 (*);;所有文件 (*)"
            )
        if file_path :
            print("file_path: ",file_path)
            self.new_line_edit1.setText(file_path[0])

    def new_func_for_choose_dir(self,line_edit):
        dir_path = QFileDialog.getExistingDirectory(
            self,
            "选择文件夹",
            "",  # 默认起始目录，空表示当前目录或上次使用的目录
            )
        if dir_path:
            print("dir_path: ",dir_path)
            line_edit.setText(dir_path)
    

# 菜单中 , 设置 周边路径
class Dialog_to_set_extra_path(QDialog):
    def __init__(self, settings,*args, **kwargs):
        super().__init__(*args, **kwargs)

        self.new_settings = settings
        
        self.setWindowTitle("周边 路径 设置")
        

        # 创建垂直布局（对话框的主布局）
        main_layout = QVBoxLayout(self)

        # 1. 创建滚动区域
        scroll_area = QScrollArea()
        scroll_area.setWidgetResizable(True)  # 重要：让内容自适应大小
        scroll_area.setVerticalScrollBarPolicy(Qt.ScrollBarAlwaysOn) 

        # 2. 创建容器部件
        container = QWidget()

        # 3. 为容器设置布局
        layout = QGridLayout(container)

        # 4. 添加大量小部件

        self.new_line_edit_widgets_dict = dict()


        row = 0
        # extra/folders
        col = 0
        label_for_folders = QLabel("自定义目录位置")
        layout.addWidget(label_for_folders,row,col)
        col += 1
        self.new_line_edit_widgets_dict["extra/folders"] = QLineEdit()
        self.new_line_edit_widgets_dict["extra/folders"] .setPlaceholderText("设置文件夹路径，如有多个值，以英文分号(;)分隔")
        layout.addWidget(self.new_line_edit_widgets_dict["extra/folders"],row,col)
        col += 1
        button_for_folders = QPushButton("...")
        button_for_folders.clicked.connect(lambda: self.new_func_for_choose_dir(self.new_line_edit_widgets_dict["extra/folders"]))
        layout.addWidget(button_for_folders,row,col)
        col += 1

        # extra/icons
        row += 1
        col = 0
        label_for_icon = QLabel("图标")
        layout.addWidget(label_for_icon,row,col)
        col += 1
        self.new_line_edit_widgets_dict["extra/icons"] = QLineEdit()
        self.new_line_edit_widgets_dict["extra/icons"] .setPlaceholderText("zip 文件路径")
        layout.addWidget(self.new_line_edit_widgets_dict["extra/icons"],row,col)
        col += 1
        button_for_icons = QPushButton("...")
        button_for_icons.clicked.connect(lambda: self.new_func_for_choose_file(self.new_line_edit_widgets_dict["extra/icons"]))
        layout.addWidget(button_for_icons,row,col)
        col += 1

        
        def make_func(widget,filter_string):
            return lambda: self.new_func_for_choose_file(widget,filter_string)
        
        # extra 文档
        translation_dict = {
                "extra/history":"history.xml",
                "extra/history_dat":"history.dat",
                "extra/gameinit":"gameinit.dat",
                "extra/mameinfo":"mameinfo.dat",
                "extra/messinfo":"messinfo.dat",
                "extra/command":"command.dat(中文版)",
                "extra/command_english":"command.dat(英文版)",
        }
        for key in [
                "extra/history",
                "extra/history_dat",
                "extra/gameinit",
                "extra/mameinfo",
                "extra/messinfo",
                "extra/command",
                "extra/command_english",
        ]:
            filter_string = "dat (*.dat);;所有文件 (*.*)"
            if key == "extra/history":
                filter_string = "xml (*.xml);;所有文件 (*.*)"
            row += 1
            col = 0
            label_for_file = QLabel(translation_dict.get(key,key))
            layout.addWidget(label_for_file,row,col)
            col += 1
            self.new_line_edit_widgets_dict[key] = QLineEdit()
            self.new_line_edit_widgets_dict[key] .setPlaceholderText("设置文件路径")
            layout.addWidget(self.new_line_edit_widgets_dict[key],row,col)
            col += 1
            button_for_file = QPushButton("...")
            button_for_file.clicked.connect(make_func(self.new_line_edit_widgets_dict[key],filter_string))
            layout.addWidget(button_for_file,row,col)
            col += 1
        
        # extra images zip
        for n in range(1,the_variables.image_dockwidget_numbers+1):
            filter_string="zip (*.zip);;所有文件 (*.*)"
            key_for_image_zip = "extra_image_zip_path/image_"+str(n)
            row += 1
            col = 0
            label_for_file = QLabel("图片_zip_路径_" + str(n))
            #label_for_file = QLabel(key_for_image_zip)
            layout.addWidget(label_for_file,row,col)
            col += 1
            self.new_line_edit_widgets_dict[key_for_image_zip] = QLineEdit()
            self.new_line_edit_widgets_dict[key_for_image_zip] .setPlaceholderText("设置 zip文件 路径")
            layout.addWidget(self.new_line_edit_widgets_dict[key_for_image_zip],row,col)
            col += 1
            button_for_file = QPushButton("...")
            button_for_file.clicked.connect(make_func(self.new_line_edit_widgets_dict[key_for_image_zip],filter_string))
            layout.addWidget(button_for_file,row,col)
            col += 1

        def make_func_for_folder(widget):
            return lambda: self.new_func_for_choose_dir(widget)
        # extra images folder
        for n in range(1,the_variables.image_dockwidget_numbers+1):
            key_for_image_folder = "extra_image_folder_path/image_"+str(n)
            row += 1
            col = 0
            label_for_file = QLabel("图片文件夹路径_" + str(n))
            layout.addWidget(label_for_file,row,col)
            col += 1
            self.new_line_edit_widgets_dict[key_for_image_folder] = QLineEdit()
            self.new_line_edit_widgets_dict[key_for_image_folder] .setPlaceholderText("设置 文件夹 路径")
            layout.addWidget(self.new_line_edit_widgets_dict[key_for_image_folder],row,col)
            col += 1
            button_for_dir = QPushButton("...")
            button_for_dir.clicked.connect(make_func_for_folder(self.new_line_edit_widgets_dict[key_for_image_folder]))
            layout.addWidget(button_for_dir,row,col)
            col += 1

        # 5. 将容器设为滚动区域的内容
        scroll_area.setWidget(container)

        # 6. 将滚动区域添加到对话框主布局中
        main_layout.addWidget(scroll_area)

        # 可选：添加一个普通按钮（如“关闭”），位于滚动区域下方
        ok_btn = QPushButton("确认")
        ok_btn.clicked.connect(self.new_func_for_ok) 
        ok_btn.clicked.connect(self.accept)  # 点击关闭对话框

        cancel_btn = QPushButton("取消")
        cancel_btn.clicked.connect(self.reject)  # 点击关闭对话框
        
        main_layout.addWidget(cancel_btn)
        main_layout.addWidget(ok_btn)

        for key in self.new_line_edit_widgets_dict.keys():
            self.new_line_edit_widgets_dict[key].setMinimumWidth(300)

    def new_func_for_ok(self,):
        print("func for ok")
        settings = self.new_settings

        for key in self.new_line_edit_widgets_dict.keys():
            value = self.new_line_edit_widgets_dict[key].text()
            if value:
                settings.setValue(key,value)
            else:
                settings.setValue(key,"")

        # 图片路径，更新到 the_variables ，需要频繁使用
        the_variables.update_extra_path() 

    def new_func_set_values(self,):
        for key in self.new_line_edit_widgets_dict.keys():
            value = self.new_settings.value(key)
            if value:
                self.new_line_edit_widgets_dict[key].setText(value)
            else:# 空值，或无值
                self.new_line_edit_widgets_dict[key].clear()

    def new_func_for_choose_dir(self,line_edit):
        dir_path = QFileDialog.getExistingDirectory(
            self,
            "选择文件夹",
            "",  # 默认起始目录，空表示当前目录或上次使用的目录
            )
        if dir_path:
            print("dir_path: ",dir_path)
            line_edit.setText(dir_path)
    
    def new_func_for_choose_file(self,line_edit,filter_string="zip (*.zip);;所有文件 (*.*)"):
        file_path = QFileDialog.getOpenFileName(
            self,
            "选择文件",
            "",  # 默认起始目录，空表示当前目录或上次使用的目录
            filter_string
            )
        if file_path:
            print("file_path: ",file_path)
            if file_path[0]:
                line_edit.setText(file_path[0])

# 菜单中 , 设置 游戏列表翻译文件 路径
class Dialog_for_translation_file_path(QDialog):  

    def __init__(self, settings,*args, **kwargs):
        super().__init__(*args, **kwargs)
        self.new_settings = settings
        
        self.setWindowTitle("游戏列表翻译文件")

        self.setSizeGripEnabled(True)
        
        self.setMinimumWidth(500)
        #self.setMinimumHeight(300)

        # 垂直布局管理器
        layout = QVBoxLayout()

        # 第一行布局
        first_row_layout = QHBoxLayout()
        label_1 = QLabel("翻译文件路径：")
        self.new_line_edit1 = QLineEdit()
        button1 = QPushButton("...")
        button1.clicked.connect(lambda:self.new_func_for_choose_file(self.new_line_edit1))
        first_row_layout.addWidget(label_1)
        first_row_layout.addWidget(self.new_line_edit1)
        first_row_layout.addWidget(button1)
        layout.addLayout(first_row_layout)

        layout.addWidget(QLabel("注：程序启动时，自动载入翻译文件"))
        layout.addWidget(QLabel("注：翻译文件的字符编码为 utf-8，如果不是的话自行转换一下"))

        ## 第二行布局
        #second_row_layout = QHBoxLayout()
        #label_2 = QLabel("翻译文件编辑后的保存路径：")
        #self.new_line_edit2 = QLineEdit()
        ##button2 = QPushButton("...")
        ##button2.clicked.connect(lambda:self.new_func_for_choose_file(self.new_line_edit2))
        #second_row_layout.addWidget(label_2)
        #second_row_layout.addWidget(self.new_line_edit2)
        ##second_row_layout.addWidget(button2)
        #layout.addLayout(second_row_layout)

        # 添加一个按钮以演示如何关闭对话框（可选）
        button_ok = QPushButton("确认")
        button_ok.clicked.connect(self.new_func_for_ok)
        button_ok.clicked.connect(self.accept)
        layout.addWidget(button_ok)

        button_cancel = QPushButton("取消")
        button_cancel.clicked.connect(self.reject)
        layout.addWidget(button_cancel)

        self.setLayout(layout)

    def new_func_set_values(self,):
        settings = self.new_settings

        translation_file = settings.value("mame/translation_file",)
        if translation_file:
            self.new_line_edit1.setText(translation_file)
        else:
            self.new_line_edit1.clear()

    def new_func_for_ok(self,checked):
        settings = self.new_settings

        translation_file = self.new_line_edit1.text()
        if translation_file :
            print("translation_file: ",translation_file)

            # 保存 设置
            settings.setValue("mame/translation_file",translation_file)

            # 加载翻译数据
            ui_models.load_gamelist_translation_file(translation_file,clear_old_data=True)

            # 刷新列表
            self.parent().centralWidget().new_func_refresh_layoutchange()

    def new_func_for_choose_file(self,line_edit,filter_string="lst (*.lst);;所有文件 (*.*)"):
        file_path = QFileDialog.getOpenFileName(
            self,
            "选择文件",
            "",  # 默认起始目录，空表示当前目录或上次使用的目录
            filter_string
            )
        if file_path:
            print("file_path: ",file_path)
            if file_path[0]:
                line_edit.setText(file_path[0])


# 菜单中 , 设置 游戏列表翻译文件 路径
class Dialog_for_save_translation_file(QDialog):  

    def __init__(self, settings,*args, **kwargs):
        super().__init__(*args, **kwargs)
        self.new_settings = settings
        
        self.setWindowTitle("游戏列表翻译文件保存")

        self.setSizeGripEnabled(True)
        
        self.setMinimumWidth(500)
        #self.setMinimumHeight(300)

        # 垂直布局管理器
        layout = QVBoxLayout()

        ## 第一行布局
        first_row_layout = QHBoxLayout()
        label_1 = QLabel("翻译文件路径：")
        self.new_line_edit1 = QLineEdit()
        self.new_line_edit1.setReadOnly(True)
        #button1 = QPushButton("...")
        #button1.clicked.connect(lambda:self.new_func_for_choose_file(self.new_line_edit1))
        first_row_layout.addWidget(label_1)
        first_row_layout.addWidget(self.new_line_edit1)
        #first_row_layout.addWidget(button1)
        layout.addLayout(first_row_layout)


        ## 第二行布局
        second_row_layout = QHBoxLayout()
        label_2 = QLabel("翻译文件编辑后的保存路径：")
        self.new_line_edit2 = QLineEdit()
        #button2 = QPushButton("...")
        #button2.clicked.connect(lambda:self.new_func_for_choose_file(self.new_line_edit2))
        second_row_layout.addWidget(label_2)
        second_row_layout.addWidget(self.new_line_edit2)
        #second_row_layout.addWidget(button2)
        layout.addLayout(second_row_layout)


        layout.addWidget(QLabel("注：保存的翻译文件，字符编码为 utf-8 带 bom"))


        last_row_layout = QHBoxLayout()
        # 添加一个按钮以演示如何关闭对话框（可选）
        button_ok = QPushButton("保存")
        button_ok.clicked.connect(self.new_func_for_ok)
        #button_ok.clicked.connect(self.accept)
        last_row_layout.addWidget(button_ok)

        button_cancel = QPushButton("取消")
        button_cancel.clicked.connect(self.reject)
        last_row_layout.addWidget(button_cancel)

        layout.addLayout(last_row_layout)
        self.setLayout(layout)

    def new_func_set_values(self,):
        settings = self.new_settings

        translation_file = settings.value("mame/translation_file",)
        if translation_file:
            self.new_line_edit1.setText(translation_file)
        else:
            self.new_line_edit1.clear()

        edit_translation_file = settings.value("mame/edit_translation_file",)
        if edit_translation_file:
            self.new_line_edit2.setText(edit_translation_file)
        else:
            self.new_line_edit2.clear()

    def new_func_for_ok(self,checked):
        settings = self.new_settings

        edit_translation_file = self.new_line_edit2.text()
        if not edit_translation_file:
            QMessageBox.warning(self, "错误", "请输入翻译文件编辑后的保存路径")
            return
        
        if edit_translation_file :
            print("edit_translation_file: ",edit_translation_file)

            # 保存 设置
            settings.setValue("mame/edit_translation_file",edit_translation_file)

            # 保存文件
            f=None
            try:
                f=open(edit_translation_file,"w",encoding="utf_8_sig")
            except:
                QMessageBox.warning(self, "错误", "无法打开文件写入内容")
                f=None
                return

            try:
                if f is not None:
                    index_translation = ui_models.columns.index("translation")
                    index_description = ui_models.columns.index("description")
                    for game_id in ui_models.machine_dict:
                        translation = ui_models.machine_dict[game_id][index_translation]
                        description = ui_models.machine_dict[game_id][index_description]
                        if description != translation:
                            translation = translation.replace("\t"," ")
                            f.write(f"{game_id}\t{translation}\t{translation}\n")
                    self.accept()
            except:
                print("write file error")


# 菜单中 , 游戏列表 图标大小
class Dialog_for_set_gamelist_icon_size(QDialog):  

    def __init__(self, settings,*args, **kwargs):
        super().__init__(*args, **kwargs)
        self.new_settings = settings
        
        self.setWindowTitle("游戏列表图标")

        self.setSizeGripEnabled(True)
        
        self.setMinimumWidth(400)
        #self.setMinimumHeight(300)

        # 垂直布局管理器
        layout = QVBoxLayout()

        # 第一行布局
        first_row_layout = QHBoxLayout()
        label_1 = QLabel("普通列表，图标宽度:")
        self.new_line_edit1 = QLineEdit()
        first_row_layout.addWidget(label_1)
        first_row_layout.addWidget(self.new_line_edit1)
        layout.addLayout(first_row_layout)

        # 第二行布局
        second_row_layout = QHBoxLayout()
        label_2 = QLabel("图标列表，图标宽度:")
        self.new_line_edit2 = QLineEdit()
        second_row_layout.addWidget(label_2)
        second_row_layout.addWidget(self.new_line_edit2)
        layout.addLayout(second_row_layout)

        # 第三行布局
        third_row_layout = QHBoxLayout()
        label_3 = QLabel("图标列表，间距:")
        self.new_line_edit3 = QLineEdit()
        third_row_layout.addWidget(label_3)
        third_row_layout.addWidget(self.new_line_edit3)
        layout.addLayout(third_row_layout)

        layout.addWidget(QLabel("注：设置整数,大于0 "))

        layout.addWidget(QLabel(""),1)
        # 
        button_ok = QPushButton("确认")
        button_ok.clicked.connect(self.new_func_for_ok)
        button_ok.clicked.connect(self.accept)
        layout.addWidget(button_ok)

        button_cancel = QPushButton("取消")
        button_cancel.clicked.connect(self.reject)
        layout.addWidget(button_cancel)

        self.setLayout(layout)

    def new_func_set_values(self,):
        settings = self.new_settings

        self.new_line_edit1.clear()
        self.new_line_edit2.clear()
        self.new_line_edit3.clear()


        # 图标大小（普通列表）
        try:icon_size = settings.value("gamelist/icon_size_for_gamelist",type=int)
        except:icon_size = 0
        if type(icon_size) is int:
            if icon_size > 0:
                the_variables.icon_size = icon_size
        self.new_line_edit1.setText(str(the_variables.icon_size))
        
        # 图标大小（图标列表）
        try:
            icon_size_for_icon_table = self.new_settings.value("gamelist/icon_size_for_icon_table",type=int) # 取值到 the_variables.icon_size
        except:
            icon_size_for_icon_table = 0
        if type(icon_size_for_icon_table) is int:
            if icon_size_for_icon_table > 0:
                ui_models.icon_size_for_icon_table = icon_size_for_icon_table
        self.new_line_edit2.setText(str(ui_models.icon_size_for_icon_table))

        # 间距（图标列表）
        try:
            spacing_for_icon_table = self.new_settings.value("gamelist/spacing_for_icon_table",type=int) # 取值到 the_variables.icon_size
        except:
            spacing_for_icon_table = 0
        if type(spacing_for_icon_table) is int:
            if spacing_for_icon_table > 0:
                the_variables.spacing_for_icon_table = spacing_for_icon_table
        self.new_line_edit3.setText(str(the_variables.spacing_for_icon_table))
        

    def new_func_for_ok(self,checked):
        settings = self.new_settings

        icon_size = self.new_line_edit1.text()
        icon_size_for_icon_table = self.new_line_edit2.text()
        spacing_for_icon_table = self.new_line_edit3.text()

        try:
            icon_size = int(icon_size)
            icon_size_for_icon_table = int(icon_size_for_icon_table)
            spacing_for_icon_table = int(spacing_for_icon_table)
        except:
            QMessageBox.warning(self, "错误", "请输入整数,大于0")
            return
        
        if (icon_size <= 0) or (icon_size_for_icon_table <= 0) or (spacing_for_icon_table <= 0):
            QMessageBox.warning(self, "错误", "请输入整数,大于0")
            return

        # 赋值
        the_variables.icon_size = icon_size
        ui_models.icon_size_for_icon_table = icon_size_for_icon_table
        the_variables.spacing_for_icon_table = spacing_for_icon_table
        # 保存
        settings.setValue("gamelist/icon_size_for_gamelist",icon_size)
        settings.setValue("gamelist/spacing_for_icon_table",spacing_for_icon_table)
        settings.setValue("gamelist/icon_size_for_icon_table",icon_size_for_icon_table)
        
        ui_models.load_and_resize_internal_icon()
        self.parent().centralWidget().new_func_refresh_layoutchange()
        self.parent().new_func_for_set_icon_table_spacing()
        self.accept()
        
# 菜单中 , 游戏列表 行高
class Dialog_for_set_gamelist_row_height(QDialog):  

    def __init__(self, settings,*args, **kwargs):
        super().__init__(*args, **kwargs)
        self.new_settings = settings
        
        self.setWindowTitle("游戏列表行高")

        self.setSizeGripEnabled(True)
        
        self.setMinimumWidth(400)
        #self.setMinimumHeight(300)

        # 垂直布局管理器
        layout = QVBoxLayout()

        # 第一行布局
        first_row_layout = QHBoxLayout()
        label_1 = QLabel("行高 QTableView:")
        self.new_line_edit1 = QLineEdit()
        first_row_layout.addWidget(label_1)
        first_row_layout.addWidget(self.new_line_edit1)
        layout.addLayout(first_row_layout)

        # 第二行布局
        second_row_layout = QHBoxLayout()
        label_2 = QLabel("行高 QTreeView:")
        self.new_line_edit2 = QLineEdit()
        second_row_layout.addWidget(label_2)
        second_row_layout.addWidget(self.new_line_edit2)
        layout.addLayout(second_row_layout)        

        layout.addWidget(QLabel(""))
        layout.addWidget(QLabel("注：设置整数,大于0 "))
        layout.addWidget(QLabel("注：0 代表默认值 "))


        # 
        button_ok = QPushButton("确认")
        button_ok.clicked.connect(self.new_func_for_ok)
        layout.addWidget(button_ok)

        button_cancel = QPushButton("取消")
        button_cancel.clicked.connect(self.reject)
        layout.addWidget(button_cancel)

        self.setLayout(layout)

    def new_func_set_values(self,):
        settings = self.new_settings

        try:height_for_tableview = settings.value("gamelist/row_height_for_tableview",type=int)
        except:height_for_tableview = 0
        try:height_for_treeview  = settings.value("gamelist/row_height_for_treeview",type=int)
        except:height_for_treeview = 0

        if type(height_for_tableview) is not int:
            height_for_tableview = 0
        if height_for_tableview < 0:
            height_for_tableview = 0
        
        if type(height_for_treeview) is not int:
            height_for_treeview = 0
        if height_for_treeview < 0:
            height_for_treeview = 0

        self.new_line_edit1.setText(str(height_for_tableview))
        self.new_line_edit2.setText(str(height_for_treeview))
    
    def new_func_for_ok(self,checked):
        settings = self.new_settings

        height_for_tableview = self.new_line_edit1.text()
        height_for_treeview = self.new_line_edit2.text()

        try:
            height_for_tableview = int(height_for_tableview)
        except:
            QMessageBox.warning(self, "错误", "请输入整数,大于0")
            return
        if height_for_tableview < 0:
            QMessageBox.warning(self, "错误", "请输入整数,大于0")
            return
        
        try:
            height_for_treeview = int(height_for_treeview)
        except:
            QMessageBox.warning(self, "错误", "请输入整数,大于0")
            return
        if height_for_treeview < 0:
            QMessageBox.warning(self, "错误", "请输入整数,大于0")
            return
        
        changed = False

        try:old_height_for_tableview = settings.value("gamelist/row_height_for_tableview",type=int)
        except:old_height_for_tableview=0
        try:old_height_for_treeview  = settings.value("gamelist/row_height_for_treeview",type=int)
        except:old_height_for_treeview=0

        

        if old_height_for_tableview != height_for_tableview:
            changed = True

            # 保存 设置
            settings.setValue("gamelist/row_height_for_tableview",height_for_tableview)

            self.parent().new_func_set_row_height_for_tableview()


        if old_height_for_treeview != height_for_treeview:
            changed = True

            # 保存 设置
            settings.setValue("gamelist/row_height_for_treeview",height_for_treeview)

            self.parent().new_func_set_internal_qss()

        if changed:
            self.accept()
        else:
            self.hide()

# 菜单中 , 字体
class Dialog_for_set_font(QDialog):  

    def __init__(self, settings,*args, **kwargs):
        super().__init__(*args, **kwargs)
        self.new_settings = settings
        
        self.setWindowTitle("字体")

        self.setSizeGripEnabled(True)
        
        self.setMinimumWidth(400)
        #self.setMinimumHeight(300)

        # 垂直布局管理器
        layout = QVBoxLayout()

        self.new_keys =   ["all",    "gamelist",   "extra",     "extra_command","extra_command_english","QHeaderView"  ]
        self.new_titles = ["所有字体","游戏列表字体","周边文档字体","中文出招表字体","英文出招表字体",        "列表标题栏字体"]
        self.new_line_edit_for_font_family_dict = {}
        self.new_line_edit_for_font_size_dict = {}

        for key,title in zip(self.new_keys,self.new_titles):
            row_layout = QHBoxLayout()

            row_layout.addWidget(QLabel(title))

            row_layout.addWidget(QLabel("字体:"))
            self.new_line_edit_for_font_family_dict[key] = QLineEdit(self)
            row_layout.addWidget(self.new_line_edit_for_font_family_dict[key])

            row_layout.addWidget(QLabel("大小:"))
            self.new_line_edit_for_font_size_dict[key] = QLineEdit()
            row_layout.addWidget(self.new_line_edit_for_font_size_dict[key])

            button = QPushButton("...")
            row_layout.addWidget(button)
            button.clicked.connect(functools.partial(self.new_func_for_choose_font, 
                                                     self.new_line_edit_for_font_family_dict[key],
                                                     self.new_line_edit_for_font_size_dict[key]))

            layout.addLayout(row_layout)


        # 注释
        layout.addWidget(QLabel(""))
        layout.addWidget(QLabel("注：删除留空表示使用默认值"))
        layout.addWidget(QLabel("注：字体大小值为整数,大于0 "))


        # 
        button_ok = QPushButton("确认")
        button_ok.clicked.connect(self.new_func_for_ok)
        layout.addWidget(button_ok)

        button_cancel = QPushButton("取消")
        button_cancel.clicked.connect(self.reject)
        layout.addWidget(button_cancel)

        button_clear = QPushButton("清空")
        button_clear.clicked.connect(self.new_func_clear)
        layout.addWidget(button_clear)

        self.setLayout(layout)

    def new_func_set_values(self,):
        settings = self.new_settings

        self.new_func_clear()

        for key,title in zip(self.new_keys,self.new_titles):
            font_family = settings.value(f"font_family/{key}",type=str)
            try:font_size = settings.value(f"font_size/{key}",type=int)
            except:font_size = 0

            if font_family:
                self.new_line_edit_for_font_family_dict[key].setText(font_family)
            if type(font_size) == int:
                if font_size > 0:
                    self.new_line_edit_for_font_size_dict[key].setText(str(font_size))

    def new_func_for_choose_font(self,line_edit_font,line_edit_size):
        ok,font = QFontDialog.getFont(self)
        if ok:
            print(font)
            font_info = QFontInfo(font)
            family = font_info.family()
            size = font_info.pixelSize()
            line_edit_font.setText(family)
            line_edit_size.setText(str(size))
        else:
            print("用户取消选择")

    def new_func_for_ok(self,checked):
        settings = self.new_settings

        for key in self.new_keys:
            
            # font_family
            value = self.new_line_edit_for_font_family_dict[key].text()
            value = value.strip()
            settings.setValue(f"font_family/{key}",value)
            
            # font_size
            value = self.new_line_edit_for_font_size_dict[key].text()
            try:
                int(value)
            except :
                value = "" # 清空
            settings.setValue(f"font_size/{key}",value)
        
        # 生成 qss 文件
        # mainwindow
        # new_func_set_internal_qss()
        self.parent().new_func_set_internal_qss()

        self.accept()

    def new_func_clear(self):
        # 清空所有 QLineEdit
        for child in self.children():
            if isinstance(child, QLineEdit):
                child.setText("")

# 菜单中 , 游戏列表 行高
class Dialog_for_set_gamelist_highlight_row_colour(QDialog):  

    def __init__(self, settings,*args, **kwargs):
        super().__init__(*args, **kwargs)
        self.new_settings = settings
        
        self.setWindowTitle("游戏列表选中行颜色")

        self.setSizeGripEnabled(True)
        
        #self.setMinimumWidth(600)
        #self.setMinimumHeight(300)

        self.new_background_r = -1
        self.new_background_g = -1
        self.new_background_b = -1
        self.new_background_a = 255

        self.new_colour_r = -1
        self.new_colour_g = -1
        self.new_colour_b = -1
        self.new_colour_a = 255

        # 垂直布局管理器
        layout = QVBoxLayout()

        # 第一行布局
        first_row_layout = QHBoxLayout()
        #
        label_1 = QLabel("选中行背景色:")
        #
        button_1 = QPushButton("选色")
        #
        label_transparent_1 = QLabel("透明度:")
        #
        self.new_line_edit1 = QLineEdit()
        self.new_line_edit1.setPlaceholderText("此处可填写透明度 0 - 255")
        #
        first_row_layout.addWidget(label_1)
        first_row_layout.addWidget(button_1)
        first_row_layout.addWidget(label_transparent_1)
        first_row_layout.addWidget(self.new_line_edit1)
        layout.addLayout(first_row_layout)



        # 第二行布局
        second_row_layout = QHBoxLayout()
        #
        label_2 = QLabel("选中行文本颜色:")
        #
        button_2 = QPushButton("选色")
        #
        label_transparent_2 = QLabel("透明度:")
        #
        self.new_line_edit2 = QLineEdit()
        self.new_line_edit2.setPlaceholderText("此处可填写透明度 0 - 255")
        #
        second_row_layout.addWidget(label_2)
        second_row_layout.addWidget(button_2)
        second_row_layout.addWidget(label_transparent_2)
        second_row_layout.addWidget(self.new_line_edit2)
        layout.addLayout(second_row_layout)

        # 第三行 测试文本
        self.new_label_colour_test = QLabel()
        layout.addWidget(self.new_label_colour_test)
        self.new_label_colour_test.setText("测试文本 Test Text")

        ###
        button_1.clicked.connect(self.new_func_for_choose_colour_background)
        button_2.clicked.connect(self.new_func_for_choose_colour_text)
        self.new_line_edit1.textChanged.connect(self.new_func_for_background_alpha_changed)
        self.new_line_edit2.textChanged.connect(self.new_func_for_text_alpha_changed)

        # 注释
        layout.addWidget(QLabel(""))
        layout.addWidget(QLabel("注：透明度，设置整数,范围 0 - 255。0 为全透明，255 为不透明。"))
        layout.addWidget(QLabel("注：此选项，适用于 Fusion (菜单→UI→style→Fusion),其它 sytle 有可能不管用。"))

        # 
        button_ok = QPushButton("确认")
        button_ok.clicked.connect(self.new_func_for_ok)
        layout.addWidget(button_ok)

        button_cancel = QPushButton("取消")
        button_cancel.clicked.connect(self.reject)
        layout.addWidget(button_cancel)


        button_clear = QPushButton("清除")
        button_clear.clicked.connect(self.new_func_for_clear)
        layout.addWidget(button_clear)        

        self.setLayout(layout)

    def new_func_build_qss(self):
        qss=""

        if self.new_background_r >= 0 and self.new_background_g >= 0 and self.new_background_b >= 0 and self.new_background_a >= 0:
            if self.new_background_r <= 255 and self.new_background_g <= 255 and self.new_background_b <= 255 and self.new_background_a <= 255:
                qss += f"background-color: rgba({self.new_background_r},{self.new_background_g},{self.new_background_b},{self.new_background_a});"
        
        if self.new_colour_r >= 0 and self.new_colour_g >= 0 and self.new_colour_b >= 0 and self.new_colour_a >= 0:
            if self.new_colour_r <= 255 and self.new_colour_g <= 255 and self.new_colour_b <= 255 and self.new_colour_a <= 255:
                qss += f"color: rgba({self.new_colour_r},{self.new_colour_g},{self.new_colour_b},{self.new_colour_a});"
        
        return qss
    
    def new_func_use_qss(self):
        qss=self.new_func_build_qss()
        self.new_label_colour_test.setStyleSheet(qss)

    def new_func_for_choose_colour_background(self,):
        colour = QColorDialog.getColor()
        #print(type(colour))
        #print(colour)
        if colour.isValid():
            self.new_background_r = colour.red()
            self.new_background_g = colour.green()
            self.new_background_b = colour.blue()
            
            self.new_func_use_qss()

    def new_func_for_choose_colour_text(self,):
        colour = QColorDialog.getColor()
        #print(type(colour))
        #print(colour)
        if colour.isValid():
            self.new_colour_r = colour.red()
            self.new_colour_g = colour.green()
            self.new_colour_b = colour.blue()
            self.new_colour_a = colour.alpha()

            self.new_func_use_qss()

    @Slot(str)
    def new_func_for_background_alpha_changed(self,text):
        try:
            self.new_background_a = int(text)
        except:
            self.new_background_a = 255
        
        if self.new_background_a < 0: 
            self.new_background_a = 255
        
        if self.new_background_a > 255:
            self.new_background_a = 255

        self.new_func_use_qss()

    @Slot(str)
    def new_func_for_text_alpha_changed(self,text):
        try:
            self.new_colour_a = int(text)
        except:
            self.new_colour_a = 255
        
        if self.new_colour_a < 0: 
            self.new_colour_a = 255
        
        if self.new_colour_a > 255:
            self.new_colour_a = 255

        self.new_func_use_qss()



    def new_func_set_values(self,):
       
        settings = self.new_settings

        try:
            background = settings.value("gamelist_highlight/background")
        except:
            background = ""
        if background :
            try:
                self.new_background_r = int(background.split(",")[0])
                self.new_background_g = int(background.split(",")[1])
                self.new_background_b = int(background.split(",")[2])
                self.new_background_a = int(background.split(",")[3])
            except:
                self.new_background_r = -1
                self.new_background_g = -1
                self.new_background_b = -1
                self.new_background_a = 255

        value_ok=False
        if self.new_background_r >= 0 and self.new_background_g >= 0 and self.new_background_b >= 0 and self.new_background_a >= 0: 
            if self.new_background_a <= 255 and self.new_background_r <= 255 and self.new_background_g <= 255 and self.new_background_b <= 255:
                value_ok=True
                self.new_line_edit1.setText(str(self.new_background_a))
        if not value_ok:
            self.new_background_r = -1
            self.new_background_g = -1
            self.new_background_b = -1
            self.new_background_a = 255

        try:
            colour = settings.value("gamelist_highlight/colour",)
        except:
            colour = ""
        if colour :
            try:
                self.new_colour_r = int(colour.split(",")[0])
                self.new_colour_g = int(colour.split(",")[1])
                self.new_colour_b = int(colour.split(",")[2])
                self.new_colour_a = int(colour.split(",")[3])
            except:
                self.new_colour_r = -1
                self.new_colour_g = -1
                self.new_colour_b = -1
                self.new_colour_a = 255
        value_ok=False
        if self.new_colour_r >= 0 and self.new_colour_g >= 0 and self.new_colour_b >= 0 and self.new_colour_a >= 0: 
            if self.new_colour_a <= 255 and self.new_colour_r <= 255 and self.new_colour_g <= 255 and self.new_colour_b <= 255:
                value_ok=True
                self.new_line_edit2.setText(str(self.new_colour_a))
        if not value_ok:
            self.new_colour_r = -1
            self.new_colour_g = -1
            self.new_colour_b = -1
            self.new_colour_a = 255

        self.new_func_use_qss()
    
    def new_func_for_ok(self,checked):
        settings = self.new_settings
        
        backgroud_string = self.new_background_r,self.new_background_g,self.new_background_b,self.new_background_a
        backgroud_string = ",".join(map(str, backgroud_string))
        settings.setValue("gamelist_highlight/background",backgroud_string)
        
        colour_string = self.new_colour_r,self.new_colour_g,self.new_colour_b,self.new_colour_a
        colour_string = ",".join(map(str, colour_string))
        settings.setValue("gamelist_highlight/colour",colour_string)

        self.parent().new_func_set_internal_qss()
        self.accept()


    def new_func_for_clear(self):
        settings = self.new_settings
        self.new_background_r,self.new_background_g,self.new_background_b,self.new_background_a = -1,-1,-1,255
        backgroud_string = self.new_background_r,self.new_background_g,self.new_background_b,self.new_background_a
        backgroud_string = ",".join(map(str, backgroud_string))
        settings.setValue("gamelist_highlight/background",backgroud_string)
        
        self.new_colour_r,self.new_colour_g,self.new_colour_b,self.new_colour_a = -1,-1,-1,255
        colour_string = self.new_colour_r,self.new_colour_g,self.new_colour_b,self.new_colour_a
        colour_string = ",".join(map(str, colour_string))
        settings.setValue("gamelist_highlight/colour",colour_string)

        self.new_func_use_qss()


# 菜单中 , 字体，游戏列表 2 level tree like ，设置打开关闭字符串
class Dialog_for_set_open_colse_string_for_tableview_2_level_tree_like(QDialog):  

    def __init__(self, settings,*args, **kwargs):
        super().__init__(*args, **kwargs)
        self.new_settings = settings
        
        self.setWindowTitle("列表展开收起字符设置")

        self.setSizeGripEnabled(True)
        
        self.setMinimumWidth(400)
        #self.setMinimumHeight(300)

        # 垂直布局管理器
        layout = QVBoxLayout()

        self.new_keys           = ["string_for_open",    "string_for_close",   "string_for_empty",   ]
        self.new_titles         = ["展开字符串",          "收起字符串",          "空字符串"]
        self.new_default_values = [" + ",                " - ",                "   "]

        self.new_line_edit_dict = {}

        for key,title in zip(self.new_keys,self.new_titles):
            row_layout = QHBoxLayout()

            row_layout.addWidget(QLabel(title))
            
            self.new_line_edit_dict[key] = QLineEdit(self)
            row_layout.addWidget(self.new_line_edit_dict[key])

            layout.addLayout(row_layout)


        # 注释
        layout.addWidget(QLabel(""))
        layout.addWidget(QLabel("注：可以有部分空白字符"))
        layout.addWidget(QLabel("注：字符串前后如果有空白，用英文双引号括起来"))
        layout.addWidget(QLabel("注：字符串显示宽度相等最好"))
        


        # 
        button_ok = QPushButton("确认")
        button_ok.clicked.connect(self.new_func_for_ok)
        layout.addWidget(button_ok)

        button_cancel = QPushButton("取消")
        button_cancel.clicked.connect(self.reject)
        layout.addWidget(button_cancel)

        button_reset = QPushButton("重置")
        button_reset.clicked.connect(self.new_func_reset)
        layout.addWidget(button_reset)

        self.setLayout(layout)

    def new_func_set_values(self,):
        settings = self.new_settings

        self.new_func_clear()

        for key,default_value in zip(self.new_keys,self.new_default_values):

            try:
                string = settings.value(f"gamelist_faketree/{key}",type=str)
            except:
                string = default_value
            
            if not string:
                string = default_value

            if string:
                string = string.strip('"')
                string = '"' + string + '"'
                self.new_line_edit_dict[key].setText(string)

    def new_func_for_ok(self,checked):
        settings = self.new_settings

        for key,default_value in zip(self.new_keys,self.new_default_values):
            
            # font_family
            value = self.new_line_edit_dict[key].text()

            value = value.strip()
            value = value.strip('"')

            if not value:
                value = default_value

            setattr(ui_models,key,value) # 内部数据修改

            value = '"' + value + '"'
            
            settings.setValue(f"gamelist_faketree/{key}",value) # 外部数据保存

            
        
        self.accept()

    def new_func_reset(self):
        # 清空所有 QLineEdit
        for key,value in zip(self.new_keys,self.new_default_values):
            valute = '"' + value + '"'
            self.new_line_edit_dict[key].setText(value)
    
    def new_func_clear(self):
        # 清空所有 QLineEdit
        for child in self.children():
            if isinstance(child, QLineEdit):
                child.setText("")



# 菜单中 , gamelist 全局过滤
class Dialog_to_set_gamelist_filter(QDialog):
    def __init__(self, settings,*args, **kwargs):
        super().__init__(*args, **kwargs)

        self.new_settings = settings
        
        self.setWindowTitle("过滤")
        

        # 创建垂直布局（对话框的主布局）
        main_layout = QVBoxLayout(self)

        # 1. 创建滚动区域
        scroll_area = QScrollArea()
        scroll_area.setWidgetResizable(True)  # 重要：让内容自适应大小
        scroll_area.setVerticalScrollBarPolicy(Qt.ScrollBarAlwaysOn) 

        # 2. 创建容器部件
        container = QWidget()

        # 3. 为容器设置布局
        layout = QVBoxLayout(container)



        self.new_checkbox_dict = {}

        # parent_set
        self.new_checkbox_dict["parent_set"] = QCheckBox("主版本")
        layout.addWidget(self.new_checkbox_dict["parent_set"])

        # clone_set
        self.new_checkbox_dict["clone_set"] = QCheckBox("克隆版本")
        layout.addWidget(self.new_checkbox_dict["clone_set"])

        # bios
        self.new_checkbox_dict["bios"] = QCheckBox("BIOS")
        layout.addWidget(self.new_checkbox_dict["bios"])

        # device
        self.new_checkbox_dict["device"] = QCheckBox("device")
        layout.addWidget(self.new_checkbox_dict["device"])

        # mechanical
        self.new_checkbox_dict["mechanical"] = QCheckBox("机械")
        layout.addWidget(self.new_checkbox_dict["mechanical"])

        # chd
        self.new_checkbox_dict["chd"] = QCheckBox("CHD")
        layout.addWidget(self.new_checkbox_dict["chd"])

        # softwarelist
        self.new_checkbox_dict["softwarelist"] = QCheckBox("softwarelist")
        layout.addWidget(self.new_checkbox_dict["softwarelist"])

        # status good
        self.new_checkbox_dict["status good"] = QCheckBox("模拟状态 good")
        layout.addWidget(self.new_checkbox_dict["status good"])

        # status imperfect
        self.new_checkbox_dict["status imperfect"] = QCheckBox("模拟状态 imperfect")
        layout.addWidget(self.new_checkbox_dict["status imperfect"])

        # status preliminary
        self.new_checkbox_dict["status preliminary"] = QCheckBox("模拟状态 preliminary")
        layout.addWidget(self.new_checkbox_dict["status preliminary"])

        # 5. 将容器设为滚动区域的内容
        scroll_area.setWidget(container)

        # 6. 将滚动区域添加到对话框主布局中
        main_layout.addWidget(scroll_area)

        # 可选：添加一个普通按钮（如“关闭”），位于滚动区域下方
        ok_btn = QPushButton("确认")
        ok_btn.clicked.connect(self.new_func_for_ok) 
        ok_btn.clicked.connect(self.accept)  # 点击关闭对话框

        cancel_btn = QPushButton("取消")
        cancel_btn.clicked.connect(self.reject)  # 点击关闭对话框
        
        main_layout.addWidget(cancel_btn)
        main_layout.addWidget(ok_btn)


    def new_func_set_values(self,):
        settings = self.new_settings

        checked_items=set()

        value = self.new_settings.value("gamelist/filter")
        if type(value) == str:
            value = value.strip()
            if value:
                for item in value.split(","):
                    if item in self.new_checkbox_dict.keys():
                        checked_items.add(item)

        for item in self.new_checkbox_dict.keys():
            if item not in checked_items:
                self.new_checkbox_dict[item].setChecked(False)
            else:
                self.new_checkbox_dict[item].setChecked(True)

    def new_func_for_ok(self,):
        print("func for ok")

        checked_items=set()

        #checkState
        for item in self.new_checkbox_dict.keys():
            if self.new_checkbox_dict[item].checkState() == Qt.Checked:
                checked_items.add(item)

        value = ",".join(sorted(checked_items))

        self.new_settings.setValue("gamelist/filter", value)

        misc_funcs.update_filter_set(self.new_settings)

        self.accept()


# 菜单中，显示 python 版本
class Dialog_for_show_python_version(QDialog):  

    def __init__(self,*args, **kwargs):
        super().__init__(*args, **kwargs)

        self.setWindowTitle("Python 版本")

        self.setSizeGripEnabled(True)
        
        #self.setMinimumWidth(400)
        #self.setMinimumHeight(400)

        # 垂直布局管理器
        layout = QVBoxLayout()

        # python
        python_version  = str(sys.version)
        layout.addWidget(QLabel("" ))
        layout.addWidget(QLabel("Python : " + python_version))

        # qtpy
        try:
            version_qtpy = qtpy.__version__
            layout.addWidget(QLabel("" ))
            layout.addWidget(QLabel("QtPy : "  + str(version_qtpy)))
        except:
            pass
        
        # pyside or pyqt
        try:
            version_qt = str(qtpy.API_NAME) + " : " + str(qtpy.QT_VERSION)
            layout.addWidget(QLabel("" ))
            layout.addWidget(QLabel(version_qt))
        except:
            pass


        self.setLayout(layout)




# extra , image， dock widget
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
        self.new_label_for_image.setFocusPolicy(Qt.ClickFocus)
        
        # 窗口大小变化 ？？？
        self.new_label_for_image.setSizePolicy(QSizePolicy.Ignored, QSizePolicy.Ignored)        


        self.new_the_old_id = None
        self.new_zip_file_path = ""
        self.new_zip_opened_file = None

        self.new_pixmap_original = None

        self.new_visible = False
        self.visibilityChanged.connect(self.new_func_for_visibilityChanged)

        self.parent().tabifiedDockWidgetActivated.connect(self.new_slot_for_tabifiedDockWidgetActivated)

    @Slot(str)
    def new_slot_for_id_change(self,game_id=""):

        #print("slot for image a:",self.objectName())

        #if not self.isVisible(): # 在签标页面 重叠时，不管用
        #    return

        if not self.new_visible:
            return

        #print("slot for image b:",self.objectName())

        if not game_id:
            return

        if game_id != the_variables.current_id:
            return
        
        if self.new_func_get_image_from_file(game_id):
            self.new_the_old_id = game_id
            return

        #print("slot for image c:",self.objectName())

        if self.new_func_get_image_from_zip(game_id):
            self.new_the_old_id = game_id
            return
        
        # 如果克隆版，无内容，使用原版的内容
        if game_id in ui_models.clone_set:
            parent_id = ui_models.clone_to_parent[game_id]

            if self.new_func_get_image_from_file(parent_id):
                self.new_the_old_id = game_id
                return
        
            if self.new_func_get_image_from_zip(parent_id):
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

        if not zip_file_path:
            if self.new_zip_opened_file is not None:
                self.new_func_close_zip()
            return
        
        if zip_file_path != self.new_zip_file_path:
            if not os.path.isfile(zip_file_path):
                if self.new_zip_opened_file is not None:
                    self.new_func_close_zip()
                return
            
            # 文件变化，打开新文件
            if zip_file_path != self.new_zip_file_path:
                if self.new_zip_opened_file is not None:
                    self.new_func_close_zip()
                self.new_func_open_zip(zip_file_path)

        if zip_file_path == self.new_zip_file_path:
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
                            Qt.KeepAspectRatio,            # 保持宽高比
                            Qt.SmoothTransformation        # 平滑变换
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
            print("open zip file :",self.new_zip_file_path)
        except:
            self.new_zip_file_path = ""
            self.new_zip_opened_file = None
    
    def new_func_close_zip(self):
        if self.new_zip_opened_file is not None:
            try:
                self.new_zip_opened_file.close()
                print("close zip file :",self.new_zip_file_path)
                self.new_zip_opened_file = None
                self.new_zip_file_path = ""
            except:
                pass

    def new_func_clear_image(self):
        self.new_label_for_image.clear()
        self.new_pixmap_original= None

    def closeEvent(self, event):
        
        self.new_func_close_zip()
        self.new_func_clear_image()
        self.new_the_old_id=None

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

        #print(self.objectName(),"iamge dock visible :",visible,"*****************************")
        
        # 窗口显示，同步内容
        if visible:
            if self.new_the_old_id != the_variables.current_id:
                self.new_slot_for_id_change(the_variables.current_id)

    @Slot(QDockWidget)
    def new_slot_for_tabifiedDockWidgetActivated(self,widget):
        # 判定 在分组中，被折叠了
        #print("a",self.objectName())
        if self.isVisible(): # 这个也是奇怪。 isVisible() ，被折叠了，值还是 True
            
            #print("b",self.objectName())

            if not self.new_visible: 
                # 虽然 测试使用没感觉到问题
                # 但，这个值 是 另一个 slot 中更新的，怎么确定，不会比这个 slot 更晚执行？
                
                #print("c",self.objectName())

                tabified_list = self.parent().tabifiedDockWidgets(self)
                if tabified_list:
                    if self.new_zip_opened_file is not None:
                        self.new_func_close_zip() # 分组中被折叠了，关闭 zip 文件
                        self.new_func_clear_image() # 清理
                        self.new_the_old_id=None 



# extra ，文档，dock widget
#
class Text_edit_0(QTextEdit):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.setContextMenuPolicy(Qt.ActionsContextMenu)

        action_no_line_wrap = QAction("不换行", self)
        action_no_line_wrap.triggered.connect(self.new_slot_for_set_no_line_wrap)
        
        action_line_wrap = QAction("自动换行", self)
        action_line_wrap.triggered.connect(self.new_slot_for_set_line_wrap)

        self.addAction(action_no_line_wrap)
        self.addAction(action_line_wrap)
        

    @Slot()
    def new_slot_for_set_no_line_wrap(self):
        self.setLineWrapMode(QTextEdit.NoWrap)

    @Slot()
    def new_slot_for_set_line_wrap(self):
        self.setLineWrapMode(QTextEdit.WidgetWidth)
#
# extra , history.xml 、history.dat 、gameinit.dat
class Text_dockwidget_0(QDockWidget): 
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.new_textedit = Text_edit_0(self)
        
        self.setWidget(self.new_textedit)

        self.new_textedit.setReadOnly(True)
        self.new_textedit.setUndoRedoEnabled(False)
        self.new_textedit.setContextMenuPolicy(Qt.ActionsContextMenu)
        self.new_textedit.setTabChangesFocus(False)
        self.new_textedit.setFocusPolicy(Qt.ClickFocus)

        self.new_the_old_id = None
        self.new_cursor = None

        self.new_visible = False
        self.visibilityChanged.connect(self.new_func_for_visibilityChanged)

        self.new_column_name= None
        self.new_reuse_column_name = None

    def closeEvent(self, event):
        
        self.new_textedit.clear()

        self.new_the_old_id=None

        if  self.new_cursor is not None:
            try:
                self.new_cursor.close()
                self.new_cursor = None
            except:
                pass

        super().closeEvent(event)

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

        # 清空文本
        self.new_textedit.clear()

        #
        if self.new_cursor is None:
            extra_database.connect_database()
            self.new_cursor = extra_database.conn.cursor()

        content = self.new_func_get_content(game_id)
        if content:
            self.new_textedit.insertPlainText(content)

        # 记录 id
        self.new_the_old_id = game_id

    @Slot(bool)
    def new_func_for_visibilityChanged(self,visible):
        self.new_visible = visible
        
        # 窗口显示，同步内容
        if visible:
            if self.new_the_old_id != the_variables.current_id:
                self.new_slot_for_id_change(the_variables.current_id)

    # 子类 重写
    def new_func_get_content(self,game_id):
        return ""
# extra , history.xml
class Text_dockwidget_for_history(Text_dockwidget_0):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.setObjectName("extra_history")
    def new_func_get_content(self,game_id):
        return extra_database.func_for_get_history(self.new_cursor,game_id)
# extra , history.dat
class Text_dockwidget_for_history_dat(Text_dockwidget_0):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.setObjectName("extra_history_dat")
    def new_func_get_content(self,game_id):
        return extra_database.func_for_get_history_dat(self.new_cursor,game_id)
# extra , gameinit.dat
class Text_dockwidget_for_gameinit(Text_dockwidget_0):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.setObjectName("extra_gameinit_dat")
    def new_func_get_content(self,game_id):
        return extra_database.func_for_get_gameinit(self.new_cursor,game_id)
###
# extra , mameinfo.dat 、 messinfo.dat
class Text_dockwidget_1(QDockWidget):
  
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        a_widget=QWidget(self)
        layout = QVBoxLayout(a_widget)

        self.new_textedit = Text_edit_0(self)
        #
        self.new_textedit.setReadOnly(True)
        self.new_textedit.setUndoRedoEnabled(False)
        #self.new_textedit.setContextMenuPolicy(Qt.ActionsContextMenu)
        self.new_textedit.setTabChangesFocus(False)
        self.new_textedit.setFocusPolicy(Qt.ClickFocus)

        self.new_button = QPushButton("sourcefile",self)
        self.new_button.clicked.connect(self.new_func_show_sourcefile)

        layout.addWidget(self.new_button)
        layout.addWidget(self.new_textedit)
        self.setWidget(a_widget)


        self.new_the_old_id = None
        self.new_cursor = None

        self.new_visible = False
        self.visibilityChanged.connect(self.new_func_for_visibilityChanged)

        self.new_column_name= None
        self.new_reuse_column_name = None

        self.new_content_for_sourcefile = ""

    def closeEvent(self, event):
        
        self.new_textedit.clear()

        self.new_the_old_id=None

        if  self.new_cursor is not None:
            try:
                self.new_cursor.close()
                self.new_cursor = None
            except:
                pass

        super().closeEvent(event)
    
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

        # 清空文本
        self.new_textedit.clear()

        #
        if self.new_cursor is None:
            extra_database.connect_database()
            self.new_cursor = extra_database.conn.cursor()        

        content = self.new_func_get_content(game_id)
        source_id = ui_models.get_sourcefile(game_id)
        source_content = self.new_func_get_content(source_id)

        if source_content:
            self.new_content_for_sourcefile = source_content
            self.new_button.setText(source_id)
            self.new_button.setVisible(True)
        else:
            self.new_content_for_sourcefile = ""
            self.new_button.setVisible(False)
            self.new_button.setText("")

        if content :
            self.new_textedit.insertPlainText(content)



        # 记录 id
        self.new_the_old_id = game_id
    
    @Slot(bool)
    def new_func_for_visibilityChanged(self,visible):
        self.new_visible = visible
        
        # 窗口显示，同步内容
        if visible:
            if self.new_the_old_id != the_variables.current_id:
                self.new_slot_for_id_change(the_variables.current_id)

    def new_func_show_sourcefile(self):
        self.new_button.setVisible(False)
        self.new_textedit.clear()
        self.new_textedit.insertPlainText(self.new_content_for_sourcefile)

    # 子类 重写
    def new_func_get_content(self,game_id):
        return ""
# extra , mameinfo.dat
class Text_dockwidget_for_mameinfo(Text_dockwidget_1):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.setObjectName("extra_mameinfo_dat")

    def new_func_get_content(self,game_id):
        return extra_database.func_for_get_mameinfo(self.new_cursor,game_id)    
# extra , messinfo.dat
class Text_dockwidget_for_messinfo(Text_dockwidget_1):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.setObjectName("extra_messinfo_dat")

    def new_func_get_content(self,game_id):
        return extra_database.func_for_get_messinfo(self.new_cursor,game_id)    
###
# extra , command.dat 、 command_english.dat
class Text_dockwidget_2(QDockWidget):
  
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        a_widget=QWidget(self)
        layout = QVBoxLayout(a_widget)

        self.new_textedit = Text_edit_0(self)
        #
        self.new_textedit.setReadOnly(True)
        self.new_textedit.setUndoRedoEnabled(False)
        self.new_textedit.setContextMenuPolicy(Qt.ActionsContextMenu)
        self.new_textedit.setTabChangesFocus(False)
        self.new_textedit.setFocusPolicy(Qt.ClickFocus)

        self.new_combo_box = QComboBox(self)
        #self.new_combo_box.clicked.connect(self.new_func_show_sourcefile)

        layout.addWidget(self.new_combo_box)
        layout.addWidget(self.new_textedit)
        self.setWidget(a_widget)

        self.new_combo_box.currentIndexChanged.connect(self.new_func_for_combo_box_change)
        self.new_the_old_id = None
        self.new_cursor = None

        self.new_visible = False
        self.visibilityChanged.connect(self.new_func_for_visibilityChanged)

        self.new_content_remember = dict()

    def closeEvent(self, event):
        
        self.new_textedit.clear()

        self.new_the_old_id=None

        if  self.new_cursor is not None:
            try:
                self.new_cursor.close()
                self.new_cursor = None
            except:
                pass

        super().closeEvent(event)
    
    def new_func_for_combo_box_change(self,index):
        #print("combo box change:",index)
        if index == 0:
            self.new_textedit.clear()
            for keys in sorted(self.new_content_remember):
                self.new_textedit.insertPlainText("".join(self.new_content_remember[keys]))
        elif index > 0:
            self.new_textedit.clear()
            self.new_textedit.insertPlainText("".join(self.new_content_remember[index]))

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

        # 清空文本
        self.new_textedit.clear()

        #
        if self.new_cursor is None:
            extra_database.connect_database()
            self.new_cursor = extra_database.conn.cursor()

        dict_content = self.new_func_get_content(game_id)
        if dict_content:
            self.new_content_remember = dict_content
            max_number = max(dict_content.keys())

            if max_number <= 1:
                self.new_combo_box.setVisible(False)
            else:
                self.new_combo_box.clear()
                self.new_combo_box.setVisible(True)
                self.new_combo_box.addItem("全部")
                for key in sorted(dict_content.keys()):
                    if key > 0:
                        title = dict_content[key][0].strip()
                        self.new_combo_box.addItem(title)

            
            for keys in sorted(dict_content):
                self.new_textedit.insertPlainText("".join(dict_content[keys]))
        else:
            self.new_combo_box.setVisible(False)
            self.new_content_remember = dict()

        # 记录 id
        self.new_the_old_id = game_id
    
    @Slot(bool)
    def new_func_for_visibilityChanged(self,visible):
        self.new_visible = visible
        
        # 窗口显示，同步内容
        if visible:
            if self.new_the_old_id != the_variables.current_id:
                self.new_slot_for_id_change(the_variables.current_id)

    # 子类 重写
    def new_func_get_content(self,game_id):
        return ""
# extra , command.dat
class Text_dockwidget_for_command(Text_dockwidget_2):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.setObjectName("extra_command_dat")
        self.new_textedit.setObjectName("textedit_command")

    def new_func_get_content(self,game_id):
        pickle_content = extra_database.func_for_get_command(self.new_cursor,game_id)
        if pickle_content:
            content = pickle.loads(pickle_content)
            return content
# extra , command.dat , english version
class Text_dockwidget_for_command_english(Text_dockwidget_2):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.setObjectName("extra_command_dat_english")
        self.new_textedit.setObjectName("textedit_command_english")

    def new_func_get_content(self,game_id):
        pickle_content = extra_database.func_for_get_command_english(self.new_cursor,game_id)
        if pickle_content:
            content = pickle.loads(pickle_content)
            return content
#
# 显示 命令行 查询结果
# 也用 上面的 Text_edit_0
class Dialog_for_show_command_line_result_of_mame(QDialog):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.setWindowTitle("命令行查询结果")
        self.setWindowFlags(self.windowFlags() | Qt.WindowType.WindowMaximizeButtonHint) # 最大化按钮

        self.setSizeGripEnabled(True)
        
        self.setMinimumWidth(500)
        self.setMinimumHeight(400)

        # 垂直布局管理器
        layout = QVBoxLayout()

        self.new_textedit = Text_edit_0(self)
        self.new_textedit.setReadOnly(True)
        #layout.addWidget(self.new_textedit,)
        layout.addWidget(self.new_textedit,stretch=1)

        buttor_ok = QPushButton("确定", self)
        buttor_ok.clicked.connect(self.accept)
        layout.addWidget(buttor_ok)

        self.setLayout(layout)

    def new_func_set_text(self,text):
        self.new_textedit.setPlainText(text)


class TableWidget_0(QTableWidget):
    new_signal_for_press_return = Signal(int,int)       # row,column
    new_signal_for_press_return_ctrl = Signal(int,int)  # row,column
    new_signal_for_double_click = Signal(int,int)      # row,column
    new_signal_for_double_click_ctrl = Signal(int,int) # row,column
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
     
        self.setEditTriggers(QAbstractItemView.NoEditTriggers)

        # 水平滚动条，按像素滚动，
        #   而不是 按完整列 滚动
        self.setHorizontalScrollMode(QAbstractItemView.ScrollPerPixel)
        
        # 不换行
        self.setWordWrap(False)
        
        # 选择一行，
        #   而不是选择 单元格
        self.setSelectionBehavior(QAbstractItemView.SelectRows)
        
        # 单选、多选
        self.setSelectionMode(QAbstractItemView.SingleSelection )

        # 列标题，上侧
        #   点击 标题
        #self.horizontalHeader().setSectionsClickable(True)
        #   拖动
        #self.horizontalHeader().setSectionsMovable(True)
        #   第一列，禁止拖动
        self.horizontalHeader().setFirstSectionMovable(False)
        #   关闭列标题高亮，阻止选中时字体加粗
        #   没有效果 ？？？
        #   但是小片段代码测试，有效 ？？？
        self.horizontalHeader().setHighlightSections(False)
        #   列标题，上侧，最后一列，不拉伸
        self.horizontalHeader().setStretchLastSection(False)

        # 行标题，左侧
        #   禁止用户变化行高度
        self.verticalHeader().setSectionResizeMode(QHeaderView.Fixed) 
        #   不显示，行标题
        self.verticalHeader().setVisible(False)
        #   行高度
        #self.verticalHeader().setDefaultSectionSize(80)
        #self.verticalHeader().resetDefaultSectionSize()
        self.verticalHeader().setHighlightSections(False)
        
        
        # 不显示 单元格
        self.setShowGrid(False)

        self.setTabKeyNavigation(False)

        self.setSortingEnabled(False)
        #
                
    def mouseDoubleClickEvent(self, event):
        index=self.indexAt(event.position().toPoint())
        
        if index.isValid():
            if event.button() == Qt.LeftButton:
                row = self.currentRow()
                column = self.currentColumn()

                if event.modifiers() & Qt.ControlModifier:
                    self.new_signal_for_double_click_ctrl.emit(row,column)
                else:
                    self.new_signal_for_double_click.emit(row,column)

                self.setCurrentIndex(index)
        super().mouseDoubleClickEvent(event)

    def keyPressEvent(self, event):
        print(event.key(),event.text())
        selected_indexes = self.selectionModel().selectedIndexes()
        if selected_indexes:
            index = selected_indexes[0]
            row = index.row()
            column = index.column()

            if event.key() == Qt.Key_Return:
                if event.modifiers() & Qt.ControlModifier:
                    print("Ctrl + Return")
                    self.new_signal_for_press_return_ctrl.emit(row,column)
                else:
                    print("Return")
                    self.new_signal_for_press_return.emit(row,column)
        super().keyPressEvent(event)
#
# gamelist 右键菜单 弹出窗口, bios 选择器
class Dialog_for_show_bios_selector(QDialog):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.setWindowTitle("BIOS选择器")

        self.new_bios_list = []
        self.new_width = 0
        self.new_height = 0
        self.new_game_id = ""

        self.setWindowFlags(self.windowFlags() | Qt.WindowType.WindowMaximizeButtonHint) # 最大化按钮
        self.setSizeGripEnabled(True)
        
        self.setMinimumWidth(500)
        self.setMinimumHeight(400)

        # 垂直布局管理器
        layout = QVBoxLayout()

        self.new_table = TableWidget_0(self)

        self.new_table.new_signal_for_double_click.connect(self.new_slot_for_start_mame)
        self.new_table.new_signal_for_press_return.connect(self.new_slot_for_start_mame)
        self.new_table.new_signal_for_double_click_ctrl.connect(self.new_slot_for_start_mame_detached)
        self.new_table.new_signal_for_press_return_ctrl.connect(self.new_slot_for_start_mame_detached)

        self.new_table.setColumnCount(2)
        self.new_table.setHorizontalHeaderLabels(["BIOS名称","BIOS描述"])
        self.new_table.setColumnWidth(0,200)
        self.new_table.setColumnWidth(1,300)

        
        layout.addWidget(self.new_table,stretch=1)

        #buttor_ok = QPushButton("确定", self)
        #buttor_ok.clicked.connect(self.accept)
        #layout.addWidget(buttor_ok)

        self.setLayout(layout)

    def new_func_set_values(self,game_id,bios_list):
        # bios_list
        #   [[bios_name,bios_description],[bios_name_2,bios_description_2],...]
        self.new_table.clearContents()
        self.new_bios_list = bios_list
        self.new_game_id = game_id


        if not bios_list:
            self.setWindowTitle(f"BIOS选择器 - {game_id} - 没有 BIOS")
            self.new_table.setRowCount(len(bios_list))
            return
        else:
            self.setWindowTitle(f"BIOS选择器 - {game_id}")
            self.new_table.setRowCount(len(bios_list))
            for n in range(len(bios_list)):
                self.new_table.setItem(n,0,QTableWidgetItem(bios_list[n][0]))
                self.new_table.setItem(n,1,QTableWidgetItem(bios_list[n][1]))
        
    def hideEvent(self, event):
        self.new_width = self.width()  
        self.new_height = self.height()  
        super().hideEvent(event)

    def showEvent(self, event):
        if self.new_width  and self.new_height:
            self.resize(self.new_width,self.new_height)
        super().showEvent(event)
    
    @Slot(int,int)
    def new_slot_for_start_mame(self,row,column):

        print(row,column)
        print(self.new_bios_list[row])
        bios_name = self.new_bios_list[row][0]
        if self.new_game_id:
            self.parentWidget().new_func_start_emulator(self.new_game_id,other_command_list=["-bios",bios_name])
            self.accept()

    @Slot(int,int)
    def new_slot_for_start_mame_detached(self,row,column):
        print(row,column)
        print(self.new_bios_list[row])
        bios_name = self.new_bios_list[row][0]
        if self.new_game_id:
            self.parentWidget().new_func_start_emulator(self.new_game_id,hide=False,other_command_list=["-bios",bios_name])
            self.accept()
#
# F1 ，用户自定义运行方式，选择器
class Dialog_for_show_script_selector(QDialog):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.setWindowTitle("选择自定义运行方式")

        self.new_script_list = []
        self.new_width = 0
        self.new_height = 0
        self.new_game_id = ""

        self.setWindowFlags(self.windowFlags() | Qt.WindowType.WindowMaximizeButtonHint) # 最大化按钮
        self.setSizeGripEnabled(True)
        
        self.setMinimumWidth(300)
        self.setMinimumHeight(400)

        # 垂直布局管理器
        layout = QVBoxLayout()

        self.new_table = TableWidget_0(self)
        self.new_table.horizontalHeader().setStretchLastSection(True)

        self.new_table.new_signal_for_double_click.connect(self.new_slot_for_start_mame)
        self.new_table.new_signal_for_press_return.connect(self.new_slot_for_start_mame)
        self.new_table.new_signal_for_double_click_ctrl.connect(self.new_slot_for_start_mame_detached)
        self.new_table.new_signal_for_press_return_ctrl.connect(self.new_slot_for_start_mame_detached)

        self.new_table.setColumnCount(1)
        self.new_table.setHorizontalHeaderLabels( ["所在文件夹："+the_files.script_folder] )
        #self.new_table.setColumnWidth(0,400)
        #self.new_table.setColumnWidth(1,300)

        
        layout.addWidget(self.new_table,stretch=1)

        #buttor_ok = QPushButton("确定", self)
        #buttor_ok.clicked.connect(self.accept)
        #layout.addWidget(buttor_ok)

        self.setLayout(layout)

    def new_func_set_values(self,game_id):
        # script_list

        self.new_table.clearContents()

        self.new_script_list = []
        self.new_game_id = game_id

        def get_text_file_list(folder): # 仅搜一层目录
            file_list = []
            
            if not os.path.isdir(folder):
                return file_list
                        
            (dirpath, dirnames, filenames) = next( os.walk(folder) )
            for file_name in filenames:
                if file_name.lower().endswith(".txt"):
                    file_list.append( file_name )
            return file_list

        file_list = get_text_file_list(the_files.script_folder)
        
        self.new_script_list = file_list

        if not file_list:
            self.setWindowTitle("选择自定义运行方式" + " - " + game_id + " - 还没添加自定义运行方式")
            return
        else:
            self.setWindowTitle("选择自定义运行方式" + " - " + game_id)

            self.new_table.setRowCount(len(file_list))
            for n in range(len(file_list)):
                self.new_table.setItem(n,0,QTableWidgetItem(file_list[n]))
 
        
    def hideEvent(self, event):
        self.new_width = self.width()  
        self.new_height = self.height()  
        super().hideEvent(event)

    def showEvent(self, event):
        if self.new_width  and self.new_height:
            self.resize(self.new_width,self.new_height)
        super().showEvent(event)
    
    @Slot(int,int)
    def new_slot_for_start_mame(self,row,column):

        print(row,column)
        print(self.new_script_list[row])
        script_name = self.new_script_list[row]
        if self.new_game_id:
            self.parentWidget().new_func_start_process_by_script(self.new_game_id,script_name,hide=True)
            self.accept()

    @Slot(int,int)
    def new_slot_for_start_mame_detached(self,row,column):
        print(row,column)
        print(self.new_script_list[row])
        script_name = self.new_script_list[row]
        if self.new_game_id:
            self.parentWidget().new_func_start_process_by_script(self.new_game_id,script_name,hide=False)   
            self.accept()
#







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
        self.new_ui_line_edit.setPlaceholderText("游戏列表搜索")
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

        return self.new_ignore_case, self.new_search_columns
    
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

