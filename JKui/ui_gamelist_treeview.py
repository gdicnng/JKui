from qtpy.QtGui import *
from qtpy.QtWidgets import *
from qtpy.QtCore import *

import ui_models
import the_variables



class My_Tree_View(QTreeView):
    def __init__(self,*args,**kwargs ):
        super().__init__(*args,**kwargs)

        self.new_func_set_model()

        self.new_table_type = "tree_view"
        self.setObjectName("tree_view")


        self.setUniformRowHeights(True)
       
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
    
    def new_func_set_model(self,):
        self.setModel(ui_models.Model_for_tree_view(self))
        self.model().new_signal_time_for_choose_remember_game.connect(self.new_func_scrollto_to_last_game)
    
    # 右键 菜单
    def contextMenuEvent(self,e):
        context = QMenu(self)
        
        action=QAction("test 1", self)
        action.triggered.connect(self.new_func_do_nothing)
        context.addAction(action)
        
        action=QAction("test 2", self)
        action.triggered.connect(self.new_func_do_nothing)
        context.addAction(action)

        context.exec_(e.globalPos())
    
    def new_func_do_nothing(self,):
        print("")
        print("do nothing")
    
    def selectionChanged(self, selected, deselected):
        if not selected.isEmpty():
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

    def new_func_scrollto_row_by_game_id(self,game_id):
        if not game_id:
            return

        index = self.model().new_func_get_index_by_game_id(game_id)

        if not index: # 可能返回 None
            return
        
        if index.isValid():
            self.scrollTo(index,hint=QAbstractItemView.PositionAtCenter)
            self.setCurrentIndex(index)

    @Slot()
    def new_func_scrollto_to_last_game(self,):
        if not the_variables.auto_select_last_game:
            return
        if not the_variables.current_id:
            return        
        self.new_func_scrollto_row_by_game_id(the_variables.current_id)

    
    #def keyPressEvent(self, event):
    #    # home 
    #    if event.key() == Qt.Key_Home:
    #        self.scrollToTop()
    #    # end
    #    elif event.key() == Qt.Key_End:
    #        self.scrollToBottom()
    #    else:
    #        super().keyPressEvent(event)            

