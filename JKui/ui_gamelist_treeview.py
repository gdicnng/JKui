import functools

from qtpy.QtGui import *
from qtpy.QtWidgets import *
from qtpy.QtCore import *

import ui_models
import the_variables



class My_Tree_View(QTreeView):
    def __init__(self,*args,**kwargs ):
        super().__init__(*args,**kwargs)

        self.new_func_set_model()
        self.new_func_create_context_menu()

        self.new_table_type = "tree_view"
        self.setObjectName("tree_view")

        # 获取水平表头，并设置上下文菜单策略
        header = self.header()
        header.setContextMenuPolicy(Qt.ContextMenuPolicy.CustomContextMenu)
        header.customContextMenuRequested.connect(self.new_func_show_header_context_menu)


        self.setUniformRowHeights(True)

        # 进入编辑状态 方式
        self.setEditTriggers(QAbstractItemView.CurrentChanged)
       
        self.setSortingEnabled(True)

        # 水平滚动条，按像素滚动，
        #   而不是 按完整列 滚动
        self.setHorizontalScrollMode(QAbstractItemView.ScrollPerPixel)
        
        # 不换行
        self.setWordWrap(False)
        
        # 选择一行，
        self.setSelectionBehavior(QAbstractItemView.SelectRows)
        
        # 单选、多选
        self.setSelectionMode(QAbstractItemView.SingleSelection )

        self.header().setStretchLastSection(False)

        self.setVerticalScrollBarPolicy(Qt.ScrollBarAlwaysOn)
    
    def new_func_set_model(self,):
        self.setModel(ui_models.Model_for_tree_view(self))
        self.model().new_signal_time_for_choose_remember_game.connect(self.new_func_scrollto_to_last_game)


    def new_func_show_header_context_menu(self, pos):
        """在表头位置显示右键菜单"""
        menu = QMenu(self)
        header = self.header()
        
        # 遍历所有列
        for col in range(self.model().columnCount()):
            # 获取列名
            col_name = self.model().headerData(col, Qt.Orientation.Horizontal)
            # 创建可勾选的QAction
            action = QAction(col_name, self, checkable=True)
            # 根据当前列的可见性设置初始勾选状态
            action.setChecked(not header.isSectionHidden(col))
            # 为每个action绑定切换列可见性的槽函数
            action.toggled.connect(lambda checked, c=col: self.new_func_toggle_column_visibility(c, checked))
            menu.addAction(action)
        
        # 在鼠标位置显示菜单
        menu.exec(header.mapToGlobal(pos))

    def new_func_toggle_column_visibility(self, column, visible):
        """切换列的可见性"""
        if visible:
            self.showColumn(column)
        else:
            self.hideColumn(column)


    # 右键 菜单
    def new_func_create_context_menu(self,):
        self.new_context_menu = QMenu(self)
        
        action_run_game=QAction("运行游戏", self)
        action_run_game.triggered.connect(lambda: self.new_func_context_menu_run_game(True))
        self.new_context_menu.addAction(action_run_game)

        action_run_game_not_hide_ui=QAction("运行游戏，不隐藏UI窗口", self)
        action_run_game_not_hide_ui.triggered.connect(lambda: self.new_func_context_menu_run_game(False))
        self.new_context_menu.addAction(action_run_game_not_hide_ui)

        action_run_game_by_user_setting=QAction("自定义运行方式", self)
        action_run_game_by_user_setting.triggered.connect(self.new_func_context_menu_script_selector)
        self.new_context_menu.addAction(action_run_game_by_user_setting)

        action_bios_selector=QAction("BIOS选择(仅部分游戏有)", self)
        action_bios_selector.triggered.connect(self.new_func_context_menu_bios_selector)
        self.new_context_menu.addAction(action_bios_selector)

        self.new_context_menu.addSeparator()
        # ["-verifyroms",]
        action_verifyroms=QAction("-verifyroms,校验 roms", self)
        action_verifyroms.triggered.connect(lambda: self.new_func_context_menu_show_command_line_result( ["-verifyroms"] ,))
        self.new_context_menu.addAction(action_verifyroms)
        # ["-verifysamples",]
        action_verifysamples=QAction("-verifysamples,校验 samples", self)
        action_verifysamples.triggered.connect(lambda: self.new_func_context_menu_show_command_line_result( ["-verifysamples"] ,))
        self.new_context_menu.addAction(action_verifysamples)
        # ["-listroms",]
        action_listroms=QAction("-listroms,列出 roms (信息过于简略)", self)
        action_listroms.triggered.connect(lambda: self.new_func_context_menu_show_command_line_result( ["-listroms"] ,))
        self.new_context_menu.addAction(action_listroms)
        # ["-listxml",]
        action_listxml=QAction("-listxml,显示 roms 信息 （含大量其它信息）", self)
        action_listxml.triggered.connect(lambda: self.new_func_context_menu_show_command_line_result( ["-listxml"] ,))
        self.new_context_menu.addAction(action_listxml)
        # ["-listxml","-nodtd"]
        action_listxml_nodtd=QAction("-listxml -nodtd,同上，不包含 DTD 文件头", self)
        action_listxml_nodtd.triggered.connect(lambda: self.new_func_context_menu_show_command_line_result( ["-listxml","-nodtd"] ,))
        self.new_context_menu.addAction(action_listxml_nodtd)
        # 其它指令
        menu_other_command_line = self.new_context_menu.addMenu("其他指令")
        temp_list = [
            ["-listbios"],
            ["-listmedia"],
            ["-listcrc"],
            ["-listsamples"],
            ["-listdevices"],
            ["-listsource"],
            ["-listclones"],
            ["-listbrothers"],
            ["-listslots"],
        ]
        for command_list in temp_list:
            action = QAction(command_list[0], self)
            action.triggered.connect(functools.partial(self.new_func_context_menu_show_command_line_result, command_list))
            menu_other_command_line.addAction(action)

        self.new_context_menu.addSeparator()
        ## 编辑目录
        # 单选，从本列表删除
        self.new_action_delete_selected_item_from_current_table=QAction("单选，从本列表删除", self)
        self.new_action_delete_selected_item_from_current_table.triggered.connect(self.new_func_context_menu_delete_current_item)
        self.new_context_menu.addAction(self.new_action_delete_selected_item_from_current_table)
        # 单选，添加到其它目录
        self.new_action_add_current_item_to_index=QAction("单选，添加到其它目录", self)
        self.new_action_add_current_item_to_index.triggered.connect(self.new_func_context_menu_add_current_item_to_index)
        self.new_context_menu.addAction(self.new_action_add_current_item_to_index)
        ## 多选（勾选），从本列表删除
        #self.new_action_delete_selected_items_from_current_table=QAction("多选（勾选），从本列表删除", self)
        #self.new_action_delete_selected_items_from_current_table.triggered.connect(self.new_func_context_menu_delete_selected_items_from_current_table)
        #self.new_context_menu.addAction(self.new_action_delete_selected_items_from_current_table)
        ## 多选（勾选），从选中列表删除
        #self.new_action_delete_selected_items_from_index=QAction("多选（勾选），从选中列表删除", self)
        #self.new_action_delete_selected_items_from_index.triggered.connect(self.new_func_context_menu_delete_selected_items_from_index)
        #self.new_context_menu.addAction(self.new_action_delete_selected_items_from_index)
        ## 多选（勾选），添加到其它目录
        #self.new_action_add_selected_items_to_index=QAction("多选（勾选），添加到其它目录", self)
        #self.new_action_add_selected_items_to_index.triggered.connect(self.new_func_context_menu_add_selected_items_to_index)
        #self.new_context_menu.addAction(self.new_action_add_selected_items_to_index)


        self.new_context_menu.addSeparator()
        ############
        # 显示选中行的信息
        self.new_action_show_cell_data=QAction(" - ", self)
        self.new_action_show_cell_data.triggered.connect(lambda: self.new_func_context_menu_click_to_copy_action_text(self.new_action_show_cell_data))
        self.new_context_menu.addAction(self.new_action_show_cell_data)

        self.new_context_menu.addSeparator()
  
    def contextMenuEvent(self,e):
        index=self.indexAt(e.pos())
        if index.isValid():
            game_id, game_info = self.model().new_func_get_id_and_item_by_index(index)
            print("contextMenuEvent",index.row(),game_id)

            cell_data = self.model().data(index, Qt.DisplayRole)
            self.new_action_show_cell_data.setText(cell_data)

            # 目录编辑，根据需要禁用、启用
            self.new_action_delete_selected_item_from_current_table.setEnabled(False)
            self.new_action_add_current_item_to_index.setEnabled(False)
            #self.new_action_delete_selected_items_from_index.setEnabled(False)
            #self.new_action_add_selected_items_to_index.setEnabled(False)
            #self.new_action_delete_selected_items_from_current_table.setEnabled(False)
            #
            if ui_models.index_edit_mode:
                if ui_models.editable_index_files:
                    # 有可编辑目录
                    self.new_action_add_current_item_to_index.setEnabled(True)
                    #if ui_models.the_selected_items:
                    #    self.new_action_add_selected_items_to_index.setEnabled(True)
                    #    self.new_action_delete_selected_items_from_index.setEnabled(True)
                    
                    # 当前表格 在 可编辑目录 中
                    id_1 = self.model().new_remember_index_id_1
                    if id_1 in ui_models.editable_index_files:
                        print(id_1)
                        self.new_action_delete_selected_item_from_current_table.setEnabled(True)
                        #if ui_models.the_selected_items:
                        #    self.new_action_delete_selected_items_from_current_table.setEnabled(True)



            self.new_context_menu.exec(e.globalPos())
    
    def selectionChanged(self, selected, deselected):
        if selected.isEmpty():
            # ctrl + 点击，会取消选中。
            # 这，对于单选模式来说，挺麻烦，重新选上
            if not deselected.isEmpty():
                old_index = deselected.indexes()[0]
                
                index = self.currentIndex()
                if index.isValid():
                    old_id, old_info = self.model().new_func_get_id_and_item_by_index(old_index)
                    game_id, game_info = self.model().new_func_get_id_and_item_by_index(index)
                    if game_id == old_id:
                        #self.parent().new_signal_for_id_change.emit(game_id)
                        self.setCurrentIndex(index)
                        #print("row",index.row(),"column",index.column())
                         
        else:
            #print("selected: ", selected.indexes()[0].row())
            game_id, game_info= self.model().new_func_get_id_and_item_by_index(selected.indexes()[0])
            print("selectionChanged",game_id)
            self.parent().new_signal_for_id_change.emit(game_id)
        super().selectionChanged(selected, deselected)

    def mouseDoubleClickEvent(self, event):
        index=self.indexAt(event.position().toPoint())

        super().mouseDoubleClickEvent(event)

        if index.isValid():
            game_id, game_info = self.model().new_func_get_id_and_item_by_index(index)        

            if event.modifiers() & Qt.ControlModifier:
                hide = False
            else:
                hide = True

            print()
            print("doubleClicked: ", game_id)
            self.parent().new_func_start_emulator(game_id,game_info=game_info,hide=hide)


    def keyPressEvent(self, event):
        #
        #if event.key() == Qt.Key_A:
        #    if event.modifiers() == Qt.ControlModifier:
        #        # 全选
        #        self.model().new_func_select_all_items()
        #    elif event.modifiers() == Qt.AltModifier:
        #        # 全不选
        #        self.model().new_func_deselect_all_items()
        #elif event.key() == Qt.Key_X:
        #    if event.modifiers() == Qt.ControlModifier:
        #        # 反选
        #        self.model().new_func_select_reverse()

        # ctrl + B
        if event.key() == Qt.Key_B:
            if event.modifiers() == Qt.ControlModifier:
                self.new_func_context_menu_bios_selector()

        # return
        elif event.key() == Qt.Key_Return:
            current_index = self.currentIndex()
            if current_index.isValid():
                if self.selectionModel().isSelected(current_index):

                    # 编辑模式下，翻译列，正在编辑时，回车键，不处理
                    if ui_models.gamelist_editable_mode:
                        if current_index.column() == ui_models.translation_column_index:
                            if self.state() == QAbstractItemView.EditingState:
                                # 正在编辑，不处理回车键
                                super().keyPressEvent(event)
                                return

                    game_id, game_info = self.model().new_func_get_id_and_item_by_index(current_index)
                    
                    if event.modifiers() & Qt.ControlModifier:
                        print("Ctrl + Return")
                        self.parent().new_func_start_emulator(game_id,game_info=game_info,hide=False)
                    else:
                        print("Return")
                        self.parent().new_func_start_emulator(game_id,game_info=game_info,hide=True)
                

        # F1
        elif event.key() == Qt.Key_F1:
            current_index = self.currentIndex()
            if current_index.isValid():
                if self.selectionModel().isSelected(current_index):
                    game_id, game_info = self.model().new_func_get_id_and_item_by_index(current_index)
                    self.parent().new_func_mame_show_script_selector(game_id)
        # F2-F12
        # NoModifier
        elif event.key() in { 
                            Qt.Key_F2,Qt.Key_F3,Qt.Key_F4,Qt.Key_F5,
                            Qt.Key_F6,Qt.Key_F7,Qt.Key_F8,Qt.Key_F9,Qt.Key_F10,
                            Qt.Key_F11,Qt.Key_F12,
                           }:
            # NoModifier
            if event.modifiers() == Qt.NoModifier:
                hide = True

                print("script")
                current_index = self.currentIndex()
                if current_index.isValid():
                    if self.selectionModel().isSelected(current_index):
                        #print(event.key(),event.text())
                        game_id ,game_info = self.model().new_func_get_id_and_item_by_index(current_index)
                        self.parentWidget().new_func_start_emulator(game_id,game_info,hide = hide,keypress_event=event,)
        
        # 2-9,0 ,需要 Ctrl or Alt
        elif event.key() in { 
                            Qt.Key_2,Qt.Key_3,Qt.Key_4,Qt.Key_5,
                            Qt.Key_6,Qt.Key_7,Qt.Key_8,Qt.Key_9,Qt.Key_0,
                           }:
            # Ctrl or Alt
            if (event.modifiers() == Qt.ControlModifier) or (event.modifiers() == Qt.AltModifier):
                
                print(event.key(),event.text())
                
                current_index = self.currentIndex()
                if current_index.isValid():
                    if self.selectionModel().isSelected(current_index):
                        #print(event.key(),event.text())
                        game_id ,game_info = self.model().new_func_get_id_and_item_by_index(current_index)
                        self.parentWidget().new_func_start_emulator(game_id,game_info,keypress_event=event,)
                    else:
                        print(current_index.row(),current_index.column(),current_index)
                        print("no selected")
                else:
                    print("no current index")

        ###
        super().keyPressEvent(event)

    def new_func_scrollto_row_by_game_id(self,game_id):
        if not game_id:
            return

        value=self.horizontalScrollBar().value() # 滚动条 位置 记录
        index = self.model().new_func_get_index_by_game_id(game_id)

        if not index: # 可能返回 None
            return
        
        if index.isValid():
            self.scrollTo(index,hint=QAbstractItemView.PositionAtCenter)
            self.setCurrentIndex(index)
            self.horizontalScrollBar().setValue(value) # 滚动条 位置 还原

    @Slot()
    def new_func_scrollto_to_last_game(self,):
        if not the_variables.auto_select_last_game:
            return
        if not the_variables.current_id:
            return        
        self.new_func_scrollto_row_by_game_id(the_variables.current_id)

    ###########
    # 右键菜单

    def new_func_context_menu_run_game(self,hide=True):
        game_id, game_info = self.model().new_func_get_id_and_item_by_index(self.currentIndex())
        if not game_id:
            return
        #print(hide)
        self.parent().new_func_start_emulator(game_id,game_info=game_info,hide=hide)

    def new_func_context_menu_show_command_line_result(self,command_list=None):
        if command_list is None:
            command_list = []
        if not command_list:
            return
        game_id, game_info = self.model().new_func_get_id_and_item_by_index(self.currentIndex())
        if not game_id:
            return
        command_list_2 = []
        command_list_2.append(game_id)
        command_list_2.extend(command_list)
        self.parentWidget().new_func_show_mame_command_line_result( command_list_2 ,)

    def new_func_context_menu_bios_selector(self,):
        current_index = self.currentIndex()
        
        if not current_index.isValid():
            return

        selected_index_list = self.selectionModel().selectedIndexes()
        if current_index in selected_index_list:
        
            game_id, game_info = self.model().new_func_get_id_and_item_by_index(current_index)
            
            if not game_id:
                return
            
            print(game_id)
            self.parentWidget().new_func_mame_show_bios_selector( game_id,)

    def new_func_context_menu_script_selector(self,):
        current_index = self.currentIndex()
        
        if not current_index.isValid():
            return
        
        game_id, game_info = self.model().new_func_get_id_and_item_by_index(current_index)
        
        if not game_id:
            return
        
        self.parent().new_func_mame_show_script_selector(game_id)

    def new_func_context_menu_click_to_copy_action_text(self,action,):
        text = action.text()
        clipboard = QGuiApplication.clipboard()
        clipboard.setText(text)


    def new_func_context_menu_delete_current_item(self,):
        
        if not ui_models.index_edit_mode:
            return

        # 编辑 本身，检查本身 是否可编辑
        if not the_variables.index_id_1 in ui_models.editable_index_files:
            return

        # 单选模式，删除当前项
        current_index = self.currentIndex()
        selected_index_list = self.selectionModel().selectedIndexes()
        if current_index in selected_index_list:
            self.model().new_func_remove_one_item_by_index(current_index)

    def new_func_context_menu_add_current_item_to_index(self,):
        if not ui_models.index_edit_mode:
            return

        # 单选模式，添加当前项到其他索引
        current_index = self.currentIndex()
        selected_index_list = self.selectionModel().selectedIndexes()
        if current_index in selected_index_list:
            game_id, game_info = self.model().new_func_get_id_and_item_by_index(current_index)
            self.parentWidget().new_func_show_editable_index_selector(game_id,add_mode=True)
