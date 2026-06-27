from qtpy.QtWidgets import *
from qtpy.QtGui import *
from qtpy.QtCore import *

import ui_models

class My_index_table(QTreeView):
    new_signal_change_index = Signal(str,str)
    def __init__(self,*args,**kwargs):
        super().__init__(*args,**kwargs)
        
        self.setUniformRowHeights(True)

        self.setHorizontalScrollMode(QAbstractItemView.ScrollPerPixel)
        self.setVerticalScrollBarPolicy(Qt.ScrollBarAlwaysOn)

        self.setHeaderHidden(True)

        self.new_func()

    
    def new_func(self):
        model_for_index = ui_models.Model_for_index()
        self.setModel( model_for_index )
        self.setObjectName("index_table")
        
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
    
    # 这个，有焦点时，一定会自动选一个，麻烦
    #def currentChanged(self,current, previous): # QModelIndex
    #    if previous.isValid():
    #        row_previous = previous.row()
    #    else:
    #        row_previous = None
#
    #    if current.isValid():
    #        row_current = current.row()
    #    else:
    #        row_current = None
#
    #    if row_current != row_previous:
    #        id_1,id_2 = self.model().new_func_get_index_id_by_index(current)
    #        #print("index current row changed,index is:",id_1," :: ",id_2)
    #        self.new_signal_change_index.emit(id_1,id_2)
    #    super().currentChanged(current, previous)

    ##selectionChanged(const QItemSelection &selected, const QItemSelection &deselected)
    def selectionChanged(self, selected, deselected):
        print("selectionChanged")
        if not selected.isEmpty():
            #print("selected: ", selected.indexes()[0].row())
            id_1,id_2 = self.model().new_func_get_index_id_by_index(selected.indexes()[0])
            self.new_signal_change_index.emit(id_1,id_2)
        #if not deselected.isEmpty():
        #    print("deselected: ", deselected.indexes()[0].row())
        super().selectionChanged(selected, deselected)
    
    def new_func_select_row_by_index_id(self,index_id_1,index_id_2,scroll_to = False) :
        index = self.model().new_func_find_item(index_id_1,index_id_2)
        if index is None:
            return None

        if index.isValid():
            #self.setCurrentIndex(index)
            self.selectionModel().select(index,QItemSelectionModel.Select)
            if scroll_to:
                self.scrollTo(index,QAbstractItemView.PositionAtCenter)
    
