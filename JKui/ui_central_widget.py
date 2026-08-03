import io,re,os,shutil,time
import xml.etree.ElementTree

from qtpy.QtWidgets import *
from qtpy.QtGui import *
from qtpy.QtCore import *

import ui_gamelist_tableview
import ui_models
import ui_gamelist_treeview
import misc_funcs
import the_variables
import ui_small_windows
import the_files
import ui_index
import ui_gamelist_listview



class TheCentralWidget(QStackedWidget):
    new_signal_for_id_change=Signal(str,)#id
    new_signal_for_gamelist_number_change=Signal(int,) # 列表数量

    def __init__(self,parent=None):
        super().__init__(parent)

        self.new_signal_for_id_change.connect(self.new_slot_record_game_id)

        self.new_flag_search = False
        self.new_search_content = None

        ## QSortFilterProxyModel ，这东西太卡了,不能用

        ####
        # tableview
        self.new_ui_gamelist_tableview = ui_gamelist_tableview.My_Table(self)
        self.addWidget(self.new_ui_gamelist_tableview)

        ####
        # tableview 2 level
        self.new_ui_gamelist_tableview_2_level = ui_gamelist_tableview.My_Table_for_2_level(self)
        self.addWidget(self.new_ui_gamelist_tableview_2_level)


        ####
        # tableview 2 level tree like
        self.new_ui_gamelist_tableview_2_level_tree_like = ui_gamelist_tableview.My_Table_for_2_level_tree_like(self)
        self.addWidget(self.new_ui_gamelist_tableview_2_level_tree_like)

        ####
        # tree view
        self.new_ui_gamelist_treeview = ui_gamelist_treeview.My_Tree_View(self)
        self.addWidget(self.new_ui_gamelist_treeview)

        ####
        # list view icon
        self.new_ui_gamelist_icon_table = ui_gamelist_listview.My_Icon_Table(self)
        self.addWidget(self.new_ui_gamelist_icon_table)

        ####
        # list view image
        self.new_ui_gamelist_image_table = ui_gamelist_listview.My_Image_Table(self)
        self.addWidget(self.new_ui_gamelist_image_table)


        self.setCurrentWidget(self.new_ui_gamelist_tableview)

        for table in self.children():
            if hasattr(table,"model"):
                if hasattr(table.model(),"new_signal_need_reload_gamelist"):
                    table.model().new_signal_need_reload_gamelist.connect(self.new_func_reload_gamelist)
                    print("connect","new_signal_need_reload_gamelist",table.objectName(),)

 
    def new_func_show_table(self,the_table):
        old_table = self.currentWidget()

        if old_table is the_table:
            return

        old_table.model().beginResetModel()
        old_table.model().new_func_clear_all_data()
        old_table.model().endResetModel()

        if old_table is self.new_ui_gamelist_image_table:
            old_table.model().new_func_close_zip()

        if the_table is self.new_ui_gamelist_image_table:
            the_table.model().new_func_open_zip()
        
        self.setCurrentWidget(the_table)

        id_1 = the_variables.index_id_1 
        id_2 = the_variables.index_id_2 
        if id_1 :
            the_table.model().new_func_show_by_index(id_1,id_2)
    #
    def new_func_show_tableview(self,):
        self.new_func_show_table(self.new_ui_gamelist_tableview)
    #
    def new_func_show_tableview_2_level(self,):
        self.new_func_show_table(self.new_ui_gamelist_tableview_2_level)
    def new_func_show_tableview_2_level_tree_like(self,):
        self.new_func_show_table(self.new_ui_gamelist_tableview_2_level_tree_like)
    #
    def new_func_show_treeview(self,):
        self.new_func_show_table(self.new_ui_gamelist_treeview)

    def new_func_show_icon_table(self,):
        self.new_func_show_table(self.new_ui_gamelist_icon_table)

    def new_func_show_image_table(self,):
        self.new_func_show_table(self.new_ui_gamelist_image_table)

    def new_func_refresh_layoutchange(self,):
        widget = self.currentWidget()
        if hasattr(widget,"model"):
            widget.model().layoutAboutToBeChanged.emit() # ? 数据整体结构发生重大变化（如重置所有数据）
            print("refresh layoutchange")
            widget.model().layoutChanged.emit() # ? 数据整体结构发生重大变化（如重置所有数据）
    
    def new_func_refresh_modelReset(self,):
        widget = self.currentWidget()
        if hasattr(widget,"model"):
            #模型被完全重置
            widget.model().beginResetModel()
            print("refresh modelReset")
            widget.model().endResetModel()
    
    # 程序关闭时，调用这个函数
    def new_func_for_save_settings(self,):
        
        settings = self.parentWidget().new_settings

        # 保存表格的状态
        for widget in self.children():
            if  isinstance(widget,QTableView) or isinstance(widget,QTreeView):

                object_name = widget.objectName()

                if  isinstance(widget,QTableView):
                    header_state = widget.horizontalHeader().saveState()
                else:
                    header_state = widget.header().saveState()
                
                temp_text = "gamelist_table/" + object_name 
                settings.setValue(temp_text, header_state)
                print("table header save data :",object_name,temp_text)

        # 保存置顶的表格
        current_widget = self.currentWidget()
        object_name = current_widget.objectName()
        temp_text = "current_table"
        settings.setValue(temp_text, object_name)

    # 程序启动时，用这个函数
    # 初始化，之后，载入数据后，再用
    def new_func_for_load_settings(self,):
        
        settings = self.parentWidget().new_settings

        # 加载表格的状态
        for widget in self.children():
            if  isinstance(widget,QTableView) or isinstance(widget,QTreeView):
                object_name = widget.objectName()
                temp_text = "gamelist_table/" + object_name

                if  isinstance(widget,QTableView):
                    header = widget.horizontalHeader()
                else:
                    header = widget.header()
                
                try:
                    header_state = settings.value(temp_text)
                    if header_state:
                        load_ok = header.restoreState(header_state)
                        print("table header load data :",widget.objectName(),temp_text,load_ok)
                except:
                    pass

                header.setSortIndicator(-1,Qt.AscendingOrder)
        
        # 加载置顶的表格
        the_object_name = settings.value("current_table")

        for widget in self.children():
            if  isinstance(widget,QTableView) or isinstance(widget,QTreeView) or isinstance(widget,QListView):
                object_name = widget.objectName()
                if object_name == the_object_name:
                    #self.setCurrentWidget(widget)
                    self.new_func_show_table(widget)
                    break


    # 启动模拟器
    def new_func_start_emulator(self,game_id="",game_info=None,hide=True,keypress_event=None,other_command_list=None):
        if not game_info : game_info = []
        print()
        
        settings = self.parentWidget().new_settings
        mame_exe_path = settings.value("mame/path") 
        mame_working_directory = settings.value("mame/working_directory") 
        mame_exe_path, mame_working_directory = misc_funcs.get_abspath_for_mame_and_working_directory(mame_exe_path, mame_working_directory)        
        
        if other_command_list is None:
            other_command_list=[]

        command_list = []

        # 不通过快捷键启动
        if keypress_event is None:
            
            if game_id:# 空模拟器
                command_list.append(game_id)
                if other_command_list:
                    command_list.extend(other_command_list)
            
            print("start emulator",game_id)
            print("hide UI",hide)
            print("working directory : ",mame_working_directory)
            print("mame path         : ",mame_exe_path)
            print("command list      : ",command_list)

            exe_path = mame_exe_path
            working_directory = mame_working_directory

            self.new_func_start_process(exe_path,working_directory,command_list,hide)

        # 通过快捷键启动
        else:
            event = keypress_event

            if event.key() == Qt.Key_F2:
                number = 2
                hide=True
            elif event.key() == Qt.Key_F3:
                number = 3
                hide=True
            elif event.key() == Qt.Key_F4:
                number = 4
                hide=True
            elif event.key() == Qt.Key_F5:
                number = 5
                hide=True
            elif event.key() == Qt.Key_F6:
                number = 6
                hide=True
            elif event.key() == Qt.Key_F7:
                number = 7
                hide=True
            elif event.key() == Qt.Key_F8:
                number = 8
                hide=True
            elif event.key() == Qt.Key_F9:
                number = 9
                hide=True
            elif event.key() == Qt.Key_F10:
                number = 10
                hide=True
            elif event.key() == Qt.Key_F11:
                number = 11
                hide=True
            elif event.key() == Qt.Key_F12:
                number = 12
                hide=True
            elif event.key() in {
                            Qt.Key_2,Qt.Key_3,Qt.Key_4,Qt.Key_5,
                            Qt.Key_6,Qt.Key_7,Qt.Key_8,Qt.Key_9,Qt.Key_0,
            }:
                number = int(event.text())

                if number == 0: # 0键转为10
                    number = 10

                hide=True
                if (event.modifiers() == Qt.ControlModifier):
                    hide=False
            else:
                return

            print("number",number)
            print("hide UI",hide)

            script_file = os.path.join(the_files.script_folder, str(number) + ".txt")
            
            self.new_func_start_process_by_script(game_id,script_file,hide)
    # *****
    def new_func_start_process(self,exe_path,working_directory,command_list=None,hide=True):
        if command_list is None:
            command_list = []
        # 判断程序是否可以执行
        #   不然，UI 隐藏后，感觉它不退出了
        if shutil.which(exe_path) is None:
            QMessageBox.warning(self.parentWidget(), "出错", "程序不可以执行：" + exe_path)
            return

        if hide:
            self.new_saved_geometry_for_parent = None
            self.new_saved_state_for_parent = None
            self.new_saved_geometry_for_parent = self.parentWidget().saveGeometry()
            self.new_saved_state_for_parent = self.parentWidget().saveState()
            self.parentWidget().hide()

            self.new_buffer_to_hold_error_data = io.BytesIO()
            self.new_process = QProcess()
            if working_directory:
                self.new_process.setWorkingDirectory(working_directory)
            #self.new_process.setProcessChannelMode(QProcess.ForwardedChannels)
            self.new_process.setProcessChannelMode(QProcess.ForwardedOutputChannel)
            self.new_process.readyReadStandardError.connect(lambda: self.new_buffer_to_hold_error_data.write(self.new_process.readAllStandardError().data()))
            self.new_process.finished.connect(self.new_slot_for_show_parent_window)
            self.new_process.finished.connect(self.new_slot_for_standard_error_data)
            
            self.new_process.setProgram(exe_path)
            self.new_process.setArguments(command_list)

            self.new_process_start_time = time.time()
            self.new_process.start()

            #new_process.waitForFinished(-1)
        else:
            print("start detached")
            process = QProcess()
            if working_directory:
                process.setWorkingDirectory(working_directory)
            process.setProgram(exe_path)
            process.setArguments(command_list)
            process.setProcessChannelMode(QProcess.ForwardedChannels)
            process.startDetached()
    def new_func_start_process_by_script(self,game_id,script_file_name,hide=True):

        if os.path.split(script_file_name)[0] == "":
            script_file = os.path.join(the_files.script_folder,script_file_name)
        else:
            script_file = os.path.abspath(script_file_name)


        settings = self.parentWidget().new_settings
        mame_exe_path = settings.value("mame/path") 
        mame_working_directory = settings.value("mame/working_directory") 
        mame_exe_path, mame_working_directory = misc_funcs.get_abspath_for_mame_and_working_directory(mame_exe_path, mame_working_directory)        
        

        if os.path.isfile(script_file):
            try:
                working_directory,command_list = self.get_script_content(script_file,game_id,mame_exe_path,mame_working_directory,hide)
            except:
                print("get_script_content() ,failed")
                return

            if command_list:
                print("command_list:",command_list)
                exe_path = command_list[0]
                command_list = command_list[1:]

                print()
                print("game_id",game_id)
                print()
                print("working_directory",working_directory)
                print("exe_path",exe_path)
                print("command_list",command_list)

                self.new_func_start_process(exe_path,working_directory,command_list,hide)
    #
    @Slot()
    def new_slot_for_show_parent_window(self):
        if self.new_saved_geometry_for_parent:
            self.parentWidget().restoreGeometry(self.new_saved_geometry_for_parent)
        if self.new_saved_state_for_parent:
            self.parentWidget().restoreState(self.new_saved_state_for_parent)
        self.parentWidget().show()
    @Slot(int,QProcess.ExitStatus)
    def new_slot_for_standard_error_data(self,exitCode,exitStatus,):
        self.new_buffer_to_hold_error_data.seek(0)
        error_data = self.new_buffer_to_hold_error_data.read()

        print()
        print("standard error data :")
        print(error_data)
        print()

        error_string=""
        for encoding in ['utf_8_sig','ansi','gbk']:
            try:
                error_string = error_data.decode(encoding=encoding,)
                print(error_string)
                print()
                print("encoding:",encoding)
                break
            except:
                error_string = ""
        
        if not error_string:
            if error_data:
                error_string = error_data.decode(encoding='utf_8_sig', errors='backslashreplace')

        if exitCode != 0:
            print("exitCode:",exitCode)
            QMessageBox.warning(self.parentWidget(), "exitCode: " + str(exitCode), error_string)
        else:
            # 虽然 exitCode 为 0 ，但有 标准错误输出
            # 正常情况，比如 模拟状态不佳、roms dump 状态不佳，会有 标准错误输出
            # 官方模拟器，可以不用考虑

            # 但，其它模拟器的情况可能不太一致，比如 老核心的 mame32m
            # 如果短时间内退出，暂定3秒，认为是非正常退出，弹出提示窗口

            print("exitCode:",exitCode)
            if error_string:
                if time.time() - self.new_process_start_time <= 3:
                    QMessageBox.information(self.parentWidget(), "exitCode: " + str(exitCode), error_string)

    @Slot(str)
    def new_slot_record_game_id(self,game_id,):
        the_variables.current_id = game_id

    # 取消搜索
    def new_func_cancel_search(self):
        self.new_func_clear_search_record()

        table = self.currentWidget()
        table.model().new_func_cancel_search()
    
    # 目录切换，需更新游戏列表
    def new_func_show_by_index(self,id_1,id_2,):
        # 记录 
        the_variables.index_id_1 = id_1
        the_variables.index_id_2 = id_2

        self.new_func_clear_search_record()

        current_table = self.currentWidget()
        current_table.model().new_func_show_by_index(id_1,id_2)

    # 搜索
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
            
            self.new_flag_search = True
            self.new_search_content= search_string,use_re,ignore_case,search_columns

            current_table = self.currentWidget()
            current_table.model().new_func_show_search_result(search_string,use_re=use_re,ignore_case=ignore_case,search_columns=search_columns)

    def new_func_clear_search_record(self):
        self.new_flag_search = False
        self.new_search_content = None

    #############
    # reload
    @Slot()
    def new_func_reload_gamelist(self):
        # 数据变化，更新 重载列表
        # 比如 选择 过滤项目后

        # 搜索状态
        finished = False
        if self.new_flag_search:
            if self.new_search_content is not None:
                if len(self.new_search_content) == 4:
                    self.new_func_for_search(*self.new_search_content)
                    finished = True
            else:
                #QMessageBox.warning(self,"warning","搜索内容可能出错")
                pass
            return

        # 其它
        if not finished:
            id_1 = the_variables.index_id_1
            id_2 = the_variables.index_id_2
            self.new_func_show_by_index(id_1,id_2)

    #
    # 显示 mame  命令行 结果
    def new_func_show_mame_command_line_result(self,command_list=None):
        print()
        print("show mame command line result")

        if command_list is None:
            command_list = []

        if not command_list:
            return

        settings = self.parent().new_settings

        mame_path = settings.value("mame/path") 
        mame_working_directory = settings.value("mame/working_directory") 
        mame_path, mame_working_directory = misc_funcs.get_abspath_for_mame_and_working_directory(mame_path, mame_working_directory)

        print(mame_path)
        print(mame_working_directory)
        print(command_list)

        self.new_process_for_mame_commmandlist_reuslt = QProcess(self)
        if mame_working_directory:
            if os.path.isdir(mame_working_directory):
               self.new_process_for_mame_commmandlist_reuslt.setWorkingDirectory(mame_working_directory)
        
        self.new_buffer_to_hold_mame_path_info = io.BytesIO()

        self.new_process_for_mame_commmandlist_reuslt.setProcessChannelMode(QProcess.MergedChannels)

        self.new_process_for_mame_commmandlist_reuslt.readyReadStandardOutput.connect(lambda: self.new_buffer_to_hold_mame_path_info.write(self.new_process_for_mame_commmandlist_reuslt.readAllStandardOutput().data()))
        
        self.new_process_for_mame_commmandlist_reuslt.finished.connect(self.new_func_show_mame_command_line_result_step_2)
        self.new_process_for_mame_commmandlist_reuslt.finished.connect(self.new_process_for_mame_commmandlist_reuslt.deleteLater)
        self.new_process_for_mame_commmandlist_reuslt.start(mame_path, command_list)
        self.new_process_for_mame_commmandlist_reuslt.waitForFinished()

    def new_func_show_mame_command_line_result_step_2(self,):
        
        try:
            self.new_dialog_for_show_command_line_result_of_mame
        except:
            self.new_dialog_for_show_command_line_result_of_mame = ui_small_windows.Dialog_for_show_command_line_result_of_mame(self)

        self.new_buffer_to_hold_mame_path_info.seek(0)
        data = self.new_buffer_to_hold_mame_path_info.read()
        reusult = data.decode("utf_8_sig",errors='backslashreplace')
        #print(type(reusult))
        #print(reusult)

        self.new_dialog_for_show_command_line_result_of_mame.new_func_set_text(reusult)
        self.new_dialog_for_show_command_line_result_of_mame.exec() 

    #
    # 显示  BIOS 选择器
    def new_func_mame_show_bios_selector(self,game_id,):

        command_list = []
        command_list.append("-listxml")
        command_list.append(game_id)

        settings = self.parent().new_settings

        mame_path = settings.value("mame/path") 
        mame_working_directory = settings.value("mame/working_directory") 
        mame_path, mame_working_directory = misc_funcs.get_abspath_for_mame_and_working_directory(mame_path, mame_working_directory)

        bios_list = self.new_func_get_bios_result(game_id,mame_path,mame_working_directory)

        try:
            self.new_dialog_for_show_bios_selector
        except:
            self.new_dialog_for_show_bios_selector = ui_small_windows.Dialog_for_show_bios_selector(self)
        self.new_dialog_for_show_bios_selector.new_func_set_values(game_id,bios_list)
        self.new_dialog_for_show_bios_selector.exec()
    # 得到 命令行 BIOS 查询结果
    # bios_name,bios_description
    def new_func_get_bios_result(self,game_id,executable_path,cwd):
        # 返回 [[bios_name,bios_description],[bios_name_2,bios_description_2],...]

        command_list = []
        command_list.append("-listxml")
        command_list.append(game_id)

        print(executable_path)
        print(cwd)
        print(command_list)

        self.new_process_for_bios = QProcess(self)
        if cwd:
            if os.path.isdir(cwd):
               self.new_process_for_bios.setWorkingDirectory(cwd)
        
        data_buffer = io.BytesIO()
        self.new_process_for_bios.setProcessChannelMode(QProcess.ForwardedErrorChannel)
        self.new_process_for_bios.readyReadStandardOutput.connect(lambda: data_buffer.write(self.new_process_for_bios.readAllStandardOutput().data()))
        self.new_process_for_bios.start(executable_path, command_list)
        self.new_process_for_bios.waitForFinished()
        self.new_process_for_bios.deleteLater()

        data_buffer.seek(0)

        bios_list = []
        tree = xml.etree.ElementTree.parse(data_buffer)
        root = tree.getroot()
        #print(root)
        for child in root:
            if child.tag in ("machine" ,"game"):

                if( "name" in child.attrib ):
                    
                    game_name = child.attrib["name"].strip().lower()
                    
                    if game_name==game_id:
                        for grandchild in child:
                            if grandchild.tag=="biosset" :
                                temp=["",""]
                                if "name" in grandchild.attrib:
                                    bios_name = grandchild.attrib["name"]
                                    temp[0]=bios_name
                                if "description" in grandchild.attrib:
                                    bios_description = grandchild.attrib["description"]
                                    temp[1]=bios_description
                                if temp[0]:
                                    bios_list.append(temp)
                        break
        
        return bios_list

    #
    # 显示  运行方式 选择器
    def new_func_mame_show_script_selector(self,game_id,):
        try:
            self.new_dialog_for_show_script_selector
        except:
            self.new_dialog_for_show_script_selector = ui_small_windows.Dialog_for_show_script_selector(self)
        self.new_dialog_for_show_script_selector.new_func_set_values(game_id)
        self.new_dialog_for_show_script_selector.exec()    

    # 显示 可编辑目录 选择器
    def new_func_show_editable_index_selector(self,game_id_s,add_mode=True): # 单个 game_id ，或多个 game_id 可迭代对象
        if not game_id_s:
            return
        
        try:
            self.new_dialog_for_show_editable_index_selector
        except:
            self.new_dialog_for_show_editable_index_selector = ui_index.Dialog_for_index_chooser(self)
        
        self.new_dialog_for_show_editable_index_selector.new_func_set_values(game_id_s,add_mode)

        if self.new_dialog_for_show_editable_index_selector.exec():
            index_id_1,index_id_2 = self.new_dialog_for_show_editable_index_selector.new_func_get_index_id()
            if (index_id_1 == the_variables.index_id_1) and (index_id_2 == the_variables.index_id_2):
                self.new_func_reload_gamelist()

    # 参数运行
    def get_script_content(self,script_file_path,game_id,mame_exe,mame_working_directory,hide=True):
        # return 
        #   cwd,command_list
        
        cwd = "" # 默认值
        command_list = [] # 默认值

        # game_id 为 machine
        machine      = game_id
        
        the_file   = script_file_path
        
        ##############
        
        flag_use_mame = False # 如果用了 mame ，cwd 需要考虑原有值
        
        # 自定义部分不要包含空字符，方便后面处理
        #   用户定义部分，中间，可以含空字符，末尾空字符去掉
        #
        # %mame% ，不管内容，替换为 mame_exe
        # %machine% ，不管内容，替换为 machine
        #
        # command 普通指令
        #
        # %cwd% ，换到内容，如果有效，替换为 cwd
        
        # 正则


        # 以空字符分隔

        # 内容 1
        #   仅一段
        str_1 = r'^([^\s]+)$'
        p=re.compile(str_1,)
        
        # 内容2
        #   两段
        str_2 = r'^([^\s]+)\s*([^\s].*)$'
        p2=re.compile(str_2,)

        with open(the_file,mode="rt",encoding="utf_8_sig") as f:
            for line in f :
                line = line.strip()

                # 注释
                if line.startswith("#") : 
                    continue
                
                # 内容行 1 ，仅一段
                m=p.search( line )
                if m:
                    if m.group(1)   == r"%mame%" :
                        command_list.append(mame_exe)
                        flag_use_mame = True
                    elif m.group(1) == r"%machine%" :
                        command_list.append(machine)
                    elif m.group(1) == r"%unibios_last%" : # 使用默认 模拟器
                        uni_bios = self.get_uni_bios_last(machine,mame_path=mame_exe,cwd=cwd)
                        if uni_bios:
                            command_list.append("-bios")
                            command_list.append(uni_bios)
                    elif m.group(1) == r"%unibios_last_other%" :# 使用 其它 mame 模拟器
                        if command_list:
                            uni_bios = self.get_uni_bios_last(machine,mame_path=command_list[0],cwd=cwd)
                            if uni_bios:
                                command_list.append("-bios")
                                command_list.append(uni_bios)
                    continue

                # 内容行 2，两段
                m=p2.search( line )
                if m:
                    if   m.group(1) == "command" : 
                        command_list.append(m.group(2))
                    elif m.group(1) == r"%cwd%" : 
                        if os.path.isdir(m.group(2)):
                            cwd = m.group(2)
                        else:
                            print("error,cwd value not found :",m.group(2))

        # 如果用了 mame
        if flag_use_mame == True:
            if not cwd:
                cwd = mame_working_directory

        if flag_use_mame :
            return cwd,command_list
        else:
            if command_list:
                print("command_list o :",command_list)
                exe_path = command_list[0]

                exe_path, cwd = misc_funcs.get_abspath_for_exe_path_and_working_directory(exe_path,cwd)

                command_list[0]=exe_path
            return cwd,command_list
    def get_uni_bios_last(self,machine,mame_path,cwd,):

        # bios_name,bios_description
        bios_list = self.new_func_get_bios_result(machine,mame_path,cwd)
        if not bios_list:
            return ""
        
        uni_bios_list = []
        for bios_name,bios_description in bios_list:
            if "uni" in bios_name.lower():
                if "universe" in bios_description.lower():
                    uni_bios_list.append(bios_name)

        # 倒序排列
        uni_bios_list.sort(reverse=True)

        #for x in uni_bios_list:
        #    print(x)

        if not uni_bios_list:
            return ""
        
        the_bios = uni_bios_list[0]
        for n in range(len(uni_bios_list)):
            the_bios = uni_bios_list[n]
            if not the_bios.endswith("o"): # o 表示 older , 应该不是最新的
                break
        
        return the_bios


    # menu 字体等， 游戏列表 2 level tree like ，设置打开关闭字符串
    @Slot()
    def new_func_set_open_colse_string_for_tableview_2_level_tree_like(self):
        try:
            self.new_dialog_for_set_open_colse_string_for_tableview_2_level_tree_like
        except:
            self.new_dialog_for_set_open_colse_string_for_tableview_2_level_tree_like=ui_small_windows.Dialog_for_set_open_colse_string_for_tableview_2_level_tree_like(self.parentWidget().new_settings)

        self.new_dialog_for_set_open_colse_string_for_tableview_2_level_tree_like.new_func_set_values()

        if self.new_dialog_for_set_open_colse_string_for_tableview_2_level_tree_like.exec_() :
            current_table = self.currentWidget()

            if current_table is self.new_ui_gamelist_tableview_2_level_tree_like:
                self.new_ui_gamelist_tableview_2_level_tree_like.model().new_func_vertical_header_changed()


