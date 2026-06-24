import sys

import qtpy
from qtpy.QtWidgets import *
from qtpy.QtGui import *
from qtpy.QtCore import * # Qt


print( "the qt binding version" )
if qtpy.PYSIDE_VERSION:
    print( "pyside",qtpy.PYSIDE_VERSION)
if qtpy.PYQT_VERSION:
    print( "pyqt",qtpy.PYQT_VERSION )
print()

the_max_row_number = 10000*30
the_max_column_number = 20

dict_data = {}
dict_data[(3,3)]="3,3 for test"

def get_data(row,column):
    if (row,column) not in dict_data:
        return f"row:{row},column:{column}"
    return dict_data[(row,column)]

class My_model(QAbstractTableModel):
    def __init__(self,*args,**kwargs):
        super().__init__(*args,**kwargs)
        #self._data = data

    def data(self, index, role=Qt.DisplayRole):
        if role == Qt.DisplayRole:
            #return self._data[index.row()][index.column()] 
            return get_data(index.row(),index.column())
            

    def headerData(self,section,orientation,role ):
        if role == Qt.DisplayRole:
            if orientation == Qt.Horizontal:
                #return header_horizontal[section]
                return str(section)

            if orientation == Qt.Vertical:
                #return header_vertical[section]
                return str(section)

    def rowCount(self, parent ):
        return the_max_row_number

    def columnCount(self, parent ):  
        # 相同长度
        return the_max_column_number

class My_Table(QTableView):
    def __init__(self,*args,**kwargs):
        super().__init__(*args,**kwargs)
        
        self.new_func_some_settings()
        
    def new_func_some_settings(self,):

        

        # 不换行
        self.setWordWrap(False)
        
        # 字体
        #self.setFont( QFont("宋体", 16,) )
        
        # 选择一行，
        #   而不是选择 单元格
        self.setSelectionBehavior(QAbstractItemView.SelectRows)
        
        # 单选、多选
        #self.setSelectionMode(self.SingleSelection )
        self.setSelectionMode(QAbstractItemView.ExtendedSelection )
        #self.setSelectionMode(self.MultiSelection )
            # enum QAbstractItemView::SelectionMode
            #   SingleSelection
            #   ContiguousSelection
            #   ExtendedSelection
                # ctrl + A ，全选 卡死
                # 性能 不行
            #   MultiSelection
            #   NoSelection

        
        
        
        # 列标题，上侧
        horizontal_header = self.horizontalHeader()
        #   点击 标题
        horizontal_header.setSectionsClickable(False)
        #   拖动
        horizontal_header.setSectionsMovable(True)
        #   第一列，禁止拖动
        horizontal_header.setFirstSectionMovable(False)
        
        
        # 行标题，左侧
        vertical_header = self.verticalHeader()
        #
        #   禁止用户变化行高度
        vertical_header.setSectionResizeMode(QHeaderView.Fixed) 
            # QHeaderView::Fixed	The user cannot resize the section. The section can only be resized programmatically using resizeSection(). The section size defaults to defaultSectionSize.
        #
        #   行高度
        vertical_header.setDefaultSectionSize(50)        
        #
        #   不显示，行标题
        vertical_header.setVisible(False)
        
        
        #   表格分隔线
        #
        #self.setGridStyle(Qt.NoPen) 
        #self.setGridStyle(Qt.SolidLine) # 
        #self.setGridStyle(Qt.DotLine) # 
        #
        #   不显示
        self.setShowGrid(False)

        
        



class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()

        self.setWindowTitle("My App")

        self.table = My_Table()

        self.setCentralWidget(self.table)
        

app = QApplication(sys.argv)
#app.setStyle('Fusion')

# with open("a.qss",mode="rt",encoding="utf_8",errors="ignore") as f:
#     a=f.read()
# app.setStyleSheet(a)

window = MainWindow()
model = My_model()
window.table.setModel(model)


window.resize(800,600)
window.show()

app.exec_()
