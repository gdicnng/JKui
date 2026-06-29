import sys,os,time,shutil,io
import pickle
import locale
import re

from qtpy.QtWidgets import *
from qtpy.QtGui import *
from qtpy.QtCore import *

import the_variables
import the_files
import ui_index
import ui_gamelist_tableview
import ui_small_windows
import misc_funcs
import xml_parse_mame
import ui_models
import ui_central_widget
import the_user_settings_default_value
import extra_folders



class TheMainWindow(QMainWindow):
    

    def __init__(self):
        super().__init__()

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
        print(self.new_settings.fileName())

        the_variables.user_settings = self.new_settings # 记录
        # Store the settings in INI files. Note that INI files lose the distinction between numeric data and the strings used to encode them, 
        # so values written as numbers shall be read back as QString.
        
        # 加载默认值
        for key, value in the_user_settings_default_value.default_value.items():
            if not self.new_settings.value(key):
                self.new_settings.setValue(key, value)
        # 更新 extra 路径记录
        the_variables.update_extra_path()
          

        

        # 
        self.new_func_creatCentralWidget()
        self.new_func_createActions()
        self.new_func_createMenus()
        self.new_func_createStatusBar()
        self.new_func_createDockWindows()
        self.new_func_createToolBars()



        
        self.new_dialog_for_choose_emulator_path_and_working_dir = None

    ##################
    def new_func_creatCentralWidget(self):
        self.new_ui_central_widget = ui_central_widget.TheCentralWidget(self)
        self.new_ui_central_widget.setObjectName("central_widget")
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
        self.new_ui_menu_ui = self.menuBar().addMenu("UI")
        #self.new_ui_menu_ui.addAction(self.new_action_save_settings)
        #self.new_ui_menu_ui.addAction(self.new_action_load_settings)
        
        self.new_ui_menu_ui.addSeparator()
        self.new_ui_menu_ui_dock_windows = self.new_ui_menu_ui.addMenu("显示/隐藏 周边窗口")
        
        self.new_ui_menu_ui.addSeparator()
        self.new_ui_menu_ui_style = self.new_ui_menu_ui.addMenu("style")
        self.new_ui_menu_ui_qss = self.new_ui_menu_ui.addMenu("qss")
        
        self.new_ui_menu_ui.addSeparator()
        
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
                action.triggered.connect( self.new_func_set_style_by_menu )
                
                # 初始化 UI 时，标记 当前 style
                if cuttent_style_name.lower() == style_name.lower():
                    action.setChecked(True)
                
                self.new_action_group_for_style.addAction(action)
                
                self.new_ui_menu_ui_style.addAction(action)
        
        make_menu_for_sytle()
        
        # UI → qss
        def make_menu_for_qss():
            #self.new_ui_menu_ui_qss
            
            # 重置按钮
            action =  QAction("重置",self,)
            action.triggered.connect(self.new_func_clear_qss)
            self.new_ui_menu_ui_qss.addAction( action )
            self.new_ui_menu_ui_qss.addSeparator()
            
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
                action.triggered.connect( self.new_func_load_qss_file_by_menu )
                action.setCheckable(True)
                self.new_action_group_for_qss.addAction(action)
                self.new_ui_menu_ui_qss.addAction( action )
        make_menu_for_qss()
        

        ##### 游戏列表
        self.new_ui_menu_gamelist=self.menuBar().addMenu("游戏列表")
        # 显示 tableview
        self.new_action_show_tableview = QAction("显示 tableview",self,)
        self.new_action_show_tableview.triggered.connect( self.centralWidget().new_func_show_tableview )
        self.new_ui_menu_gamelist.addAction(self.new_action_show_tableview)
        # 显示 tableview 2 level
        self.new_action_show_tableview_2_level = QAction("显示 tableview 2 level",self,)
        self.new_action_show_tableview_2_level.triggered.connect( self.centralWidget().new_func_show_tableview_2_level )
        self.new_ui_menu_gamelist.addAction(self.new_action_show_tableview_2_level)
        # 显示 treeview
        self.new_action_show_treeview = QAction("显示 treeview",self,)
        self.new_action_show_treeview.triggered.connect( self.centralWidget().new_func_show_treeview )
        self.new_ui_menu_gamelist.addAction(self.new_action_show_treeview)

        self.new_ui_menu_other = self.menuBar().addMenu("其它")
        self.new_ui_menu_other = self.menuBar().addMenu("其它")
        self.new_ui_menu_other.addAction(self.new_action_test)
        self.new_ui_menu_other.addAction(self.new_action_test_progressbar)
        
        #self.new_ui_menu_view = self.menuBar().addMenu("view")
        #self.new_ui_menu_view.addAction(self.new_action_b)

    def new_func_test(self):
        print("test")

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
            
            self.new_ui_menu_ui_dock_windows.addAction(self.new_dock_index.toggleViewAction())
            self.new_ui_index.new_signal_change_index.connect(self.new_func_slot_for_receive_index)
        func_for_index()
        
        self.new_ui_menu_ui_dock_windows.addSeparator()
        
        # 创建 重复 类型的 dock window
        def func_for_make_dock_window(ui_type,title_prefix,object_name_prefix,number = 1): # range(1,number)
            
            if number < 1 : return
            
            # 小窗口 1-5
            for n in range(1,number + 1):
                
                title       = title_prefix + str(n)
                object_name = object_name_prefix + str(n)
                
                # self.new_dock_image_n
                # self.new_dock_text_n
                variable_name = "new_dock_" + object_name_prefix + str(n)
                
                print()
                print(title)
                print(object_name)
                print(variable_name)
                
                setattr(self,variable_name,QDockWidget(title, self), )
                dock_window = getattr( self, variable_name)
                
                dock_window.setObjectName( object_name )
                dock_window.setAllowedAreas(Qt.AllDockWidgetAreas )
                
                child_window = ui_type(dock_window)
                dock_window.setWidget(child_window)
                
                self.addDockWidget(Qt.RightDockWidgetArea, dock_window)
                
                # 隐藏
                dock_window.setVisible(False) 
                
                # 菜单
                self.new_ui_menu_ui_dock_windows.addAction(dock_window.toggleViewAction())
        
        # 文本
        func_for_make_dock_window( QTextEdit, "文本_", "text_" , number = 8 )
        self.new_ui_menu_ui_dock_windows.addSeparator()


        def func_for_image_dockwindow(title_prefix,object_name_prefix,number = 1):
            if number < 1 : return
            
            # 小窗口 1-5
            for n in range(1,number + 1):
                
                title       = title_prefix + str(n)
                object_name = object_name_prefix + str(n)
                
                # self.new_dock_image_n
                # self.new_dock_text_n
                variable_name = "new_dock_" + object_name_prefix + str(n)
                
                print()
                print(title)
                print(object_name)
                print(variable_name)
                
                setattr(self,variable_name,ui_small_windows.Image_dockwidget(title, self), )
                dock_window = getattr( self, variable_name)
                
                dock_window.setObjectName( object_name )
                dock_window.setAllowedAreas(Qt.AllDockWidgetAreas )
                
                
                self.addDockWidget(Qt.RightDockWidgetArea, dock_window)
                
                # 隐藏
                dock_window.setVisible(False) 
                
                # 菜单
                self.new_ui_menu_ui_dock_windows.addAction(dock_window.toggleViewAction())

                self.centralWidget().new_signal_for_id_change.connect(dock_window.new_slot_for_id_change)

        # 图片
        func_for_image_dockwindow("图片_","image_",number=the_variables.image_dockwidget_numbers)
        #func_for_make_dock_window( QLabel   , "图片_", "image_", number = 20 )
        self.new_ui_menu_ui_dock_windows.addSeparator()
        

        
        # 仅显示两个就行了
        dock_window_1 = getattr(self,"new_dock_image_1")
        dock_window_1.setVisible(True)
        dock_window_2 = getattr(self,"new_dock_image_2")
        dock_window_2.setVisible(True)


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
        #new_action_tableview.setCheckable(True)
        new_action_tableview.triggered.connect( self.centralWidget().new_func_show_tableview )
        new_action_tableview_2_level = QAction("2",self,)
        new_action_tableview_2_level.triggered.connect( self.centralWidget().new_func_show_tableview_2_level )
        new_action_treeview = QAction("3",self,)
        new_action_treeview.triggered.connect( self.centralWidget().new_func_show_treeview )

        self.new_toolbar_for_gamelist.addAction(new_action_tableview)
        self.new_toolbar_for_gamelist.addAction(new_action_tableview_2_level)
        self.new_toolbar_for_gamelist.addAction(new_action_treeview)
        #self.new_toolbar_for_gamelist.addSeparator()

        self.new_tool_bar_for_search = ui_small_windows.Toolbars_for_search(self)
        self.new_tool_bar_for_search.setObjectName("toolbar_for_search")
        self.new_tool_bar_for_search.setWindowTitle("搜索栏")
        self.new_tool_bar_for_search.setFloatable(False)
        #self.new_tool_bar_for_search.setMovable(False)
        self.new_tool_bar_for_search.setAllowedAreas(Qt.TopToolBarArea)
        self.new_tool_bar_for_search.new_signal_for_search.connect(self.new_func_for_search)
        self.addToolBar(self.new_tool_bar_for_search)


    ####################

    def closeEvent(self,event):
        print()
        print("close")
        self.new_func_save_settings()
        
        super().closeEvent(event)


    
    # 初始化，从 MAME 导出 数据
    def new_func_load_data_from_emulator(self,):
        print()
        print( "export data from emulator")

        mame_path = self.new_settings.value("mame/path") 
        mame_working_directory = self.new_settings.value("mame/working_directory") 
        mame_path, mame_working_directory = misc_funcs.get_mame_path_and_working_directory(mame_path, mame_working_directory)
        
        process = QProcess(self)
        if mame_working_directory:
            if os.path.isdir(mame_working_directory):
               process.setWorkingDirectory(mame_working_directory)
        self.new_buffer_to_hold_mame_data = io.BytesIO()
        #process.setProcessChannelMode(QProcess.ForwardedErrorChannel)
        process.readyReadStandardOutput.connect(lambda: self.new_buffer_to_hold_mame_data.write(process.readAllStandardOutput().data()))
        process.readyReadStandardError.connect(lambda: process.readAllStandardError())
        process.finished.connect(lambda: self.new_func_data_from_emulator_is_ready())
        process.start(mame_path, the_variables.command_line_options_for_emulator_to_export_data)
    # 初始化，解析 MAME xml
    @Slot()
    def new_func_data_from_emulator_is_ready(self,):
        print()
        print("data from emulator is ready")
        self.new_func_parse_xml()

    def new_func_parse_xml(self,):
        print()
        print("parse xml")
        self.new_thread_for_parse_xml = QThread(self)
        self.new_worker_for_parse_xml = Worker_parse_xml(self.new_buffer_to_hold_mame_data)

        self.new_worker_for_parse_xml.moveToThread(self.new_thread_for_parse_xml)

        self.new_thread_for_parse_xml.started.connect(self.new_worker_for_parse_xml.new_func_do_work)
        self.new_worker_for_parse_xml.new_finished.connect(self.new_func_on_xml_parse_finished)
        self.new_worker_for_parse_xml.new_finished.connect(self.new_thread_for_parse_xml.quit)
        self.new_worker_for_parse_xml.new_finished.connect(self.new_worker_for_parse_xml.deleteLater)
        self.new_thread_for_parse_xml.finished.connect(self.new_thread_for_parse_xml.deleteLater)

        print("parsing xml")
        self.new_thread_for_parse_xml.start()
    #
    @Slot(dict)
    def new_func_on_xml_parse_finished(self, result):
        """XML解析完成"""
        print()
        print("xml parse finish ###########")
        self.new_buffer_to_hold_mame_data.close()

        print(type(result))
        print(result.keys())
        
        # 保存游戏列表数据
        self.new_func_save_gamelist_data(result)
        self.new_func_update_model_data(result)

        # 读取列表翻译数据


        self.new_func_progressbar_hide()

    # 初始化，从 临时文件 读取 数据
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
                sys.exit()
        
        self.new_func_update_model_data(data)


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
            sys.exit()
    
    #################################
    #################################
    #################################
    #################################
    def new_func_update_model_data(self,data):
        print()
        print( "update model data" )

        # 原始图标
        ui_models.load_icon()

        # 更新模型数据
        ##'columns', 'dict_data', 'internal_index', 'machine_dict', 'mame_version', 'set_data'
        #
        ## clounms = []
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
        print(str(len(data['set_data']['all_set'])))
        print(str(len(data['set_data']['all_set'])))
        print(str(len(data['set_data']['all_set'])))
        print(str(len(data['set_data']['all_set'])))
        print(str(len(data['set_data']['all_set'])))
        print(str(len(data['set_data']['all_set'])))
        self.new_ui_statusbar_for_total_number.setText( str(len(data['set_data']['all_set'])) )

        #
        ui_models.update_some_value()

        # 加载外部索引,wip
        # external_index
        # external_index_by_source
        ######
        folders_path = self.new_settings.value("extra/folders")
        print(folders_path)
        extra_folders.all_dict = {game_id:game_id for game_id in data["set_data"]["all_set"]} # 
        external_index = extra_folders.get_external_index_data(folders_path,file_extension=".ini")
        external_index_by_source = extra_folders.get_external_index_data(folders_path,file_extension=".source_ini")
        ui_models.set_value("external_index",external_index)
        ui_models.set_value("external_index_by_source",external_index_by_source)
        extra_folders.all_dict = dict() # 清空
        print(external_index.keys())
        print(external_index_by_source.keys())

        # 加载翻译文件
        self.new_func_load_translation_file()
        
        # 重新构建索引列表
        self.new_ui_index.model().beginResetModel()
        top_index_list_string = self.new_settings.value("index/top_index_list")
        if not top_index_list_string:
            top_index_list = []
        else:
            top_index_list = top_index_list_string.split(";")
        ui_models.rebuild_index(top_index_list)
        self.new_ui_index.model().endResetModel()
        
        
        ######
        ######
        ######
        ######

        #ui_models.set_game_list_to_all()
        #self.new_ui_central_widget.new_func_refresh()

        #初始化之后，读取的设置
        self.centralWidget().new_func_for_load_settings()
        self.new_func_index_select_remember_after_load_settings()


    def new_func_load_external_index(self,):
        external_inedex = dict()
        # 待补充
        return external_inedex
        

    def new_func_load_translation_file(self,):
        translation_file_path = self.new_settings.value("mame/translation_file")
        if not translation_file_path:
            return
        if os.path.isfile(translation_file_path):
            try:
                ui_models.load_gamelist_translation_file(translation_file_path)
            except:
                print("load translation file failed")
        

    #################
    #################
    #################

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

        self.new_settings.setValue("index/index_id_1",the_variables.index_id_1)
        self.new_settings.setValue("index/index_id_2",the_variables.index_id_2)

        self.centralWidget().new_func_for_save_settings()

    def new_func_load_settings_at_start(self,):
        print( )
        print( "load settings")
        
        # 刚开始，初始化之前，还没有设置时，没有数据
        
        try: self.restoreGeometry(self.new_settings.value("mainwindow/geometry"))
        except: pass
        
        try:self.restoreState(self.new_settings.value("mainwindow/state"))
        except:pass
        
        # style
        try : style_name = self.new_settings.value("mainwindow/style")
        except : pass
        if style_name:
            self.new_func_set_style(style_name)
        
        # qss
        try : qss_file = self.new_settings.value("mainwindow/qss")
        except : pass
        if qss_file:
            self.new_func_load_qss_file_at_start(qss_file)
        
        # 排序
        try:    the_variables.sort_column = self.new_settings.value("gamelist/sort_column").toInt()
        except: the_variables.sort_column = -1
        try:    the_variables.sort_reverse = self.new_settings.value("gamelist/sort_reverse").toBool()
        except: the_variables.sort_reverse = False
        try:    the_variables.sort_use_locale = self.new_settings.value("gamelist/sort_use_locale").toBool()
        except: the_variables.sort_use_locale = False

    @Slot()
    def new_func_load_qss_file_by_menu(self,):
        # qss 文件，位于 the_files.folder_qss 中
        
        print()
        print("slot app.setStyleSheet")
        
        sender = self.sender()
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

    @Slot()
    def new_func_set_style_by_menu(self,):
        print("")
        print("set style by menu")
        
        sender = self.sender()
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
            self.new_dialog_for_choose_emulator_path_and_working_dir = ui_small_windows.Dialog_to_choose_emulator_path(self)
        
        mame_path = self.new_settings.value("mame/path") 
        mame_working_directory = self.new_settings.value("mame/working_directory") 
        self.new_dialog_for_choose_emulator_path_and_working_dir.new_func_set_values(mame_path,mame_working_directory)
        
        self.new_dialog_for_choose_emulator_path_and_working_dir.exec()

    @Slot(str,str)
    def new_func_slot_to_receive_emulator_path_and_working_dir(self,mame_path,mame_working_directory):
        print("")
        print("slot to receive emulator path and working dir")
        print("mame_path: ",mame_path)
        print("mame_working_directory: ",mame_working_directory)
        
        self.new_settings.setValue("mame/path",mame_path)
        self.new_settings.setValue("mame/working_directory",mame_working_directory)

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

        self.setEnabled(False)
        
        self.new_progressbar_on_statusbar.setVisible(True)

    @Slot()
    def new_func_progressbar_hide(self):
        print("progressbar hide")

        self.new_progressbar_on_statusbar.setVisible(False)
        self.setEnabled(True)

    @Slot(str,str)
    def new_func_slot_for_receive_index(self,id_1,id_2):
        #print("")
        #print("slot to receive index id")
        #print("id_1: ",id_1)
        #print("id_2: ",id_2)

        # 记录 
        the_variables.index_id_1 = id_1
        the_variables.index_id_2 = id_2

        central_widget = self.centralWidget()
        current_table = central_widget.currentWidget()
        current_table.model().new_func_show_by_index(id_1,id_2)
    
    @Slot(str,bool,bool,tuple)
    def new_func_for_search(self,search_string,use_re=False,ignore_case=True,search_columns=tuple(),):
        # search_string,use_re=False,ignore_case=True,search_columns=tuple(),
        # 搜索字符串
        # 是否正则
        # 是否忽略大小写
        # 搜索列 范围 tuple
        

        temp = search_string.strip()
        if temp:
            if use_re:
                try:
                    re.compile(temp)
                except:
                    QMessageBox.warning(self,"warning","正则表达式可能出错")
                    return

            central_widget = self.centralWidget()
            current_table = central_widget.currentWidget()
            current_table.model().new_func_show_search_result(search_string,use_re=use_re,ignore_case=ignore_case,search_columns=search_columns)


    def new_func_index_select_remember_after_load_settings(self,):
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
            self.new_func_slot_for_receive_index(index_id_1,index_id_2)

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
class Thread_for_parse_xml(QObject):
    pass
class Worker_parse_xml(QObject):
    
    new_finished = Signal(dict)
    def __init__(self, xml_file,*args,**kwargs):
        super().__init__(*args,**kwargs)
        self.new_xml_file = xml_file

    def new_func_do_work(self):
            print("parse xml$$$$$$$$$$$$$$$$$")
            
            result = xml_parse_mame.main(self.new_xml_file)
            self.new_finished.emit(result)

class Controller(QObject):
    new_thread_for_parse_xml = QThread()




def main():
    
    the_variables.locale_original = locale.setlocale(locale.LC_ALL)  # 获取当前语言区域
    print("locale :",the_variables.locale_original)

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