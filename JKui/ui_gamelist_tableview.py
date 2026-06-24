from qtpy.QtGui import *
from qtpy.QtWidgets import *
from qtpy.QtCore import *

import ui_models
import the_variables



class My_model_test(QAbstractTableModel):
    # 假 数据
    # 测试 QTableView
    
    the_max_row_number = 1000
    the_max_column_number = 10
    
    def __init__(self,*args,**kwargs):
        super().__init__(*args,**kwargs)
        #self._data = data

    def data(self, index, role=Qt.DisplayRole):
        if role == Qt.DisplayRole:
            #return self._data[index.row()][index.column()] 
            return "row :" + str(index.row()) + ", column :" + str(index.column())

    def headerData(self,section,orientation,role=Qt.DisplayRole):
        if role == Qt.DisplayRole:
            if orientation == Qt.Horizontal:
                #return header_horizontal[section]
                return str(section)

            if orientation == Qt.Vertical:
                #return header_vertical[section]
                return str(section)

    def rowCount(self, parent=QModelIndex()):
        return self.the_max_row_number

    def columnCount(self, parent=QModelIndex()):  
        # 相同长度
        return self.the_max_column_number


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
        #   enum QAbstractItemView::SelectionMode

        # 列标题，上侧
        horizontal_header = self.horizontalHeader()
        #   点击 标题
        horizontal_header.setSectionsClickable(True)
        #   拖动
        horizontal_header.setSectionsMovable(True)
        #   第一列，禁止拖动
        horizontal_header.setFirstSectionMovable(False)

        # 行标题，左侧
        vertical_header = self.verticalHeader()
        #   禁止用户变化行高度
        vertical_header.setSectionResizeMode(QHeaderView.Fixed) ########
        #   不显示，行标题
        vertical_header.setVisible(False)
        #   行高度
        #vertical_header.setDefaultSectionSize(50)
        
        # 不显示 单元格
        self.setShowGrid(False)

        self.setTabKeyNavigation(False)
    
    def new_func(self,):
        self.new_table_type = "table_view_1_level"
        self.setObjectName("table_view_1_level")
        self.setModel(ui_models.Model_for_table_view(self))
    
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

    def keyPressEvent(self, event):
        # home 
        if event.key() == Qt.Key_Home:
            self.scrollToTop()
        # end
        elif event.key() == Qt.Key_End:
            self.scrollToBottom()
        else:
            super().keyPressEvent(event)


class My_Table_for_2_level(My_Table):
    def __init__(self,*args,**kwargs ):
        super().__init__(*args,**kwargs)
        #
        self.new_table_type = "table_view_2_level"
        self.setObjectName("table_view_2_level")










#####