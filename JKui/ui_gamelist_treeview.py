from qtpy.QtGui import *
from qtpy.QtWidgets import *
from qtpy.QtCore import *

import ui_models



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

        ## 列标题，上侧
        #horizontal_header = self.horizontalHeader()
        ##   点击 标题
        #horizontal_header.setSectionsClickable(True)
        ##   拖动
        #horizontal_header.setSectionsMovable(True)
        ##   第一列，禁止拖动
        #horizontal_header.setFirstSectionMovable(False)

        #self.verticalHeader().setVisible(False)
    
    def new_func_set_model(self,):
        self.setModel(ui_models.Model_for_tree_view(self))
    
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
    
    def currentChanged(self,current, previous): # QModelIndex
        if previous.isValid():
            row_previous = previous.row()
        else:
            row_previous = None

        if current.isValid():
            row_current = current.row()
        else:
            row_current = None

        if row_current != row_previous:
            game_id, game_info = self.model().new_func_get_id_and_item_by_index(current)
            print("row changed: ",row_current, game_id)
            self.parent().new_signal_for_id_change.emit(game_id)
    
        super().currentChanged(current, previous)

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



    #def keyPressEvent(self, event):
    #    # home 
    #    if event.key() == Qt.Key_Home:
    #        self.scrollToTop()
    #    # end
    #    elif event.key() == Qt.Key_End:
    #        self.scrollToBottom()
    #    else:
    #        super().keyPressEvent(event)            

