from qtpy.QtGui import *
from qtpy.QtWidgets import *
from qtpy.QtCore import *

import ui_models
import the_variables


class My_Table(QTableView):
    def __init__(self,*args,**kwargs ):
        super().__init__(*args,**kwargs)

        self.new_func()

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
        #   没有效果 ？？？
        #   但是小片段代码测试，有效 ？？？
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
        
        
        # 不显示 单元格
        self.setShowGrid(False)

        self.setTabKeyNavigation(False)

        self.setSortingEnabled(True)

        # 可选：启用鼠标跟踪，让鼠标移出时能立即隐藏 ToolTip（但 QToolTip 本身会在移出时隐藏）
        # self.setMouseTracking(True)
    
    def new_func(self,):
        self.new_table_type = "table_view_1_level"
        self.setObjectName("table_view_1_level")
        self.setModel(ui_models.Model_for_table_view(self))
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
            row = selected.indexes()[0].row()
            print("selectionChanged",row,game_id)
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
        # home 
        if event.key() == Qt.Key_Home:
            self.scrollToTop()
        # end
        elif event.key() == Qt.Key_End:
            self.scrollToBottom()
        else:
            super().keyPressEvent(event)

    def new_func_scrollto_row_by_game_id(self,game_id):
        if not game_id:
            return
        
        index = self.model().new_func_get_index_by_game_id(game_id)

        if not index: # 可能返回 None
            return
        
        if index.isValid():
            self.scrollTo(index,QAbstractItemView.PositionAtCenter)
            self.setCurrentIndex(index)

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



class My_Table_for_2_level(My_Table):
    def __init__(self,*args,**kwargs ):
        super().__init__(*args,**kwargs)
        
    def new_func(self,):
        self.new_table_type = "table_view_2_level"
        self.setObjectName("table_view_2_level")
        self.setModel(ui_models.Model_for_table_view_2_level(self))
        self.model().new_signal_time_for_choose_remember_game.connect(self.new_func_scrollto_to_last_game)










#####