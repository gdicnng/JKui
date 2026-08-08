
from qtpy.QtGui import *
from qtpy.QtWidgets import *
from qtpy.QtCore import *

import ui_models
import the_variables


class My_Table(QTableView):
    def __init__(self,*args,**kwargs ):
        super().__init__(*args,**kwargs)

        self.new_func()
        self.new_func_create_context_menu()
        self.new_mouse_move_record = -1  
            # row number ,记录，鼠标点击并移动
            # 鼠标点击，记录行号
            # 鼠标移动，记录行号
            # 鼠标释放，重置为 -1

        # 获取水平表头，并设置上下文菜单策略
        header = self.horizontalHeader()
        header.setContextMenuPolicy(Qt.ContextMenuPolicy.CustomContextMenu)
        header.customContextMenuRequested.connect(self.new_func_show_header_context_menu)

        # 进入编辑状态 方式
        self.setEditTriggers(QAbstractItemView.CurrentChanged)

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
        self.horizontalHeader().setSectionsClickable(True)
        #   拖动
        self.horizontalHeader().setSectionsMovable(True)
        #   第一列，禁止拖动
        self.horizontalHeader().setFirstSectionMovable(False)
        #   关闭列标题高亮，阻止选中时字体加粗
        #   没有效果 ？什么时候又有效果了？
        self.horizontalHeader().setHighlightSections(False)
        #   列标题，上侧，最后一列，不拉伸
        self.horizontalHeader().setStretchLastSection(False)

        # 行标题，左侧
        #   禁止用户变化行高度
        self.verticalHeader().setSectionResizeMode(QHeaderView.Fixed) ########
        #   不显示，行标题
        self.verticalHeader().setVisible(False)
        #   行高度
        #self.verticalHeader().setDefaultSectionSize(80)
        #self.verticalHeader().resetDefaultSectionSize()
        self.verticalHeader().setHighlightSections(False)
        #
        self.verticalHeader().setObjectName("verticalHeaderForTableView")
        
        
        # 不显示 单元格
        self.setShowGrid(False)

        self.setTabKeyNavigation(False)

        self.setSortingEnabled(True)

        # 可选：启用鼠标跟踪，让鼠标移出时能立即隐藏 ToolTip（但 QToolTip 本身会在移出时隐藏）
        # self.setMouseTracking(True)
    
        self.setVerticalScrollBarPolicy(Qt.ScrollBarAlwaysOn)

    def new_func(self,):
        self.new_table_type = "table_view_1_level"
        self.setObjectName("table_view_1_level")
        self.setModel(ui_models.Model_for_table_view(self))
        self.model().new_signal_time_for_choose_remember_game.connect(self.new_func_scrollto_to_last_game)

    def new_func_show_header_context_menu(self, pos):
        """在表头位置显示右键菜单"""
        menu = QMenu(self)
        header = self.horizontalHeader()
        
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
            action.triggered.connect(lambda cheched,the_command_list = command_list:self.new_func_context_menu_show_command_line_result(the_command_list) )
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
        # 多选（勾选），从本列表删除
        self.new_action_delete_selected_items_from_current_table=QAction("多选（勾选），从本列表删除", self)
        self.new_action_delete_selected_items_from_current_table.triggered.connect(self.new_func_context_menu_delete_selected_items_from_current_table)
        self.new_context_menu.addAction(self.new_action_delete_selected_items_from_current_table)
        # 多选（勾选），从选中列表删除
        self.new_action_delete_selected_items_from_index=QAction("多选（勾选），从其它列表删除", self)
        self.new_action_delete_selected_items_from_index.triggered.connect(self.new_func_context_menu_delete_selected_items_from_index)
        self.new_context_menu.addAction(self.new_action_delete_selected_items_from_index)
        # 多选（勾选），添加到其它目录
        self.new_action_add_selected_items_to_index=QAction("多选（勾选），添加到其它目录", self)
        self.new_action_add_selected_items_to_index.triggered.connect(self.new_func_context_menu_add_selected_items_to_index)
        self.new_context_menu.addAction(self.new_action_add_selected_items_to_index)
        # 多选（勾选），选择同类项（清除原有选项内容，选择本列表中此列值相同的项目）
        self.new_action_select_same_type_items=QAction("多选（勾选），选择同类项（清除原有选项内容，选择本列表中此列值相同的项目）", self)
        self.new_action_select_same_type_items.triggered.connect(self.new_func_context_menu_select_same_type_items)
        self.new_context_menu.addAction(self.new_action_select_same_type_items)
        # 其它
        self.new_menu_current_gamelist_other_options = self.new_context_menu.addMenu("当前列表，其他")
        # 当前列表，为所有克隆版本，补全其主版本
        action_add_parent_game=QAction("当前列表，为所有克隆版本，补全其主版本", self)
        action_add_parent_game.triggered.connect(self.model().new_func_add_parent_game)
        self.new_menu_current_gamelist_other_options.addAction(action_add_parent_game)
        # 当前列表，为所有主版本，补全其克隆版本
        action_add_clone_game=QAction("当前列表，为所有主版本，补全其克隆版本", self)
        action_add_clone_game.triggered.connect(self.model().new_func_add_colne_game)
        self.new_menu_current_gamelist_other_options.addAction(action_add_clone_game)
        # 当前列表，删除所有主版本
        action_delete_parent_game=QAction("当前列表，删除所有主版本", self)
        action_delete_parent_game.triggered.connect(self.model().new_func_delete_parent_game)
        self.new_menu_current_gamelist_other_options.addAction(action_delete_parent_game)
        # 当前列表，删除所有克隆版本
        action_delete_clone_game=QAction("当前列表，删除所有克隆版本", self)
        action_delete_clone_game.triggered.connect(self.model().new_func_delete_clone_game)
        self.new_menu_current_gamelist_other_options.addAction(action_delete_clone_game)

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
            self.new_action_delete_selected_items_from_index.setEnabled(False)
            self.new_action_add_selected_items_to_index.setEnabled(False)
            self.new_action_delete_selected_items_from_current_table.setEnabled(False)
            self.new_action_select_same_type_items.setEnabled(False)
            #
            self.new_menu_current_gamelist_other_options.setEnabled(False)
            #
            #
            if ui_models.multi_selection_mode:
                self.new_action_select_same_type_items.setEnabled(True)
            #
            if ui_models.index_edit_mode:
                if ui_models.editable_index_files:
                    # 有可编辑目录
                    self.new_action_add_current_item_to_index.setEnabled(True)

                    if ui_models.multi_selection_mode and ui_models.the_selected_items:
                        self.new_action_add_selected_items_to_index.setEnabled(True)
                        self.new_action_delete_selected_items_from_index.setEnabled(True)

                    # 当前表格 在 可编辑目录 中
                    id_1 = self.model().new_remember_index_id_1
                    if id_1 in ui_models.editable_index_files:
                        print(id_1)
                        self.new_action_delete_selected_item_from_current_table.setEnabled(True)

                        self.new_menu_current_gamelist_other_options.setEnabled(True)

                        if ui_models.multi_selection_mode and ui_models.the_selected_items:
                            self.new_action_delete_selected_items_from_current_table.setEnabled(True)

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
            row = selected.indexes()[0].row()
            print("selectionChanged",row,game_id)
            self.parent().new_signal_for_id_change.emit(game_id)
        super().selectionChanged(selected, deselected)
    
    def mousePressEvent(self, event):
        if ui_models.multi_selection_mode:

            if event.buttons() == Qt.LeftButton:

                index=self.indexAt(event.pos()) 
                # ????
                #   (deprecated (6.0)) QPoint 	pos() const
                
                if index.isValid():
                    row=index.row()
                    self.new_mouse_move_record = row

                    # Ctrl
                    if event.modifiers()  == Qt.ControlModifier:
                        #print("ctrl")
                        game_id = self.model().new_func_get_item_id_by_index(index)
                        if game_id in ui_models.the_selected_items:
                            ui_models.the_selected_items.remove(game_id)
                        else:
                            ui_models.the_selected_items.add(game_id)
                        the_index = self.model().index(row,0)
                        self.dataChanged(the_index,the_index, [Qt.CheckStateRole])
                    # Shift
                    elif event.modifiers()  == Qt.ShiftModifier :
                        old_index_list = self.selectedIndexes()
                        if old_index_list:
                            old_index = old_index_list[0]

                            if old_index.isValid():
                                
                                new_index=self.indexAt(event.pos())
                                
                                if new_index.isValid():
                                    print( old_index.row(),old_index.column() )
                                    print( new_index.row(),new_index.column() )
                                    
                                    old_row=old_index.row()
                                    new_row=new_index.row()
                                    
                                    if old_row != new_row:
                                        small_row,big_row = old_row,new_row
                                        if old_row > new_row:
                                            small_row,big_row= new_row,old_row
                                        
                                        for item_row in range(small_row,big_row+1):
                                            game_id = self.model().new_func_get_item_id_by_row(item_row)
                                            if game_id:
                                                if game_id in ui_models.the_selected_items:
                                                    ui_models.the_selected_items.remove(game_id)
                                                else:
                                                    ui_models.the_selected_items.add(game_id)
                                        
                                        index_1 = self.model().index(small_row,0)
                                        index_2 = self.model().index(big_row,0)
                                        self.dataChanged( index_1, index_2, [Qt.CheckStateRole])

                else:
                    self.new_mouse_move_record=-1

        super().mousePressEvent(event)

    def mouseMoveEvent(self, event):
        if ui_models.multi_selection_mode:

            if event.buttons() == Qt.LeftButton:
                
                if event.modifiers() == Qt.ControlModifier:
                    #print("ctrl")
                    
                    
                    index=self.indexAt(event.pos()) 
                    
                    if index.isValid():
                        row=index.row()
                        
                        if row != self.new_mouse_move_record:
                            self.new_mouse_move_record = row

                            game_id = self.model().new_func_get_item_id_by_index(index)
                            if game_id:
                                if game_id in ui_models.the_selected_items:
                                    ui_models.the_selected_items.remove(game_id)
                                else:
                                    ui_models.the_selected_items.add(game_id)
                                the_index = self.model().index(row,0)
                                self.dataChanged(the_index,the_index, [Qt.CheckStateRole])
                    else:
                        self.new_mouse_move_record=-1
        
        super().mouseMoveEvent(event)

    def mouseReleaseEvent(self, event):
        if event.button() == Qt.LeftButton:
            if self.new_mouse_move_record != -1:
                self.new_mouse_move_record = -1
        
        super().mouseReleaseEvent(event)

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
        
        # home 
        if event.key() == Qt.Key_Home:
            self.scrollToTop()
            return
        
        # end
        elif event.key() == Qt.Key_End:
            self.scrollToBottom()
            return

        elif event.key() == Qt.Key_A:
            if event.modifiers() == Qt.ControlModifier:
                # 全选
                self.model().new_func_select_all_items()
            elif event.modifiers() == Qt.AltModifier:
                # 全不选
                self.model().new_func_deselect_all_items()
        elif event.key() == Qt.Key_X:
            if event.modifiers() == Qt.ControlModifier:
                # 反选
                self.model().new_func_select_reverse()

        # ctrl + B
        elif event.key() == Qt.Key_B:
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

        value=self.horizontalScrollBar().value()
        
        index = self.model().new_func_get_index_by_game_id(game_id,)

        if not index: # 可能返回 None
            return
        
        if index.isValid():
            self.scrollTo(index,QAbstractItemView.PositionAtCenter)
            self.setCurrentIndex(index) 
            #self.selectionModel().select(index, QItemSelectionModel.Clear | QItemSelectionModel.Select |QItemSelectionModel.Rows)

            self.horizontalScrollBar().setValue(value) # 滚动条 位置 还原
    @Slot()
    def new_func_scrollto_to_last_game(self,):
        if not the_variables.auto_select_last_game:
            return
        if not the_variables.current_id:
            return
        
        #self.new_func_scrollto_row_by_game_id(the_variables.current_id)
        QTimer.singleShot(0, lambda: self.new_func_scrollto_row_by_game_id(the_variables.current_id))
        # ai
        # scrollTo 配合 PositionAtCenter 有时不生效，是一个经典的时序（Timing）问题。这通常发生在视图的布局或数据尚未就绪时，它无法准确计算目标单元格的位置
        # 即使延迟为0，也能让 scrollTo 在UI就绪后执行

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

    def new_func_context_menu_delete_selected_items_from_index(self,):
        if not ui_models.index_edit_mode:
            return
        if not ui_models.editable_index_files:
            return
        
        if not ui_models.multi_selection_mode:
            return
        if not ui_models.the_selected_items:
            return

        # 多选模式，删除
        self.parentWidget().new_func_show_editable_index_selector(ui_models.the_selected_items,add_mode=False)

    def new_func_context_menu_add_selected_items_to_index(self,):
        if not ui_models.index_edit_mode:
            return
        if not ui_models.editable_index_files:
            return
        
        if not ui_models.multi_selection_mode:
            return
        if not ui_models.the_selected_items:
            return

        # 多选模式，添加
        self.parentWidget().new_func_show_editable_index_selector(ui_models.the_selected_items,add_mode=True)

    def new_func_context_menu_delete_selected_items_from_current_table(self,):

        # 多选模式，删除
        self.model().new_func_remove_selected_items()

    def new_func_context_menu_select_same_type_items(self,):
        if not ui_models.multi_selection_mode:
            return

        # 单选模式，添加当前项到其他索引
        current_index = self.currentIndex()
        selected_index_list = self.selectionModel().selectedIndexes()
        if current_index in selected_index_list:
            # 多选模式，选择同类项
            self.model().new_func_select_same_type_items(current_index)


class My_Table_for_2_level(My_Table):
    def __init__(self,*args,**kwargs ):
        super().__init__(*args,**kwargs)
        
    def new_func(self,):
        self.new_table_type = "table_view_2_level"
        self.setObjectName("table_view_2_level")
        self.setModel(ui_models.Model_for_table_view_2_level(self))
        self.model().new_signal_time_for_choose_remember_game.connect(self.new_func_scrollto_to_last_game)


class My_Table_for_2_level_tree_like(My_Table):
    def __init__(self,*args,**kwargs ):
        super().__init__(*args,**kwargs)

        # 行标题，左侧
        #   禁止用户变化行高度
        self.verticalHeader().setSectionResizeMode(QHeaderView.Fixed) ########
        #   不显示，行标题
        self.verticalHeader().setVisible(True)
        #   行高度
        #self.verticalHeader().setDefaultSectionSize(80)
        #self.verticalHeader().resetDefaultSectionSize()
        self.verticalHeader().setHighlightSections(False)
        # 可点击
        self.verticalHeader().setSectionsClickable(True)

        self.verticalHeader().sectionPressed.connect(self.model().new_func_expand_or_collapse_item)
        
    def new_func(self,):
        self.new_table_type = "table_view_2_level_tree_like"
        self.setObjectName("table_view_2_level_tree_like")
        self.setModel(ui_models.Model_for_table_view_2_level_tree_like(self))
        self.model().new_signal_time_for_choose_remember_game.connect(self.new_func_scrollto_to_last_game)

    def keyPressEvent(self, event):

        # left/right，展开/收起 子项
        if event.key() == Qt.Key_Left:
            current_index = self.currentIndex()
            if current_index.isValid():
                row = current_index.row()
                self.model().new_func_delete_children(row)
                return
        elif event.key() == Qt.Key_Right:
            current_index = self.currentIndex()
            if current_index.isValid():
                row = current_index.row()
                self.model().new_func_insert_children(row)
                return

        super().keyPressEvent(event)








#####