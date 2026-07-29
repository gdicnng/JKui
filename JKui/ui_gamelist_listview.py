from qtpy.QtGui import *
from qtpy.QtWidgets import *
from qtpy.QtCore import *

import ui_models
import the_variables


class My_Icon_Table(QListView):
    def __init__(self,*args,**kwargs ):
        super().__init__(*args,**kwargs)

        self.new_func()
        self.new_func_create_context_menu()

        self.setViewMode(QListView.IconMode)
        #self.setViewMode(QListView.ListMode)
        
        self.setUniformItemSizes(True)
        
        #self.setIconSize(QSize(32,32))
        #self.setGridSize(QSize(120,60))

        # 间隔
        self.setSpacing(the_variables.spacing_for_icon_table)
        #self.setSpacing(15)

        self.setTextElideMode(Qt.ElideNone) 
        # 默认文字省略
        #  宽度不够时，右边省略号
        # 如果文字不省略
        #  如果宽度不够，虽然没有省略号，文字两边被截断
        #
        # 默认的宽度，好像是根据初始化时的某个单元格的宽度调整的，当显示的元素都是长文字时，宽度自然就加长了。
        # 宽度 初始化时的调整，随机度太高了
        # 和间距没有关系，间距宽了也没用
        
        self.setFlow(QListView.LeftToRight)
        #self.setFlow(QListView.TopToBottom)
        
        self.setWrapping(True)
        #self.setWrapping(False)
        
        self.setResizeMode(QListView.Adjust)
        
        # ？？？
        self.setLayoutMode(QListView.SinglePass)
        #self.setLayoutMode(QListView.Batched)
        #self.setBatchSize(10) # ???
        

        
        ## 行高，宽度
        #if the_image_width and the_image_height:
        #    temp = "QListView::item{}height: {}px;width: {}px;{}".format("{",the_item_height,the_item_width,"}")
        #    self.setStyleSheet(temp)
        #    print(temp)

        #self.setDragEnabled(True)
        #self.setDragDropMode(QListView.InternalMove)
        #self.setAcceptDrops(True)

    def new_func(self):
        model = ui_models.Model_for_icon(self)
        self.setModel(model)

        self.setObjectName("icon_table")
        self.model().new_signal_time_for_choose_remember_game.connect(self.new_func_scrollto_to_last_game)

    def new_func_create_context_menu(self,):
        self.new_context_menu = QMenu(self)
        
        ############
        # id
        self.new_action_show_id=QAction(" - ", self)
        self.new_action_show_id.triggered.connect(lambda: self.new_func_context_menu_click_to_copy_action_text(self.new_action_show_id))
        self.new_context_menu.addAction(self.new_action_show_id)

        # description
        self.new_action_show_description=QAction(" - ", self)
        self.new_action_show_description.triggered.connect(lambda: self.new_func_context_menu_click_to_copy_action_text(self.new_action_show_description))
        self.new_context_menu.addAction(self.new_action_show_description)

        # translation
        self.new_action_show_translation=QAction(" - ", self)
        self.new_action_show_translation.triggered.connect(lambda: self.new_func_context_menu_click_to_copy_action_text(self.new_action_show_translation))
        self.new_context_menu.addAction(self.new_action_show_translation)

        # year
        self.new_action_show_year=QAction(" - ", self)
        self.new_action_show_year.triggered.connect(lambda: self.new_func_context_menu_click_to_copy_action_text(self.new_action_show_year))
        self.new_context_menu.addAction(self.new_action_show_year)

        # manufacturer
        self.new_action_show_manufacturer=QAction(" - ", self)
        self.new_action_show_manufacturer.triggered.connect(lambda: self.new_func_context_menu_click_to_copy_action_text(self.new_action_show_manufacturer))
        self.new_context_menu.addAction(self.new_action_show_manufacturer)

        self.new_context_menu.addSeparator()
    
    def contextMenuEvent(self,e):
        index=self.indexAt(e.pos())
        if index.isValid():
            game_id, game_info = self.model().new_func_get_id_and_item_by_index(index)

            # id
            self.new_action_show_id.setText(game_id)

            # description
            try:self.new_action_show_description.setText(game_info[ ui_models.columns.index("description") ])
            except:self.new_action_show_description.setText("")

            # translation
            try:self.new_action_show_translation.setText(game_info[ ui_models.columns.index("translation") ])
            except:self.new_action_show_translation.setText("")

            # year
            try:self.new_action_show_year.setText(game_info[ ui_models.columns.index("year") ])
            except:self.new_action_show_year.setText("")

            # manufacturer
            try:self.new_action_show_manufacturer.setText(game_info[ ui_models.columns.index("manufacturer") ])
            except:self.new_action_show_manufacturer.setText("")

            self.new_context_menu.exec(e.globalPos())
    
    def new_func_context_menu_click_to_copy_action_text(self,action,):
        text = action.text()
        clipboard = QGuiApplication.clipboard()
        clipboard.setText(text)

    def currentChanged(self, current, previous):
        if current.isValid():
            #print("selected: ", selected.indexes()[0].row())
            game_id, game_info= self.model().new_func_get_id_and_item_by_index(current)
            row = current.row()
            print("selectionChanged",row,game_id)
            self.parent().new_signal_for_id_change.emit(game_id)

        super().currentChanged(current, previous)
    
    def new_func_do_nothing(self,):
        print("")
        print("func do nothing ,popup menu test for game list table")

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

    def new_func_scrollto_row_by_game_id(self,game_id):
        if not game_id:
            return
        
        index = self.model().new_func_get_index_by_game_id(game_id,)

        if not index: # 可能返回 None
            return
        
        if index.isValid():
            self.scrollTo(index,QAbstractItemView.PositionAtCenter)
            self.setCurrentIndex(index) 
            #self.selectionModel().select(index, QItemSelectionModel.Clear | QItemSelectionModel.Select |QItemSelectionModel.Rows)

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

    def keyPressEvent(self, event):
        
        # ctrl + B
        if event.key() == Qt.Key_B:
            if event.modifiers() == Qt.ControlModifier:
                #self.new_func_context_menu_bios_selector()
                current_index = self.currentIndex()
                if current_index.isValid():
                    game_id, game_info = self.model().new_func_get_id_and_item_by_index(current_index)
                    self.parentWidget().new_func_mame_show_bios_selector( game_id,)

        # return
        elif event.key() == Qt.Key_Return:
            current_index = self.currentIndex()
            if current_index.isValid():
                
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
