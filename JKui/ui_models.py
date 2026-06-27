import os
import re
import collections
import operator
import locale
import time
import functools

from qtpy.QtGui import *
from qtpy.QtWidgets import *
from qtpy.QtCore import *

import the_files
import the_variables
import misc_funcs

# 以下为空值，显示空列表
# 需要填充新值，然后使用
#######################################
#'columns', 'dict_data', 'internal_index', 'machine_dict', 'mame_version', 'set_data'
mame_version = ""

columns = []

machine_dict = dict()

# dict_data
#    clone_to_parent parent_to_clone
clone_to_parent = dict()
parent_to_clone = dict()

# set data
#   all_set parent_set clone_set
all_set = dict()
parent_set = dict()
clone_set = dict()
#######
#######
available_set = set()
unavailable_set = set()
filter_set = set()
#######

###
# 内部目录
internal_index = dict()
#################
# 拥有列表、未拥有列表
#internal_index_2={"available_set":"available_set","unavailable_set":"unavailable_set"}
internal_index_2={"available_set":"available_set",}
# 外部目录，需要读取 用户自定义目录
# 外部目录，第一层，有文件名后缀，以文件名后缀为区分
external_index = dict()
# 外部目录，source 分类，需要读取 用户自定义目录
external_index_by_source = dict()
# 之后，合并以上几类目录
index_chainmap = collections.ChainMap()
#######################################

##
icon_column_index = -1
translation_column_index = -1
id_column_index = -1
parent_have_more_than_1_clone_set = set() # parent_id set
#parent_to_clone__keys_set = set() 

# 图标
# 需要启动 qt 后，用它的 QPixmap 类加载图片
icon_red_pixmap = None
icon_green_pixmap = None
icon_yellow_pixmap = None
icon_black_pixmap = None
icon_red_pixmap_2_level = None
icon_green_pixmap_2_level = None
icon_yellow_pixmap_2_level = None
icon_black_pixmap_2_level = None

# new_table_type 
# 变量记录在 model 里 , new_table_type
# 变量也记录在 view 里 , new_table_type ,setObjectName("xxxx")
#
# "table_view_1_level" 单层列表,QTableView,
# "table_view_2_level" 双层列表 伪，QTableView
# "tree_view", 双层列表，树状列表,QTreeView


the_index_info = None  # 记录 目录名称
the_index_content = [] # 记录 目录内容

def the_timer(func):
    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        start = time.perf_counter()      # 高精度计时
        result = func(*args, **kwargs)
        end = time.perf_counter()
        elapsed = end - start
        print(f"{func.__name__} time : {elapsed:.6f} sec")
        return result
    return wrapper

def set_value(value_name,new_value):
    if value_name in globals():
        globals()[value_name]=new_value
    else:
        print("Error: value_name not found",value_name)

def load_gamelist_translation_file(file_path):
    index = -1
    try:
        index = columns.index("translation")
    except:
        return
    
    match_str = r'([^\t]+)\t([^\t]+)'
    p = re.compile(match_str)    

    global machine_dict
    with open(file_path, 'rt',encoding='utf-8_sig',errors="backslashreplace") as file:
        for line in file:
            
            result = p.match( line )
            
            if result:
                game_name   = result.group(1).strip().lower()
                translation = result.group(2).strip()
                if game_name and translation:
                    if game_name in machine_dict:
                        machine_dict[ game_name ][index] = translation

def load_icon():
    global icon_red_pixmap, icon_green_pixmap, icon_yellow_pixmap, icon_black_pixmap
    global icon_red_pixmap_2_level, icon_green_pixmap_2_level, icon_yellow_pixmap_2_level, icon_black_pixmap_2_level

    icon_red_pixmap = QPixmap()
    try:
        icon_red_pixmap.loadFromData(the_files.icon_red)
    except:
        pass
        
    icon_green_pixmap = QPixmap()
    try:
        icon_green_pixmap.loadFromData(the_files.icon_green)
    except:
        pass
        
    icon_yellow_pixmap = QPixmap()
    try:
        icon_yellow_pixmap.loadFromData(the_files.icon_yellow)
    except:
        pass
        
    icon_black_pixmap = QPixmap()
    try:
        icon_black_pixmap.loadFromData(the_files.icon_black)
    except:
        pass

    size = 	QSize(the_variables.icon_size * 2,the_variables.icon_size)

    empty_icon = QPixmap(size)
    empty_icon.fill(Qt.transparent)
    painter = QPainter()
    painter.begin(empty_icon)
    painter.drawPixmap(the_variables.icon_size, 0,icon_red_pixmap)
    painter.end()    
    icon_red_pixmap_2_level = empty_icon

    empty_icon = QPixmap(size)
    empty_icon.fill(Qt.transparent)
    painter = QPainter()
    painter.begin(empty_icon)
    painter.drawPixmap(the_variables.icon_size, 0,icon_green_pixmap)
    painter.end()    
    icon_green_pixmap_2_level = empty_icon


    empty_icon = QPixmap(size)
    empty_icon.fill(Qt.transparent)
    painter = QPainter()
    painter.begin(empty_icon)
    painter.drawPixmap(the_variables.icon_size, 0,icon_yellow_pixmap)
    painter.end()    
    icon_yellow_pixmap_2_level = empty_icon   

    empty_icon = QPixmap(size)
    empty_icon.fill(Qt.transparent)
    painter = QPainter()
    painter.begin(empty_icon)
    painter.drawPixmap(the_variables.icon_size, 0,icon_black_pixmap)
    painter.end()    
    icon_black_pixmap_2_level = empty_icon

def update_some_value():
    global icon_column_index
    global translation_column_index
    global id_column_index
    global parent_have_more_than_1_clone_set
    #global parent_to_clone__keys_set

    try:
        icon_column_index = columns.index("status")
    except:
        pass

    try:
        id_column_index = columns.index("id")
    except:
        pass

    try:
        translation_column_index = columns.index("translation")
        the_variables.sort_colums_use_locale.append(translation_column_index)
    except:
        pass

    def get_parent_have_more_than_1_children():
        # 子元素 大于 1 个的，子元素需要 排序
        
        temp = []
        
        for parent_id in parent_to_clone :
            if len( parent_to_clone[parent_id] ) > 1:
                temp.append( parent_id )
        
        temp = set( temp )
        
        return temp
    parent_have_more_than_1_clone_set = get_parent_have_more_than_1_children()

    #parent_to_clone__keys_set = set( parent_to_clone.keys() )

    
    


# 目录用
index_list = []
index_has_children = dict()
index_list_for_search = []
index_has_children_for_search = dict()

def rebuild_index_bak(top_index_list=None):
    # 第一层 index_list : 
    #   主目录 id
    # 第二层 index_has_children
    #   主目录 id : 子目录 id 列表

    if top_index_list is None:
        top_index_list = []
    
    global index_list
    global index_has_children
    global index_chainmap
    index_list.clear()
    index_has_children.clear()
    index_chainmap = collections.ChainMap(internal_index, external_index,external_index_by_source)

    user_order = top_index_list + list(the_variables.index_order)
    
    used_id = set()
    for index_id in user_order:
        if index_id in index_chainmap:
            index_list.append(index_id)
            used_id.add(index_id)
    not_in_user_order=[]
    for index_id in index_chainmap:
        if index_id not in used_id:
            not_in_user_order.append(index_id)

    not_in_user_order.sort()
    index_list = index_list + not_in_user_order

    for parent_index_id in index_list:
        parent_item = index_chainmap[parent_index_id]
        if "children" in parent_item:
            if parent_item["children"]:
                #print()
                #print(parent_index_id,parent_item["children"].keys()  )
                index_has_children[parent_index_id] = sorted( parent_item["children"].keys() )


def rebuild_index(top_index_list=None):
    # 第一层 index_list : 
    #   主目录 id
    # 第二层 index_has_children
    #   主目录 id : 子目录 id 列表

    if top_index_list is None:
        top_index_list = []
    
    global index_list
    global index_has_children
    global index_chainmap
    index_list.clear()
    index_has_children.clear()
    index_chainmap = collections.ChainMap(internal_index, internal_index_2, external_index,external_index_by_source)

    used_id = set()

    # 第一层 置顶
    for index_id in top_index_list:
        if index_id in index_chainmap:
            if index_id not in used_id:
                index_list.append(index_id)
                used_id.add(index_id)
    # 第一层 内置
    for index_id in ( the_variables.index_order ): # 内置固定优先排序
        if index_id in ( internal_index.keys() | internal_index_2.keys() ):
            if index_id not in used_id:
                index_list.append(index_id)
                used_id.add(index_id)
    for index_id in sorted( internal_index.keys() | internal_index_2.keys() ): # 其它
        if index_id in index_chainmap:
            if index_id not in used_id:
                index_list.append(index_id)
                used_id.add(index_id)
    # 第一层 external_index
    for index_id in sorted( external_index.keys() ): # 其它
        if index_id in index_chainmap:
            if index_id not in used_id:
                index_list.append(index_id)
                used_id.add(index_id)
    # 第一层 external_index_by_source
    for index_id in sorted( external_index_by_source.keys() ): # 其它
        if index_id in index_chainmap:
            if index_id not in used_id:
                index_list.append(index_id)
                used_id.add(index_id)                

    # 第二层
    # internal_index
    # internal_index_2 无
    # external_index
    # external_index_by_source
    for parent_index_id in index_list:
        if parent_index_id in internal_index.keys():
            parent_item = index_chainmap[parent_index_id]
            if "children" in parent_item:
                if parent_item["children"]:
                    #print()
                    #print(parent_index_id,parent_item["children"].keys()  )
                    index_has_children[parent_index_id] = sorted( parent_item["children"].keys() )
        elif parent_index_id in external_index.keys():
            parent_item = index_chainmap[parent_index_id]

            the_keys = set( parent_item.keys() )
            the_other_keys = the_keys - {"FOLDER_SETTINGS","ROOT_FOLDER"}
            if the_other_keys :
                index_has_children[parent_index_id] = sorted( the_other_keys )
        elif parent_index_id in external_index_by_source.keys():
            parent_item = index_chainmap[parent_index_id]

            the_keys = set( parent_item.keys() )
            the_other_keys = the_keys - {"FOLDER_SETTINGS","ROOT_FOLDER"}
            if the_other_keys :
                index_has_children[parent_index_id] = sorted( the_other_keys )                    











####################
@the_timer
def get_id_list_from_index(id_1,id_2="",):
    # 拥有列表、未拥有列表
    # 内部目录
    # 外部目录
    # 外部目录 by source

    the_index = index_chainmap
    
    temp_result = []

    def get_id_list_from_internal_index(id_1,id_2=""):
        def for_level_1(id_1):
            temp = [] # 可能为 list 也可能为 set
            if id_1 in the_index:
                if "gamelist" in the_index[id_1]:
                    temp = the_index[id_1]["gamelist"]
            return temp
        
        def for_level_2(id_1,id_2):
            temp = [] # 可能为 list 也可能为 set
            if id_1 in the_index:
                if "children" in the_index[id_1]:
                    if id_2 in the_index[id_1]["children"]:
                        if "gamelist" in the_index[id_1]["children"][id_2]:
                            temp = the_index[id_1]["children"][id_2]["gamelist"]
            return temp
        
        if id_1 and id_2:
            return for_level_2(id_1,id_2)
        elif id_1 and (not id_2):
            return for_level_1(id_1)


    # 拥有列表
    if id_1 == "available_set":
        temp_result = available_set
    # 未拥有列表
    elif id_1 == "unavailable_set":
        temp_result = unavailable_set
    # 外部目录
    elif id_1.lower().endswith(".ini"):
        temp_result = misc_funcs.get_id_list_from_external_index(id_1,id_2)
    # 外部目录 by source
    elif id_1.lower().endswith(".source_ini"):
        temp_result = misc_funcs.get_id_list_from_external_index_by_source(id_1,id_2)
    # 内部目录
    else:
        temp_result = misc_funcs.get_id_list_from_internal_index(id_1,id_2)

    if not filter_set: # 不过滤
        if all_set is temp_result:
            return all_set
        else:
            return all_set.intersection(temp_result)
    else:
        return all_set.intersection(temp_result) - filter_set
    
#########################
# for test
def set_game_list_to_all():
    global game_list
    game_list = list(machine_dict.keys())
###################




###############
@the_timer
def func_for_search(search_string,search_object_list=None,use_re=False,ignore_case=True,search_columns=tuple(),):
    # 都用 re 写吧，正常的搜索也写成 re 模式，少写一次代码

    if search_object_list is None:search_object_list = []

    result_list = []

    flag_search_all = False
    # search_columns ，用数字表示的切片，
    # 例如：[0,1,2] 表示搜索 第0列、第1列、第2列
    # 空值表示搜索所有列
    if not search_columns:
        flag_search_all = True
    else:
        temp_all_set = {n for n in range(len(columns))} # 以列号的数字表示的
        if set(search_columns) == temp_all_set :
            flag_search_all = True

    #print()
    #print("search_columns:",search_columns)
    #print("flag_search_all:",flag_search_all)

    if use_re:
        re_string = search_string
    else:
        re_string = re.escape(search_string)
    
    if ignore_case:
        p=re.compile(re_string,re.IGNORECASE)
    else:
        p=re.compile(re_string)
    

    # 每个游戏中，各列，
    # 返回 ，搜索到第一个匹配的列 ;
    # 未搜索到，返回 False
    def first_true(column_text_list):
        #return next(filter(lambda column_text:p.search(column_text), column_text_list), False)
        return any( map(lambda column_text:p.search(column_text), column_text_list) )

    if flag_search_all:
        for iteralble_object in  search_object_list:
            temp_result_list = list( filter( lambda game_id:first_true( machine_dict[game_id] ) , iteralble_object ) ) 
            result_list.extend(temp_result_list)
    else:
        search_columns = sorted(set(search_columns))
        get_column_text_list = operator.itemgetter(*search_columns)
        for iteralble_object in  search_object_list:
            temp_result_list = list( filter( lambda game_id:first_true( get_column_text_list(machine_dict[game_id]) ) , iteralble_object ) ) 
            result_list.extend(temp_result_list)

    re.purge()
    return result_list


class Model_for_table_view(QAbstractTableModel):

    def __init__(self,*args,**kwargs):
        super().__init__(*args,**kwargs)

        self.new_table_type = "table_view_1_level"

        self.new_game_list_to_show=[]
        self.new_data_remember_for_search=[]
        
    def data(self, index, role=Qt.DisplayRole):
        if role == Qt.DisplayRole:
            return machine_dict[ self.new_game_list_to_show[index.row()] ] [ index.column() ]
        elif role == Qt.DecorationRole:
            if index.column() == 0:

                value = machine_dict[ self.new_game_list_to_show[index.row()] ] [ icon_column_index ]

                if value == "good":
                    return icon_green_pixmap
                elif value == "imperfect":
                    return icon_yellow_pixmap
                elif value == "preliminary":
                    return icon_red_pixmap
                else:
                    return icon_black_pixmap


    def headerData(self,section,orientation,role=Qt.DisplayRole):
        if role == Qt.DisplayRole:
            if orientation == Qt.Horizontal:
                if section < len(columns):
                    return columns[section]

            if orientation == Qt.Vertical:
                return str(section)

    def rowCount(self, parent=QModelIndex()):
        return len(self.new_game_list_to_show)

    def columnCount(self, parent=QModelIndex()):  
        # 相同长度
        return len(columns)

    def new_func_get_id_and_item_by_index(self, index):
        row = index.row()
        game_id = self.new_game_list_to_show[row]
        return game_id, machine_dict[ game_id ] 

    # 鼠标点击排序
    def sort(self,column, order = Qt.AscendingOrder):
        
        # Qt::AscendingOrder          0
        # Qt::DescendingOrder        1
        
        if column < 0 or column >= len(columns):
            return

        if order == Qt.AscendingOrder:
            reverse = False
        else:
            reverse = True
        
        the_variables.sort_column = column
        the_variables.sort_reverse = reverse

        ###
        #self.layoutAboutToBeChanged.emit()
        self.beginResetModel()
        
        self.new_func_for_sort(column,reverse)
        
        ###
        #self.layoutChanged.emit()
        self.endResetModel()
    
 
    @the_timer
    def new_func_for_sort(self,column=None,reverse=None):
        
        # 未指定值，则，读取默认值
        if column is None:
            column = the_variables.sort_column
        if reverse is None:
            reverse = the_variables.sort_reverse
        if column < 0 or column >= len(columns):
            column = 0
        if type(reverse) is not bool:
            reverse = False

        def sort_key_func_1(game_id):
            return locale.strxfrm(machine_dict[game_id][column])
        def sort_key_func_2(game_id):
            return machine_dict[game_id][column]
        
        sort_key_func = sort_key_func_2
        if the_variables.sort_colums_use_locale:
            if column in the_variables.sort_colums_use_locale:
                sort_key_func = sort_key_func_1
        if column == id_column_index:
            sort_key_func = None
            print("sort by id")
        
        if isinstance(self.new_game_list_to_show,list):
            self.new_game_list_to_show.sort( key = sort_key_func,reverse = reverse, )
        else:
            self.new_game_list_to_show= sorted( self.new_game_list_to_show, key = sort_key_func,reverse = reverse, )

    # 目录发出信号
    # 显示新内容
    def new_func_show_by_index(self,id_1,id_2):
        print("")
        print("show by index")
        print("id_1: ",id_1)
        print("id_2: ",id_2)   

        ###
        #self.layoutAboutToBeChanged.emit()
        self.beginResetModel()
        
        self.new_func_clear_search_data()

        self.new_game_list_to_show = all_set.intersection( get_id_list_from_index(id_1,id_2) ) 
        self.new_func_for_sort()

        ###
        #self.layoutChanged.emit()
        self.endResetModel()
    
    def new_func_show_search_result(self,search_string,use_re=False,ignore_case=True,search_columns=tuple()):
        print("")
        print("show search result")

        if (not self.new_data_remember_for_search) and (not self.new_game_list_to_show):
            return

        ###
        self.beginResetModel()
        #self.layoutAboutToBeChanged.emit()

        # 记录原有数据
        if not self.new_data_remember_for_search:
            self.new_data_remember_for_search = self.new_game_list_to_show

        # 搜索
        self.new_game_list_to_show = func_for_search(search_string,search_object_list=[self.new_data_remember_for_search,],use_re=use_re,ignore_case=ignore_case,search_columns=search_columns)

        # sort
        self.new_func_for_sort()

        ###
        #self.layoutChanged.emit()
        self.endResetModel()

    def new_func_clear_all_data(self):
        print("clear data")
        self.new_game_list_to_show.clear()
        self.new_data_remember_for_search.clear()
    def new_func_clear_search_data(self):
        self.new_data_remember_for_search.clear()




@the_timer
def func_for_sort_table_view_2_level(column=None,reverse=False,games_to_be_sorted=None):
    
    #print()
    #print("func for sort treeview")
    #print(len(games_to_be_sorted))    
    
    if games_to_be_sorted is None:games_to_be_sorted = []
    
    # return value
    current_game_list_for_level_1 = []
    current_parent_have_children_set = set()
    current_clone_have_parent = set()

    # 未指定值，则，读取默认值
    if column is None:
        column = the_variables.sort_column
    if reverse is None:
        reverse = the_variables.sort_reverse
    if column < 0 or column >= len(columns):
        column = 0
    if type(reverse) is not bool:
        reverse = False
    
    # sort key func
    def sort_key_func_1(game_id):
        return locale.strxfrm(machine_dict[game_id][column])
    def sort_key_func_2(game_id):
        return machine_dict[game_id][column]
    #
    sort_key_func = sort_key_func_2
    if the_variables.sort_colums_use_locale:
        if column in the_variables.sort_colums_use_locale:
            sort_key_func = sort_key_func_1
    if column == id_column_index:
        sort_key_func = None
        #print("sort by id")

    
    ###################################
    t=time.time()
    #current_parent = parent_set.intersection(games_to_be_sorted)
    #current_clone = clone_set.intersection(games_to_be_sorted)    
    if games_to_be_sorted is all_set:
        current_parent = parent_set
        current_clone = clone_set 
        print("same")
    else:
        current_parent = parent_set.intersection(games_to_be_sorted)
        current_clone = clone_set.intersection(games_to_be_sorted)
        print("diff")

    print(time.time()-t)
   
    #### 空
    if ( not current_parent)  and ( not current_clone):
        return current_game_list_for_level_1,current_clone_have_parent
    
    #### 半空
    if not current_parent:
        current_game_list_for_level_1 = list(current_clone)
        current_game_list_for_level_1.sort( key = sort_key_func ,reverse = reverse, )
        return current_game_list_for_level_1,current_clone_have_parent
    
    #### 半空 2
    if not current_clone:
        current_game_list_for_level_1 = list(current_parent)
        current_game_list_for_level_1.sort( key = sort_key_func ,reverse = reverse, )
        return current_game_list_for_level_1,current_clone_have_parent
    
    #### 其它
    ###########################
    
    def get_some_data():

        # current_clone_have_parent
        current_clone_have_parent = []
        for parent_id in (current_parent & parent_to_clone.keys() ):  # 有 clone 的 parent 交集，缩小范围
            current_clone_have_parent.extend(parent_to_clone[parent_id]) # 超范围
        current_clone_have_parent = current_clone.intersection(current_clone_have_parent) # 处理超范围 # set
        
        # current_clone_not_have_parent
        #current_clone_not_have_parent = current_clone - current_clone_have_parent
        if len(current_clone_have_parent) == len(current_clone) :
            current_clone_not_have_parent = set()
        elif len(current_clone_have_parent) == 0 :
            current_clone_not_have_parent = current_clone
        else:
            current_clone_not_have_parent = current_clone - current_clone_have_parent
        
        # current_parent_have_children_set
        current_parent_have_children_set = {clone_to_parent[clone_id] for clone_id in current_clone_have_parent}
    
        return current_clone_have_parent,current_clone_not_have_parent,current_parent_have_children_set

    current_clone_have_parent,current_clone_not_have_parent,current_parent_have_children_set = get_some_data()

    if not current_clone_have_parent:
        # 仅一层
        current_game_list_for_level_1 = sorted( current_parent | current_clone_not_have_parent,key = sort_key_func ,reverse = reverse, )
        return current_game_list_for_level_1,current_clone_have_parent
    else:
        # 两层
        
        current_game_list_for_level_1 = current_parent | current_clone_not_have_parent
        current_game_list_for_level_1 = sorted( current_game_list_for_level_1, key = sort_key_func ,reverse = reverse, ) 

        for parent_id in ( current_parent_have_children_set & parent_have_more_than_1_clone_set ):
            parent_to_clone[parent_id].sort( key = sort_key_func,reverse = reverse,)
        
        temp_list = []
        for game_id in current_game_list_for_level_1:
            temp_list.append(game_id)
            if game_id in current_parent_have_children_set:
                for clone_id in parent_to_clone[game_id]:
                    if clone_id  in current_clone_have_parent:
                        temp_list.append(clone_id)
                    
        return temp_list,current_clone_have_parent
    return [],set()

@the_timer
def func_for_sort_table_view_2_level_bak(column=None,reverse=False,games_to_be_sorted=None):

    #print()
    #print("func for sort treeview")
    #print(len(games_to_be_sorted))    
    
    if games_to_be_sorted is None:games_to_be_sorted = []
    
    # return value
    current_game_list_for_level_1 = []
    #current_parent_have_children_set = set()
    current_clone_have_parent = set()

    # 未指定值，则，读取默认值
    if column is None:
        column = the_variables.sort_column
    if reverse is None:
        reverse = the_variables.sort_reverse
    if column < 0 or column >= len(columns):
        column = 0
    if type(reverse) is not bool:
        reverse = False

    # sort key func
    def sort_key_func_1(game_id):
        return locale.strxfrm(machine_dict[game_id][column])
    def sort_key_func_2(game_id):
        return machine_dict[game_id][column]
    #
    sort_key_func = sort_key_func_2
    if the_variables.sort_colums_use_locale:
        if column in the_variables.sort_colums_use_locale:
            sort_key_func = sort_key_func_1
    if column == id_column_index:
        sort_key_func = None
        #print("sort by id")

    ###################################

    #t1 = time.time()

    #current_parent = parent_set.intersection(games_to_be_sorted)
    #current_clone = clone_set.intersection(games_to_be_sorted)    
    if games_to_be_sorted is all_set:
        current_parent = parent_set
        current_clone = clone_set 
    else:
        current_parent = parent_set.intersection(games_to_be_sorted)
        current_clone = clone_set.intersection(games_to_be_sorted)

    #t2 = time.time()
    #print("time - 1: ",f"{t2-t1:.5f}")

    #### 空
    if ( not current_parent)  and ( not current_clone):
        return current_game_list_for_level_1,current_clone_have_parent
    
    #### 半空
    if not current_parent:
        current_game_list_for_level_1 = list(current_clone)
        current_game_list_for_level_1.sort( key = sort_key_func ,reverse = reverse, )
        return current_game_list_for_level_1,current_clone_have_parent
    
    #### 半空 2
    if not current_clone:
        current_game_list_for_level_1 = list(current_parent)
        current_game_list_for_level_1.sort( key = sort_key_func ,reverse = reverse, )
        return current_game_list_for_level_1,current_clone_have_parent

    #### 其它
    ###########################
    
    # current_clone_have_parent
    current_clone_have_parent = []
    for parent_id in current_parent.intersection(parent_to_clone): # 有 clone 的 parent 交集，缩小范围
        current_clone_have_parent.extend(parent_to_clone[parent_id]) # 超范围
    current_clone_have_parent = current_clone.intersection(current_clone_have_parent) # 处理超范围 # set
    
    # current_clone_not_have_parent
    if len(current_clone_have_parent) == len(current_clone) :
        current_clone_not_have_parent = set()
    elif len(current_clone_have_parent) == 0 :
        current_clone_not_have_parent = current_clone
    else:
        current_clone_not_have_parent = current_clone - current_clone_have_parent

    if not current_clone_have_parent:
        # 仅一层
        current_game_list_for_level_1 = sorted( current_parent | current_clone_not_have_parent,key = sort_key_func ,reverse = reverse, )
        return current_game_list_for_level_1,current_clone_have_parent
    else:
        # 两层
        
        # current_parent_have_children_set
        current_parent_have_children_set = [clone_to_parent[clone_id] for clone_id in current_clone_have_parent]
        current_parent_have_children_set = set(current_parent_have_children_set)

        #t3 = time.time()
        #print("time - 2: ",f"{t3-t2:.5f}")  

        temp_set=current_parent.union(current_clone_not_have_parent)
        current_game_list_for_level_1 = sorted( temp_set, key = sort_key_func ,reverse = reverse, )

        #t4 = time.time()
        #print("time - 3: ",f"{t4-t3:.5f}")
        

        for parent_id in ( current_parent_have_children_set & parent_have_more_than_1_clone_set ):
            parent_to_clone[parent_id].sort( key = sort_key_func,reverse = reverse,)
        
        temp_list = []
        for game_id in current_game_list_for_level_1:
            temp_list.append(game_id)
            if game_id in current_parent_have_children_set:
                for clone_id in parent_to_clone[game_id]:
                    if clone_id  in current_clone_have_parent:
                        temp_list.append(clone_id)
                        
        return temp_list,current_clone_have_parent



class Model_for_table_view_2_level(QAbstractTableModel):

    def __init__(self,*args,**kwargs):
        super().__init__(*args,**kwargs)

        self.new_table_type = "table_view_2_level"

        self.new_game_list_to_show=[]
        self.new_data_remember_for_search=[]
        self.new_current_clone_have_parent=set()
        
    def data(self, index, role=Qt.DisplayRole):
        if role == Qt.DisplayRole:
            return machine_dict[ self.new_game_list_to_show[index.row()] ] [ index.column() ]
        elif role == Qt.DecorationRole:
            if index.column() == 0:
                
                game_id = self.new_game_list_to_show[index.row()]
                value = machine_dict[ game_id ] [ icon_column_index ]
                return self.new_func_get_icon(value,game_id)


    def headerData(self,section,orientation,role=Qt.DisplayRole):
        if role == Qt.DisplayRole:
            if orientation == Qt.Horizontal:
                if section < len(columns):
                    return columns[section]

            if orientation == Qt.Vertical:
                return str(section)

    def rowCount(self, parent=QModelIndex()):
        return len(self.new_game_list_to_show)

    def columnCount(self, parent=QModelIndex()):  
        # 相同长度
        return len(columns)

    def new_func_get_id_and_item_by_index(self, index):
        row = index.row()
        game_id = self.new_game_list_to_show[row]
        return game_id, machine_dict[ game_id ] 

    # 鼠标点击排序
    def sort(self,column, order = Qt.AscendingOrder):
        
        # Qt::AscendingOrder          0
        # Qt::DescendingOrder        1
        
        if column < 0 or column >= len(columns):
            return

        if order == Qt.AscendingOrder:
            reverse = False
        else:
            reverse = True
        
        the_variables.sort_column = column
        the_variables.sort_reverse = reverse

        ###
        #self.layoutAboutToBeChanged.emit()
        self.beginResetModel()
        
        self.new_func_for_sort(column,reverse)
        
        ###
        #self.layoutChanged.emit()
        self.endResetModel()
    
 
    def new_func_for_sort(self,column=None,reverse=None):

        self.new_game_list_to_show,self.new_current_clone_have_parent = func_for_sort_table_view_2_level(column=column,reverse=reverse,games_to_be_sorted=self.new_game_list_to_show)

    # 目录发出信号
    # 显示新内容
    def new_func_show_by_index(self,id_1,id_2):
        print("")
        print("show by index")
        print("id_1: ",id_1)
        print("id_2: ",id_2)   
        
        ###
        #self.layoutAboutToBeChanged.emit()
        self.beginResetModel()
        
        self.new_func_clear_all_data()

        #self.new_game_list_to_show =  get_id_list_from_index(id_1,id_2) 
        self.new_game_list_to_show = all_set.intersection( get_id_list_from_index(id_1,id_2) ) 
        self.new_func_for_sort()

        ###
        #self.layoutChanged.emit()
        self.endResetModel()
    
    def new_func_show_search_result(self,search_string,use_re=False,ignore_case=True,search_columns=tuple()):
        print("")
        print("show search result")
        print("search_string: ",search_string)   

        if (not self.new_data_remember_for_search) and (not self.new_game_list_to_show):
            return

        ###
        self.beginResetModel()
        #self.layoutAboutToBeChanged.emit()

        # 记录原有数据
        if not self.new_data_remember_for_search:
            self.new_data_remember_for_search = self.new_game_list_to_show
        
        # 搜索
        self.new_game_list_to_show = func_for_search(search_string,search_object_list=[self.new_data_remember_for_search,],use_re=use_re,ignore_case=ignore_case,search_columns=search_columns)

        # sort
        self.new_func_for_sort()

        ###
        #self.layoutChanged.emit()
        self.endResetModel()

    def new_func_clear_all_data(self):
        print("clear data")
        self.new_game_list_to_show.clear()
        self.new_data_remember_for_search.clear()
        self.new_current_clone_have_parent.clear()
    def new_func_clear_search_data(self):
        self.new_data_remember_for_search.clear()

    def new_func_get_icon(self,value,game_id):
        if game_id in self.new_current_clone_have_parent:
            if value == "good":
                return icon_green_pixmap_2_level
            elif value == "imperfect":
                return icon_yellow_pixmap_2_level
            elif value == "preliminary":
                return icon_red_pixmap_2_level
            else:
                return icon_black_pixmap_2_level
        else:
            if value == "good":
                return icon_green_pixmap
            elif value == "imperfect":
                return icon_yellow_pixmap
            elif value == "preliminary":
                return icon_red_pixmap
            else:
                return icon_black_pixmap

@the_timer
def func_for_sort_treeview(column=None,reverse=False,games_to_be_sorted=None):

    #print()
    #print("func for sort treeview")
    #print(len(games_to_be_sorted))    
    
    if games_to_be_sorted is None:games_to_be_sorted = []
    
    # return value
    current_game_list_for_level_1 = []
    current_parent_have_children = dict()

    # 未指定值，则，读取默认值
    if column is None:
        column = the_variables.sort_column
    if reverse is None:
        reverse = the_variables.sort_reverse
    if column < 0 or column >= len(columns):
        column = 0
    if type(reverse) is not bool:
        reverse = False

    # sort key func
    def sort_key_func_1(game_id):
        return locale.strxfrm(machine_dict[game_id][column])
    def sort_key_func_2(game_id):
        return machine_dict[game_id][column]
    #
    sort_key_func = sort_key_func_2
    if the_variables.sort_colums_use_locale:
        if column in the_variables.sort_colums_use_locale:
            sort_key_func = sort_key_func_1
    if column == id_column_index:
        sort_key_func = None
        #print("sort by id")

    ###################################

    #t1 = time.time()

    #current_parent = parent_set.intersection(games_to_be_sorted)
    #current_clone = clone_set.intersection(games_to_be_sorted)    
    if games_to_be_sorted is all_set:
        current_parent = parent_set
        current_clone = clone_set 
    else:
        current_parent = parent_set.intersection(games_to_be_sorted)
        current_clone = clone_set.intersection(games_to_be_sorted)

    
   
    #t2 = time.time()
    #print("time - 1: ",f"{t2-t1:.5f}")

    #### 空
    if ( not current_parent)  and ( not current_clone):
        return current_game_list_for_level_1,current_parent_have_children
    
    #### 半空
    if not current_parent:
        current_game_list_for_level_1 = list(current_clone)
        current_game_list_for_level_1.sort( key = sort_key_func ,reverse = reverse, )
        return current_game_list_for_level_1,current_parent_have_children
    
    #### 半空 2
    if not current_clone:
        current_game_list_for_level_1 = list(current_parent)
        current_game_list_for_level_1.sort( key = sort_key_func ,reverse = reverse, )
        return current_game_list_for_level_1,current_parent_have_children

    #### 其它
    ###########################
    
    # current_clone_have_parent
    current_clone_have_parent = []
    for parent_id in current_parent.intersection(parent_to_clone): # 有 clone 的 parent 交集，缩小范围
        current_clone_have_parent.extend(parent_to_clone[parent_id]) # 超范围
    current_clone_have_parent = current_clone.intersection(current_clone_have_parent) # 处理超范围 # set
    
    # current_clone_not_have_parent
    if len(current_clone_have_parent) == len(current_clone) :
        current_clone_not_have_parent = set()
    elif len(current_clone_have_parent) == 0 :
        current_clone_not_have_parent = current_clone
    else:
        current_clone_not_have_parent = current_clone - current_clone_have_parent

    # current_parent_have_children_set
    current_parent_have_children_set = {clone_to_parent[clone_id] for clone_id in current_clone_have_parent}

    #t3 = time.time()
    #print("time - 2: ",f"{t3-t2:.5f}")  

    temp_set=current_parent.union(current_clone_not_have_parent)
    current_game_list_for_level_1 = sorted( temp_set, key = sort_key_func ,reverse = reverse, )

    #t4 = time.time()
    #print("time - 3: ",f"{t4-t3:.5f}")
    
    # 1
    #current_parent_have_children={  parent_id : sorted( current_clone_have_parent.intersection( parent_to_clone[parent_id] ), 
    #                                        key = sort_key_func ,
    #                                        reverse = reverse, ) 
    #                                    for parent_id in current_parent_have_children_set
    #                                    }

    # or 2
    for parent_id in ( current_parent_have_children_set & parent_have_more_than_1_clone_set ):
        parent_to_clone[parent_id].sort( key = sort_key_func,reverse = reverse,)
    for parent_id in current_parent_have_children_set :
        for clone_id in parent_to_clone[parent_id]:
            if clone_id in current_clone_have_parent:
                if parent_id not in current_parent_have_children:
                    current_parent_have_children[parent_id] = []
                current_parent_have_children[parent_id].append(clone_id)

    
    #t5 = time.time()
    #print("time - 4: ",f"{t5-t4:.5f}")

    return current_game_list_for_level_1,current_parent_have_children


class Model_for_tree_view(QAbstractItemModel):
    def __init__(self,*args,**kwargs):
        super().__init__(*args,**kwargs)
        self.new_table_type = "tree_view"

        self.new_games_all=set() # set or list
        self.new_games_all_data_remember_for_search=set()

        self.new_game_list_for_level_1 = []
        self.new_parent_have_children = dict() 


    def data(self, index, role):
        if not index.isValid():return None;
        
        internal_id = index.internalId()
        if internal_id == 1:
            game_id = self.new_game_list_for_level_1[index.row()]
        else:
            parent_row = internal_id - 2
            parent_id = self.new_game_list_for_level_1[parent_row]
            game_id = self.new_parent_have_children[parent_id][index.row()]

        if role == Qt.DisplayRole:
            return machine_dict[game_id][index.column()]
        elif role == Qt.DecorationRole:
            if index.column() == 0:

                value = machine_dict[ game_id ] [ icon_column_index ]

                if value == "good":
                    return icon_green_pixmap
                elif value == "imperfect":
                    return icon_yellow_pixmap
                elif value == "preliminary":
                    return icon_red_pixmap
                else:
                    return icon_black_pixmap
        
        return None

    def headerData(self,section,orientation,role ):
        if role == Qt.DisplayRole:
            if orientation == Qt.Horizontal:
                if section < len(columns):
                    return columns[section]

            if orientation == Qt.Vertical:
                return str(section)

    def rowCount(self, parent ):

        if parent.isValid():
            if parent.internalId() == 1 :
                parent_id = self.new_game_list_for_level_1[parent.row()]
                if parent_id in self.new_parent_have_children:
                    return len( self.new_parent_have_children[parent_id] )            
        else :
            return len(self.new_game_list_for_level_1)
        return 0

    def columnCount(self, parent ):  
        # 相同长度
        return len(columns)
        
    def index(self,row,column,parent):
        if parent==QModelIndex():
            return self.createIndex( row,column,1 ) # 第一层
        elif parent.internalId() == 1 :
            # parent.row() + 2 
            return self.createIndex( row,column, parent.row() + 2 ) # 第二层
        return QModelIndex()
        
    def parent(self,index):
        if index.isValid():
            id_number = index.internalId()

            if id_number == 1:
                return QModelIndex()
            
            if id_number > 1:
                temp = id_number - 2
                return self.createIndex( temp,0,1)
        return QModelIndex()

    #######
    #######
    #######

    def new_func_get_id_and_item_by_index(self, index):
        if not index.isValid():return None;
        
        internal_id = index.internalId()
        if internal_id == 1:
            game_id = self.new_game_list_for_level_1[index.row()]
        else:
            parent_row = internal_id - 2
            parent_id = self.new_game_list_for_level_1[parent_row]
            game_id = self.new_parent_have_children[parent_id][index.row()]
        
        return game_id, machine_dict[ game_id ] 

    # 仅排序
    
    def sort(self,column, order = Qt.AscendingOrder):
        
        # Qt::AscendingOrder          0
        # Qt::DescendingOrder        1
        
        if column < 0 or column >= len(columns):
            return

        if order == Qt.AscendingOrder:
            reverse = False
        else:
            reverse = True
        
        the_variables.sort_column = column
        the_variables.sort_reverse = reverse

        ###

        #self.layoutAboutToBeChanged.emit()
        self.beginResetModel()
        
        # 清除所有数据
        #self.new_func_clear_all_data() 
        # 清除部分数据
        self.new_func_clear_data_for_sort()

        self.new_func_for_sort(column, reverse)
        
        ###
        #self.layoutChanged.emit()
        self.endResetModel()
    

    def new_func_for_sort(self,column=None,reverse=False,in_search_mode=False):
        self.new_game_list_for_level_1,self.new_parent_have_children = func_for_sort_treeview(column=column, reverse=reverse, games_to_be_sorted=self.new_games_all)

    @the_timer
    def new_func_for_sort_back(self,column=None,reverse=False,in_search_mode=False):

        # 未指定值，则，读取默认值
        if column is None:
            column = the_variables.sort_column
        if reverse is None:
            reverse = the_variables.sort_reverse
        if column < 0 or column >= len(columns):
            column = 0
        if type(reverse) is not bool:
            reverse = False

        def sort_key_func_1(game_id):
            return locale.strxfrm(machine_dict[game_id][column])
        def sort_key_func_2(game_id):
            return machine_dict[game_id][column]

        sort_key_func = sort_key_func_2
        if the_variables.sort_colums_use_locale:
            if column in the_variables.sort_colums_use_locale:
                sort_key_func = sort_key_func_1
        if column == id_column_index:
            sort_key_func = None
            print("sort by id")

        ###################################

        #t1 = time.time()

        current_parent = parent_set.intersection(self.new_games_all)
        current_clone = clone_set.intersection(self.new_games_all)
       
        #t2 = time.time()
        #print("time - 1: ",t2-t1)

        #### 空
        if ( not current_parent)  and ( not current_clone):
            self.new_game_list_for_level_1 = []
            self.new_parent_have_children = dict()
            return
        
        #### 半空
        if not current_parent:
            self.new_game_list_for_level_1 = list(current_clone)
            self.new_game_list_for_level_1.sort( key = sort_key_func ,reverse = reverse, )
            self.new_parent_have_children = dict()
            return
        
        #### 半空 2
        if not current_clone:
            self.new_game_list_for_level_1 = list(current_parent)
            self.new_game_list_for_level_1.sort( key = sort_key_func ,reverse = reverse, )
            self.new_parent_have_children = dict()
            return

        #### 其它
        ###########################
        
        #current_clone_not_have_parent = []
        current_clone_have_parent = []

        for clone_id in current_clone:
            parent_id = clone_to_parent[clone_id]
            if  parent_id in current_parent:
                current_clone_have_parent.append(clone_id)
                if parent_id in self.new_parent_have_children:
                    self.new_parent_have_children[parent_id].append(clone_id)
                else:
                    self.new_parent_have_children[parent_id] = [clone_id]
        current_clone_not_have_parent = current_clone.difference(current_clone_have_parent)
        
        #t3 = time.time()
        #print("time - 2: ",t3-t2)

        #################
        self.new_game_list_for_level_1 = list(current_parent | current_clone_not_have_parent )
        self.new_game_list_for_level_1.sort( key = sort_key_func ,reverse = reverse, )
        #self.new_game_list_for_level_1 = sorted( current_parent.union(current_clone_not_have_parent) , key = sort_key_func ,reverse = reverse, )
        
        #t4 = time.time()
        #print("time - 3: ",t4-t3)

        for k in ( parent_have_more_than_1_clone_set.intersection(self.new_parent_have_children) ) :
            if len(self.new_parent_have_children[k]) >1:
                self.new_parent_have_children[k].sort( key = sort_key_func ,reverse = reverse, ) 
        
        #t5 = time.time()
        #print("time - 4: ",t5-t4)

    # 目录发出信号
    # 显示新内容
    def new_func_show_by_index(self,id_1,id_2):
        print("")
        print(self.new_table_type)
        print("show by index")
        print("id_1: ",id_1)
        print("id_2: ",id_2)
        
        ###
        #self.layoutAboutToBeChanged.emit()
        self.beginResetModel()
        
        self.new_func_clear_all_data()
        

        self.new_games_all =  get_id_list_from_index(id_1,id_2) 
        
        print(len(self.new_games_all))

        column = the_variables.sort_column
        reverse = the_variables.sort_reverse

        self.new_func_for_sort(column, reverse)

        ###
        #self.layoutChanged.emit()
        self.endResetModel()
    
    def new_func_show_search_result(self,search_string,use_re=False,ignore_case=True,search_columns=tuple()):
        print("")
        print("show search result")
        print("search_string: ",search_string)   

        if (not self.new_games_all) and (not self.new_games_all_data_remember_for_search):
            return


        ###
        #self.layoutAboutToBeChanged.emit()
        self.beginResetModel()

        if not self.new_games_all_data_remember_for_search:
            self.new_games_all_data_remember_for_search = self.new_games_all
        
        self.new_func_clear_data_for_sort()
        self.new_games_all = func_for_search(search_string,search_object_list=[self.new_games_all_data_remember_for_search,],use_re=use_re,ignore_case=ignore_case,search_columns=search_columns)
        self.new_func_for_sort()

        ###
        #self.layoutChanged.emit()
        self.endResetModel()



    #####
    def new_func_clear_all_data(self):
        print("clear data ",self.new_table_type)

        # 不要直接删，有些变量直接 复制 的地址，
        # 重新赋 空值
        self.new_games_all= set() # set or list
        self.new_games_all_data_remember_for_search = set()
        self.new_game_list_for_level_1=[]
        self.new_parent_have_children=dict()

    def new_func_clear_data_for_sort(self):
        self.new_game_list_for_level_1=[]
        self.new_parent_have_children=dict()
    
    def new_func_clear_search_data(self):
        # 不要直接删，有些变量直接 复制 的地址，
        # 重新赋 空值
        self.new_games_all_data_remember_for_search = set()



# index_list = []
# index_list_for_search = []
class Model_for_index(QAbstractItemModel):
    def __init__(self,):
        super().__init__()

    def data(self, index, role):
        if not index.isValid():return None;

        if role == Qt.DisplayRole:
            internal_id = index.internalId()
            if internal_id == 1:
                text = index_list[index.row()]
                if text.lower().endswith(".ini") or text.lower().endswith(".source_ini"):
                    the_text = os.path.basename(text)
                else:
                    the_text = the_variables.index_translation.get(text,text)
                return the_text
            elif internal_id > 1:
                parent_row = internal_id -2
                parent_id = index_list[parent_row]
                if parent_id in index_has_children:
                    text =  index_has_children[parent_id][index.row()]
                    return text
            
    def headerData(self,section,orientation,role ):
        if role == Qt.DisplayRole:
            if orientation == Qt.Horizontal:
                return str(section)
            if orientation == Qt.Vertical:
                return str(section)

    def rowCount(self, parent ):

        if parent==QModelIndex():
            return len(index_list)
        else :
            if parent.internalId() == 1 :
                parent_id = index_list[parent.row()]
                if parent_id in index_has_children:
                    return len( index_has_children[parent_id] )
            
        return 0

    def columnCount(self, parent ):  
        # 相同长度
        return 1
        
    def index(self,row,column,parent):
        if parent==QModelIndex():
            return self.createIndex( row,column,1 ) # 第一层
        elif parent.internalId() == 1 :
            # parent.row() + 2 
            return self.createIndex( row,column, parent.row() + 2 ) # 第二层
        return QModelIndex()
        
    def parent(self,index):
        if index.isValid():
            id_number = index.internalId()

            if id_number == 1:
                return QModelIndex()
            
            if id_number > 1:
                temp = id_number - 2
                return self.createIndex( temp,0,1)
        return QModelIndex()

    def new_func_get_index_id_by_index(self, index):
        id_1,id_2="",""
        
        if index.isValid():
            internal_id = index.internalId()
            if internal_id == 1:
                id_1 = index_list[index.row()]
            elif internal_id > 1:
                parent_row = internal_id -2
                id_1 = index_list[parent_row]
                id_2 = index_has_children[id_1][index.row()]
                
        return id_1,id_2
    
    def new_func_find_item(self,index_id_1,index_id_2):
        row_level_1 = -1
        row_level_2 = -1

        if not index_id_1:
            return None

        for n in range(len(index_list)):
            if index_list[n] == index_id_1:
                row_level_1 = n
        if row_level_1 == -1:
            return None
        
        if index_id_2:
            if index_id_1 in index_has_children:
                for n in range(len(index_has_children[index_id_1])):
                    if index_has_children[index_id_1][n] == index_id_2:
                        row_level_2 = n
            if index_id_2 == -1 :
                return None
        
        if row_level_2 == -1:
                return self.createIndex( row_level_1,0,1 )
        else:
                return self.createIndex( row_level_2,0,row_level_1 + 2 )  


                
        

    

    ###
    # def hasChildren(self,parent_index):
    #     if parent_index.isValid():
    #         return False
    #     return True





if __name__ == "__main__":
    print("")
    print("test")
    filename = the_files.data_file
    data = None

    import os
    import pickle

    if os.path.isfile(filename):
        try:
            file = open(filename, 'rb')
            data = pickle.load( file )
            file.close()
        except:
            print( "read pickle failed")
            print( filename )
            

    if data:


        # 更新模型数据
        ##'columns', 'dict_data', 'internal_index', 'machine_dict', 'mame_version', 'set_data'
        #
        ## clounms = []
        set_value("columns",data["columns"])
        #
        ## dict_data
        ##    clone_to_parent parent_to_clone
        # clone_to_parent = dict()
        # parent_to_clone = dict()
        set_value("clone_to_parent",data["dict_data"]["clone_to_parent"])
        set_value("parent_to_clone",data["dict_data"]["parent_to_clone"])
        #print(data["dict_data"].keys())
        #
        ## internal_index = dict()
        set_value("internal_index",data["internal_index"])
        #
        #machine_dict = dict()
        set_value("machine_dict",data["machine_dict"])
        #
        ## mame_version = ""
        set_value("mame_version",data["mame_version"])
        #
        ## set data
        ##   all_set parent_set clone_set
        ## all_set = dict()
        ## parent_set = dict()
        ## clone_set = dict()
        set_value("all_set",data["set_data"]["all_set"])
        set_value("parent_set",data["set_data"]["parent_set"])
        set_value("clone_set",data["set_data"]["clone_set"])
        

        #
        update_some_value()    

  

        x=set()
        x.add("kof97")
        temp_set= all_set - x


        print("........")
        a,b=func_for_sort_treeview(column = None,games_to_be_sorted=temp_set)               
        a,b=func_for_sort_treeview(column = None,reverse=True,games_to_be_sorted=temp_set)  
        a,b=func_for_sort_treeview(column = 1,games_to_be_sorted=temp_set)                   
        a,b=func_for_sort_treeview(column = 1,reverse=True,games_to_be_sorted=temp_set)      
        a,b=func_for_sort_treeview(column = 2,games_to_be_sorted=temp_set)                   
        a,b=func_for_sort_treeview(column = 2,reverse=True,games_to_be_sorted=temp_set)      

        a,b=func_for_sort_table_view_2_level(column = None,games_to_be_sorted=temp_set)               
        a,b=func_for_sort_table_view_2_level(column = None,reverse=True,games_to_be_sorted=temp_set)  
        a,b=func_for_sort_table_view_2_level(column = 1,games_to_be_sorted=temp_set)                   
        a,b=func_for_sort_table_view_2_level(column = 1,reverse=True,games_to_be_sorted=temp_set)      
        a,b=func_for_sort_table_view_2_level(column = 2,games_to_be_sorted=temp_set)                   
        a,b=func_for_sort_table_view_2_level(column = 2,reverse=True,games_to_be_sorted=temp_set)      
                
        print("........")
        print("all_set:",len(all_set))
        print("temp_set:",len(temp_set))
        print("levle 1:",len(a))
        print("parent have children:",len(b))

          

