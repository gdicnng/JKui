import io

from qtpy.QtWidgets import *
from qtpy.QtGui import *
from qtpy.QtCore import *

import ui_gamelist_tableview
import ui_models
import ui_gamelist_treeview
import misc_funcs
import the_variables



class TheCentralWidget(QStackedWidget):
    new_signal_for_id_change=Signal(str,)#id

    def __init__(self,parent=None):
        super().__init__(parent)

        self.new_signal_for_id_change.connect(self.new_slot_record_game_id)

        ####
        # tableview
        self.new_ui_gamelist_tableview = ui_gamelist_tableview.My_Table(self)
        self.addWidget(self.new_ui_gamelist_tableview)

        # 排序
        self.new_ui_gamelist_tableview.setSortingEnabled(True)
        self.new_ui_gamelist_tableview.sortByColumn(-1, Qt.AscendingOrder)

        ## QSortFilterProxyModel ，这东西太卡了,不能用




        ####
        # tableview fake 2 level

        ####
        # tree view
        self.new_ui_gamelist_treeview = ui_gamelist_treeview.My_Tree_View(self)
        self.addWidget(self.new_ui_gamelist_treeview)

   

    def new_func_show_table(self,the_table):
        old_table = self.currentWidget()

        if old_table is the_table:
            return

        old_table.model().beginResetModel()
        old_table.model().new_func_clear_all_data()
        old_table.model().endResetModel()
        
        self.setCurrentWidget(the_table)

        id_1 = the_variables.index_id_1 
        id_2 = the_variables.index_id_2 
        if id_1 :
            the_table.model().new_func_show_by_index(id_1,id_2)

    def new_func_show_tableview(self,):
        self.new_func_show_table(self.new_ui_gamelist_tableview)

    def new_func_show_treeview(self,):
        self.new_func_show_table(self.new_ui_gamelist_treeview)

    def new_func_refresh(self,):
        widget = self.currentWidget()
        if hasattr(widget,"model"):
            #widget.model().layoutChanged.emit() # ? 数据整体结构发生重大变化（如重置所有数据）
            widget.model().modelReset.emit() # ? 模型被完全重置
            print("refresh")
    
    def new_func_for_save_settings(self,):
        # 程序关闭时，掉用这个函数

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
                print(object_name,"save data",temp_text)




        # 保存置顶的表格
        current_widget = self.currentWidget()
        object_name = current_widget.objectName()
        temp_text = "current_table"
        settings.setValue(temp_text, object_name)

    def new_func_for_load_settings(self,):
        # 程序启动时，掉用这个函数
        # 初始化，之后，载入数据后，再用

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
                        print(widget.objectName(),"load data",temp_text,load_ok)
                except:
                    pass

                header.setSortIndicator(-1,Qt.AscendingOrder)
        
        # 加载置顶的表格
        the_object_name = settings.value("current_table")

        for widget in self.children():
            if  isinstance(widget,QTableView) or isinstance(widget,QTreeView):
                object_name = widget.objectName()
                if object_name == the_object_name:
                    self.setCurrentWidget(widget)
                    break

    def new_func_start_emulator(self,game_id,game_info=None,hide=True,keypress_event=None,):
        if not game_info : game_info = []
        print()
        print("start emulator",game_id)
        print("hide UI",hide)
        
        command_list=[]
        command_list.append(game_id)

        settings = self.parentWidget().new_settings
        mame_exe_path = settings.value("mame/path") 
        mame_working_directory = settings.value("mame/working_directory") 
        mame_exe_path, mame_working_directory = misc_funcs.get_mame_path_and_working_directory(mame_exe_path, mame_working_directory)        

        print("working directory : ",mame_working_directory)
        print("mame path         : ",mame_exe_path)
        print("command list      : ",command_list)

        if hide:
            self.parentWidget().hide()

            self.new_buffer_to_hold_error_data = io.BytesIO()
            self.new_process = QProcess()
            self.new_process.setWorkingDirectory(mame_working_directory)
            self.new_process.setProcessChannelMode(QProcess.ForwardedChannels)
            self.new_process.setProcessChannelMode(QProcess.ForwardedOutputChannel)
            self.new_process.readyReadStandardError.connect(lambda: self.new_buffer_to_hold_error_data.write(self.new_process.readAllStandardError().data()))
            self.new_process.finished.connect(self.parentWidget().show)
            self.new_process.finished.connect(self.new_slot_for_standard_error_data)
            self.new_process.start(mame_exe_path,command_list)

            #new_process.waitForFinished(-1)
        else:
            print("start detached")
            process = QProcess()
            process.setWorkingDirectory(mame_working_directory)
            process.setProgram(mame_exe_path)
            process.setArguments(command_list)
            process.setProcessChannelMode(QProcess.ForwardedChannels)
            process.startDetached()
    
    @Slot(int,QProcess.ExitStatus)
    def new_slot_for_standard_error_data(self,exitCode,exitStatus,):
        self.new_buffer_to_hold_error_data.seek(0)
        error_data = self.new_buffer_to_hold_error_data.read()

        print()
        print("standard error data :")
        print(error_data)

        if exitCode != 0:
            QMessageBox.warning(self.parentWidget(), "error", error_data.decode(encoding='utf-8', errors='backslashreplace'))

    @Slot(str)
    def new_slot_record_game_id(self,game_id,):
        the_variables.current_id = game_id



