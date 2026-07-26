import re

from qtpy.QtWidgets import *
from qtpy.QtGui import *
from qtpy.QtCore import *

import ui_models
import misc_funcs


class My_index_table(QTreeView):
    new_signal_change_index = Signal(str,str)
    new_signal_for_press_escape = Signal()
    def __init__(self,*args,**kwargs):
        super().__init__(*args,**kwargs)
        
        self.setUniformRowHeights(True)

        self.setHorizontalScrollMode(QAbstractItemView.ScrollPerPixel)
        self.setVerticalScrollBarPolicy(Qt.ScrollBarAlwaysOn)

        self.setHeaderHidden(True)

        self.new_func()
        self.new_func_create_context_menu()

    def new_func(self):
        model_for_index = ui_models.Model_for_index()
        self.setModel( model_for_index )
        self.setObjectName("index_table")

    def new_func_create_context_menu(self,):
        self.new_context_menu = QMenu(self)
        
        action_collapse_all=QAction("折叠所有项", self)
        action_collapse_all.triggered.connect(self.collapseAll)
        self.new_context_menu.addAction(action_collapse_all)
    

    def contextMenuEvent(self,e):
        index=self.indexAt(e.pos())
        if index.isValid():
            self.new_context_menu.exec(e.globalPos())
    
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
    
    def keyPressEvent(self, event):
        # Qt.Key_Escape
        if event.key() == Qt.Key_Escape:
            self.new_signal_for_press_escape.emit()
        else:
            super().keyPressEvent(event)

    def new_func_select_row_by_index_id(self,index_id_1,index_id_2,scroll_to = False) :
        index = self.model().new_func_find_item(index_id_1,index_id_2)
        if index is None:
            return None

        if index.isValid():
            #self.setCurrentIndex(index)
            self.selectionModel().select(index,QItemSelectionModel.Select)
            if scroll_to:
                self.scrollTo(index,QAbstractItemView.PositionAtCenter)

class Line_editor_for_search(QLineEdit):
    new_signal_for_press_enter = Signal()
    new_signal_for_press_ctrl_enter = Signal()
    new_signal_for_press_escape = Signal()
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    def keyPressEvent(self, event):
        # Qt.Key_Escape
        if event.key() == Qt.Key_Enter or event.key() == Qt.Key_Return:
            if event.modifiers() & Qt.ControlModifier:
                self.new_signal_for_press_ctrl_enter.emit()
            else:
                self.new_signal_for_press_enter.emit()
        elif event.key() == Qt.Key_Escape:
            #self.clear()
            self.new_signal_for_press_escape.emit()
        else:
            super().keyPressEvent(event)

class Index_dockwidget(QDockWidget):
    def __init__(self,*args,**kwargs):
        super().__init__(*args,**kwargs)
        
        self.new_index_id_remember = "",""

        #
        a_widget=QWidget(self)

        layout = QVBoxLayout(a_widget)

        # 搜索框
        self.new_ui_line_editor_for_search = Line_editor_for_search(a_widget)
        self.new_ui_line_editor_for_search.setPlaceholderText("目录搜索")
        
        # 目录表格
        self.new_ui_index = My_index_table(a_widget)

        layout.addWidget(self.new_ui_line_editor_for_search)
        layout.addWidget(self.new_ui_index)

        self.setWidget(a_widget)

        self.new_ui_index.new_signal_change_index.connect(self.new_slot_for_receive_index_id)
        self.new_ui_index.new_signal_for_press_escape.connect(self.new_func_cancel_search)
        self.new_ui_line_editor_for_search.new_signal_for_press_enter.connect(self.new_func_for_search)
        self.new_ui_line_editor_for_search.new_signal_for_press_ctrl_enter.connect(self.new_func_for_search_re)
        self.new_ui_line_editor_for_search.new_signal_for_press_escape.connect(self.new_func_cancel_search)

    @Slot()
    def new_func_for_search(self):
        print("search")
        search_string = self.new_ui_line_editor_for_search.text()

        search_string = search_string.strip()
        if not search_string:
            return
        
        self.new_ui_index.model().new_func_search_index(search_string)
        self.new_ui_index.expandAll()
        self.new_ui_index.scrollToTop()
    
    @Slot()
    def new_func_for_search_re(self):
        print("search re")
        search_string = self.new_ui_line_editor_for_search.text()

        search_string = search_string.strip()
        if not search_string:
            return

        try:
            re.compile(search_string)
        except:
            QMessageBox.warning(self,"warning","正则表达式可能出错")
            return
        
        self.new_ui_index.model().new_func_search_index(search_string,use_re=True)
        self.new_ui_index.expandAll()
        self.new_ui_index.scrollToTop()
    
    @Slot()
    def new_func_cancel_search(self):
        self.new_ui_line_editor_for_search.clear()
        self.new_ui_index.model().new_func_cancel_search()
        
        id_1,id_2 = self.new_index_id_remember
        if id_1 :
            try:
                index = self.new_ui_index.model().new_func_find_item(id_1,id_2)
                self.new_ui_index.scrollTo(index,QAbstractItemView.PositionAtCenter)
                self.new_ui_index.setCurrentIndex(index)
                self.new_ui_index.selectionModel().select(index,QItemSelectionModel.Select)
            except:
                pass

    @Slot(str,str)
    def new_slot_for_receive_index_id(self,index_id_1,index_id_2):

        self.new_index_id_remember = index_id_1,index_id_2


# 目录选择器
class Treeview_for_index_chooser(QTreeView):

    def __init__(self,*args,**kwargs):
        super().__init__(*args,**kwargs)
        
        self.setUniformRowHeights(True)

        self.setHorizontalScrollMode(QAbstractItemView.ScrollPerPixel)
        self.setVerticalScrollBarPolicy(Qt.ScrollBarAlwaysOn)

        self.header().setStretchLastSection(False)

        self.setHeaderHidden(False)
        #self.setColumnWidth(0,200) # 不管用？
        #self.setColumnWidth(1,300)

        self.new_func()
        self.new_func_create_context_menu()
    
    def new_func(self):
        model_for_index_chooser = ui_models.Model_for_index_chooser()
        self.setModel( model_for_index_chooser )
        self.setObjectName("editable_index_chooser")

    def new_func_create_context_menu(self,):
        self.new_context_menu = QMenu(self)
        
        action_collapse_all=QAction("折叠所有项", self)
        action_collapse_all.triggered.connect(self.collapseAll)
        self.new_context_menu.addAction(action_collapse_all)

    def contextMenuEvent(self,e):
        index=self.indexAt(e.pos())
        if index.isValid():
            self.new_context_menu.exec(e.globalPos())
    
class Dialog_for_index_chooser(QDialog):  

    def __init__(self,*args, **kwargs):
        super().__init__(*args, **kwargs)

        self.new_add_mode = True
        self.new_game_id_set = set()
        self.new_index_id_1 = ""
        self.new_index_id_2 = ""
        
        self.new_title_string = "目录选择"
        
        self.setWindowTitle(self.new_title_string)

        self.setSizeGripEnabled(True)
        
        self.setMinimumWidth(500)
        #self.setMinimumHeight(300)

        # 垂直布局管理器
        layout = QVBoxLayout()
        
        # 第一行布局
        tree_for_index_chooser = Treeview_for_index_chooser(self)
        layout.addWidget(tree_for_index_chooser, 1)
        self.new_tree = tree_for_index_chooser

        # 第二行
        last_row_layout = QHBoxLayout()
        button_ok = QPushButton("确认")
        button_ok.clicked.connect(self.new_func_for_ok)
        last_row_layout.addWidget(button_ok)

        button_cancel = QPushButton("取消")
        button_cancel.clicked.connect(self.reject)
        last_row_layout.addWidget(button_cancel)

        layout.addLayout(last_row_layout)
        self.setLayout(layout)

    def new_func_set_values(self,game_id_s,add_mode=True):
        if not game_id_s:
            return
        
        self.new_add_mode = add_mode

        self.new_game_id_set.clear()
        self.new_index_id_1 = ""
        self.new_index_id_2 = ""

        self.new_tree.resizeColumnToContents(0)
        self.new_tree.resizeColumnToContents(1)
        
        if isinstance(game_id_s,str):
            self.new_game_id_set.add(game_id_s) # 单个 game_id
        else:
            self.new_game_id_set.update(game_id_s) # 多个 game_id 可迭代对象

        if add_mode:
            self.setWindowTitle(self.new_title_string + " + " + str(len(self.new_game_id_set)))
        else:
            self.setWindowTitle(self.new_title_string + " - " + str(len(self.new_game_id_set)))

    def new_func_get_index_id(self):
        return self.new_index_id_1,self.new_index_id_2

    def new_func_for_ok(self,checked):
        tree = self.new_tree
        current_index = tree.currentIndex()
        if current_index.isValid():
            selected_index_list = tree.selectionModel().selectedIndexes()
            if current_index in selected_index_list:
                index_id_1 ,index_id_2 = tree.model().new_func_get_index_id_by_index(current_index)
                
                print()
                print("index_id_1",index_id_1)
                print("index_id_2",index_id_2)
                if self.new_add_mode:
                    changed = misc_funcs.add_items_to_external_index(self.new_game_id_set,index_id_1,index_id_2)
                else:
                    changed = misc_funcs.delect_items_from_external_index(self.new_game_id_set,index_id_1,index_id_2)


                if changed:
                    self.new_index_id_1,self.new_index_id_2 = index_id_1,index_id_2 # 记录
                    self.accept()
                else:
                    self.reject()

