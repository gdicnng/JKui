import sys,os,time,shutil,io
import pickle
import locale
import re
import sqlite3
import functools
import traceback
import webbrowser

from qtpy.QtWidgets import *
from qtpy.QtGui import *
from qtpy.QtCore import *

import the_variables
import the_files
import ui_index
import ui_small_windows
import misc_funcs
import xml_parse_mame
import ui_models
import ui_central_widget
import the_user_settings_default_value
import extra_folders
import extra_database


class TheMainWindow(QMainWindow):

    def __init__(self):
        super().__init__()
        self.setObjectName("mainWindow")

        self.setWindowTitle(the_variables.software_name)
        #self.setGeometry(100, 100, 600, 400)

        icon_pixmap = QPixmap()
        try:
            icon_pixmap.loadFromData(the_files.icon_for_mainwindow)
        except:
            pass
        
        
        self.setWindowIcon( QIcon(icon_pixmap) )
        

        # 用户配置文件
        #self.new_settings = QSettings( "gdicnng" ,the_variables.software_name , self)
        self.new_settings = QSettings( the_files.user_config_file , QSettings.IniFormat , self)
        if hasattr(self.new_settings, 'setIniCodec'):# pyside2
            self.new_settings.setIniCodec(QTextCodec.codecForName("UTF-8")) 
        print(self.new_settings.fileName())

        def func_for_qsettings():
            the_variables.user_settings = self.new_settings # 记录
            # Store the settings in INI files. Note that INI files lose the distinction between numeric data and the strings used to encode them, 
            # so values written as numbers shall be read back as QString.
            
            # 加载默认值
            for key, value in the_user_settings_default_value.default_value.items():
                if not self.new_settings.value(key):
                    self.new_settings.setValue(key, value)
            
            # 更新 extra 路径记录
            the_variables.update_extra_path()

            # last game ，这个得移到启动最后，不然周边会使用 game_id 加载内容

            # auto_select_last_game
            try: the_variables.auto_select_last_game = self.new_settings.value("auto_select_last_game",False,type=bool)
            except: the_variables.auto_select_last_game = False
            # use_icon_not_have
            try: the_variables.use_icon_not_have = self.new_settings.value("use_icon_not_have",False,type=bool)
            except: the_variables.use_icon_not_have = False

        func_for_qsettings()
          

        

        # 
        self.new_func_creatCentralWidget()
        self.new_func_createActions()
        self.new_func_createMenus()
        self.new_func_createStatusBar()
        self.new_func_createDockWindows()
        self.new_func_createToolBars()



        
        self.new_dialog_for_choose_emulator_path_and_working_dir = None


        self.new_shortcut = QShortcut(QKeySequence("Ctrl+P"), self)
        self.new_shortcut.activated.connect(self.new_func_key_ctrl_p)

        QMetaObject.connectSlotsByName(self)
    ##################
    def new_func_creatCentralWidget(self):
        self.new_ui_central_widget = ui_central_widget.TheCentralWidget(self)
        self.new_ui_central_widget.setObjectName("centralwidget")
        self.setCentralWidget(self.new_ui_central_widget)
        
        self.new_ui_central_widget.new_signal_for_id_change.connect( self.new_func_slot_for_receive_id_change )

    def new_func_createActions(self):
        
        self.new_action_test = QAction("test",self,)
        self.new_action_test.triggered.connect( self.new_func_do_nothing )
        
        self.new_action_test_progressbar = QAction("test progress bar",self,)
        self.new_action_test_progressbar.triggered.connect( self.new_func_show_progress_bar_on_statusbar_for_test )
        
        self.new_action_save_settings = QAction("save settings",self,)
        #self.new_action_save_settings.triggered.connect( self.new_func_save_settings )
    
    def new_func_createMenus(self):
        self.new_menu_ui = self.menuBar().addMenu("UI")
        #self.new_menu_ui.addAction(self.new_action_save_settings)
        #self.new_menu_ui.addAction(self.new_action_load_settings)
        
        
        self.new_menu_ui.addSeparator()
        self.new_menu_ui_style = self.new_menu_ui.addMenu("style")
        self.new_menu_ui_qss = self.new_menu_ui.addMenu("qss")
        
        self.new_menu_ui.addSeparator()
        
        # UI → style
        def make_menu_for_sytle():
            self.new_action_group_for_style=QActionGroup(self)
            
            style_list = QStyleFactory.keys()
            app = QCoreApplication.instance()
            cuttent_style_name = app.style().objectName()
            
            for style_name in style_list:
                action =  QAction(style_name,self,)
                action.setCheckable(True)
                action.setChecked(False)
                action.triggered.connect( functools.partial(self.new_func_set_style_by_menu,action) )
                
                # 初始化 UI 时，标记 当前 style
                if cuttent_style_name.lower() == style_name.lower():
                    action.setChecked(True)
                
                self.new_action_group_for_style.addAction(action)
                
                self.new_menu_ui_style.addAction(action)
        
        make_menu_for_sytle()
        
        # UI → qss
        def make_menu_for_qss():
            #self.new_ui_menu_ui_qss
            
            # 重置按钮
            action =  QAction("重置",self,)
            action.triggered.connect(self.new_func_clear_qss)
            self.new_menu_ui_qss.addAction( action )
            self.new_menu_ui_qss.addSeparator()
            
            self.new_action_group_for_qss=QActionGroup(self)
            
            # qss 文件
            folder_qss = the_files.folder_qss
            if not os.path.isdir(folder_qss):return
            
            qss_file_list = []
            
            for (dirpath, dirnames, filenames) in os.walk( folder_qss ):
                for file_name  in filenames:
                    if file_name.lower().endswith(".qss"):
                        qss_file_list.append( file_name )
                break
            
            # creat action for qss
            for qss_file_name in qss_file_list:
                action =  QAction(qss_file_name,self,)
                action.triggered.connect( functools.partial(self.new_func_load_qss_file_by_menu,action) )
                action.setCheckable(True)
                self.new_action_group_for_qss.addAction(action)
                self.new_menu_ui_qss.addAction( action )
        make_menu_for_qss()
        
        ##### 语言
        self.new_menu_language = self.menuBar().addMenu("语言/language")
        # 游戏列表翻译文件
        self.new_action_for_gamelist_translation_file = QAction("游戏列表翻译文件(game list translation file)",self,)
        self.new_action_for_gamelist_translation_file.triggered.connect( self.new_func_set_gamelist_translation_file )
        self.new_menu_language.addAction(self.new_action_for_gamelist_translation_file)
        # ui 翻译文件
        # 未完等续
        self.new_action_for_ui_translation_file = QAction("ui 翻译文件 ，未完成(ui translation file,not finished yet)",self,)
        #self.new_action_for_ui_translation_file.triggered.connect( self.new_func_set_ui_translation_file )
        self.new_menu_language.addAction(self.new_action_for_ui_translation_file)

        ##### 字体等
        self.new_menu_font = self.menuBar().addMenu("字体等")
        # 字体 设置 字体
        action_set_font = QAction("设置字体",self,)
        action_set_font.setCheckable(False)
        action_set_font.triggered.connect( self.new_func_for_set_font )
        self.new_menu_font.addAction(action_set_font)

        # 字体等 列表 行高
        self.new_menu_font.addSeparator()
        action_set_row_height = QAction("设置游戏列表行高",self,)
        action_set_row_height.setCheckable(False)
        action_set_row_height.triggered.connect( self.new_func_for_set_row_height )
        self.new_menu_font.addAction(action_set_row_height)

        # 字体等 游戏列表 设置图标大小
        # 图标大小（普通列表）
        try:
            icon_size = self.new_settings.value("gamelist/icon_size_for_gamelist",type=int) # 取值到 the_variables.icon_size
        except:
            icon_size = 0
        if type(icon_size) is int:
            if icon_size > 0:
                the_variables.icon_size = icon_size
        # 图标大小（图标列表）
        try:
            icon_size_for_icon_table = self.new_settings.value("gamelist/icon_size_for_icon_table",type=int) # 取值到 the_variables.icon_size
        except:
            icon_size_for_icon_table = 0
        if type(icon_size_for_icon_table) is int:
            if icon_size_for_icon_table > 0:
                ui_models.icon_size_for_icon_table = icon_size_for_icon_table
        # 单元格间距（图标列表）
        try:
            spacing_for_icon_table = self.new_settings.value("gamelist/spacing_for_icon_table",type=int) # 取值到 the_variables.icon_table_cell_size
        except:
            spacing_for_icon_table = 0
        if type(spacing_for_icon_table) is int:
            if spacing_for_icon_table > 0:
                the_variables.spacing_for_icon_table = spacing_for_icon_table
        # 单元格间距（图片列表）
        try:
            sapcing_for_image_table = self.new_settings.value("gamelist/sapcing_for_image_table",type=int) # 取值到 the_variables.sapcing_for_image_table
        except:
            sapcing_for_image_table = 0
        if type(sapcing_for_image_table) is int:
            if sapcing_for_image_table > 0:
                the_variables.sapcing_for_image_table = sapcing_for_image_table
        # 图片宽度（图片列表）
        try:
            image_width_for_image_table = self.new_settings.value("gamelist/image_width_for_image_table",type=int) 
        except:
            image_width_for_image_table = 0
        if type(image_width_for_image_table) is int:
            if image_width_for_image_table > 0:
                ui_models.image_width_for_image_table = image_width_for_image_table
        # 图片高度（图片列表）
        try:
            image_height_for_image_table = self.new_settings.value("gamelist/image_height_for_image_table",type=int) 
        except:
            image_height_for_image_table = 0
        if type(image_height_for_image_table) is int:
            if image_height_for_image_table > 0:
                ui_models.image_height_for_image_table = image_height_for_image_table
        # 文字区域高度 （图片列表）
        try:
            text_height_for_image_table = self.new_settings.value("gamelist/text_height_for_image_table",type=int)
        except:
            text_height_for_image_table = 0
        if type(text_height_for_image_table) is int:
            if text_height_for_image_table > 0:
                ui_models.text_height_for_image_table = text_height_for_image_table
        # 图标列表，文字区域宽度（如果比图标宽度小，自动取值于图标宽度）
        try:
            text_width_for_icon_table = self.new_settings.value("gamelist/text_width_for_icon_table",type=int)
        except:
            text_width_for_icon_table = 0
        if type(text_width_for_icon_table) is int:
            if text_width_for_icon_table > 0:
                ui_models.text_width_for_icon_table = text_width_for_icon_table
        # 图标列表，文字区域高度
        try:
            text_height_for_icon_table = self.new_settings.value("gamelist/text_height_for_icon_table",type=int)
        except:
            text_height_for_icon_table = 0
        if type(text_height_for_icon_table) is int:
            if text_height_for_icon_table > 0:
                ui_models.text_height_for_icon_table = text_height_for_icon_table
        # 图标大小（普通列表、图标列表）、图片大小（普通列表、图标列表）、图片大小（图片列表）",self,)
        
        self.new_menu_font.addSeparator()
        action_set_icon_size = QAction("设置 图标大小 、图片大小 等",self,)
        action_set_icon_size.setCheckable(False)
        action_set_icon_size.triggered.connect( self.new_func_for_set_icon_size )
        self.new_menu_font.addAction(action_set_icon_size)

        # 字体等 游戏列表 选中行颜色
        self.new_menu_font.addSeparator()
        action_set_highlight_row_colour = QAction("设置选中行颜色",self,)
        action_set_highlight_row_colour.setCheckable(False)
        action_set_highlight_row_colour.triggered.connect( self.new_func_for_set_highlight_row_colour )
        self.new_menu_font.addAction(action_set_highlight_row_colour)

        # 字体等 游戏列表 2 level tree like ，设置打开关闭字符串
        self.new_menu_font.addSeparator()
        action_set_open_colse_string_for_tableview_2_level_tree_like = QAction("设置打开关闭字符串",self,)
        action_set_open_colse_string_for_tableview_2_level_tree_like.setCheckable(False)
        action_set_open_colse_string_for_tableview_2_level_tree_like.triggered.connect( self.centralWidget().new_func_set_open_colse_string_for_tableview_2_level_tree_like )
        self.new_menu_font.addAction(action_set_open_colse_string_for_tableview_2_level_tree_like)



        ##### 设置
        self.new_menu_settings = self.menuBar().addMenu("设置")
        #
        self.new_action_delete_emulator = QAction("删除模拟器路径",self,)
        self.new_action_delete_emulator.triggered.connect( self.new_func_delete_emulator )
        self.new_menu_settings.addAction(self.new_action_delete_emulator)
        #
        self.new_action_emulator_settings = QAction("模拟器设置( MAME新版本的话，可以打开模拟器直接设置了 )",self,)
        self.new_action_emulator_settings.triggered.connect( self.centralWidget().new_func_start_emulator )
        self.new_menu_settings.addAction(self.new_action_emulator_settings)
        #
        self.new_action_extra_path = QAction("周边路径",self,)
        self.new_menu_settings.addAction(self.new_action_extra_path)
        self.new_action_extra_path.triggered.connect( self.new_func_set_extra_path )

        ##### 目录
        self.new_menu_index = self.menuBar().addMenu("目录列表")
        # 编辑
        try:
            value = self.new_settings.value("index/edit_mode",type=bool)
        except:
            value = False
        if value:ui_models.index_edit_mode = True
        new_action_set_index_edit_mode = QAction("编辑目录",self,)
        new_action_set_index_edit_mode.setCheckable(True)
        new_action_set_index_edit_mode.setChecked(ui_models.index_edit_mode)
        new_action_set_index_edit_mode.toggled.connect( self.new_func_set_index_edit_mode )
        self.new_menu_index.addAction(new_action_set_index_edit_mode)
        # 保存
        new_action_save_index = QAction("保存目录(编辑完成后，记得手动点击此处保存)",self,)
        new_action_save_index.setCheckable(False)
        new_action_save_index.triggered.connect( self.new_func_save_index )
        self.new_menu_index.addAction(new_action_save_index)
        # 显示、隐藏 内置目录
        self.new_menu_index.addSeparator()
        
        self.new_menu_show_or_hide_internal_index = self.new_menu_index.addMenu("显示、隐藏 内置目录")
        # 等读取数据后，再添加内容

        self.new_menu_index.addSeparator()





        ##### 游戏列表
        self.new_menu_gamelist=self.menuBar().addMenu("游戏列表")
        # 游戏列表 刷新游戏列表
        self.new_action_scan_roms_exist_split = QAction("刷新游戏列表 split (极简版本，仅检查文件是否存在)",self,)
        self.new_action_scan_roms_exist_split.triggered.connect( self.new_func_scan_game_files_only_check_if_file_exists )
        self.new_menu_gamelist.addAction(self.new_action_scan_roms_exist_split)
        self.new_action_scan_roms_exist_merged = QAction("刷新游戏列表 merged (极简版本，仅检查文件是否存在)",self,)
        self.new_action_scan_roms_exist_merged.triggered.connect(lambda:self.new_func_scan_game_files_only_check_if_file_exists(True))
        self.new_menu_gamelist.addAction(self.new_action_scan_roms_exist_merged)
        self.new_menu_gamelist.addSeparator()
        # 游戏列表 显示 tableview
        self.new_action_show_tableview = QAction("显示 tableview",self,)
        self.new_action_show_tableview.triggered.connect( self.centralWidget().new_func_show_tableview )
        self.new_menu_gamelist.addAction(self.new_action_show_tableview)
        # 游戏列表 显示 tableview 2 level
        self.new_action_show_tableview_2_level = QAction("显示 tableview 2 level",self,)
        self.new_action_show_tableview_2_level.triggered.connect( self.centralWidget().new_func_show_tableview_2_level )
        self.new_menu_gamelist.addAction(self.new_action_show_tableview_2_level)
        # 游戏列表 显示 tableview 2 level tree like
        self.new_action_show_tableview_2_level_tree_like = QAction("显示 tableview 2 level 树状",self,)
        self.new_action_show_tableview_2_level_tree_like.triggered.connect( self.centralWidget().new_func_show_tableview_2_level_tree_like )
        self.new_menu_gamelist.addAction(self.new_action_show_tableview_2_level_tree_like)
        # 游戏列表 显示 treeview
        self.new_action_show_treeview = QAction("显示 treeview",self,)
        self.new_action_show_treeview.triggered.connect( self.centralWidget().new_func_show_treeview )
        self.new_menu_gamelist.addAction(self.new_action_show_treeview)
        # 游戏列表 显示 icon table
        self.new_action_show_icon_table = QAction("显示 图标模式",self,)
        self.new_action_show_icon_table.triggered.connect( self.centralWidget().new_func_show_icon_table )
        self.new_menu_gamelist.addAction(self.new_action_show_icon_table)
        # 游戏列表 显示 image table
        self.new_action_show_image_table = QAction("显示 图片模式（使用最后一个 .zip 压缩包中的图片资源）",self,)
        self.new_action_show_image_table.triggered.connect( self.centralWidget().new_func_show_image_table )
        self.new_menu_gamelist.addAction(self.new_action_show_image_table)
        self.new_menu_gamelist.addSeparator()
        # 游戏列表 本地化排序
        self.new_menu_gamelist.addSeparator()
        action_set_sort_use_locale = QAction("本地化排序(仅翻译这一列)",self,)
        action_set_sort_use_locale.setCheckable(True)
        try:    the_variables.sort_use_locale = self.new_settings.value("gamelist/sort_use_locale",type=bool)
        except: the_variables.sort_use_locale = False
        action_set_sort_use_locale.setChecked(the_variables.sort_use_locale)
        action_set_sort_use_locale.toggled.connect( self.new_func_gamelist_sort_use_locale )
        self.new_menu_gamelist.addAction(action_set_sort_use_locale)
        # 游戏列表 自动选择上一个游戏
        self.new_menu_gamelist.addSeparator()
        action_set_auto_select_last_game = QAction("自动选择上一个游戏",self,)
        action_set_auto_select_last_game.setCheckable(True)
        try:    the_variables.auto_select_last_game = self.new_settings.value("auto_select_last_game",False,type=bool)
        except: the_variables.auto_select_last_game = False
        action_set_auto_select_last_game.setChecked(the_variables.auto_select_last_game)
        action_set_auto_select_last_game.toggled.connect( self.new_func_gamelist_auto_select_last_game )
        self.new_menu_gamelist.addAction(action_set_auto_select_last_game)
        # 游戏列表 标记未拥有游戏
        self.new_menu_gamelist.addSeparator()
        action_set_mark_not_have = QAction("标记未拥有游戏",self,)
        action_set_mark_not_have.setCheckable(True)
        try:    the_variables.use_icon_not_have = self.new_settings.value("use_icon_not_have",False,type=bool)
        except: the_variables.use_icon_not_have = False
        action_set_mark_not_have.setChecked(the_variables.use_icon_not_have)
        action_set_mark_not_have.toggled.connect( self.new_func_gamelist_mark_not_have )
        self.new_menu_gamelist.addAction(action_set_mark_not_have)
        # 游戏列表 使用额外 icon 资源包
        self.new_menu_gamelist.addSeparator()
        action_set_use_icon_extra_resource = QAction("使用图标",self,)
        action_set_use_icon_extra_resource.setCheckable(True)
        try:    the_variables.use_icon_extra_resource = self.new_settings.value("gamelist/use_icon_extra_resource",False,type=bool)
        except: the_variables.use_icon_extra_resource = False
        action_set_use_icon_extra_resource.setChecked(the_variables.use_icon_extra_resource)
        action_set_use_icon_extra_resource.toggled.connect( self.new_func_gamelist_use_icon_extra_resource )
        self.new_menu_gamelist.addAction(action_set_use_icon_extra_resource)

        # 游戏列表 全局过滤
        self.new_menu_gamelist.addSeparator()
        action_set_gamelist_filter = QAction("全局过滤",self,)
        action_set_gamelist_filter.setCheckable(False)
        action_set_gamelist_filter.triggered.connect( self.new_func_for_set_gamelist_filter )
        self.new_menu_gamelist.addAction(action_set_gamelist_filter)
        # 游戏列表 多选模式（勾选）
        self.new_menu_gamelist.addSeparator()
        action_set_multi_selection_mode = QAction("多选模式（勾选）(仅前三个列表)",self,)
        action_set_multi_selection_mode.setCheckable(True)
        try:    ui_models.multi_selection_mode = self.new_settings.value("gamelist/multi_selection_mode",False,type=bool)
        except: ui_models.multi_selection_mode = False
        action_set_multi_selection_mode.setChecked(ui_models.multi_selection_mode)
        action_set_multi_selection_mode.toggled.connect( self.new_func_gamelist_multi_selection_mode )
        self.new_menu_gamelist.addAction(action_set_multi_selection_mode)
        # 游戏列表 列表编辑模式 仅翻译列
        self.new_menu_gamelist.addSeparator()
        action_set_gamelist_edit_mode = QAction("列表编辑模式 仅翻译列（编辑后记得手动点击下方选项保存）",self,)
        action_set_gamelist_edit_mode.setCheckable(True)
        #try:    ui_models.gamelist_editable_mode = self.new_settings.value("gamelist/gamelist_editable_mode",False,type=bool)
        #except: ui_models.gamelist_editable_mode = False
        action_set_gamelist_edit_mode.setChecked(ui_models.gamelist_editable_mode)
        action_set_gamelist_edit_mode.toggled.connect( self.new_func_gamelist_list_edit_mode )
        self.new_menu_gamelist.addAction(action_set_gamelist_edit_mode)
        # 游戏列表 保存
        action_for_save_gamelist = QAction("保存游戏列表",self,)
        action_for_save_gamelist.triggered.connect( self.new_func_save_gamelist )
        self.new_menu_gamelist.addAction(action_for_save_gamelist)
        self.new_menu_gamelist.addSeparator()


        ##### 周边
        self.new_menu_extra = self.menuBar().addMenu("周边")
        # 周边 显示/隐藏 周边窗口
        self.new_menu_for_show_dock_windows = self.new_menu_extra.addMenu("显示/隐藏 周边窗口")
        self.new_menu_extra.addSeparator()
        # 周边 重新加载周边文本
        action_for_load_extra_text = QAction("重新加载周边文本",self,)
        action_for_load_extra_text.triggered.connect(self.new_func_load_extra_text_to_database)
        self.new_menu_extra.addAction(action_for_load_extra_text)

        ##### 其它
        self.new_ui_menu_other = self.menuBar().addMenu("其它")

        the_url = r"https://github.com/gdicnng/JKui"
        action_website = QAction("网址：" + the_url,self,)
        action_website.triggered.connect(lambda: webbrowser.open(url=the_url))
        self.new_ui_menu_other.addAction(action_website)

        self.new_ui_menu_other.addSeparator()

        action_show_python_version = QAction("显示 python 版本",self,)
        action_show_python_version.triggered.connect(self.new_func_show_python_version)
        self.new_ui_menu_other.addAction(action_show_python_version)

        #self.new_ui_menu_other.addAction(self.new_action_test_progressbar)

    def new_func_createStatusBar(self):
        statusbar = self.statusBar()

        self.new_ui_statusbar_for_current_number = QLabel(statusbar)
        statusbar.addPermanentWidget( self.new_ui_statusbar_for_current_number , 0 )
        self.new_ui_statusbar_for_current_number.setVisible(True) 
        #self.new_ui_statusbar_for_current_number.setText("0/")
#
        #a_label = QLabel(statusbar)
        #statusbar.addPermanentWidget( a_label, 0 )
        #a_label.setVisible(True)
        #a_label.setText("/")

        self.new_ui_statusbar_for_total_number = QLabel(statusbar)
        statusbar.addPermanentWidget( self.new_ui_statusbar_for_total_number , 0 )
        self.new_ui_statusbar_for_total_number.setVisible(True)

     

        self.new_progressbar_on_statusbar = QProgressBar(statusbar)
        self.new_progressbar_on_statusbar.setMinimum(0)
        self.new_progressbar_on_statusbar.setMaximum(0)
        # If minimum and maximum both are set to 0, the bar shows a busy indicator instead of a percentage of steps        

        statusbar.addWidget( self.new_progressbar_on_statusbar , 1 )
        self.new_progressbar_on_statusbar.setVisible(False)

        statusbar.showMessage("StatusBar")

    # dock window
    def new_func_createDockWindows(self):
        
        extra_dock_window_list = []

        self.setDockOptions(QMainWindow.AnimatedDocks | QMainWindow.VerticalTabs | QMainWindow.AllowTabbedDocks | QMainWindow.AllowNestedDocks)
        
        # 目录
        def func_for_index():
            
            self.new_dock_index = ui_index.Index_dockwidget("目录",self,)
            self.new_dock_index.setObjectName("index") # 不设置，不好保存
            self.new_dock_index.setAllowedAreas(Qt.AllDockWidgetAreas )
            features =self.new_dock_index.features()
            self.new_dock_index.setFeatures(features & (~QDockWidget.DockWidgetFloatable) )
            
            self.new_ui_index = self.new_dock_index.new_ui_index
            
            self.addDockWidget(Qt.LeftDockWidgetArea, self.new_dock_index)
            
            self.new_ui_index.new_signal_change_index.connect(self.new_func_slot_for_receive_index)
        func_for_index()
                

        ########
        # extras text
        #
        # history.xml
        self.new_list_for_dock_window_use_database = []
        dock_window_for_history_xml = ui_small_windows.Text_dockwidget_for_history("history.xml",self)
        dock_window_for_history_dat = ui_small_windows.Text_dockwidget_for_history_dat("history.dat",self)
        dock_window_for_gameinit_dat = ui_small_windows.Text_dockwidget_for_gameinit("gameinit.dat",self)
        dock_window_for_mameinfo_dat = ui_small_windows.Text_dockwidget_for_mameinfo("mameinfo.dat",self)
        dock_window_for_messinfo_dat = ui_small_windows.Text_dockwidget_for_messinfo("messinfo.dat",self)
        dock_window_for_command_dat = ui_small_windows.Text_dockwidget_for_command("command.dat",self)
        dock_window_for_command_english = ui_small_windows.Text_dockwidget_for_command_english("(English)command.dat",self)

        self.new_list_for_dock_window_use_database.append(dock_window_for_history_xml)
        self.new_list_for_dock_window_use_database.append(dock_window_for_history_dat)
        self.new_list_for_dock_window_use_database.append(dock_window_for_gameinit_dat)
        self.new_list_for_dock_window_use_database.append(dock_window_for_mameinfo_dat)
        self.new_list_for_dock_window_use_database.append(dock_window_for_messinfo_dat)
        self.new_list_for_dock_window_use_database.append(dock_window_for_command_dat)
        self.new_list_for_dock_window_use_database.append(dock_window_for_command_english)

        for text_dock_window in self.new_list_for_dock_window_use_database:
            extra_dock_window_list.append(text_dock_window)
            text_dock_window.setAllowedAreas(Qt.AllDockWidgetAreas )
            self.addDockWidget(Qt.RightDockWidgetArea, text_dock_window)
            text_dock_window.setVisible(False) 



        # extras 图片
        def func_for_image_dockwindow(title_prefix,object_name_prefix,number = 1):
            if number < 1 : return
            
            # 小窗口 1-5
            for n in range(1,number + 1):
                
                title       = title_prefix + str(n)
                object_name = object_name_prefix + str(n)
                
                # self.new_dock_image_n
                # self.new_dock_text_n
                variable_name = "new_dock_" + object_name_prefix + str(n)
                
                #print()
                #print(title)
                #print(object_name)
                #print(variable_name)
                
                setattr(self,variable_name,ui_small_windows.Image_dockwidget(title, self), )
                dock_window = getattr( self, variable_name)
                extra_dock_window_list.append(dock_window)
                
                dock_window.setObjectName( object_name )
                dock_window.setAllowedAreas(Qt.AllDockWidgetAreas )
                
                
                self.addDockWidget(Qt.RightDockWidgetArea, dock_window)
                
                # 隐藏
                dock_window.setVisible(False) 
                

        #
        func_for_image_dockwindow("图片_","image_",number=the_variables.image_dockwidget_numbers)
        self.new_menu_for_show_dock_windows.addSeparator()
        

        
        # 仅显示两个就行了
        # 不显示算了
        #dock_window_1 = getattr(self,"new_dock_image_1")
        #dock_window_1.setVisible(True)
        #dock_window_2 = getattr(self,"new_dock_image_2")
        #dock_window_2.setVisible(True)
        

        # index,添加到菜单
        self.new_menu_for_show_dock_windows.addAction(self.new_dock_index.toggleViewAction())
        for extra_dock_window in extra_dock_window_list:
            # extras 选中项变化，连接信号槽
            self.centralWidget().new_signal_for_id_change.connect(extra_dock_window.new_slot_for_id_change)
            # extras 添加到菜单
            self.new_menu_for_show_dock_windows.addAction(extra_dock_window.toggleViewAction())

    def new_func_createToolBars(self):
        # 目录
        self.new_toolbar_for_index = self.addToolBar("目录切换")
        self.new_toolbar_for_index.setObjectName("toolbar_for_index")
        self.new_toolbar_for_index.setAllowedAreas(Qt.TopToolBarArea)
        self.new_toolbar_for_index.setMovable(False)
        self.new_toolbar_for_index.setFloatable(False)
        new_action = QAction("1",self,)
        new_action.setChecked(False)
        new_action.setText("=")
        self.new_index_show_action = self.new_dock_index.toggleViewAction() # 这个原生的 action ，选中时会高亮
        new_action.triggered.connect( self.new_index_show_action.trigger )
        self.new_toolbar_for_index.addAction(new_action)

    
        self.new_toolbar_for_gamelist = self.addToolBar("列表切换")
        self.new_toolbar_for_gamelist.setObjectName("toolbar_for_gamelist")
        self.new_toolbar_for_gamelist.setAllowedAreas(Qt.TopToolBarArea)
        self.new_toolbar_for_gamelist.setMovable(False)
        self.new_toolbar_for_gamelist.setFloatable(False)
        new_action_tableview = QAction("1",self,)
        new_action_tableview.triggered.connect( self.centralWidget().new_func_show_tableview )
        new_action_tableview_2_level = QAction("2",self,)
        new_action_tableview_2_level.triggered.connect( self.centralWidget().new_func_show_tableview_2_level )
        new_action_tableview_2_level_tree_like = QAction("3",self,)
        new_action_tableview_2_level_tree_like.triggered.connect( self.centralWidget().new_func_show_tableview_2_level_tree_like )
        new_action_treeview = QAction("4",self,)
        new_action_treeview.triggered.connect( self.centralWidget().new_func_show_treeview )
        new_action_icon_table = QAction("5",self,)
        new_action_icon_table.triggered.connect( self.centralWidget().new_func_show_icon_table )
        new_action_image_table = QAction("6",self,)
        new_action_image_table.triggered.connect( self.centralWidget().new_func_show_image_table )

        self.new_toolbar_for_gamelist.addAction(new_action_tableview)
        self.new_toolbar_for_gamelist.addAction(new_action_tableview_2_level)
        self.new_toolbar_for_gamelist.addAction(new_action_tableview_2_level_tree_like)
        self.new_toolbar_for_gamelist.addAction(new_action_treeview)
        self.new_toolbar_for_gamelist.addAction(new_action_icon_table)
        self.new_toolbar_for_gamelist.addAction(new_action_image_table)

        #self.new_toolbar_for_gamelist.addSeparator()

        self.new_tool_bar_for_search = ui_small_windows.Toolbars_for_search(self)
        self.new_tool_bar_for_search.setObjectName("toolbar_for_search")
        self.new_tool_bar_for_search.setWindowTitle("搜索栏")
        self.new_tool_bar_for_search.setFloatable(False)
        #self.new_tool_bar_for_search.setMovable(False)
        self.new_tool_bar_for_search.setAllowedAreas(Qt.TopToolBarArea)
        self.new_tool_bar_for_search.new_signal_for_search.connect(self.new_func_for_search)
        self.new_tool_bar_for_search.new_signal_for_clear_search.connect(self.centralWidget().new_func_cancel_search)
        self.addToolBar(self.new_tool_bar_for_search)


    ####################

    def closeEvent(self,event):
        print()
        print("close")
        self.new_func_save_settings()

        if extra_database.conn is not None:
            extra_database.conn.close()
        
        super().closeEvent(event)

    ####################
    
    # 初始化 类型一，从 MAME 导出 数据
    def new_func_load_data_from_emulator(self,):
        print()
        print( "export data from emulator")
        self.setWindowTitle(the_variables.software_name + " - 从模拟器导出xml")

        mame_path = self.new_settings.value("mame/path") 
        mame_working_directory = self.new_settings.value("mame/working_directory") 
        mame_path, mame_working_directory = misc_funcs.get_abspath_for_mame_and_working_directory(mame_path, mame_working_directory)
        
        if shutil.which(mame_path) is None:
            QMessageBox.warning(self.parentWidget(), "出错", "程序不可以执行：" + mame_path)
            self.new_settings.setValue("mame/path", "")
            self.new_settings.setValue("mame/working_directory", "")
            self.new_settings.sync()
            sys.exit()

        process = QProcess(self)
        if mame_working_directory:
            if os.path.isdir(mame_working_directory):
               process.setWorkingDirectory(mame_working_directory)
        self.new_buffer_to_hold_mame_data = io.BytesIO()
        process.setProcessChannelMode(QProcess.ForwardedErrorChannel)
        process.readyReadStandardOutput.connect(lambda: self.new_buffer_to_hold_mame_data.write(process.readAllStandardOutput().data()))
        #process.readyReadStandardError.connect(lambda: process.readAllStandardError())
        process.finished.connect(lambda: self.new_func_data_from_emulator_is_ready())
        process.start(mame_path, the_variables.command_line_options_for_emulator_to_export_data)
    # 初始化，解析 MAME xml
    @Slot()
    def new_func_data_from_emulator_is_ready(self,):
        print()
        print("data from emulator is ready")
        number = self.new_buffer_to_hold_mame_data.tell()
        if number == 0:
            QMessageBox.warning(self.parentWidget(), "出错", "导出数据为空")
            self.new_settings.setValue("mame/path", "")
            self.new_settings.setValue("mame/working_directory", "")
            self.new_settings.sync()
            sys.exit()
        self.new_func_parse_xml()

    def new_func_parse_xml(self,):
        print()
        print("parse xml")
        self.setWindowTitle(the_variables.software_name + " - 解析xml")
        self.new_thread_for_parse_xml = QThread(self)
        self.new_worker_for_parse_xml = Worker_parse_xml(self.new_buffer_to_hold_mame_data)

        self.new_worker_for_parse_xml.moveToThread(self.new_thread_for_parse_xml)

        self.new_thread_for_parse_xml.started.connect(self.new_worker_for_parse_xml.new_func_do_work)

        self.new_worker_for_parse_xml.new_signal_for_save_file_failed.connect(self.new_func_save_gamelist_data_failed)
        self.new_worker_for_parse_xml.new_signal_finished.connect(self.new_func_on_xml_parse_finished)

        self.new_thread_for_parse_xml.finished.connect(self.new_worker_for_parse_xml.deleteLater)

        self.new_thread_for_parse_xml.start()
    #
    @Slot()
    def new_func_save_gamelist_data_failed(self):
        QMessageBox.warning(self.parentWidget(), "出错", "数据文件保存失败：" + the_files.data_file)
    #
    @Slot(bytes)
    def new_func_on_xml_parse_finished(self,result):
        """XML解析完成"""
        print()
        print("xml parse finish ###########")

        self.new_thread_for_parse_xml.quit()
        self.new_thread_for_parse_xml.wait()

        if result:
            result = pickle.loads(result)


        if not result:
            QMessageBox.warning(self, "出错", "xml 解析失败")
            self.new_settings.setValue("mame/path", "")
            self.new_settings.setValue("mame/working_directory", "")
            self.new_settings.sync()
            sys.exit()

        
        self.new_buffer_to_hold_mame_data.close()
        
        print(type(result))
        print(result.keys())
        
        self.new_func_update_model_data(result)
    
    # 初始化 类型二，从 临时文件 读取 数据
    def new_func_load_gamelist_data_from_file(self):
        filename = the_files.data_file
        data = None

        if os.path.isfile(filename):
            try:
                file = open(filename, 'rb')
                data = pickle.load( file )
                file.close()
            except:
                print( "read pickle failed")
                print( filename )
                QMessageBox.critical(self, "错误", "pickle文件读取失败。\n文件可能损坏;\n或者用户无权限读取该文件：\n" + filename)
                sys.exit()
        
        self.new_func_update_model_data(data)

    #################################
    #################################
    #################################
    #################################
    def new_func_update_model_data(self,data):
        print()
        print( "update model data" )
        self.setWindowTitle(the_variables.software_name + " - 更新模型数据")

        # 更新模型数据
        ##'columns', 'dict_data', 'internal_index', 'machine_dict', 'mame_version', 'set_data'
        #
        ## clounms = []
        print(data["columns"])
        ui_models.set_value("columns",data["columns"])
        #
        ## dict_data
        ##    clone_to_parent parent_to_clone
        # clone_to_parent = dict()
        # parent_to_clone = dict()
        ui_models.set_value("clone_to_parent",data["dict_data"]["clone_to_parent"])
        ui_models.set_value("parent_to_clone",data["dict_data"]["parent_to_clone"])
        print(data["dict_data"].keys())
        #
        ## internal_index = dict()
        ui_models.set_value("internal_index",data["internal_index"])
        #
        #machine_dict = dict()
        ui_models.set_value("machine_dict",data["machine_dict"])
        #
        ## mame_version = ""
        ui_models.set_value("mame_version",data["mame_version"])
        #
        ## set data
        ##   all_set parent_set clone_set
        ## all_set = dict()
        ## parent_set = dict()
        ## clone_set = dict()
        ui_models.set_value("all_set",   data["set_data"]["all_set"])
        ui_models.set_value("parent_set",data["set_data"]["parent_set"])
        ui_models.set_value("clone_set", data["set_data"]["clone_set"])
        print(data["set_data"].keys())
        #        
        # 原始图标
        ui_models.load_and_resize_internal_icon()
        #
        ui_models.update_some_value()


        # 菜单
        #  显示、隐藏 内置目录 （内置目录在更新数据后，才有）
        # 取值
        try:hidden_index = self.new_settings.value("index/hidden_index_set")
        except:hidden_index = ""
        if type(hidden_index) != str: hidden_index = ""
        hidden_index_set = {x for x in hidden_index.split(";")}
        hidden_index_set = hidden_index_set & (ui_models.internal_index.keys() | ui_models.internal_index_2.keys())
        if hidden_index_set:
            ui_models.hidden_index_set = hidden_index_set
            print("ui_models.hidden_index_set",ui_models.hidden_index_set)
        # internal_index_list
        internal_index_list = list( ui_models.internal_index.keys() | ui_models.internal_index_2.keys() )
        # 排序
        temp_list = []
        used_index_set=set()
        for index_id in the_variables.index_order:
            if index_id in internal_index_list:
                if index_id not in used_index_set:
                    temp_list.append(index_id)
                    used_index_set.add(index_id)
        for index_id in sorted( set(internal_index_list) - used_index_set):
            temp_list.append(index_id)
        internal_index_list = temp_list
        del temp_list
        del used_index_set
        # 新建菜单
        for index_id in internal_index_list:
            the_text = index_id
            if index_id in the_variables.index_translation:
                the_text = the_variables.index_translation[index_id]
            action = QAction(the_text,self)
            self.new_menu_show_or_hide_internal_index.addAction(action)
            action.setCheckable(True)
            if index_id in ui_models.hidden_index_set:
                action.setChecked(False)
            else:
                action.setChecked(True)
            action.triggered.connect(lambda checked,internal_index_id=index_id : self.new_func_for_show_or_hide_index(checked,internal_index_id))



        self.setWindowTitle(the_variables.software_name + " - 更新模型数据2")

        # translation_file_path
        try:translation_file_path = self.new_settings.value("mame/translation_file")
        except:translation_file_path = ""
        if type(translation_file_path) != str:
            translation_file_path = ""

        # gamelist_filter
        try:gamelist_filter = self.new_settings.value("gamelist/filter")
        except:gamelist_filter = ""
        if type(gamelist_filter) != str: 
            gamelist_filter = ""

        # folders_path
        try:folders_path = self.new_settings.value("extra/folders")
        except:folders_path = ""
        if type(folders_path) != str: 
            folders_path = ""

        # top_index_list_string
        try:top_index_list_string = self.new_settings.value("index/top_index_list")
        except:top_index_list_string = ""
        if type(top_index_list_string) != str: 
            top_index_list_string = ""

        # icon_zip_path
        try:icon_zip_path = self.new_settings.value("extra/icons")
        except:icon_zip_path = ""
        if type(icon_zip_path) != str: 
            icon_zip_path = ""

        self.new_thread_for_update_model_data = QThread(self)
        self.new_worker_after_parse_xml = Worker_after_parse_xml({
                "translation_file_path":translation_file_path,
                "gamelist_filter":gamelist_filter,
                "folders_path":folders_path,
                "top_index_list_string":top_index_list_string,
                "icon_zip_path":icon_zip_path,
                },
                )
        self.new_worker_after_parse_xml.moveToThread(self.new_thread_for_update_model_data)

        self.new_thread_for_update_model_data.started.connect(self.new_worker_after_parse_xml.new_func_do_work)

        self.new_worker_after_parse_xml.new_signal_for_finished.connect(self.new_func_update_model_data_after)

        self.new_thread_for_update_model_data.finished.connect(self.new_worker_after_parse_xml.deleteLater)

        self.new_thread_for_update_model_data.start()

    # 启动时，初始化，最后一步，到这里
    def new_func_update_model_data_after(self):
        print()
        print( "update model data after" )
        self.setWindowTitle(the_variables.software_name + " - 更新模型数据完成")

        self.new_thread_for_update_model_data.quit()
        self.new_thread_for_update_model_data.wait()

        
        # 目录列表，刷新
        self.new_ui_index.model().beginResetModel()
        self.new_ui_index.model().endResetModel()

        self.new_ui_statusbar_for_total_number.setText( str(len(ui_models.all_set)) )

        # 更新标题
        if ui_models.mame_version:
            temp = str( ui_models.mame_version )
            temp = temp.strip()
            self.setWindowTitle(the_variables.software_name + "  -  " + temp)
        
        #初始化之后，读取的设置
        self.centralWidget().new_func_for_load_settings() # 游戏列表状态恢复
        self.new_func_set_row_height_for_tableview(at_start=True) # tableview 行高
        self.new_func_set_internal_qss() # treeview 行高，以及字体等，在 qss 中设置
        self.new_func_for_set_listview_spacing() # 图标列表，单元格间距

        # last game ，这个得移动到启动最后，不然周边会使用 game_id 加载内容
        try:last_game = self.new_settings.value("game_remember",type=str)
        except:last_game = ""
        if last_game:
            the_variables.current_id = last_game

        self.new_func_index_select_remember_after_load_settings()
    
        self.new_func_progressbar_hide()

        #print("for test,quit")
        #sys.exit()
        #QTimer.singleShot(3000, self.close)

    #################################
    #################################
    #################################
    #################################

    def new_func_do_nothing(self,):
        print( "do nothing")

    def new_func_save_settings(self,):
        print( "save settings")
        
        self.new_settings.setValue("mainwindow/state",self.saveState())
        self.new_settings.setValue("mainwindow/geometry",self.saveGeometry())

        self.new_settings.setValue("gamelist/sort_column",the_variables.sort_column) # int
        self.new_settings.setValue("gamelist/sort_reverse",the_variables.sort_reverse)
        self.new_settings.setValue("gamelist/sort_use_locale",the_variables.sort_use_locale)# bool
        
        
        # style ,在设置 style 的地方保存
        
        # qss ，在设置的地方保存

        # 记录 目录
        self.new_settings.setValue("index/index_id_1",the_variables.index_id_1)
        self.new_settings.setValue("index/index_id_2",the_variables.index_id_2)

        # 记录游戏
        if the_variables.current_id is not None:
            self.new_settings.setValue("game_remember",the_variables.current_id)
        # 是否自动选择游戏
        self.new_settings.setValue("auto_select_last_game",the_variables.auto_select_last_game)
        # 标记未拥有游戏
        self.new_settings.setValue("use_icon_not_have",the_variables.use_icon_not_have)

        # 目录列表置顶项 index/top_index_list
        self.new_settings.setValue("index/top_index_list",";".join(ui_models.top_index_list))

        self.centralWidget().new_func_for_save_settings()

    def new_func_load_settings_at_start(self,):
        print( )
        print( "load settings")
        
        # 刚开始，初始化之前，还没有设置时，没有数据
        
        try: 
            self.restoreGeometry(self.new_settings.value("mainwindow/geometry"))
            print("restoreGeometry")
        except: pass
        
        try:
            self.restoreState(self.new_settings.value("mainwindow/state"))
            print("restoreState")
        except:pass

        # style
        try : style_name = self.new_settings.value("mainwindow/style")
        except : style_name = "Fusion"
        if not style_name:
            style_name = "Fusion"
        if style_name:
            self.new_func_set_style(style_name)
        
        # qss
        try : qss_file = self.new_settings.value("mainwindow/qss")
        except : qss_file = ""
        if qss_file:
            self.new_func_load_qss_file_at_start(qss_file)
        
        # 排序
        try:    the_variables.sort_column = self.new_settings.value("gamelist/sort_column",type=int)
        except: the_variables.sort_column = -1
        try:    the_variables.sort_reverse = self.new_settings.value("gamelist/sort_reverse",type=bool)
        except: the_variables.sort_reverse = False
        try:    the_variables.sort_use_locale = self.new_settings.value("gamelist/sort_use_locale",type=bool)
        except: the_variables.sort_use_locale = False

        # gamelist_faketree ,展开、收起 字符串
        for key in ["string_for_open",    "string_for_close",   "string_for_empty",   ]:
            try: 
                value = self.new_settings.value(f"gamelist_faketree/{key}",type=str)
            except: 
                value = ""

            value = value.strip()
            value = value.strip('"')
            if value:
                setattr(ui_models,key,value)

    # menu qss
    def new_func_load_qss_file_by_menu(self,sender): # sender = self.sender() # pyside2 中没用？
        # qss 文件，位于 the_files.folder_qss 中
        
        print()
        print("slot app.setStyleSheet")
        
        qss_file = sender.text()
        if not qss_file : return
        
        print(qss_file)
        
        # qss 文件
        file_path = os.path.join( the_files.folder_qss , qss_file )
        
        if not os.path.isfile(file_path):return
        
        app = QCoreApplication.instance()
        if os.path.isfile(file_path):
            try:
                the_qss_content = ""
                
                with open(file_path,mode="rt",encoding="utf_8",errors="ignore") as f:
                    the_qss_content = f.read()
                
                # 设置
                if the_qss_content : app.setStyleSheet(the_qss_content)
                
                # 保存
                self.new_settings.setValue("mainwindow/qss",qss_file)
                
            except:
                pass
    
    def new_func_load_qss_file_at_start(self,qss_file=""):
        # qss 文件，位于 the_files.folder_qss 中
        
        print()
        print("load qss file")
        
        if type(qss_file) != str : return
        if not qss_file : return
        
        print(qss_file)
        
        # qss 文件
        file_path = os.path.join( the_files.folder_qss , qss_file )
        
        if not os.path.isfile(file_path):return
        
        app = QCoreApplication.instance()
        if os.path.isfile(file_path):
            try:
                # 保存
                self.new_settings.setValue("mainwindow/qss",qss_file)

                the_qss_content = ""
                with open(file_path,mode="rt",encoding="utf_8_sig",errors="ignore") as f:
                    the_qss_content = f.read()
                
                # UI 菜单，选中 ，标记
                # UI 初始化时用到
                action_list = self.new_action_group_for_qss.actions()
                for action in action_list:
                    if os.path.normcase(action.text()) == os.path.normcase(qss_file):
                        action.setChecked(True)
                        break
                
                # 设置
                if the_qss_content : 
                    app.setStyleSheet(the_qss_content)
            except:
                pass
    
    def new_func_clear_qss(self):
        app = QCoreApplication.instance()
        app.setStyleSheet("")
        
        action_list = self.new_action_group_for_qss.actions()
        for action in action_list:
            action.setChecked(False)
        
        # 保存 设置
        self.new_settings.setValue("mainwindow/qss","")
    
    def new_func_set_style(self,style_name=""):
        print("")
        print("app.setStyle")
        
        if type(style_name) != str : return
        
        if not style_name : return
        
        print(style_name)
        
        ########
        
        style_list = QStyleFactory.keys()
        
        if style_name.lower() in list( map( str.lower , style_list ) ):
            
            app = QCoreApplication.instance()
            
            # 设置
            app.setStyle(style_name)
            
            # 保存
            self.new_settings.setValue("mainwindow/style",style_name)
            
            # UI 初始化时,对应菜单 的 选中标记 ，设置 被选中 状态
            action_list = self.new_action_group_for_style.actions()
            for action in action_list:
                if action.text().lower() == style_name.lower():
                    action.setChecked(True)
                    break        

    # menu style
    def new_func_set_style_by_menu(self,sender): # sender = self.sender() # pyside2 中没用？
        print("")
        print("set style by menu")
        
        style_name = sender.text()
        
        if not style_name : return
        
        print(style_name)
        
        ########
        
        style_list = QStyleFactory.keys()

        if style_name.lower() in list( map( str.lower , style_list ) ):
            app = QCoreApplication.instance()
            # 设置
            app.setStyle(style_name)
            # 保存
            self.new_settings.setValue("mainwindow/style",style_name)
    
    def new_func_show_dialog_for_choose_emulator_path_and_working_dir(self,):
        print("show dialog for choose emulator path and working dir")

        if self.new_dialog_for_choose_emulator_path_and_working_dir is None:
            self.new_dialog_for_choose_emulator_path_and_working_dir = ui_small_windows.Dialog_to_choose_emulator_path(self.new_settings,self)
        
        self.new_dialog_for_choose_emulator_path_and_working_dir.new_func_set_values()
        
        self.new_dialog_for_choose_emulator_path_and_working_dir.exec()

    def new_func_check_mame_path(self):
        is_ok = False
        settings = self.new_settings
        mame_path = settings.value("mame/path") 

        if mame_path:
            # 检查 mame_path 是否是 可执行程序
            if os.access(os.path.abspath(mame_path),os.X_OK):
                is_ok = True
            
            # 检查 mame_path 是否是 命令行中已有程序
            # 也可能是当前目录下文件名的缩写 比如 mame.exe 缩写为 mame ；这样虽然找不到路径，但可以执行
            if os.path.split(mame_path)[0] == "": # 不含分隔路径符号
                if shutil.which(mame_path) is not None:
                    is_ok = True

        return is_ok

    #######
    def new_func_show_progress_bar_on_statusbar_for_test(self):
        print("show progress bar on statusbar")

        self.setEnabled(False)
        
        self.new_progressbar_on_statusbar.setVisible(True)
        
        worker=Worker_Test()
        threadpool = QThreadPool.globalInstance()
        threadpool.start(worker)
        worker.new_signals.new_finished.connect(self.new_func_progressbar_hide)
    
    @Slot()
    def new_func_show_progress_bar(self):
        print("show progress bar on statusbar")

        self.new_progressbar_on_statusbar.setVisible(True)

        self.setEnabled(False)

    @Slot()
    def new_func_progressbar_hide(self):
        print("progressbar hide")

        self.new_progressbar_on_statusbar.setVisible(False)
        self.setEnabled(True)

    @Slot(str,str)
    def new_func_slot_for_receive_index(self,id_1,id_2):
        central_widget = self.centralWidget()
        central_widget.new_func_show_by_index(id_1,id_2)

    
    @Slot(str,bool,bool,tuple)
    def new_func_for_search(self,search_string,use_re=False,ignore_case=True,search_columns=tuple(),):
        central_widget = self.centralWidget()
        central_widget.new_func_for_search(search_string,use_re=use_re,ignore_case=ignore_case,search_columns=search_columns)
    
    def new_func_index_select_remember_after_load_settings(self,):
        print()
        print("index select the remembered one")
        #
        index_id_1 = ""
        index_id_2 = ""
        try:
            index_id_1 = self.new_settings.value("index/index_id_1")
            index_id_2 = self.new_settings.value("index/index_id_2")
        except: 
            pass
        if index_id_1:
            self.new_ui_index.new_func_select_row_by_index_id(index_id_1,index_id_2,scroll_to=True) 
            #self.new_func_slot_for_receive_index(index_id_1,index_id_2)

    @Slot(str)
    def new_func_slot_for_receive_id_change(self,game_id):
        
        if not game_id:
            return
        
        the_string = ui_models.get_string_for_statusbar(game_id)

        if the_string:
            self.statusBar().showMessage(the_string)

    @Slot(int)
    def new_func_slot_for_receive_gamelist_number_change(self,number):
        self.new_ui_statusbar_for_current_number.setText( str(number)+"/" )

    # menu 加载周边文本到数据库
    @Slot()
    def new_func_load_extra_text_to_database(self,):
        self.new_func_show_progress_bar()

        extra_database.delete_table()

        # 多线程时候
        # 数据库 需要先关闭吗 ？
        #
        for dock_window in self.new_list_for_dock_window_use_database:
            try:
                dock_window.new_cursor.close()
                dock_window.new_cursor = None
            except:
                dock_window.new_cursor = None
        #
        if extra_database.conn is not None:
            try:
                extra_database.conn.close()
                extra_database.conn = None
            except:
                pass
        #
        if os.path.isfile(the_files.extra_database_file):
            try:
                os.remove(the_files.extra_database_file)
            except:
                pass

        settings = self.new_settings

        try:history_xml_path = settings.value("extra/history")
        except:history_xml_path=""
        if type(history_xml_path) != str:
            history_xml_path=""

        try:history_dat_path = settings.value("extra/history_dat")
        except:history_dat_path=""
        if type(history_dat_path) != str:
            history_dat_path=""

        try:gameinit_path = settings.value("extra/gameinit")
        except:gameinit_path=""
        if type(gameinit_path) != str:
            gameinit_path=""

        try:mameinfo_path = settings.value("extra/mameinfo")
        except:mameinfo_path=""
        if type(mameinfo_path) != str:
            mameinfo_path=""

        try:messinfo_path = settings.value("extra/messinfo")
        except:messinfo_path=""
        if type(messinfo_path) != str:
            messinfo_path=""

        try:command_path = settings.value("extra/command")
        except:command_path=""
        if type(command_path) != str:
            command_path=""

        try:command_english_path = settings.value("extra/command_english")
        except:command_english_path=""
        if type(command_english_path) != str:
            command_english_path=""
        
        # QThread
        self.new_thread_for_load_data_to_database = QThread(self)
        self.new_worker_for_load_data_to_database = Worker_load_extra_text_to_database({
            "history_xml_path":history_xml_path,
            "history_dat_path":history_dat_path,
            "gameinit_path":gameinit_path,
            "mameinfo_path":mameinfo_path,
            "messinfo_path":messinfo_path,
            "command_path":command_path,
            "command_english_path":command_english_path,
            },
            )
        self.new_worker_for_load_data_to_database.moveToThread(self.new_thread_for_load_data_to_database)

        self.new_thread_for_load_data_to_database.started.connect(self.new_worker_for_load_data_to_database.new_func_do_work)

        self.new_worker_for_load_data_to_database.new_signal_for_finished.connect(self.new_func_progressbar_hide)
        self.new_worker_for_load_data_to_database.new_signal_for_finished.connect(self.new_thread_for_load_data_to_database.quit)

        self.new_thread_for_load_data_to_database.finished.connect(self.new_worker_for_load_data_to_database.deleteLater)
        self.new_thread_for_load_data_to_database.finished.connect(self.new_thread_for_load_data_to_database.deleteLater)
        
        self.new_thread_for_load_data_to_database.start()
    # menu 删除模拟器路径
    @Slot()
    def new_func_delete_emulator(self,):
        print("delete emulator")

        ask_string = "\n".join([
                "1.删除模拟器路径设置",
                "",
                "2.删除游戏列表临时文件：",
                f"{the_files.data_file} ",
                "",
                "删除后，程序将关闭。",
                "删除后，下次打开程序，需要重新初始化。",
                "",
                "是否继续？",
            ])

        # 显示一个询问对话框，包含 "Yes" 和 "No" 两个按钮[reference:4][reference:5]
        reply = QMessageBox.question(
            self,                      # 父窗口
            "删除模拟器路径",                # 对话框标题
            ask_string,   # 显示的问题
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No  # 按钮组合
        )

        # 根据用户的选择执行相应操作[reference:6][reference:7]
        if reply == QMessageBox.StandardButton.Yes:
            print("用户点击了“是”")
            # 在这里添加确认后的逻辑

            def delete_file(file_path):
                if os.path.isfile(file_path):
                    try:
                        os.remove(file_path)
                        return True
                    except:
                        pass
            # 删除文件
            if os.path.isfile(the_files.data_file):
                if not delete_file(the_files.data_file):
                    time.sleep(1) # 如果失败，1秒后重试一次
                    if not delete_file(the_files.data_file):
                        QMessageBox.warning(self, "删除失败", f"文件删除文件失败 {the_files.data_file} ，或可手动删除")
                        return

            self.new_settings.setValue("mame/path","")
            self.new_settings.setValue("mame/working_directory","")
            
            self.close()

        else:
            print("用户点击了“否”或关闭了对话框")
            # 在这里添加取消后的逻辑        
    # menu 周边路径设置
    @Slot()
    def new_func_set_extra_path(self,):
        print("set extra path")

        try:
            self.new_dialog_for_set_extra_path
        except:
            self.new_dialog_for_set_extra_path = ui_small_windows.Dialog_to_set_extra_path(self.new_settings , self)

        self.new_dialog_for_set_extra_path.new_func_set_values()

        if self.new_dialog_for_set_extra_path.exec() :
            print("用户点击了“确认”")
        else:
            print("用户点击了“取消”或关闭了对话框")
    # menu 翻译文件设置
    @Slot()
    def new_func_set_gamelist_translation_file(self,):
        print("set translation file")

        try:
            self.new_dialog_for_set_translation_file
        except:
            self.new_dialog_for_set_translation_file = ui_small_windows.Dialog_for_translation_file_path(self.new_settings , self)

        self.new_dialog_for_set_translation_file.new_func_set_values()

        if self.new_dialog_for_set_translation_file.exec() :
            print("用户点击了“确认”")
        else:
            print("用户点击了“取消”或关闭了对话框")
    # menu 字体等 gamelist 设置图标大小
    @Slot()
    def new_func_for_set_icon_size(self):
        print("设置图标大小")
        try:
            self.new_dialog_for_set_gamelist_icon_size
        except:
            self.new_dialog_for_set_gamelist_icon_size = ui_small_windows.Dialog_for_set_gamelist_icon_size(self.new_settings,self,)
        self.new_dialog_for_set_gamelist_icon_size.new_func_set_values()
        self.new_dialog_for_set_gamelist_icon_size.exec()
    def new_func_for_set_listview_spacing(self):
        central_widget = self.centralWidget()

        # setSpacing
        # Setting this property when the view is visible will cause the items to be laid out again.
        central_widget.new_ui_gamelist_icon_table.setSpacing(the_variables.spacing_for_icon_table)
        central_widget.new_ui_gamelist_image_table.setSpacing(the_variables.sapcing_for_image_table)

    # menu 显示 python 版本
    @Slot()
    def new_func_show_python_version(self,):
        print("show python version")

        try:
            self.new_dialog_for_show_python_version
        except:
            self.new_dialog_for_show_python_version = ui_small_windows.Dialog_for_show_python_version( self)

        self.new_dialog_for_show_python_version.exec()
    # menu gamelist 标记未拥有游戏
    @Slot(bool)
    def new_func_gamelist_mark_not_have(self,checked):
        if checked:
            the_variables.use_icon_not_have = True
        else:
            the_variables.use_icon_not_have = False
        self.centralWidget().new_func_refresh_layoutchange()
    # menu gamelist 排序使用本地化
    @Slot(bool)
    def new_func_gamelist_sort_use_locale(self,checked):
        if checked:
            the_variables.sort_use_locale = True
        else:
            the_variables.sort_use_locale = False
    # menu gamelist 切换列表时，自动选择上一个游戏
    @Slot(bool)
    def new_func_gamelist_auto_select_last_game(self,checked):
        if checked:
            the_variables.auto_select_last_game = True
        else:
            the_variables.auto_select_last_game = False
    # menu 字体等 gamelist 设置行高
    @Slot()
    def new_func_for_set_row_height(self):
        print("设置行高")
        try:
            self.new_dialog_for_set_gamelist_row_height
        except:
            self.new_dialog_for_set_gamelist_row_height = ui_small_windows.Dialog_for_set_gamelist_row_height(self.new_settings,self,)
        self.new_dialog_for_set_gamelist_row_height.new_func_set_values()
        if self.new_dialog_for_set_gamelist_row_height.exec():
            print("用户点击了“确认”")
            self.centralWidget().new_func_refresh_layoutchange()
    # menu 字体 设置字体
    @Slot()
    def new_func_for_set_font(self):
        print("设置字体")
        try:
            self.new_dialog_for_set_font
        except:
            self.new_dialog_for_set_font = ui_small_windows.Dialog_for_set_font(self.new_settings,self,)
        self.new_dialog_for_set_font.new_func_set_values()
        if self.new_dialog_for_set_font.exec() :
            self.centralWidget().new_func_refresh_layoutchange()
    # menu 字体等 游戏列表 选中行颜色
    def new_func_for_set_highlight_row_colour(self):
        print("设置选中行颜色")
        try:
            self.new_dialog_for_set_gamelist_highlight_row_colour
        except:
            self.new_dialog_for_set_gamelist_highlight_row_colour = ui_small_windows.Dialog_for_set_gamelist_highlight_row_colour(self.new_settings,self,)
        self.new_dialog_for_set_gamelist_highlight_row_colour.new_func_set_values()
        if self.new_dialog_for_set_gamelist_highlight_row_colour.exec():
            print("用户点击了“确认”")
            #self.centralWidget().new_func_refresh_layoutchange()
    # menu gamelist 设置全局过滤
    @Slot()
    def new_func_for_set_gamelist_filter(self):
        print("设置游戏列表的全局过滤")
        try:
            self.new_dialog_for_set_gamelist_filter
        except:
            self.new_dialog_for_set_gamelist_filter = ui_small_windows.Dialog_to_set_gamelist_filter(self.new_settings,self,)
        self.new_dialog_for_set_gamelist_filter.new_func_set_values()
        if self.new_dialog_for_set_gamelist_filter.exec():
            print("用户点击了“确认”")
            self.centralWidget().new_func_reload_gamelist()
    # menu index 编辑目录
    @Slot(bool)
    def new_func_set_index_edit_mode(self,checked):
        ui_models.index_edit_mode = checked
        self.new_settings.setValue("index/edit_mode",checked)
        self.centralWidget().new_func_refresh_layoutchange()
    # menu index 保存目录
    @Slot()
    def new_func_save_index(self):
        print("保存自定义目录")

        finished_list = []
        failed_list = []
        for index_file in sorted( ui_models.index_files_be_edited ):
            data = ui_models.external_index[index_file]
            try:
                extra_folders.folders_save(index_file,data)
                print("save file : ",index_file)
                finished_list.append(index_file)
            except:
                failed_list.append(index_file)

        ui_models.index_files_be_edited = ui_models.index_files_be_edited - set(finished_list)

        if failed_list:
            QMessageBox.warning(self,"文件保存失败","\n".join(failed_list))
    # menu ,index 显示、隐藏 内置目录
    def new_func_for_show_or_hide_index(self,checked,internal_index_id):
        print("checked",checked,"internal_index_id",internal_index_id)
        
        if checked:
            # 显示
            ui_models.hidden_index_set.discard(internal_index_id)
        else:
            ui_models.hidden_index_set.add(internal_index_id)

        value = ";".join(ui_models.hidden_index_set)
        self.new_settings.setValue("index/hidden_index_set",value)

        self.new_ui_index.model().new_func_refresh_index()



    # menu gamelist 多选模式（勾选）
    @Slot(bool)
    def new_func_gamelist_multi_selection_mode(self,checked):
        ui_models.multi_selection_mode = checked
        self.new_settings.setValue("gamelist/multi_selection_mode",checked)
        self.centralWidget().new_func_refresh_layoutchange()
        #print(ui_models.multi_selection_mode)
    # menu gamelist 列表编辑模式 仅翻译列
    @Slot(bool)
    def new_func_gamelist_list_edit_mode(self,checked):
        ui_models.gamelist_editable_mode = checked
        self.new_settings.setValue("gamelist/gamelist_editable_mode",checked)
        self.centralWidget().new_func_refresh_layoutchange()
    # menu gamelist 保存游戏列表
    @Slot()
    def new_func_save_gamelist(self):
        print("保存游戏列表")
        try:
            self.new_dialog_for_save_translation_file
        except:
            self.new_dialog_for_save_translation_file = ui_small_windows.Dialog_for_save_translation_file(self.new_settings,self,)
        self.new_dialog_for_save_translation_file.new_func_set_values()
        self.new_dialog_for_save_translation_file.exec()
    # menu gamelist 使用额外 icon 资源包
    @Slot(bool)
    def new_func_gamelist_use_icon_extra_resource(self,checked):
        the_variables.use_icon_extra_resource = checked
        self.new_settings.setValue("gamelist/use_icon_extra_resource",checked)
        self.centralWidget().new_func_refresh_layoutchange()

    # menu gamelist  扫描游戏文件，极简版，只扫描 .zip/.7z/文件夹 是否存在
    def new_func_scan_game_files_only_check_if_file_exists(self,merged=False):
        # 从 MAME 查询 rompath 路径信息

        self.new_func_show_progress_bar()

        # 
        self.new_variables_for_scan_roms = {}
        self.new_variables_for_scan_roms["merged"] = merged  ###

        mame_path = self.new_settings.value("mame/path") 
        mame_working_directory = self.new_settings.value("mame/working_directory") 
        mame_path, mame_working_directory = misc_funcs.get_abspath_for_mame_and_working_directory(mame_path, mame_working_directory)
        command_list = ["-showconfig"]

        self.new_variables_for_scan_roms["mame_working_directory"] = mame_working_directory  ###

        print(mame_path)
        print(mame_working_directory)
        print(command_list)

        self.new_process_for_mamepath = QProcess(self)
        if mame_working_directory:
            if os.path.isdir(mame_working_directory):
               self.new_process_for_mamepath.setWorkingDirectory(mame_working_directory)
        
        self.new_buffer_to_hold_mame_path_info = io.BytesIO()

        self.new_process_for_mamepath.setProcessChannelMode(QProcess.ForwardedErrorChannel)

        self.new_process_for_mamepath.readyReadStandardOutput.connect(lambda: self.new_buffer_to_hold_mame_path_info.write(self.new_process_for_mamepath.readAllStandardOutput().data()))
        #self.new_process_for_mamepath.readyReadStandardError.connect(lambda: self.new_process_for_mamepath.readAllStandardError())
        self.new_process_for_mamepath.finished.connect(self.new_func_scan_game_files_only_check_if_file_exists_step_2)
        self.new_process_for_mamepath.start(mame_path, command_list)
    #
    def new_func_scan_game_files_only_check_if_file_exists_step_2(self,):

        merged=self.new_variables_for_scan_roms["merged"]
        mame_working_directory = self.new_variables_for_scan_roms["mame_working_directory"]
        
        self.new_buffer_to_hold_mame_path_info.seek(0)
        
        #rompath                   "roms;"
        str_1 = r"^rompath\s+(\S.*?)\s*$"
        p=re.compile(str_1, )
        rompath=""
        for line in self.new_buffer_to_hold_mame_path_info:
            line = line.decode("utf_8_sig",errors='backslashreplace')
            m = p.search(line)
            if m :
                rompath = m.group(1)
                break
        print("rompath :")
        print(rompath)

        self.new_thread_for_scan_roms = QThread(self)

        self.new_worker_for_scan_roms = Worker_for_scan_game_files()
        self.new_worker_for_scan_roms.new_func_set_values(mame_working_directory, rompath,  merged)

        self.new_worker_for_scan_roms.moveToThread(self.new_thread_for_scan_roms)

        self.new_thread_for_scan_roms.started.connect(self.new_worker_for_scan_roms.new_func_do_work)

        self.new_worker_for_scan_roms.new_signal_for_failed.connect(self.new_func_scan_game_files_error)

        self.new_worker_for_scan_roms.new_signal_for_finished.connect(self.new_func_scan_game_files_only_check_if_file_exists_step_3)
        self.new_worker_for_scan_roms.new_signal_for_finished.connect(self.new_thread_for_scan_roms.quit)

        self.new_thread_for_scan_roms.finished.connect(self.new_worker_for_scan_roms.deleteLater)
        self.new_thread_for_scan_roms.finished.connect(self.new_thread_for_scan_roms.deleteLater)

        self.new_thread_for_scan_roms.start()
    #
    @Slot()
    def new_func_scan_game_files_error(self):
        QMessageBox.critical(self, "Error", "游戏 roms 扫描过程 貌似出错")
    #
    @Slot(set)
    def new_func_scan_game_files_only_check_if_file_exists_step_3(self,data):

        # 更新数据
        ui_models.available_set = data

        # 保存到文件
        filename = the_files.available_file
        try:
            file = open( filename , 'wb' )
            pickle.dump( data , file )
            file.close()
        except:
            QMessageBox.critical(self, "Error", "拥有列表保存失败，检查此文件是否有写入权限:"+"\n"+filename)

        # 跳转到拥有列表，刷新数据
        #the_variables.index_id_1
        #the_variables.index_id_2
        if the_variables.index_id_1 == "available_set":
            self.new_func_slot_for_receive_index(the_variables.index_id_1, the_variables.index_id_2)

        self.new_func_progressbar_hide()

    # 游戏列表数量变化
    @Slot(int)
    def on_modelForTableView_singalGamelistNumberChanged(self,game_list_number):
        self.new_func_gamelist_number_changed(game_list_number)
    @Slot(int)
    def on_modelForTableView2_singalGamelistNumberChanged(self,game_list_number):
        self.new_func_gamelist_number_changed(game_list_number)
    @Slot(int)
    def on_modelForTreeView_singalGamelistNumberChanged(self,game_list_number):
        self.new_func_gamelist_number_changed(game_list_number)
    @Slot(int)
    def on_modelForTableView2LevelTreeLike_singalGamelistNumberChanged(self,game_list_number):
        self.new_func_gamelist_number_changed(game_list_number)
    @Slot(int)
    def on_modelForIcon_singalGamelistNumberChanged(self,game_list_number):
        self.new_func_gamelist_number_changed(game_list_number)
    @Slot(int)
    def on_modelForImage_singalGamelistNumberChanged(self,game_list_number):
        self.new_func_gamelist_number_changed(game_list_number)        
    #
    @Slot(int)
    def new_func_gamelist_number_changed(self,game_list_number):
        self.new_ui_statusbar_for_current_number.setText(f"{game_list_number}/")

    def new_func_set_internal_qss(self):
        print("set internal qss")

        qss_string = []

        # QTreeview 行高
        try:row_height = self.new_settings.value("gamelist/row_height_for_treeview",type=int)
        except:row_height = 0
        if type(row_height) is int:
            if row_height == 0:
                row_height_qss = ""
                qss_string.append(row_height_qss)
            elif row_height > 0:
                row_height_qss = f"QTreeView::Item{{ height:{row_height}px; }}"
                qss_string.append(row_height_qss)

        # 字体
        the_keys = ["all","gamelist",                      "extra",     "extra_command",             "extra_command_english",             "QHeaderView",]
        the_prefix=["*",  "QTreeView,QTableView,QListView","QTextEdit", "QTextEdit#textedit_command","QTextEdit#textedit_command_english","QHeaderView",]
        for key,prefix in zip(the_keys,the_prefix):
            font_family = self.new_settings.value(f"font_family/{key}",)
            try:
                font_size = self.new_settings.value(f"font_size/{key}",type=int)
            except:
                font_size = 0
            font_family_qss = ""
            font_size_qss = ""
            if font_family:
                font_family_qss = f' font-family: "{font_family}"; '
            if type(font_size) == int:
                if font_size > 0:
                    font_size_qss = f" font-size: {font_size}px; "
            if font_family_qss or font_size_qss:
                #qss_string.append(prefix + "{ " + font_family_qss + font_size_qss + " }" )
                qss_string.append(prefix + "{ "  )
                if font_family_qss:
                    qss_string.append(font_family_qss)
                if font_size_qss:
                    qss_string.append(font_size_qss)
                qss_string.append( " }" )

        # 选中行颜色
        settings = self.new_settings
        # 背景色
        background_r = -1
        background_g = -1
        background_b = -1
        background_a = 255
        try:
            background = settings.value("gamelist_highlight/background")
        except:
            background = ""
        if background :
            try:
                background_r = int(background.split(",")[0])
                background_g = int(background.split(",")[1])
                background_b = int(background.split(",")[2])
                background_a = int(background.split(",")[3])
            except:
                background_r = -1
                background_g = -1
                background_b = -1
                background_a = 255
        value_ok=False
        if background_r >= 0 and background_g >= 0 and background_b >= 0 and background_a >= 0: 
            if  background_r <= 255 and background_g <= 255 and background_b <= 255 and background_a <= 255:
                value_ok=True
        if not value_ok:
            background_r = -1
            background_g = -1
            background_b = -1
            background_a = 255
        # 文字颜色
        colour_r = -1
        colour_g = -1
        colour_b = -1
        colour_a = 255
        try:
            colour = settings.value("gamelist_highlight/colour",)
        except:
            colour = ""
        if colour :
            try:
                colour_r = int(colour.split(",")[0])
                colour_g = int(colour.split(",")[1])
                colour_b = int(colour.split(",")[2])
                colour_a = int(colour.split(",")[3])
            except:
                colour_r = -1
                colour_g = -1
                colour_b = -1
                colour_a = 255
        value_ok=False
        if colour_r >= 0 and colour_g >= 0 and colour_b >= 0 and colour_a >= 0: 
            if colour_a <= 255 and colour_r <= 255 and colour_g <= 255 and colour_b <= 255:
                value_ok=True
        if not value_ok:
            colour_r = -1
            colour_g = -1
            colour_b = -1
            colour_a = 255

        background_qss=""
        if background_r >= 0 and background_g >= 0 and background_b >= 0 and background_a >= 0:
            if background_r <=255 and background_g <=255 and background_b <=255 and background_a <=255:
                background_qss=f"selection-background-color: rgba({background_r},{background_g},{background_b},{background_a});"
        colour_qss=""
        if colour_r >= 0 and colour_g >= 0 and colour_b >= 0 and colour_a >= 0:
            if colour_r <=255 and colour_g <=255 and colour_b <=255 and colour_a <=255:
                colour_qss=f"selection-color: rgba({colour_r},{colour_g},{colour_b},{colour_a});"
        if background_qss or colour_qss:
            qss_string.append(f"QTreeView,QTableView,QListView{{ {background_qss} {colour_qss} }}")

        # 其它 

        ###
        qss_string="\n".join(qss_string)
        print(qss_string)
        self.setStyleSheet(qss_string)

    def new_func_set_row_height_for_tableview(self,at_start=False):
        print("set row height for tableview")
        for widget in self.centralWidget().children():
            if isinstance(widget,QTableView):
                try:row_height = self.new_settings.value("gamelist/row_height_for_tableview",type=int)
                except:row_height = 0
                
                if type(row_height) is not int:
                    return
                
                if row_height < 0:
                    return

                if row_height == 0:
                    if not at_start:
                        widget.verticalHeader().resetDefaultSectionSize()
                elif row_height > 0:
                    widget.verticalHeader().setDefaultSectionSize(row_height)

    def new_func_key_ctrl_p(self):
        """按下 Ctrl+P 时触发的槽函数"""
        focused = QApplication.focusWidget()
        if focused:
            print(focused)
            # 获取部件的类名和显示的文本（如果有）
            text = ""
            if hasattr(focused, "text"):
                text = focused.text()
            elif hasattr(focused, "placeholderText"):
                text = focused.placeholderText()
            elif hasattr(focused, "title"):
                text = focused.title()
            print(f"当前焦点部件：{focused.metaObject().className()}，内容：{text}")
        else:
            print("当前没有部件获得焦点（焦点可能在窗口外或非 QWidget 上）")

#####
class WorkerSignals(QObject):
    
    #error = Signal(str)
    #result = Signal(dict)
    
    new_finished = Signal()

class Worker_Test(QRunnable):
    
    def __init__(self, ):
        super().__init__()
        self.new_signals = WorkerSignals() # Create an instance of our signals class.
    
    @Slot()
    def run(self):
        for n in range(5):
            time.sleep(1)
            print(n)
        self.new_signals.new_finished.emit()

class Worker_load_extra_text_to_database(QObject):
    new_signal_for_finished = Signal()

    def __init__(self, some_values=None,*args,**kwargs):
        super().__init__()

        if some_values is None:
            some_values = dict()
        self.new_some_values = some_values
        # history_xml_path
        # history_dat_path
        # gameinit_path
        # mameinfo_path
        # messinfo_path
        # command_path
        # command_english_path
    
    def new_func_do_work(self):
        print("--------------------------------------")
        print("load extra text to database")

        conn = sqlite3.connect(the_files.extra_database_file)
        
        history_xml_path = self.new_some_values.get("history_xml_path","")
        if os.path.isfile(history_xml_path):
            print(history_xml_path)
            extra_database.update_history(conn,history_xml_path,ui_models.parent_set)

        history_dat_path = self.new_some_values.get("history_dat_path","")
        if os.path.isfile(history_dat_path):
            print(history_dat_path)
            extra_database.update_history_2(conn,history_dat_path,ui_models.parent_set)

        gameinit_path = self.new_some_values.get("gameinit_path","")
        if os.path.isfile(gameinit_path):
            print(gameinit_path)
            extra_database.update_gameinit(conn,gameinit_path,ui_models.parent_set)

        mameinfo_path = self.new_some_values.get("mameinfo_path","")
        if os.path.isfile(mameinfo_path):
            print(mameinfo_path)
            extra_database.update_mameinfo(conn,mameinfo_path,ui_models.parent_set)

        messinfo_path = self.new_some_values.get("messinfo_path","")
        if os.path.isfile(messinfo_path):
            print(messinfo_path)
            extra_database.update_messinfo(conn,messinfo_path,ui_models.parent_set)

        command_path = self.new_some_values.get("command_path","")
        if os.path.isfile(command_path):
            print(command_path)
            extra_database.update_command(conn,command_path,ui_models.parent_set)

        command_english_path = self.new_some_values.get("command_english_path","")
        if os.path.isfile(command_english_path):
            print(command_english_path)
            extra_database.update_command_english(conn,command_english_path,ui_models.parent_set)

        conn.close()
        print("load extra text to database done")

        self.new_signal_for_finished.emit()

class Worker_parse_xml(QObject):
    
    new_signal_finished = Signal(bytes)
    new_signal_for_save_file_failed = Signal()
    def __init__(self, xml_file,*args,**kwargs):
        super().__init__(*args,**kwargs)
        self.new_xml_file = xml_file
        self.new_result = b""

    def new_func_do_work(self):
            try:
                result = xml_parse_mame.main(self.new_xml_file)
            except: 
                result = dict()
                exc_type, exc_value, exc_traceback = sys.exc_info()
                print(traceback.print_exception(exc_type, exc_value, exc_traceback))

            if result:
                # 文件：保存游戏列表数据
                self.new_func_save_gamelist_data(result)

                # 内存：结果 pickle 保存到 bytes
                self.new_result = pickle.dumps(obj=result)

            self.new_signal_finished.emit(self.new_result)

    def new_func_save_gamelist_data(self,data):
        print()
        print( "save gamelist data" )
        filename = the_files.data_file

        try:
            file = open( filename , 'wb' )
            pickle.dump( data , file )
            file.close(  )
            return 0
        except:
            print( "save pickle failed")
            print( "save to ")
            print( filename )
            self.new_signal_for_save_file_failed.emit()

class Worker_after_parse_xml(QObject):
    
    new_signal_for_finished = Signal()

    def __init__(self, some_values=None,*args,**kwargs):
        super().__init__(*args,**kwargs)

        if some_values is None:
            some_values = dict()
        
        self.new_some_values = some_values
        # translation_file_path
        # gamelist_filter
        # folders_path
        # top_index_list_string
        # icon_zip_path


    def new_func_load_translation_file(self,):
        translation_file_path = self.new_some_values.get("translation_file_path","")
        if not translation_file_path:
            return
        if os.path.isfile(translation_file_path):
            try:
                ui_models.load_gamelist_translation_file(translation_file_path)
            except:
                print("load translation file failed")
                exc_type, exc_value, exc_traceback = sys.exc_info()
                print(traceback.print_exception(exc_type, exc_value, exc_traceback))

    @Slot()
    def new_func_do_work(self,):
        print("do work")

        # 拥有列表
        print("load available set")
        filename = the_files.available_file
        if os.path.isfile(filename):
            try:
                file = open(filename, 'rb')
                data_from_pickle = pickle.load( file )
                file.close()
                if isinstance(data_from_pickle,set):
                    ui_models.available_set = data_from_pickle
                else:
                    print("拥有列表数据出错，不是 set 类型")
                    ui_models.available_set = set()
            except:
                print( "read pickle failed")
                print( filename )
                #QMessageBox.critical(self, "拥有列表数据读取失败", "pickle文件读取失败。\n文件可能损坏;\n或者用户无权限读取该文件：\n" + filename)
                ui_models.available_set = set()
                exc_type, exc_value, exc_traceback = sys.exc_info()
                print(traceback.print_exception(exc_type, exc_value, exc_traceback))

        # 更新过滤项
        print("update filter set")
        try:
            misc_funcs.update_filter_set(self.new_some_values.get("gamelist_filter",""))
        except:
            print("update filter set failed")
            exc_type, exc_value, exc_traceback = sys.exc_info()
            print(traceback.print_exception(exc_type, exc_value, exc_traceback))

        # 加载外部索引,wip
        # external_index
        # external_index_by_source
        ######
        folders_path = self.new_some_values.get("folders_path","")
        if folders_path:
            try:
                print(folders_path)
                extra_folders.all_dict = {game_id:game_id for game_id in ui_models.all_set} # 
                external_index = extra_folders.get_external_index_data(folders_path,file_extension=".ini")
                # 更新 ui_models.editable_index_files
                for x in external_index.keys():
                    if os.access(x, mode=os.W_OK):
                        #print(x,"\t",True)
                        ui_models.editable_index_files.add(x)
                #print(len(ui_models.editable_index_files))
                external_index_by_source = extra_folders.get_external_index_data(folders_path,file_extension=".source_ini")
                ui_models.set_value("external_index",external_index)
                ui_models.set_value("external_index_by_source",external_index_by_source)
                extra_folders.all_dict = dict() # 清空
                #print(external_index.keys())
                #print(external_index_by_source.keys())
            except:
                print("load external index failed")
                exc_type, exc_value, exc_traceback = sys.exc_info()
                print(traceback.print_exception(exc_type, exc_value, exc_traceback))
        else:
            print("folders_path is empty")
        #
        #
        # rebuild_index
        # 置顶项
        print("top_index_list")
        top_index_list_string = self.new_some_values.get("top_index_list_string","")
        if not top_index_list_string:
            top_index_list = []
        else:
            top_index_list = top_index_list_string.split(";")
        # 去重
        temp_list = []
        temp_set = set()
        for x in top_index_list:
            if x not in temp_set:
                temp_list.append(x)
            temp_set.add(x)
        top_index_list = temp_list
        ui_models.top_index_list = top_index_list
        ui_models.rebuild_index()
        #
        # build_editable_index_data
        ui_models.build_editable_index_data()

        # 加载翻译文件
        print("load translation file")
        self.new_func_load_translation_file()

        # 加载图标
        print("load icons")
        icon_zip_path = self.new_some_values.get("icon_zip_path","")
        if icon_zip_path:
            try:
                ui_models.icon_extra_resource = misc_funcs.load_icons_from_zip(icon_zip_path,ui_models.all_set)
            except:
                ui_models.icon_extra_resource = dict()
                exc_type, exc_value, exc_traceback = sys.exc_info()
                print(traceback.print_exception(exc_type, exc_value, exc_traceback))

        print("finish")
        self.new_signal_for_finished.emit()

class Worker_for_scan_game_files(QObject):
    new_signal_for_finished = Signal(set)
    new_signal_for_failed = Signal()

    def __init__(self,*args,**kwargs):
        super().__init__(*args,**kwargs)

        self.new_rompath = ""
        self.new_merged = False
        self.new_mame_working_directory = ""

    def new_func_set_values(self,mame_working_directory, rompath, merged=False):
        self.new_mame_working_directory = mame_working_directory
        self.new_rompath = rompath
        self.new_merged = merged
        
    def new_func_do_work(self):
        try:
            data = misc_funcs.scan_game_files_only_check_if_file_exists_work(self.new_mame_working_directory,self.new_rompath, self.new_merged)
        except:
            data = set()
            self.new_signal_for_failed.emit()

            exc_type, exc_value, exc_traceback = sys.exc_info()
            print(traceback.print_exception(exc_type, exc_value, exc_traceback))

        self.new_signal_for_finished.emit(data)



def main():
    
    the_variables.locale_original = locale.setlocale(locale.LC_ALL)  # 获取当前语言区域
    print("locale :",the_variables.locale_original)

    # 临时文件夹 the_files.folder_temporary
    if os.path.isdir(the_files.folder_temporary):
        pass
    else:
        if os.path.isfile(the_files.folder_temporary):
            try:
                os.remove(the_files.folder_temporary)
            except:
                pass
        try:
            os.makedirs(the_files.folder_temporary)
        except:
            pass

    
    app = QApplication(sys.argv)
    window = TheMainWindow()
    window.show()
    window.new_func_load_settings_at_start()

    # 初始化检查
    # 数据文件 如果不在
    # 并且，未设置 MAME 路径、或设置的不是可执行程序
    # 弹窗， 提示用户 选择 MAME 路径
    count = 0
    while True:
        if os.path.isfile(the_files.data_file):
            break
        else:
            if window.new_func_check_mame_path():
                break
            else:
                count += 1
                if count > 1:
                    QMessageBox.warning(window, "错误", "MAME 可执行文件路径 设置错误")
                window.new_func_show_dialog_for_choose_emulator_path_and_working_dir()
    
    # 初始化检查
    # 数据文件 如果不在
    # 从模拟器导入数据   
    if not os.path.isfile(the_files.data_file): 
        window.new_func_show_progress_bar()
        # 导入 MAME 数据
        # 解析 MAME xml
        window.new_func_load_data_from_emulator()
    else:
        window.new_func_show_progress_bar()
        # 从数据文件读取数据
        window.new_func_load_gamelist_data_from_file()
    
    

    #window.new_func_progressbar_hide()



    # 读取数据文件

    # 初始化之后，读取的设置
    #window.centralWidget().new_func_for_load_settings()
    #window.new_func_index_select_remember_after_load_settings()
    sys.exit(app.exec())

if __name__ == "__main__":
    main()