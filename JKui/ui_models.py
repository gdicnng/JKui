import os
import traceback
import sys
import re
import collections
import operator
import locale
import time
import functools
import zipfile

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
#unavailable_set = set() # 这个不用了吧，用 all_set - available_set
filter_set = set()
#######


###
# 内部目录
internal_index = dict()
#################
# 拥有列表、未拥有列表
internal_index_2={"available_set":"available_set","unavailable_set":"unavailable_set"}
#internal_index_2={"available_set":"available_set",}
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
cloneof_column_index = -1 # 状态栏信息用
romof_column_index = -1 # 状态栏信息用
status_column_index = -1 # 状态栏信息用
savestate_column_index = -1 # 状态栏信息用
sourcefile_column_index = -1 # 周边，mameinfo.dat 、messinfo.dat 用
parent_have_more_than_1_clone_set = set() # parent_id set ，有多个子项的父项，# 好像没用上
#parent_to_clone__keys_set = set() 

# 图标
# 需要启动 qt 后，用它的 QPixmap 类加载图片
icon_red_pixmap = None
icon_green_pixmap = None
icon_yellow_pixmap = None
icon_black_pixmap = None
icon_not_have_pixmap = None

icon_extra_resource = dict()
# 第三方图标，全部读取到此
# the_variables.icon_size # 列表图标大小，当时在 the_variables 文件里定义的

icon_red_pixmap_for_icon_table = None
icon_green_pixmap_for_icon_table = None
icon_yellow_pixmap_for_icon_table = None
icon_black_pixmap_for_icon_table = None
icon_not_have_pixmap_for_icon_table = None
image_width_for_image_table = 400
image_height_for_image_table = 300
text_height_for_image_table = 30 # 图片列表 的 文本行高
empty_image_pixmap_for_image_table = None # 这个没用了

icon_size_for_icon_table = 32 # 图标视图 的 图标大小
text_width_for_icon_table = 40 # 图标列表 的 文本宽度；与图标宽度 ，两者最大值 做为单元格宽度
text_height_for_icon_table = 30 # 图标列表 的 文本行高


# new_table_type 
# 变量记录在 model 里 , new_table_type
# 变量也记录在 view 里 , new_table_type ,setObjectName("xxxx")
#
# "table_view_1_level" 单层列表,QTableView,
# "table_view_2_level" 双层列表 伪，QTableView
# "tree_view", 双层列表，树状列表,QTreeView


# 表格中用于 展开/收起 符号
string_for_open = " + " 
string_for_close = " - "
string_for_empty = "   "

# 目录编辑 
editable_index_files = set()
index_files_be_edited = set()
index_edit_mode = False
# 多选模式（勾选）
multi_selection_mode = False
the_selected_items = set() # 多选， 记录
# 列表编辑 仅翻译列
gamelist_editable_mode = False


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

def load_gamelist_translation_file(file_path,clear_old_data=False):
    index_translation = columns.index("translation")
    index_description = columns.index("description")
    
    global machine_dict

    if clear_old_data:
        for game_id in machine_dict:
            machine_dict[game_id][index_translation] = machine_dict[game_id][index_description]
    
    if not os.path.isfile(file_path):
        return
    
    match_str = r'([^\t]+)\t([^\t]+)'
    p = re.compile(match_str)

    with open(file_path, 'rt',encoding='utf-8_sig',errors="backslashreplace") as file:
        for line in file:
            
            result = p.match( line )
            
            if result:
                game_name   = result.group(1).strip().lower()
                translation = result.group(2).strip()
                if game_name and translation:
                    if game_name in machine_dict:
                        machine_dict[ game_name ][index_translation] = translation

def load_and_resize_internal_icon():
    global icon_red_pixmap, icon_green_pixmap, icon_yellow_pixmap, icon_black_pixmap,icon_not_have_pixmap
    global icon_red_pixmap_for_icon_table, icon_green_pixmap_for_icon_table, icon_yellow_pixmap_for_icon_table
    global icon_black_pixmap_for_icon_table,icon_not_have_pixmap_for_icon_table
    #global empty_image_pixmap_for_image_table

    icon_size =QSize(the_variables.icon_size,the_variables.icon_size)
    icon_size_2 = QSize(icon_size_for_icon_table,icon_size_for_icon_table)

    icon_red_pixmap = QPixmap()
    
    try:
        icon_red_pixmap.loadFromData(the_files.icon_red)
        if (icon_red_pixmap.width() != the_variables.icon_size) or (icon_red_pixmap.height() != the_variables.icon_size):
            icon_red_pixmap = icon_red_pixmap.scaled(
                the_variables.icon_size,the_variables.icon_size,                  # 目标大小
                Qt.KeepAspectRatio,
                Qt.SmoothTransformation
                )
    except:
        pass

    icon_green_pixmap = QPixmap()
    try:
        icon_green_pixmap.loadFromData(the_files.icon_green)
        if (icon_green_pixmap.width() != the_variables.icon_size) or (icon_green_pixmap.height() != the_variables.icon_size):
            icon_green_pixmap = icon_green_pixmap.scaled(
                the_variables.icon_size,the_variables.icon_size,                  # 目标大小
                Qt.KeepAspectRatio,
                Qt.SmoothTransformation
                )
    except:
        pass
        
    icon_yellow_pixmap = QPixmap()
    try:
        icon_yellow_pixmap.loadFromData(the_files.icon_yellow)
        if (icon_yellow_pixmap.width() != the_variables.icon_size) or (icon_yellow_pixmap.height() != the_variables.icon_size):
            icon_yellow_pixmap = icon_yellow_pixmap.scaled(
                the_variables.icon_size,the_variables.icon_size,                  # 目标大小
                Qt.KeepAspectRatio,
                Qt.SmoothTransformation
                )
    except:
        pass
        
    icon_black_pixmap = QPixmap()
    try:
        icon_black_pixmap.loadFromData(the_files.icon_black)
        if (icon_black_pixmap.width() != the_variables.icon_size) or (icon_black_pixmap.height() != the_variables.icon_size):
            icon_black_pixmap = icon_black_pixmap.scaled(
                the_variables.icon_size,the_variables.icon_size,                  # 目标大小
                Qt.KeepAspectRatio,
                Qt.SmoothTransformation
                )
    except:
        pass

    icon_not_have_pixmap = QPixmap()
    try:
        icon_not_have_pixmap.loadFromData(the_files.icon_not_have)
        if (icon_not_have_pixmap.width() != the_variables.icon_size) or (icon_not_have_pixmap.height() != the_variables.icon_size):
            icon_not_have_pixmap = icon_not_have_pixmap.scaled(
                the_variables.icon_size,the_variables.icon_size,                  # 目标大小
                Qt.KeepAspectRatio,
                Qt.SmoothTransformation
                )
    except:
        pass

    ###

    icon_red_pixmap_for_icon_table = QPixmap()
    try:
        icon_red_pixmap_for_icon_table.loadFromData(the_files.icon_red)
        if (icon_red_pixmap_for_icon_table.width() != icon_size_for_icon_table) or (icon_red_pixmap_for_icon_table.height() != icon_size_for_icon_table):
            icon_red_pixmap_for_icon_table = icon_red_pixmap_for_icon_table.scaled(
                icon_size_for_icon_table,icon_size_for_icon_table,                  # 目标大小
                Qt.KeepAspectRatio,
                Qt.SmoothTransformation
                )
    except:
        pass

    icon_green_pixmap_for_icon_table = QPixmap()
    try:
        icon_green_pixmap_for_icon_table.loadFromData(the_files.icon_green)
        if (icon_green_pixmap_for_icon_table.width() != icon_size_for_icon_table) or (icon_green_pixmap_for_icon_table.height() != icon_size_for_icon_table):
            icon_green_pixmap_for_icon_table = icon_green_pixmap_for_icon_table.scaled(
                icon_size_for_icon_table,icon_size_for_icon_table,                  # 目标大小
                Qt.KeepAspectRatio,
                Qt.SmoothTransformation
                )
    except:
        pass

    icon_yellow_pixmap_for_icon_table = QPixmap()
    try:
        icon_yellow_pixmap_for_icon_table.loadFromData(the_files.icon_yellow)
        if (icon_yellow_pixmap_for_icon_table.width() != icon_size_for_icon_table) or (icon_yellow_pixmap_for_icon_table.height() != icon_size_for_icon_table):
            icon_yellow_pixmap_for_icon_table = icon_yellow_pixmap_for_icon_table.scaled(
                icon_size_for_icon_table,icon_size_for_icon_table,                  # 目标大小
                Qt.KeepAspectRatio,
                Qt.SmoothTransformation
                )
    except:
        pass

    icon_black_pixmap_for_icon_table = QPixmap()
    try:
        icon_black_pixmap_for_icon_table.loadFromData(the_files.icon_black)
        if (icon_black_pixmap_for_icon_table.width() != icon_size_for_icon_table) or (icon_black_pixmap_for_icon_table.height() != icon_size_for_icon_table):
            icon_black_pixmap_for_icon_table = icon_black_pixmap_for_icon_table.scaled(
                icon_size_for_icon_table,icon_size_for_icon_table,                  # 目标大小
                Qt.KeepAspectRatio,
                Qt.SmoothTransformation
                )
    except:
        pass

    icon_not_have_pixmap_for_icon_table = QPixmap()
    try:
        icon_not_have_pixmap_for_icon_table.loadFromData(the_files.icon_not_have)
        if (icon_not_have_pixmap_for_icon_table.width() != icon_size_for_icon_table) or (icon_not_have_pixmap_for_icon_table.height() != icon_size_for_icon_table):
            icon_not_have_pixmap_for_icon_table = icon_not_have_pixmap_for_icon_table.scaled(
                icon_size_for_icon_table,icon_size_for_icon_table,                  # 目标大小
                Qt.KeepAspectRatio,
                Qt.SmoothTransformation
                )
    except:
        pass

    #empty_image_pixmap_for_image_table = QPixmap(image_width_for_image_table,image_height_for_image_table,)
    #empty_image_pixmap_for_image_table.fill(Qt.transparent)


def update_some_value():
    global icon_column_index
    global translation_column_index
    global id_column_index
    global cloneof_column_index
    global romof_column_index
    global status_column_index
    global savestate_column_index
    global sourcefile_column_index

    #global parent_have_more_than_1_clone_set
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
        cloneof_column_index = columns.index("cloneof")
    except:
        pass

    try:
        romof_column_index = columns.index("romof")
    except:
        pass

    try:
        status_column_index = columns.index("status")
    except:
        pass

    try:
        savestate_column_index = columns.index("savestate")
    except:
        pass
    
    try:
        sourcefile_column_index = columns.index("sourcefile")
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
    #parent_have_more_than_1_clone_set = get_parent_have_more_than_1_children()

    #parent_to_clone__keys_set = set( parent_to_clone.keys() )


# 目录用
index_list = []
index_has_children = dict()
index_list_backup = []
index_has_children_backup = dict()

# 可编辑目录 选择器
editable_index_list=[]
editable_index_has_children = dict()

# 置顶目录
top_index_list = []

# 隐藏的内置目录
hidden_index_set = set()

def rebuild_index():
    # 第一层 index_list : 
    #   主目录 id
    # 第二层 index_has_children
    #   主目录 id : 子目录 id 列表
    
    global index_list
    global index_has_children
    global index_chainmap
    global index_list_backup
    global index_has_children_backup

    index_list.clear()
    index_has_children.clear()
    index_chainmap = collections.ChainMap(internal_index, internal_index_2, external_index,external_index_by_source)

    used_id = set()

    # 第一层 置顶
    for index_id in top_index_list:
        if index_id in hidden_index_set:
            continue
        if index_id in index_chainmap:
            if index_id not in used_id:
                index_list.append(index_id)
                used_id.add(index_id)
    # 第一层 内置
    #  内置固定优先排序
    for index_id in ( the_variables.index_order ): 
        if index_id in hidden_index_set:
            continue
        if index_id in ( internal_index.keys() | internal_index_2.keys() ):
            if index_id not in used_id:
                index_list.append(index_id)
                used_id.add(index_id)
    # 第一层 内置
    #  其它
    for index_id in sorted( internal_index.keys() | internal_index_2.keys() ): 
        if index_id in hidden_index_set:
            continue
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

    index_list_backup = index_list
    index_has_children_backup = index_has_children

def build_editable_index_data():
   # 第一层 index_list : 
    #   主目录 id
    # 第二层 index_has_children
    #   主目录 id : 子目录 id 列表

    global editable_index_list
    global editable_index_has_children
    # external_index
    # editable_index_files

    editable_index_list.clear()
    editable_index_has_children.clear()

    # 第一层 内置
    for index_id in sorted( external_index.keys() ): # 内置固定优先排序
        if index_id in ( editable_index_files ):
            editable_index_list.append(index_id)

    # 第二层
    for parent_index_id in editable_index_list:
        if parent_index_id in external_index.keys():
            parent_item = external_index[parent_index_id]

            the_keys = set( parent_item.keys() )
            the_other_keys = the_keys - {"FOLDER_SETTINGS","ROOT_FOLDER"}
            if the_other_keys :
                editable_index_has_children[parent_index_id] = sorted( the_other_keys )


####################
def get_id_list_from_index(id_1,id_2="",):
    # 拥有列表、未拥有列表
    # 内部目录
    # 外部目录
    # 外部目录 by source

    temp_result = []

    # 拥有列表
    if id_1 == "available_set":
        temp_result = available_set
    # 未拥有列表
    elif id_1 == "unavailable_set":
        if available_set:
            temp_result = all_set - available_set
        else:
            temp_result = all_set 
    # 外部目录
    elif id_1.lower().endswith(".ini"):
        temp_result = misc_funcs.get_id_list_from_external_index(id_1,id_2)
    # 外部目录 by source
    elif id_1.lower().endswith(".source_ini"):
        temp_result = misc_funcs.get_id_list_from_external_index_by_source(id_1,id_2)
    # 内部目录
    else:
        temp_result = misc_funcs.get_id_list_from_internal_index(id_1,id_2)

    return temp_result
#
@the_timer
def get_id_list_from_index_and_filter(id_1,id_2="",):
    # 拥有列表、未拥有列表
    # 内部目录
    # 外部目录
    # 外部目录 by source

    temp_result = get_id_list_from_index(id_1,id_2)

    # 过滤
    if filter_set:
    # 过滤
        if all_set is temp_result:
            return all_set - filter_set
        else:
            return all_set.intersection(temp_result) - filter_set
    else:
    # 不过滤
        if all_set is temp_result:
            return all_set
        else:
            return all_set.intersection(temp_result)
#
def get_illegal_id_list_from_index(id_1,id_2="",):
    temp_result = get_id_list_from_index(id_1,id_2)
    return set(temp_result) - all_set

#########################
# for test
def set_game_list_to_all():
    global game_list
    game_list = list(machine_dict.keys())
###################

def get_string_for_statusbar(game_id):
        if game_id not in machine_dict:
            return ""
        
        game_info = machine_dict[game_id]

        cloneof = game_info[cloneof_column_index]
        if cloneof:cloneof = "主版本为: " + cloneof
        
        romof = game_info[romof_column_index]
        if romof:romof = "romof: " + romof
        
        status = game_info[status_column_index]
        if status:status = "模拟状态: " + status
        
        savestate = game_info[savestate_column_index]
        if savestate:savestate = "存盘状态: " + savestate

        temp_list = []
        for x in [game_id,cloneof,romof,status,savestate]:
            if x:
                temp_list.append(x)

        return " | ".join(temp_list)

# mameinfo.dat 里需要用到
def get_sourcefile(game_id):
    sourcefile = ""

    if game_id in machine_dict:
        sourcefile = machine_dict[game_id][sourcefile_column_index]
        if sourcefile:
            sourcefile = os.path.basename(sourcefile)

    return sourcefile

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

    # search_columns,多个时，operator.itemgetter 返回的是一个列表
    # search_columns,一个时，operator.itemgetter 返回的是一个值，不如不用它了
    if flag_search_all:
        # 每个搜索单元为一个列表，元素为 str
        for iteralble_object in  search_object_list:
            temp_result_list = list( filter( lambda game_id:first_true( machine_dict[game_id] ) , iteralble_object ) ) 
            result_list.extend(temp_result_list)
    elif len(search_columns)==1:
        # 每个搜索单元为 str
        column_index = search_columns[0]
        for iteralble_object in  search_object_list:
            temp_result_list = list( filter( lambda game_id:p.search( machine_dict[game_id][column_index] ) , iteralble_object ) ) 
            result_list.extend(temp_result_list)
    else:
        # 每个搜索单元为一个列表，元素为 str
        search_columns = sorted(set(search_columns))
        get_column_text_list = operator.itemgetter(*search_columns)
        for iteralble_object in  search_object_list:
            temp_result_list = list( filter( lambda game_id:first_true( get_column_text_list(machine_dict[game_id]) ) , iteralble_object ) ) 
            result_list.extend(temp_result_list)

    re.purge()
    return result_list

def func_for_find_same_value_in_same_colmun(value,column,search_object_list=None):
    if search_object_list is None:
        return []

    result_list = []

    column_index = column
    for iteralble_object in  search_object_list:
        temp_result_list = list( filter( lambda game_id: value ==  machine_dict[game_id][column_index] , iteralble_object ) ) 
        result_list.extend(temp_result_list)

    return result_list

def func_for_index_search(search_string,use_re=False,ignore_case=True,):
    # 都用 re 写吧，正常的搜索也写成 re 模式，少写一次代码
    #print("func_for_index_search")

    if use_re:
        re_string = search_string
    else:
        re_string = re.escape(search_string)
    
    if ignore_case:
        p=re.compile(re_string,re.IGNORECASE)
    else:
        p=re.compile(re_string)
    
    new_list = []
    new_list_have_children = dict()
    
    #print(len(index_list_backup))
    #print(len(index_has_children_backup))

    for index_id in index_list_backup:
        temp_children_list =[]
        if index_id in index_has_children_backup:
            for child_id in index_has_children_backup[index_id]:
                if p.search(child_id):
                    temp_children_list.append(child_id)
        
        if temp_children_list:
            new_list_have_children[index_id] = temp_children_list
            new_list.append(index_id)
        else:
            if index_id.lower().endswith(".ini") or index_id.lower().endswith(".source_ini"):
                the_text = os.path.basename(index_id)
            else:
                the_text = the_variables.index_translation.get(index_id,index_id)
            
            if p.search(the_text):
                new_list.append(index_id)
                    
    return new_list,new_list_have_children


def get_icon_for_gamelist_table(game_id):
    #use_icon_not_have = False
    #use_icon_extra_resource = False

    value = machine_dict[ game_id ] [ icon_column_index ]

    # default icon
    if value == "good":
        the_icon =  icon_green_pixmap
    elif value == "imperfect":
        the_icon =  icon_yellow_pixmap
    elif value == "preliminary":
        the_icon =  icon_red_pixmap
    else:
        the_icon =  icon_black_pixmap

    if the_variables.use_icon_extra_resource:
    # 使用额外 icon 资源包
        if game_id in icon_extra_resource:
            try:
                user_icon = QPixmap()
                if user_icon.loadFromData(icon_extra_resource[game_id],format="ICO"):
                    the_icon = user_icon
                    if (user_icon.width() != the_variables.icon_size) or (user_icon.height() != the_variables.icon_size):
                        scaled_pixmap = user_icon.scaled(
                            the_variables.icon_size,the_variables.icon_size,                  # 目标大小
                            Qt.KeepAspectRatio,
                            Qt.SmoothTransformation
                            )
                        the_icon = scaled_pixmap
            except:
                pass
 
    if the_variables.use_icon_not_have:
        if game_id not in available_set:
            size = 	QSize(the_variables.icon_size ,the_variables.icon_size)
            new_icon = QPixmap(size)
            new_icon.fill(Qt.transparent)
            painter = QPainter()
            painter.begin(new_icon)
            painter.drawPixmap(0, 0,the_icon)
            painter.drawPixmap(0, 0,icon_not_have_pixmap)
            painter.end()
            return new_icon

    return the_icon

def get_icon_for_gamelist_table_fake_2_level(game_id):
    #use_icon_not_have = False
    #use_icon_extra_resource = False

    value = machine_dict[ game_id ] [ icon_column_index ]

    # default icon
    if value == "good":
        the_icon =  icon_green_pixmap
    elif value == "imperfect":
        the_icon =  icon_yellow_pixmap
    elif value == "preliminary":
        the_icon =  icon_red_pixmap
    else:
        the_icon =  icon_black_pixmap

    if the_variables.use_icon_extra_resource:
    # 使用额外 icon 资源包
        if game_id in icon_extra_resource:
            try:
                user_icon = QPixmap()
                if user_icon.loadFromData(icon_extra_resource[game_id],format="ICO"):
                    the_icon = user_icon
                    if (user_icon.width() != the_variables.icon_size) or (user_icon.height() != the_variables.icon_size):
                        scaled_pixmap = user_icon.scaled(
                            the_variables.icon_size,the_variables.icon_size,                  # 目标大小
                            Qt.KeepAspectRatio,            # 保持宽高比[reference:5]
                            Qt.SmoothTransformation        # 平滑变换[reference:6]
                            )
                        the_icon = scaled_pixmap
            except:
                pass
 
    # 画一个前部为空白的长条图标
    size = 	QSize(the_variables.icon_size * 2,the_variables.icon_size)
    new_icon = QPixmap(size)
    new_icon.fill(Qt.transparent)
    painter = QPainter()
    painter.begin(new_icon)
    painter.drawPixmap(the_variables.icon_size, 0,the_icon)
    if the_variables.use_icon_not_have:
        if game_id not in available_set:
            painter.drawPixmap(the_variables.icon_size, 0,icon_not_have_pixmap)
    painter.end()
    return new_icon

def get_icon_for_icon_table(game_id):
    #use_icon_not_have = False
    #use_icon_extra_resource = False

    value = machine_dict[ game_id ] [ icon_column_index ]

    # default icon
    if value == "good":
        the_icon =  icon_green_pixmap_for_icon_table
    elif value == "imperfect":
        the_icon =  icon_yellow_pixmap_for_icon_table
    elif value == "preliminary":
        the_icon =  icon_red_pixmap_for_icon_table
    else:
        the_icon =  icon_black_pixmap_for_icon_table

    # 使用额外 icon 资源包
    if game_id in icon_extra_resource:
        try:
            user_icon = QPixmap()
            if user_icon.loadFromData(icon_extra_resource[game_id],format="ICO"):
                the_icon = user_icon
                if (user_icon.width() != icon_size_for_icon_table) or (user_icon.height() != icon_size_for_icon_table):
                    scaled_pixmap = user_icon.scaled(
                        icon_size_for_icon_table,icon_size_for_icon_table,# 目标大小
                        Qt.KeepAspectRatio,
                        Qt.SmoothTransformation
                        )
                    the_icon = scaled_pixmap
            else:
                print(game_id,"   loadFromData failed !")
        except:
            pass
 
    if the_variables.use_icon_not_have:
        if game_id not in available_set:
            size = 	QSize(icon_size_for_icon_table ,icon_size_for_icon_table)
            new_icon = QPixmap(size)
            new_icon.fill(Qt.transparent)
            painter = QPainter()
            painter.begin(new_icon)
            painter.drawPixmap(0, 0,the_icon)
            painter.drawPixmap(0, 0,icon_not_have_pixmap_for_icon_table)
            painter.end()
            return new_icon

    return the_icon


def get_sort_func(column=None,reverse=None):# return function or None
        # 未指定值，则，读取默认值
        if column is None:
            column = the_variables.sort_column
        if reverse is None:
            reverse = the_variables.sort_reverse

        if type(column) is not int:
            column = 0
        
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
        if the_variables.sort_use_locale:
            if column in the_variables.sort_colums_use_locale:
                sort_key_func = sort_key_func_1
        if column == id_column_index:
            sort_key_func = None

        return sort_key_func 

#########################
#########################
#########################
class Model_for_table_view(QAbstractTableModel):
    
    singalGamelistNumberChanged = Signal(int)

    new_signal_time_for_choose_remember_game = Signal() 
        # 发信号，后续看是否需要定位到上次选中的游戏
        # 以下三个地方，都需要发送信号
            # sort() 
            # new_func_show_by_index()
            # new_func_show_search_result()
    
    new_signal_need_reload_gamelist = Signal()


    def __init__(self,*args,**kwargs):
        super().__init__(*args,**kwargs)

        self.setObjectName("modelForTableView")
        self.new_table_type = "table_view_1_level"

        self.new_game_list_to_show=[]

        self.new_remember_index_id_1 = ""
        self.new_remember_index_id_2 = ""
        self.new_search_flag = False

    def data(self, index, role=Qt.DisplayRole):
        if not index.isValid():
            return None

        if role == Qt.DisplayRole:
            return machine_dict[ self.new_game_list_to_show[index.row()] ] [ index.column() ]
        elif role == Qt.DecorationRole:
            if index.column() == 0:
                return get_icon_for_gamelist_table( self.new_game_list_to_show[index.row()] )
        elif role == Qt.EditRole:
            return self.data(index, Qt.DisplayRole)
        elif role ==Qt.CheckStateRole:
            if multi_selection_mode:
                if index.column()==0:
                    game_id = self.new_game_list_to_show[index.row()]
                    if game_id in the_selected_items:
                        return Qt.Checked
                    else:
                        return Qt.Unchecked

    def headerData(self,section,orientation,role=Qt.DisplayRole):
        if role == Qt.DisplayRole:
            if orientation == Qt.Horizontal:
                if section < len(columns):
                    return the_variables.columns_translation.get(columns[section],columns[section])

            if orientation == Qt.Vertical:
                return str(section)

    def rowCount(self, parent=QModelIndex()):
        return len(self.new_game_list_to_show)

    def columnCount(self, parent=QModelIndex()):  
        # 相同长度
        return len(columns)

    #编辑 flags()
    def flags(self, index: QModelIndex) -> Qt.ItemFlags:
        if not index.isValid():
            return Qt.NoItemFlags
        
        if index.column()==0:
            if multi_selection_mode:
                return super().flags(index) | Qt.ItemIsUserCheckable 
        elif index.column() == translation_column_index:
            if gamelist_editable_mode:
                return super().flags(index) | Qt.ItemIsEditable

        #return super().flags(index) & ( ~ Qt.ItemIsEditable ) & ( ~ Qt.ItemIsUserCheckable )
        return super().flags(index)
    
    #编辑 setData()
    def setData(self, index, value, role=Qt.EditRole):
        
        if index.isValid():
            
            if role == Qt.EditRole:
                if index.column() == translation_column_index:
                    game_id, game_info = self.new_func_get_id_and_item_by_index(index)
                    game_info[translation_column_index] = value
                    #machine_dict[game_id] = game_info
                    self.dataChanged.emit(index, index, [role] )
                    return True
        
            #Qt::Unchecked	0	The item is unchecked.
            #Qt::PartiallyChecked	1	The item is partially checked. Items in hierarchical models may be partially checked if some, but not all, of their children are checked.
            #Qt::Checked	2	The item is checked.
            elif role == Qt.CheckStateRole:
                if index.column() ==0:
                    game_id, game_info = self.new_func_get_id_and_item_by_index(index)
                    if value==2:
                        the_selected_items.add(game_id)
                    elif value == 0:
                        the_selected_items.discard(game_id)
                    self.dataChanged.emit(index, index, [role])
                    return True
        
        return False

    def new_func_get_id_and_item_by_index(self, index):
        row = index.row()
        game_id = self.new_game_list_to_show[row]
        return game_id, machine_dict[ game_id ] 

    def new_func_get_item_id_by_index(self, index):
        row = index.row()
        game_id = self.new_game_list_to_show[row]
        return game_id

    def new_func_get_item_id_by_row(self, row):
        game_id = ""
        if (row >= 0) and (row < len(self.new_game_list_to_show)):
            game_id = self.new_game_list_to_show[row]
        return game_id

    def new_func_get_index_by_game_id(self,game_id,column=0):
        result = QModelIndex()

        if not game_id:
            return result
        
        if not self.new_game_list_to_show:
            return result
        
        try:
            row = self.new_game_list_to_show.index(game_id)
        except:
            return result
        
        return self.index(row,column)

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

        # 发送信号
        self.new_signal_time_for_choose_remember_game.emit()

    
    @the_timer
    def new_func_for_sort(self,column=None,reverse=None):
        if reverse is None:
            reverse = the_variables.sort_reverse
        if column is None:
            column = the_variables.sort_column
        
        sort_key_func = get_sort_func(column,reverse)
        
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

        # 记录
        self.new_remember_index_id_1 = id_1
        self.new_remember_index_id_2 = id_2
        self.new_search_flag = False
        
        ###
        self.beginResetModel()
        
        self.new_func_clear_all_data()

        # 取值
        self.new_game_list_to_show = get_id_list_from_index_and_filter(id_1,id_2) # set
        #   取值,未过滤时，都是 传地址地来的。 set or list
        #   经过 过滤后，用 all_set 过滤，再减去用户设定的过滤项，传地址过来的，只有可能会剩下 all_set （过滤项为空时） 。 set
        #   在下面 排序时，注意不要修改
        #   这里得到的都是 set 类型，需要的是 list , 正好也不容易被修改

        # 排序
        self.new_func_for_sort()

        # 数量信号
        self.new_func_numbers_changed()



        ###
        self.endResetModel()

        # 发送信号
        self.new_signal_time_for_choose_remember_game.emit()
    
    # 列表搜索，显示搜索结果
    def new_func_show_search_result(self,search_string,use_re=False,ignore_case=True,search_columns=tuple()):
        print("")
        print("show search result")

        self.beginResetModel()

        self.new_func_clear_all_data()

        id_1 = self.new_remember_index_id_1
        id_2 = self.new_remember_index_id_2
        self.new_search_flag = True

        # 取值，搜索范围
        temp_game_ids =  get_id_list_from_index_and_filter(id_1,id_2) 
        
        # 搜索
        self.new_game_list_to_show = func_for_search(search_string,search_object_list=[temp_game_ids,],use_re=use_re,ignore_case=ignore_case,search_columns=search_columns)
        
        # 排序
        self.new_func_for_sort()

        # 数量信号
        self.new_func_numbers_changed()

        self.endResetModel()

        # 发送信号
        self.new_signal_time_for_choose_remember_game.emit()

    # 删除一个游戏，从表格菜单中选择删除
    def new_func_remove_one_item_by_index(self,index):
        if not index_edit_mode:
            return

        id_1,id_2 = self.new_remember_index_id_1,self.new_remember_index_id_2
        if not id_1:
            return
        if id_1 not in editable_index_files:
            return

        if index.isValid():

            row = index.row()

            game_id = self.new_game_list_to_show[ row ]

            # 当前列表，删除
            self.beginRemoveRows(QModelIndex(),row,row)
            del self.new_game_list_to_show[ row : row+1 ]
            self.endRemoveRows()

            # 目录文件，删除
            misc_funcs.delect_one_item_from_external_index(game_id,id_1,id_2)

            self.new_func_numbers_changed()

    # 多选删除，当前列表中，删除勾选的游戏
    def new_func_remove_selected_items(self):
        # 未修改当前列表的数据
        # 修改外面的数据，完成后，列表需要重载
        # centeral_widget new_func_reload_gamelist()

        
        if not index_edit_mode:
            return
        
        if not multi_selection_mode:
            return

        print(len(the_selected_items))
        if not the_selected_items: # 空
            return
        print("aaa")
        id_1,id_2 = self.new_remember_index_id_1,self.new_remember_index_id_2
        print("aaaa",id_1,id_2)

        if not id_1:
            return
        
        if id_1 not in editable_index_files:
            return

        print("xxxx",id_1,id_2)
        misc_funcs.delect_items_from_external_index(the_selected_items,id_1,id_2)

        self.new_signal_need_reload_gamelist.emit()

    def new_func_clear_all_data(self):
        print("clear data")
        self.new_game_list_to_show = []

    def new_func_clear_search_data(self):
        pass

    def new_func_cancel_search(self):
        if not self.new_search_flag:
            return
        
        self.new_search_flag = False

        id_1,id_2 = self.new_remember_index_id_1,self.new_remember_index_id_2
        self.new_func_show_by_index(id_1,id_2)

    def new_func_numbers_changed(self):
        game_list_number = len(self.new_game_list_to_show)
        self.singalGamelistNumberChanged.emit(game_list_number)

    def new_func_select_all_items(self):
        if not multi_selection_mode:
            return

        global the_selected_items
        the_selected_items = set(self.new_game_list_to_show)
        print(len(the_selected_items))

        if self.new_game_list_to_show:
            index_first = self.index(0,0)
            index_last  = self.index(len(self.new_game_list_to_show)-1,0)
            self.dataChanged.emit(index_first, index_last, [Qt.CheckStateRole])

    def new_func_deselect_all_items(self):
        if not multi_selection_mode:
            return
        
        the_selected_items.clear()
        print(len(the_selected_items))

        if self.new_game_list_to_show:
            index_first = self.index(0,0)
            index_last  = self.index(len(self.new_game_list_to_show)-1,0)
            self.dataChanged.emit(index_first, index_last, [Qt.CheckStateRole])        

    def new_func_select_reverse(self):
        if not multi_selection_mode:
            return

        global the_selected_items
        the_selected_items = set(self.new_game_list_to_show) - the_selected_items
        print(len(the_selected_items))
      
        if self.new_game_list_to_show:            
            index_first = self.index(0,0)
            index_last  = self.index(len(self.new_game_list_to_show)-1,0)
            self.dataChanged.emit(index_first, index_last, [Qt.CheckStateRole])            

    def new_func_select_same_type_items(self,index):
        if not multi_selection_mode:
            return

        if not index.isValid():
            return

        column = index.column()
        search_columns = tuple([column])

        cell_data = self.data(index,Qt.DisplayRole)

        reuslt = func_for_find_same_value_in_same_colmun(
                cell_data,
                column,
                search_object_list=[self.new_game_list_to_show],
                )

        the_selected_items.clear()
        the_selected_items.update(reuslt)

        if self.new_game_list_to_show:
            index_first = self.index(0,0)
            index_last  = self.index(len(self.new_game_list_to_show)-1,0)
            self.dataChanged.emit(index_first, index_last, [Qt.CheckStateRole])

    def new_func_add_parent_game(self):
        
        if not index_edit_mode:
            return

        id_1,id_2 = self.new_remember_index_id_1,self.new_remember_index_id_2

        if not id_1:
            return
        
        if id_1 not in editable_index_files:
            return

        
        result = []
        for game_id in self.new_game_list_to_show:
            result.append(game_id)
            if game_id in clone_set:
                result.append(clone_to_parent[game_id])

        result = set(result)

        new_games = result - set(self.new_game_list_to_show)

        if new_games :

            misc_funcs.add_items_to_external_index(new_games,id_1,id_2)

            self.new_signal_need_reload_gamelist.emit()

    def new_func_add_colne_game(self):
        if not index_edit_mode:
            return

        id_1,id_2 = self.new_remember_index_id_1,self.new_remember_index_id_2

        if not id_1:
            return
        
        if id_1 not in editable_index_files:
            return

        
        result = []
        for game_id in self.new_game_list_to_show:
            result.append(game_id)
            if game_id in parent_to_clone:
                result.extend(parent_to_clone[game_id])

        result = set(result)

        new_games = result - set(self.new_game_list_to_show)

        if new_games :

            misc_funcs.add_items_to_external_index(new_games,id_1,id_2)

            self.new_signal_need_reload_gamelist.emit()

    def new_func_delete_parent_game(self):
        
        if not index_edit_mode:
            return

        id_1,id_2 = self.new_remember_index_id_1,self.new_remember_index_id_2

        if not id_1:
            return
        
        if id_1 not in editable_index_files:
            return

        
        result = []
        for game_id in self.new_game_list_to_show:
            if game_id in parent_set:
                result.append(game_id)

        result = set(result)

        if result :

            misc_funcs.delect_items_from_external_index(result,id_1,id_2)

            self.new_signal_need_reload_gamelist.emit()

    def new_func_delete_clone_game(self):
        
        if not index_edit_mode:
            return

        id_1,id_2 = self.new_remember_index_id_1,self.new_remember_index_id_2

        if not id_1:
            return
        
        if id_1 not in editable_index_files:
            return

        
        result = []
        for game_id in self.new_game_list_to_show:
            if game_id in clone_set:
                result.append(game_id)

        result = set(result)

        if result :

            misc_funcs.delect_items_from_external_index(result,id_1,id_2)

            self.new_signal_need_reload_gamelist.emit()

class Model_for_table_view_2_level(QAbstractTableModel):
    
    singalGamelistNumberChanged = Signal(int)
    new_signal_time_for_choose_remember_game = Signal() # 发信号，后续看是否需要定位到上次选中的游戏
    new_signal_need_reload_gamelist = Signal() 


    def __init__(self,*args,**kwargs):
        super().__init__(*args,**kwargs)

        self.setObjectName("modelForTableView2")
        self.new_table_type = "table_view_2_level"

        self.new_game_list_to_show=[] # 这个是显示用的
        
        self.new_parent_set=set()
        self.new_clone_set=set()
        self.new_clone_have_parent=set() # 图标处也用这个
        self.new_clone_not_have_parent=set() 
        #self.new_parent_have_clone=set() # 同下面 keys
        self.new_parent_to_clone=dict() 

        self.new_remember_index_id_1 = ""
        self.new_remember_index_id_2 = ""
        self.new_search_flag = False
        
    def data(self, index, role=Qt.DisplayRole):
        if not index.isValid():
            return None
        
        if role == Qt.DisplayRole:
            return machine_dict[ self.new_game_list_to_show[index.row()] ] [ index.column() ]
        elif role == Qt.DecorationRole:
            if index.column() == 0:
                game_id = self.new_game_list_to_show[index.row()]
                if game_id in self.new_clone_have_parent:
                    return get_icon_for_gamelist_table_fake_2_level(game_id)
                else:
                    return get_icon_for_gamelist_table(game_id)
        elif role == Qt.EditRole:
            return self.data(index, Qt.DisplayRole)
        elif role ==Qt.CheckStateRole:
            if multi_selection_mode:
                if index.column()==0:
                    game_id = self.new_game_list_to_show[index.row()]
                    if game_id in the_selected_items:
                        return Qt.Checked
                    else:
                        return Qt.Unchecked

    def headerData(self,section,orientation,role=Qt.DisplayRole):
        if role == Qt.DisplayRole:
            if orientation == Qt.Horizontal:
                if section < len(columns):
                    return the_variables.columns_translation.get(columns[section],columns[section])

            if orientation == Qt.Vertical:
                return str(section)

    def rowCount(self, parent=QModelIndex()):
        return len(self.new_game_list_to_show)

    def columnCount(self, parent=QModelIndex()):  
        # 相同长度
        return len(columns)

    #编辑 flags()
    def flags(self, index: QModelIndex) -> Qt.ItemFlags:
        if not index.isValid():
            return Qt.NoItemFlags
        
        if index.column()==0:
            if multi_selection_mode:
                return super().flags(index) | Qt.ItemIsUserCheckable 
        elif index.column() == translation_column_index:
            if gamelist_editable_mode:
                return super().flags(index) | Qt.ItemIsEditable

        #return super().flags(index) & ( ~ Qt.ItemIsEditable ) & ( ~ Qt.ItemIsUserCheckable )
        return super().flags(index)
    
    #编辑 setData()
    def setData(self, index, value, role=Qt.EditRole):
        
        if index.isValid():
            
            if role == Qt.EditRole:
                if index.column() == translation_column_index:
                    game_id, game_info = self.new_func_get_id_and_item_by_index(index)
                    game_info[translation_column_index] = value
                    #machine_dict[game_id] = game_info
                    self.dataChanged.emit(index, index, [role] )
                    return True
        
            #Qt::Unchecked	0	The item is unchecked.
            #Qt::PartiallyChecked	1	The item is partially checked. Items in hierarchical models may be partially checked if some, but not all, of their children are checked.
            #Qt::Checked	2	The item is checked.
            elif role == Qt.CheckStateRole:
                if index.column() ==0:
                    game_id, game_info = self.new_func_get_id_and_item_by_index(index)
                    if value==2:
                        the_selected_items.add(game_id)
                    elif value == 0:
                        the_selected_items.discard(game_id)
                    self.dataChanged.emit(index, index, [role])
                    return True
        
        return False

    def new_func_get_id_and_item_by_index(self, index):
        row = index.row()
        game_id = self.new_game_list_to_show[row]
        return game_id, machine_dict[ game_id ] 

    def new_func_get_item_id_by_index(self, index):
        row = index.row()
        game_id = self.new_game_list_to_show[row]
        return game_id 

    def new_func_get_item_id_by_row(self, row):
        game_id = ""
        if (row >= 0) and (row < len(self.new_game_list_to_show)):
            game_id = self.new_game_list_to_show[row]
        return game_id

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
        
        self.new_func_sort_part_2(column,reverse)
        
        ###
        #self.layoutChanged.emit()
        self.endResetModel()

        # 发送信号
        self.new_signal_time_for_choose_remember_game.emit()
    
    # 数据准备
    @the_timer
    def new_func_sort_part_1(self,games_to_be_sorted=None):
        # 清空
        self.new_func_clear_all_data()

        if games_to_be_sorted is None:
            games_to_be_sorted = []

        if not games_to_be_sorted:
            # 空值
            return  # 之前已清空所有值


        if games_to_be_sorted is all_set:
            current_parent = parent_set
            current_clone = clone_set 
        else:
            if not isinstance(games_to_be_sorted,set):
                games_to_be_sorted = set(games_to_be_sorted)
            current_parent = parent_set & games_to_be_sorted
            current_clone = clone_set & games_to_be_sorted

        self.new_parent_set = current_parent
        self.new_clone_set = current_clone

        #### 空
        if ( not current_parent)  and ( not current_clone): 
            # 非空值，但超范围 都被过虑了 ，剩余空值
            return # 之前已清空所有值
        
        #### 半空
        if not current_parent:
            self.new_clone_not_have_parent = current_clone
            return # 其它值已清空
        
        #### 半空 2
        if not current_clone:
            return # 其它值已清空

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

        # current_parent_to_clone
        current_parent_to_clone = dict()
        for clone_id in current_clone_have_parent:
            parent_id = clone_to_parent[clone_id]
            current_parent_to_clone.setdefault(parent_id,[]).append(clone_id)
        
        self.new_clone_have_parent = current_clone_have_parent
        self.new_clone_not_have_parent = current_clone_not_have_parent
        self.new_parent_to_clone=current_parent_to_clone

    # 排序
    @the_timer
    def new_func_sort_part_2(self,column=None,reverse=None):

        if ( not self.new_parent_set) and ( not self.new_clone_set):
            self.new_game_list_to_show = []
            return

        if reverse is None:
            reverse = the_variables.sort_reverse
        if column is None:
            column = the_variables.sort_column
        
        sort_key_func = get_sort_func(column,reverse)

        game_list_for_levle_1 = list( self.new_parent_set | self.new_clone_not_have_parent )

        # 第一层排序
        game_list_for_levle_1.sort(key = sort_key_func ,reverse = reverse, )

        if not self.new_parent_to_clone:
            # 仅一层
            self.new_game_list_to_show = game_list_for_levle_1
            return
        else:
            # 两层
            temp_list = []
            for game_id in game_list_for_levle_1:
                temp_list.append(game_id)
                if game_id in self.new_parent_to_clone:
                    self.new_parent_to_clone[game_id].sort( key = sort_key_func,reverse = reverse,)
                    temp_list.extend( self.new_parent_to_clone[game_id] )
            self.new_game_list_to_show = temp_list
            return

    # 目录发出信号
    # 显示新内容
    def new_func_show_by_index(self,id_1,id_2):
        print("")
        print("show by index")
        print("id_1: ",id_1)
        print("id_2: ",id_2)

        self.new_remember_index_id_1 = id_1
        self.new_remember_index_id_2 = id_2
        self.new_search_flag = False

        ###
        self.beginResetModel()
        
        self.new_func_clear_all_data()

        self.new_func_sort_part_1( get_id_list_from_index_and_filter(id_1,id_2) )
        self.new_func_sort_part_2()

        self.new_func_numbers_changed()

        ###
        self.endResetModel()

        # 发送信号
        self.new_signal_time_for_choose_remember_game.emit()
    
    # 列表搜索，显示搜索结果
    def new_func_show_search_result(self,search_string,use_re=False,ignore_case=True,search_columns=tuple()):
        print("")
        print("show search result")
        print("search_string: ",search_string)   

        id_1 = self.new_remember_index_id_1
        id_2 = self.new_remember_index_id_2
        self.new_search_flag = True

        ###
        self.beginResetModel()
        #self.layoutAboutToBeChanged.emit()

        self.new_func_clear_all_data()
        
        # 搜索范围
        temp_game_ids  =  get_id_list_from_index_and_filter(id_1,id_2) 
        # 搜索结果
        temp_game_ids = func_for_search(search_string,search_object_list=[temp_game_ids,],use_re=use_re,ignore_case=ignore_case,search_columns=search_columns)
        # 排序
        self.new_func_sort_part_1(temp_game_ids)
        self.new_func_sort_part_2()

        self.new_func_numbers_changed()

        ###
        #self.layoutChanged.emit()
        self.endResetModel()

        # 发送信号
        self.new_signal_time_for_choose_remember_game.emit()

    def new_func_clear_all_data(self):
        print("clear data")

        self.new_game_list_to_show=[]
        
        self.new_parent_set=set()
        self.new_clone_set=set()
        self.new_clone_have_parent=set()
        self.new_clone_not_have_parent=set() 
        #self.new_parent_have_clone=set() # 同下面 keys
        self.new_parent_to_clone=dict()

    def new_func_clear_search_data(self):
        pass

    def new_func_get_index_by_game_id(self,game_id):
        result = QModelIndex()

        if not game_id:
            return result
        
        if not self.new_game_list_to_show:
            return result
        
        if (game_id not in self.new_clone_set) and (game_id not in self.new_parent_set):
            return result
        
        try:
            row = self.new_game_list_to_show.index(game_id)
        except:
            return result # 应该在有的，除非哪里出错了
        
        return self.index(row,0)

    def new_func_cancel_search(self):
        if not self.new_search_flag:
            return
        
        self.new_search_flag = False

        id_1,id_2 = self.new_remember_index_id_1,self.new_remember_index_id_2
        self.new_func_show_by_index(id_1,id_2)

    # 删除一个游戏，从表格菜单中选择删除
    #  可编辑的 自定义目录，通常都比较小。
    #  这样，删除后，直接重置列表，代码简点，对于小列表来说，也挺快。
    def new_func_remove_one_item_by_index(self,index):
        if not index_edit_mode:
            return

        id_1,id_2 = self.new_remember_index_id_1,self.new_remember_index_id_2
        if not id_1:
            return
        if id_1 not in editable_index_files:
            return

        if index.isValid():

            row = index.row()

            game_id = self.new_game_list_to_show[ row ]

            ###################
            # 目录文件，删除
            misc_funcs.delect_one_item_from_external_index(game_id,id_1,id_2)

            ###################
            # 重置列表
            self.new_signal_need_reload_gamelist.emit()
    #    
    # 多选删除，当前列表中，删除勾选的游戏
    def new_func_remove_selected_items(self):
        # 未修改当前列表的数据
        # 修改外面的数据，完成后，列表需要重载
        # centeral_widget new_func_reload_gamelist()

        if not index_edit_mode:
            return
        
        if not multi_selection_mode:
            return
        
        if not the_selected_items: # 空
            return
        
        id_1,id_2 = self.new_remember_index_id_1,self.new_remember_index_id_2

        if not id_1:
            return
        
        if id_1 not in editable_index_files:
            return

        misc_funcs.delect_items_from_external_index(the_selected_items,id_1,id_2)

        self.new_signal_need_reload_gamelist.emit()

    def new_func_numbers_changed(self):
        game_list_number = len(self.new_game_list_to_show)
        self.singalGamelistNumberChanged.emit(game_list_number)

    def new_func_select_all_items(self):
        if not multi_selection_mode:
            return

        global the_selected_items
        the_selected_items = set(self.new_game_list_to_show)
        print(len(the_selected_items))

        if self.new_game_list_to_show:
            index_first = self.index(0,0)
            index_last  = self.index(len(self.new_game_list_to_show)-1,0)
            self.dataChanged.emit(index_first, index_last, [Qt.CheckStateRole])

    def new_func_deselect_all_items(self):
        if not multi_selection_mode:
            return
        
        the_selected_items.clear()
        print(len(the_selected_items))

        if self.new_game_list_to_show:
            index_first = self.index(0,0)
            index_last  = self.index(len(self.new_game_list_to_show)-1,0)
            self.dataChanged.emit(index_first, index_last, [Qt.CheckStateRole])        

    def new_func_select_reverse(self):
        if not multi_selection_mode:
            return

        global the_selected_items
        the_selected_items = set(self.new_game_list_to_show) - the_selected_items
        print(len(the_selected_items))
      
        if self.new_game_list_to_show:            
            index_first = self.index(0,0)
            index_last  = self.index(len(self.new_game_list_to_show)-1,0)
            self.dataChanged.emit(index_first, index_last, [Qt.CheckStateRole])       

    def new_func_select_same_type_items(self,index):
        if not multi_selection_mode:
            return

        if not index.isValid():
            return

        column = index.column()
        search_columns = tuple([column])

        cell_data = self.data(index,Qt.DisplayRole)

        reuslt = func_for_find_same_value_in_same_colmun(
                cell_data,
                column,
                search_object_list=[self.new_game_list_to_show],
                )

        the_selected_items.clear()
        the_selected_items.update(reuslt)

        if self.new_game_list_to_show:
            index_first = self.index(0,0)
            index_last  = self.index(len(self.new_game_list_to_show)-1,0)
            self.dataChanged.emit(index_first, index_last, [Qt.CheckStateRole])

    def new_func_add_parent_game(self):
        
        if not index_edit_mode:
            return

        id_1,id_2 = self.new_remember_index_id_1,self.new_remember_index_id_2

        if not id_1:
            return
        
        if id_1 not in editable_index_files:
            return

        
        result = []
        for game_id in self.new_game_list_to_show:
            result.append(game_id)
            if game_id in clone_set:
                result.append(clone_to_parent[game_id])

        result = set(result)

        new_games = result - set(self.new_game_list_to_show)

        if new_games :

            misc_funcs.add_items_to_external_index(new_games,id_1,id_2)

            self.new_signal_need_reload_gamelist.emit()

    def new_func_add_colne_game(self):
        if not index_edit_mode:
            return

        id_1,id_2 = self.new_remember_index_id_1,self.new_remember_index_id_2

        if not id_1:
            return
        
        if id_1 not in editable_index_files:
            return

        
        result = []
        for game_id in self.new_game_list_to_show:
            result.append(game_id)
            if game_id in parent_to_clone:
                result.extend(parent_to_clone[game_id])

        result = set(result)

        new_games = result - set(self.new_game_list_to_show)

        if new_games :

            misc_funcs.add_items_to_external_index(new_games,id_1,id_2)

            self.new_signal_need_reload_gamelist.emit()

    def new_func_delete_parent_game(self):
        
        if not index_edit_mode:
            return

        id_1,id_2 = self.new_remember_index_id_1,self.new_remember_index_id_2

        if not id_1:
            return
        
        if id_1 not in editable_index_files:
            return

        
        result = []
        for game_id in self.new_game_list_to_show:
            if game_id in parent_set:
                result.append(game_id)

        result = set(result)

        if result :

            misc_funcs.delect_items_from_external_index(result,id_1,id_2)

            self.new_signal_need_reload_gamelist.emit()

    def new_func_delete_clone_game(self):
        
        if not index_edit_mode:
            return

        id_1,id_2 = self.new_remember_index_id_1,self.new_remember_index_id_2

        if not id_1:
            return
        
        if id_1 not in editable_index_files:
            return

        
        result = []
        for game_id in self.new_game_list_to_show:
            if game_id in clone_set:
                result.append(game_id)

        result = set(result)

        if result :

            misc_funcs.delect_items_from_external_index(result,id_1,id_2)

            self.new_signal_need_reload_gamelist.emit()

class Model_for_table_view_2_level_tree_like(QAbstractTableModel):
    
    singalGamelistNumberChanged = Signal(int)
    new_signal_time_for_choose_remember_game = Signal() # 发信号，后续看是否需要定位到上次选中的游戏
    new_signal_need_reload_gamelist = Signal() 


    def __init__(self,*args,**kwargs):
        super().__init__(*args,**kwargs)

        self.setObjectName("modelForTableView2LevelTreeLike")
        self.new_table_type = "table_view_2_level_tree_like"

        self.new_remember_index_id_1 = ""
        self.new_remember_index_id_2 = ""
        self.new_search_flag = False

        self.new_game_list_to_show=[] # 这个是显示用的
        
        self.new_parent_set=set()
        self.new_clone_set=set()

        self.new_clone_have_parent=set() # 图标处也用这个
        self.new_clone_not_have_parent=set()

        self.new_parent_have_clone=set()

        self.new_parent_to_clone=dict() 
        # 第二层 内容，
        # 按需 加载
        # 按需 删除

        #self.new_items_expanded=set() 
        # # 记录 展开的 项目  
        # # 重复了，和前面一项 keys 重复了

    def data(self, index, role=Qt.DisplayRole):
        if not index.isValid():
            return None
        
        if role == Qt.DisplayRole:
            return machine_dict[ self.new_game_list_to_show[index.row()] ] [ index.column() ]
        elif role == Qt.DecorationRole:
            if index.column() == 0:
                game_id = self.new_game_list_to_show[index.row()]
                if game_id in self.new_clone_have_parent:
                    return get_icon_for_gamelist_table_fake_2_level(game_id)
                else:
                    return get_icon_for_gamelist_table(game_id)
        elif role == Qt.EditRole:
            return self.data(index, Qt.DisplayRole)
        elif role ==Qt.CheckStateRole:
            if multi_selection_mode:
                if index.column()==0:
                    game_id = self.new_game_list_to_show[index.row()]
                    if game_id in the_selected_items:
                        return Qt.Checked
                    else:
                        return Qt.Unchecked

    def headerData(self,section,orientation,role=Qt.DisplayRole):
        if role == Qt.DisplayRole:
            if orientation == Qt.Horizontal:
                if section < len(columns):
                    return the_variables.columns_translation.get(columns[section],columns[section])

            if orientation == Qt.Vertical:
                if (section < 0) or (section >= len(self.new_game_list_to_show)):
                    return
                
                game_id = self.new_game_list_to_show[section]
                if game_id in self.new_parent_have_clone:
                    if game_id in self.new_parent_to_clone:
                        return string_for_close
                    else:
                        return string_for_open
                return string_for_empty

    def rowCount(self, parent=QModelIndex()):
        return len(self.new_game_list_to_show)

    def columnCount(self, parent=QModelIndex()):  
        # 相同长度
        return len(columns)

    #编辑 flags()
    def flags(self, index: QModelIndex) -> Qt.ItemFlags:
        if not index.isValid():
            return Qt.NoItemFlags
        
        if index.column()==0:
            if multi_selection_mode:
                return super().flags(index) | Qt.ItemIsUserCheckable 
        elif index.column() == translation_column_index:
            if gamelist_editable_mode:
                return super().flags(index) | Qt.ItemIsEditable

        #return super().flags(index) & ( ~ Qt.ItemIsEditable ) & ( ~ Qt.ItemIsUserCheckable )
        return super().flags(index)
    
    #编辑 setData()
    def setData(self, index, value, role=Qt.EditRole):
        
        if index.isValid():
            
            if role == Qt.EditRole:
                if index.column() == translation_column_index:
                    game_id, game_info = self.new_func_get_id_and_item_by_index(index)
                    game_info[translation_column_index] = value
                    #machine_dict[game_id] = game_info
                    self.dataChanged.emit(index, index, [role] )
                    return True
        
            #Qt::Unchecked	0	The item is unchecked.
            #Qt::PartiallyChecked	1	The item is partially checked. Items in hierarchical models may be partially checked if some, but not all, of their children are checked.
            #Qt::Checked	2	The item is checked.
            elif role == Qt.CheckStateRole:
                if index.column() ==0:
                    game_id, game_info = self.new_func_get_id_and_item_by_index(index)
                    if value==2:
                        the_selected_items.add(game_id)
                    elif value == 0:
                        the_selected_items.discard(game_id)
                    self.dataChanged.emit(index, index, [role])
                    return True
        
        return False

    def new_func_get_id_and_item_by_index(self, index):
        row = index.row()
        game_id = self.new_game_list_to_show[row]
        return game_id, machine_dict[ game_id ] 

    def new_func_get_item_id_by_index(self, index):
        row = index.row()
        game_id = self.new_game_list_to_show[row]
        return game_id 

    def new_func_get_item_id_by_row(self, row):
        game_id = ""
        if (row >= 0) and (row < len(self.new_game_list_to_show)):
            game_id = self.new_game_list_to_show[row]
        return game_id

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
        
        self.new_func_sort_part_2(column,reverse)
        
        ###
        #self.layoutChanged.emit()
        self.endResetModel()

        # 发送信号
        self.new_signal_time_for_choose_remember_game.emit()

    # 数据准备
    @the_timer
    def new_func_sort_part_1(self,games_to_be_sorted=None):
        # 清空
        self.new_func_clear_all_data()

        if games_to_be_sorted is None:
            games_to_be_sorted = []

        if not games_to_be_sorted:
            # 空值
            return  # 之前已清空所有值


        if games_to_be_sorted is all_set:
            current_parent = parent_set
            current_clone = clone_set 
        else:
            if not isinstance(games_to_be_sorted,set):
                games_to_be_sorted = set(games_to_be_sorted)
            current_parent = parent_set & games_to_be_sorted
            current_clone = clone_set & games_to_be_sorted

        self.new_parent_set = current_parent
        self.new_clone_set = current_clone

        #### 空
        if ( not current_parent)  and ( not current_clone): 
            # 非空值，但超范围 都被过虑了 ，剩余空值
            return # 之前已清空所有值
        
        #### 半空
        if not current_parent:
            self.new_clone_not_have_parent = current_clone
            return # 其它值已清空
        
        #### 半空 2
        if not current_clone:
            return # 其它值已清空

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

        # current_parent_to_clone
        #current_parent_to_clone = dict()
        #for clone_id in current_clone_have_parent:
        #    parent_id = clone_to_parent[clone_id]
        #    current_parent_to_clone.setdefault(parent_id,[]).append(clone_id)
        parent_have_clone = {clone_to_parent[clone_id] for clone_id in current_clone_have_parent}

        self.new_clone_have_parent = current_clone_have_parent
        self.new_clone_not_have_parent = current_clone_not_have_parent
        self.new_parent_have_clone=parent_have_clone

    # 排序
    @the_timer
    def new_func_sort_part_2(self,column=None,reverse=None):

        if ( not self.new_parent_set) and ( not self.new_clone_set):
            self.new_game_list_to_show = []
            return

        if reverse is None:
            reverse = the_variables.sort_reverse
        if column is None:
            column = the_variables.sort_column
        
        sort_key_func = get_sort_func(column,reverse)
    
        new_game_list_for_level_1 = list( self.new_parent_set | self.new_clone_not_have_parent )

        # 第一层排序
        new_game_list_for_level_1.sort( key = sort_key_func ,reverse = reverse, )

        if self.new_parent_to_clone:

            # 第二层排序 仅展开的部分
            if self.new_parent_to_clone:
                for clone_id_list in self.new_parent_to_clone.values():
                    clone_id_list.sort( key = sort_key_func,reverse = reverse,)
            
            self.new_game_list_to_show=[]
            for game_id in new_game_list_for_level_1:
                self.new_game_list_to_show.append(game_id)
                if game_id in self.new_parent_to_clone:
                    self.new_game_list_to_show.extend(self.new_parent_to_clone[game_id])
        else:
            self.new_game_list_to_show = new_game_list_for_level_1


    # 目录发出信号
    # 显示新内容
    def new_func_show_by_index(self,id_1,id_2):
        print("")
        print("show by index")
        print("id_1: ",id_1)
        print("id_2: ",id_2)

        self.new_remember_index_id_1 = id_1
        self.new_remember_index_id_2 = id_2
        self.new_search_flag = False

        ###
        self.beginResetModel()
        
        self.new_func_clear_all_data()

        self.new_func_sort_part_1( get_id_list_from_index_and_filter(id_1,id_2) )
        self.new_func_sort_part_2()

        self.singalGamelistNumberChanged.emit( len(self.new_parent_set) + len(self.new_clone_set) )

        ###
        self.endResetModel()

        # 发送信号
        self.new_signal_time_for_choose_remember_game.emit()
    
    # 列表搜索，显示搜索结果
    def new_func_show_search_result(self,search_string,use_re=False,ignore_case=True,search_columns=tuple()):
        print("")
        print("show search result")
        print("search_string: ",search_string)   

        id_1 = self.new_remember_index_id_1
        id_2 = self.new_remember_index_id_2
        self.new_search_flag = True

        ###
        self.beginResetModel()
        #self.layoutAboutToBeChanged.emit()

        self.new_func_clear_all_data()
        
        # 搜索范围
        temp_game_ids  =  get_id_list_from_index_and_filter(id_1,id_2) 
        # 搜索结果
        temp_game_ids = func_for_search(search_string,search_object_list=[temp_game_ids,],use_re=use_re,ignore_case=ignore_case,search_columns=search_columns)
        # 排序
        self.new_func_sort_part_1(temp_game_ids)
        self.new_func_sort_part_2()

        self.singalGamelistNumberChanged.emit( len(self.new_parent_set) + len(self.new_clone_set) )

        ###
        #self.layoutChanged.emit()
        self.endResetModel()

        # 发送信号
        self.new_signal_time_for_choose_remember_game.emit()

    def new_func_clear_all_data(self):
        print("clear data")

        self.new_game_list_to_show=[] # 这个是显示用的
        
        self.new_parent_set=set()
        self.new_clone_set=set()

        self.new_clone_have_parent=set() # 图标处也用这个
        self.new_clone_not_have_parent=set()

        self.new_parent_have_clone=set()

        self.new_parent_to_clone=dict() # 第二层 内容，按需 加载


    def new_func_clear_search_data(self):
        pass

    def new_func_get_index_by_game_id(self,game_id):
        result = QModelIndex()

        if not game_id:
            return result
        
        if not self.new_game_list_to_show:
            return result
        
        if (game_id not in self.new_clone_set) and (game_id not in self.new_parent_set):
            return result

        if game_id in self.new_clone_have_parent:
            # 第二层
            try:
                parent_id = clone_to_parent[game_id]
                parent_index = self.new_game_list_to_show.index(parent_id)
                self.new_func_insert_children(parent_index)
                clone_list_length = len(self.new_parent_to_clone[parent_id])
                for i in range(clone_list_length):
                    row = parent_index + i + 1
                    if self.new_game_list_to_show[row] == game_id:
                        return self.index(row,0)
            except:
                return result
            
        else:
            # 第一层
            try:
                row = self.new_game_list_to_show.index(game_id)
                return self.index(row,0)
            except:
                return result # 应该在有的，除非哪里出错了
        
        return result

    def new_func_cancel_search(self):
        if not self.new_search_flag:
            return
        
        self.new_search_flag = False

        id_1,id_2 = self.new_remember_index_id_1,self.new_remember_index_id_2
        self.new_func_show_by_index(id_1,id_2)

    @Slot(int)
    def new_func_expand_or_collapse_item(self,section):
        if (section < 0) or (section >= len(self.new_game_list_to_show)):
            return

        game_id = self.new_game_list_to_show[section]

        if game_id in self.new_parent_have_clone:
            if game_id in self.new_parent_to_clone:
                #return string_for_close
                # delete rows
                self.new_func_delete_children(section,)
            else:
                #return string_for_open
                # insert rows
                self.new_func_insert_children(section,)
    #
    def new_func_delete_children(self,row):

        parent_id = self.new_game_list_to_show[row]

        if parent_id not in self.new_parent_have_clone:
            return

        if parent_id not in self.new_parent_to_clone:
            return

        clone_list = self.new_parent_to_clone[parent_id]
        
        if not clone_list:
            print("clone_list is empty,maybe error")
            return # 可能 哪里 出错了
        
        #clone_set = set(clone_list)
        #for n in range(len(clone_list)):
        #    if self.new_game_list_to_show[row + 1 + n] in clone_set:
        #        #print(self.new_game_list_to_show[row + 1 + n])
        #        pass
        #    else:
        #        print("maybe error")
        
        #
        del self.new_parent_to_clone[parent_id]
        self.headerDataChanged.emit(Qt.Vertical,row,row)
        
        self.beginRemoveRows(QModelIndex(), row+1, row +len(clone_list) )
        del self.new_game_list_to_show[ row + 1 : row + len(clone_list) + 1 ]
        self.endRemoveRows()
        
        
        #
        

        print()
        print("parent opened number :", len(self.new_parent_to_clone.keys()) )
    #
    def new_func_insert_children(self, row):

        parent_id = self.new_game_list_to_show[row]

        if parent_id not in self.new_parent_have_clone:
            return

        if parent_id in self.new_parent_to_clone:
            return

        sort_key_func = get_sort_func()
        
        clone_list = list( self.new_clone_have_parent.intersection( parent_to_clone[parent_id]) )
        clone_list.sort(key=sort_key_func,reverse=the_variables.sort_reverse)

        if not clone_list:
            print("clone_list is empty,maybe error")
            return # 可能 哪里 出错了
        
        #
        self.new_parent_to_clone[parent_id] = clone_list
        self.headerDataChanged.emit(Qt.Vertical,row,row)
        
        self.beginInsertRows(QModelIndex(), row+1, row +len(clone_list) )
        self.new_game_list_to_show[row+1:row+1] = clone_list
        self.endInsertRows()
        
        
        #
        

        print()
        print("parent opened number :", len(self.new_parent_to_clone.keys()) )
    
    def new_func_vertical_header_changed(self):
        if self.new_game_list_to_show:
            self.headerDataChanged.emit(Qt.Vertical, 0, len(self.new_game_list_to_show)-1)

    # 删除一个游戏，从表格菜单中选择删除
    def new_func_remove_one_item_by_index(self,index):
        if not index_edit_mode:
            return

        id_1,id_2 = self.new_remember_index_id_1,self.new_remember_index_id_2
        if not id_1:
            return
        if id_1 not in editable_index_files:
            return

        if index.isValid():

            row = index.row()

            game_id = self.new_game_list_to_show[ row ]

            ###################
            # 目录文件，删除
            misc_funcs.delect_one_item_from_external_index(game_id,id_1,id_2)

            ###################
            # 重置列表
            self.new_signal_need_reload_gamelist.emit()
    #
    # 多选删除，当前列表中，删除勾选的游戏
    def new_func_remove_selected_items(self):
        # 未修改当前列表的数据
        # 修改外面的数据，完成后，列表需要重载
        # centeral_widget new_func_reload_gamelist()

        if not index_edit_mode:
            return
        
        if not multi_selection_mode:
            return
        
        if not the_selected_items: # 空
            return
        
        id_1,id_2 = self.new_remember_index_id_1,self.new_remember_index_id_2

        if not id_1:
            return
        
        if id_1 not in editable_index_files:
            return

        misc_funcs.delect_items_from_external_index(the_selected_items,id_1,id_2)

        self.new_signal_need_reload_gamelist.emit()

    def new_func_select_all_items(self):
        if not multi_selection_mode:
            return

        global the_selected_items
        the_selected_items = self.new_parent_set | self.new_clone_set
        print(len(the_selected_items))

        if self.new_game_list_to_show:
            index_first = self.index(0,0)
            index_last  = self.index(len(self.new_game_list_to_show)-1,0)
            self.dataChanged.emit(index_first, index_last, [Qt.CheckStateRole])

    def new_func_deselect_all_items(self):
        if not multi_selection_mode:
            return
        
        the_selected_items.clear()
        print(len(the_selected_items))

        if self.new_game_list_to_show:
            index_first = self.index(0,0)
            index_last  = self.index(len(self.new_game_list_to_show)-1,0)
            self.dataChanged.emit(index_first, index_last, [Qt.CheckStateRole])        

    def new_func_select_reverse(self):
        if not multi_selection_mode:
            return

        global the_selected_items
        the_selected_items = (self.new_parent_set | self.new_clone_set) - the_selected_items
        print(len(the_selected_items))
      
        if self.new_game_list_to_show:            
            index_first = self.index(0,0)
            index_last  = self.index(len(self.new_game_list_to_show)-1,0)
            self.dataChanged.emit(index_first, index_last, [Qt.CheckStateRole])       

    def new_func_select_same_type_items(self,index):
        if not multi_selection_mode:
            return

        if not index.isValid():
            return

        column = index.column()
        search_columns = tuple([column])

        cell_data = self.data(index,Qt.DisplayRole)

        reuslt = func_for_find_same_value_in_same_colmun(
                cell_data,
                column,
                search_object_list=[self.new_parent_set,self.new_clone_set],
                )

        the_selected_items.clear()
        the_selected_items.update(reuslt)

        if self.new_game_list_to_show:
            index_first = self.index(0,0)
            index_last  = self.index(len(self.new_game_list_to_show)-1,0)
            self.dataChanged.emit(index_first, index_last, [Qt.CheckStateRole])

    def new_func_add_parent_game(self):
        
        if not index_edit_mode:
            return

        id_1,id_2 = self.new_remember_index_id_1,self.new_remember_index_id_2

        if not id_1:
            return
        
        if id_1 not in editable_index_files:
            return

        temp_set = self.new_parent_set | self.new_clone_set
        result = []
        for game_id in temp_set:
            result.append(game_id)
            if game_id in clone_set:
                result.append(clone_to_parent[game_id])

        result = set(result)

        new_games = result - temp_set

        if new_games :

            misc_funcs.add_items_to_external_index(new_games,id_1,id_2)

            self.new_signal_need_reload_gamelist.emit()

    def new_func_add_colne_game(self):
        if not index_edit_mode:
            return

        id_1,id_2 = self.new_remember_index_id_1,self.new_remember_index_id_2

        if not id_1:
            return
        
        if id_1 not in editable_index_files:
            return

        temp_set = self.new_parent_set | self.new_clone_set
        result = []
        for game_id in temp_set:
            result.append(game_id)
            if game_id in parent_to_clone:
                result.extend(parent_to_clone[game_id])

        result = set(result)

        new_games = result - temp_set

        if new_games :

            misc_funcs.add_items_to_external_index(new_games,id_1,id_2)

            self.new_signal_need_reload_gamelist.emit()

    def new_func_delete_parent_game(self):
        
        if not index_edit_mode:
            return

        id_1,id_2 = self.new_remember_index_id_1,self.new_remember_index_id_2

        if not id_1:
            return
        
        if id_1 not in editable_index_files:
            return

        result = self.new_parent_set

        if result :

            misc_funcs.delect_items_from_external_index(result,id_1,id_2)

            self.new_signal_need_reload_gamelist.emit()

    def new_func_delete_clone_game(self):
        
        if not index_edit_mode:
            return

        id_1,id_2 = self.new_remember_index_id_1,self.new_remember_index_id_2

        if not id_1:
            return
        
        if id_1 not in editable_index_files:
            return

        result = self.new_clone_set

        if result :

            misc_funcs.delect_items_from_external_index(result,id_1,id_2)

            self.new_signal_need_reload_gamelist.emit()

class Model_for_tree_view(QAbstractItemModel):
    singalGamelistNumberChanged = Signal(int)
    new_signal_time_for_choose_remember_game = Signal() # 发信号，后续看是否需要定位到上次选中的游戏
    new_signal_need_reload_gamelist = Signal() 


    def __init__(self,*args,**kwargs):
        super().__init__(*args,**kwargs)
        self.new_table_type = "tree_view"
        self.setObjectName("modelForTreeView")

        self.new_remember_index_id_1 = ""
        self.new_remember_index_id_2 = ""
        self.new_search_flag = False

        self.new_parent_set = set()
        self.new_clone_set = set()

        self.new_parent_have_clone = set()
        self.new_clone_have_parent = set()
        self.new_clone_not_have_parent = set()

        self.new_game_list_for_level_1 = [] # 第一层 全部 一次性 加载
        self.new_parent_to_clone = dict() # 第二层 内容，按需 加载

        self.new_items_expanded = set()

    def data(self, index, role=Qt.DisplayRole):
        if not index.isValid():
            return None
        
        internal_id = index.internalId()
        if internal_id == 1:
            game_id = self.new_game_list_for_level_1[index.row()]
        else:
            parent_row = internal_id - 2
            parent_id = self.new_game_list_for_level_1[parent_row]
            game_id = self.new_parent_to_clone[parent_id][index.row()]

        if role == Qt.DisplayRole:
            return machine_dict[game_id][index.column()]
        elif role == Qt.DecorationRole:
            if index.column() == 0:
                return get_icon_for_gamelist_table(game_id)
        elif role == Qt.EditRole:
            return self.data(index, Qt.DisplayRole)
#        elif role ==Qt.CheckStateRole:
#            if multi_selection_mode:
#                if index.column()==0:
#                    if game_id in the_selected_items:
#                        return Qt.Checked
#                    else:
#                        return Qt.Unchecked
        
        return None

    def headerData(self,section,orientation,role=Qt.DisplayRole ):
        if role == Qt.DisplayRole:
            if orientation == Qt.Horizontal:
                if section < len(columns):
                    return the_variables.columns_translation.get(columns[section],columns[section])

            if orientation == Qt.Vertical:
                return str(section)

    def rowCount(self, parent=QModelIndex() ):

        if parent.isValid():
            if parent.internalId() == 1 :
                parent_id = self.new_game_list_for_level_1[parent.row()]
                if parent_id in self.new_parent_to_clone:
                    return len( self.new_parent_to_clone[parent_id] )
        else :
            return len(self.new_game_list_for_level_1)
        return 0

    def columnCount(self, parent=QModelIndex() ):  
        # 相同长度
        return len(columns)
        
    def index(self,row,column,parent=QModelIndex() ):
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

    def hasChildren(self,parent = QModelIndex()) :
        if not parent.isValid():
            if self.new_game_list_for_level_1:
                return True
            else:
                return False
        elif parent.internalId() == 1 :
            parent_id = self.new_game_list_for_level_1[parent.row()]
            if parent_id in self.new_parent_have_clone:
                return True
            else:
                return False
        else:
            return False
    
    def canFetchMore(self,parent ) :
        if not parent.isValid():
            return False
        elif parent.internalId() == 1 :
            parent_id = self.new_game_list_for_level_1[parent.row()]
            if parent_id in self.new_parent_have_clone:
                if parent_id not in self.new_parent_to_clone:
                    return True
            return False
        else:
            return False 

    def fetchMore(self,parent):
        self.new_func_insert_children(parent)

    def new_func_insert_children(self,parent): # parent 类型是 QModelIndex
        parent_id = self.new_game_list_for_level_1[parent.row()]

        if parent_id in self.new_parent_to_clone:
            return # 已展开
        
        if parent_id not in self.new_parent_have_clone:
            return # 无子项
        
        column = the_variables.sort_column
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
        sort_key_func = sort_key_func_2
        if the_variables.sort_use_locale:
            if column in the_variables.sort_colums_use_locale:
                sort_key_func = sort_key_func_1
        if column == id_column_index:
            sort_key_func = None
        
        clone_list = list( self.new_clone_have_parent.intersection( parent_to_clone[parent_id]) )
        clone_list.sort(key=sort_key_func,reverse=reverse)

        if not clone_list:
            return # 可能 哪里 出错了
        
        self.beginInsertRows(parent, 0, len(clone_list)-1 )
        self.new_parent_to_clone[parent_id] = clone_list
        self.endInsertRows()

        print()
        print("parent opened number :", len(self.new_parent_to_clone.keys()) )
        print( "clone_list", len(clone_list),clone_list )

    #编辑 flags()
    def flags(self, index: QModelIndex) -> Qt.ItemFlags:
        if not index.isValid():
            return Qt.NoItemFlags
        
        #if index.column()==0:
        #    if multi_selection_mode:
        #        return super().flags(index) | Qt.ItemIsUserCheckable 
        if index.column() == translation_column_index:
            if gamelist_editable_mode:
                return super().flags(index) | Qt.ItemIsEditable

        #return super().flags(index) & ( ~ Qt.ItemIsEditable ) & ( ~ Qt.ItemIsUserCheckable )
        return super().flags(index)
    
    #编辑 setData()
    def setData(self, index, value, role=Qt.EditRole):
        
        if index.isValid():
            
            if role == Qt.EditRole:
                if index.column() == translation_column_index:
                    game_id, game_info = self.new_func_get_id_and_item_by_index(index)
                    game_info[translation_column_index] = value
                    #machine_dict[game_id] = game_info
                    self.dataChanged.emit(index, index, [role] )
                    return True
        
            ##Qt::Unchecked	0	The item is unchecked.
            ##Qt::PartiallyChecked	1	The item is partially checked. Items in hierarchical models may be partially checked if some, but not all, of their children are checked.
            ##Qt::Checked	2	The item is checked.
            #elif role == Qt.CheckStateRole:
            #    if index.column() ==0:
            #        game_id, game_info = self.new_func_get_id_and_item_by_index(index)
            #        if value==2:
            #            the_selected_items.add(game_id)
            #        elif value == 0:
            #            the_selected_items.discard(game_id)
            #        self.dataChanged.emit(index, index, [role])
            #        return True
        
        return False
    #######
    #######
    #######
   
    # 数据准备
    @the_timer
    def new_func_sort_part_1(self,games_to_be_sorted=None):
        # 清空
        self.new_func_clear_all_data()

        if games_to_be_sorted is None:
            games_to_be_sorted = []

        if not games_to_be_sorted:
            # 空值
            return  # 之前已清空所有值


        if games_to_be_sorted is all_set:
            current_parent = parent_set
            current_clone = clone_set 
        else:
            if not isinstance(games_to_be_sorted,set):
                games_to_be_sorted = set(games_to_be_sorted)
            current_parent = parent_set & games_to_be_sorted
            current_clone = clone_set & games_to_be_sorted

        self.new_parent_set = current_parent
        self.new_clone_set = current_clone

        #### 空
        if ( not current_parent)  and ( not current_clone): 
            # 非空值，但超范围 都被过虑了 ，剩余空值
            return # 之前已清空所有值
        
        #### 半空
        if not current_parent:
            self.new_clone_not_have_parent = current_clone
            return # 其它值已清空
        
        #### 半空 2
        if not current_clone:
            return # 其它值已清空

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

        # current_parent_to_clone
        #current_parent_to_clone = dict()
        #for clone_id in current_clone_have_parent:
        #    parent_id = clone_to_parent[clone_id]
        #    current_parent_to_clone.setdefault(parent_id,[]).append(clone_id)
        parent_have_clone = {clone_to_parent[clone_id] for clone_id in current_clone_have_parent}

        self.new_clone_have_parent = current_clone_have_parent
        self.new_clone_not_have_parent = current_clone_not_have_parent
        self.new_parent_have_clone=parent_have_clone

    # 排序
    @the_timer
    def new_func_sort_part_2(self,column=None,reverse=None):

        if ( not self.new_parent_set) and ( not self.new_clone_set):
            self.new_game_list_for_level_1 = []
            return

        if reverse is None:
            reverse = the_variables.sort_reverse
        if column is None:
            column = the_variables.sort_column
        
        sort_key_func = get_sort_func(column,reverse)

        if not self.new_parent_set:
            self.new_game_list_for_level_1 = list( self.new_clone_not_have_parent )
        elif not self.new_clone_not_have_parent:
            self.new_game_list_for_level_1 = list( self.new_parent_set )
        else:
            self.new_game_list_for_level_1 = list( self.new_parent_set | self.new_clone_not_have_parent )

        # 第一层排序
        self.new_game_list_for_level_1.sort( key = sort_key_func ,reverse = reverse, )


        # 第二层排序
        if self.new_parent_to_clone:
            for clone_id_list in self.new_parent_to_clone.values():
                clone_id_list.sort( key = sort_key_func,reverse = reverse,)


    def new_func_get_id_and_item_by_index(self, index):
        if not index.isValid():return None;
        
        internal_id = index.internalId()
        if internal_id == 1:
            game_id = self.new_game_list_for_level_1[index.row()]
        else:
            parent_row = internal_id - 2
            parent_id = self.new_game_list_for_level_1[parent_row]
            game_id = self.new_parent_to_clone[parent_id][index.row()]
        
        return game_id, machine_dict[ game_id ] 

    def new_func_get_item_id_by_index(self, index):
        if not index.isValid():return None;
        
        internal_id = index.internalId()
        if internal_id == 1:
            game_id = self.new_game_list_for_level_1[index.row()]
        else:
            parent_row = internal_id - 2
            parent_id = self.new_game_list_for_level_1[parent_row]
            game_id = self.new_parent_to_clone[parent_id][index.row()]
        
        return game_id 


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
        
        self.new_func_sort_part_2(column, reverse)
        
        ###
        #self.layoutChanged.emit()
        self.endResetModel()

        # 发送信号
        self.new_signal_time_for_choose_remember_game.emit()
    
    # 目录发出信号
    # 显示新内容
    def new_func_show_by_index(self,id_1,id_2):
        print("")
        print(self.new_table_type)
        print("show by index")
        print("id_1: ",id_1)
        print("id_2: ",id_2)
        
        self.new_remember_index_id_1 = id_1
        self.new_remember_index_id_2 = id_2
        self.new_search_flag = False

        ###
        #self.layoutAboutToBeChanged.emit()
        self.beginResetModel()
        
        self.new_func_clear_all_data()
        
        self.new_func_sort_part_1(get_id_list_from_index_and_filter(id_1,id_2) )
        self.new_func_sort_part_2()

        self.singalGamelistNumberChanged.emit( len(self.new_parent_set) + len(self.new_clone_set) )

        ###
        #self.layoutChanged.emit()
        self.endResetModel()
        
        # 发送信号
        self.new_signal_time_for_choose_remember_game.emit()
    
    # 列表搜索，显示搜索结果
    def new_func_show_search_result(self,search_string,use_re=False,ignore_case=True,search_columns=tuple()):
        print("")
        print("show search result")
        print("search_string: ",search_string)   

        id_1 = self.new_remember_index_id_1
        id_2 = self.new_remember_index_id_2
        self.new_search_flag = True

        ###
        #self.layoutAboutToBeChanged.emit()
        self.beginResetModel()

        self.new_func_clear_all_data()

        temp_games = get_id_list_from_index_and_filter(id_1,id_2)
        temp_games = func_for_search(search_string,search_object_list=[temp_games,],use_re=use_re,ignore_case=ignore_case,search_columns=search_columns)

        self.new_func_sort_part_1(temp_games )
        self.new_func_sort_part_2()

        self.singalGamelistNumberChanged.emit( len(self.new_parent_set) + len(self.new_clone_set) )

        ###
        #self.layoutChanged.emit()
        self.endResetModel()

        # 发送信号
        self.new_signal_time_for_choose_remember_game.emit()

    #####
    def new_func_clear_all_data(self):
        print("clear data ",self.new_table_type)

        self.new_parent_set = set()
        self.new_clone_set = set()

        self.new_parent_have_clone = set()
        self.new_clone_have_parent = set()
        self.new_clone_not_have_parent = set()

        self.new_game_list_for_level_1 = [] # 第一层 全部 一次性 加载
        self.new_parent_to_clone = dict() # 第二层 内容，按需 加载

        self.new_items_expanded = set()

    def new_func_clear_data_for_sort(self):
        pass
    
    def new_func_clear_search_data(self):
        pass

    def new_func_get_index_by_game_id(self,game_id):
        result = QModelIndex()

        if not game_id:
            return result
        
        if not self.new_game_list_for_level_1:
            return result
        
        if (game_id not in self.new_clone_set) and (game_id not in self.new_parent_set):
            return result
        
        # 第一层
        if (game_id in self.new_parent_set) or (game_id in self.new_clone_not_have_parent):
            try:
                row = self.new_game_list_for_level_1.index(game_id)
                return self.index(row,0)
            except:
                # 应该有的，除非哪里出错了
                return result
        # 第二层
        elif game_id in self.new_clone_have_parent:
            parent_id = clone_to_parent[game_id]
            try:
                parent_row = self.new_game_list_for_level_1.index(parent_id)
                parent_index = self.index(parent_row,0)
                # 检查是否展开
                if parent_id not in self.new_parent_to_clone: # 未展开
                    self.new_func_insert_children(parent_index) # 先插入
                row = self.new_parent_to_clone[parent_id].index(game_id)
                return self.index(row,0,parent_index)
            except:
                # 应该有的，除非哪里出错了
                return result

        return result

    def new_func_cancel_search(self):
        if not self.new_search_flag:
            return
        
        self.new_search_flag = False

        id_1,id_2 = self.new_remember_index_id_1,self.new_remember_index_id_2
        self.new_func_show_by_index(id_1,id_2)

    def new_func_select_all_items(self):
        if not multi_selection_mode:
            return

        self.layoutAboutToBeChanged.emit() 

        global the_selected_items
        the_selected_items = self.new_parent_set | self.new_clone_set
        print(len(the_selected_items))

        self.layoutChanged.emit()  

    def new_func_deselect_all_items(self):
        if not multi_selection_mode:
            return

        self.layoutAboutToBeChanged.emit()

        the_selected_items.clear()
        print(len(the_selected_items))

        self.layoutChanged.emit()   

    def new_func_select_reverse(self):
        if not multi_selection_mode:
            return

        self.layoutAboutToBeChanged.emit() 

        global the_selected_items
        the_selected_items = (self.new_parent_set | self.new_clone_set) - the_selected_items
        print(len(the_selected_items))

        self.layoutChanged.emit()  

    # 删除一个游戏，从表格菜单中选择删除
    def new_func_remove_one_item_by_index(self,index):
        if not index_edit_mode:
            return

        id_1,id_2 = self.new_remember_index_id_1,self.new_remember_index_id_2
        if not id_1:
            return
        if id_1 not in editable_index_files:
            return

        if index.isValid():

            game_id = self.new_func_get_item_id_by_index(index)

            ###################
            # 目录文件，删除
            misc_funcs.delect_one_item_from_external_index(game_id,id_1,id_2)

            ###################
            # 重置列表
            self.new_signal_need_reload_gamelist.emit()
    #

class Delegate_for_Model_of_icon(QStyledItemDelegate):
    def __init__(self, parent=None, margin=5):
        super().__init__(parent)

    def paint(self, painter, option, index):
        if not index.isValid():
            return

        painter.save()
        painter.setRenderHint(QPainter.RenderHint.SmoothPixmapTransform)

        # 1. 绘制选中/悬停背景 (保持原生风格)
        if option.state & QStyle.State_Selected:
            painter.fillRect(option.rect, option.palette.highlight())
        #elif option.state & QStyle.State_MouseOver:
        #    painter.fillRect(option.rect, option.palette.alternateBase())

        # 2. 获取数据
        the_image = index.data(Qt.DecorationRole)
        the_text = index.data(Qt.DisplayRole)

        if the_image is None:
            pass
        else:
            # 图标尺寸已经调整好了
            pixmap = the_image
            if not pixmap.isNull():
                width = pixmap.width()

                x0 = option.rect.left()
                y0 = option.rect.top()
                w0 = max(icon_size_for_icon_table,text_width_for_icon_table)                

                if w0 == width:
                    # 顶点移移量  x
                    x = 0              
                else:
                    # 顶点移移量  x
                    x = int((w0 - icon_size_for_icon_table) / 2)
                    if x < 0: x=0
                painter.drawPixmap(x0 + x, y0, icon_size_for_icon_table, icon_size_for_icon_table, pixmap)
        
        if the_text:

            # 文本区域从图标下方开始
            #print()
            #print(option.rect)
            text_rect = QRect(option.rect)
            text_rect.setHeight(text_height_for_icon_table)
            #print(text_rect)
            text_rect.translate( 0 , icon_size_for_icon_table )
            #the_offset = 3
            #if text_rect.width() > the_offset:
            #    text_rect.setWidth(text_rect.width() - the_offset)
            #    text_rect.translate( the_offset , 0 )
            #print(text_rect)

            # 5. 绘制文本 (自动换行)
            if the_text:
                # 设置文字颜色
                if option.state & QStyle.State_Selected:
                    painter.setPen(option.palette.highlightedText().color())
                else:
                    painter.setPen(option.palette.text().color())
                #painter.drawText(text_rect, Qt.AlignHCenter | Qt.AlignVCenter | Qt.TextSingleLine, the_text)
                #painter.drawText(text_rect, Qt.AlignVCenter | Qt.TextSingleLine, the_text)
                metrics = QFontMetrics(painter.font())
                elided_text = metrics.elidedText(the_text, Qt.TextElideMode.ElideRight, text_rect.width()) 
                painter.drawText(text_rect, Qt.AlignHCenter | Qt.AlignVCenter | Qt.TextSingleLine, elided_text) 

        painter.restore()

    def sizeHint(self, option, index):
        """为每个项目计算合适的尺寸"""
        if not index.isValid():
            return QSize(0, 0)
        
        return QSize( max(icon_size_for_icon_table,text_width_for_icon_table), icon_size_for_icon_table + text_height_for_icon_table)

class Model_for_icon(QAbstractListModel): # QAbstractItemModel
    singalGamelistNumberChanged = Signal(int)
    new_signal_time_for_choose_remember_game = Signal() 
    new_signal_need_reload_gamelist = Signal()

    def __init__(self,*args,**kwargs):
        super().__init__(*args,**kwargs)
        self.setObjectName("modelForIcon")

        self.new_game_list_to_show = []

        self.new_remember_index_id_1 = ""
        self.new_remember_index_id_2 = ""
        self.new_search_flag = False

    def data(self, index, role=Qt.DisplayRole):
        if role == Qt.DisplayRole:
            return self.new_game_list_to_show[index.row()]

        elif role == Qt.DecorationRole:
            
            return get_icon_for_icon_table( self.new_game_list_to_show[index.row()] )

        elif role == Qt.ToolTipRole:
            return self.new_game_list_to_show[index.row()]
    
    def rowCount(self, parent ):
        return len(self.new_game_list_to_show)

    @the_timer
    def new_func_for_sort(self,column=None,reverse=None):
        #if reverse is None:
        #    reverse = the_variables.sort_reverse
        #if column is None:
        #    column = the_variables.sort_column
        #
        #sort_key_func = get_sort_func(column,reverse)
        #
        #if isinstance(self.new_game_list_to_show,list):
        #    self.new_game_list_to_show.sort( key = sort_key_func,reverse = reverse, )
        #else:
        #    self.new_game_list_to_show= sorted( self.new_game_list_to_show, key = sort_key_func,reverse = reverse, )
        if isinstance(self.new_game_list_to_show,list):
            self.new_game_list_to_show.sort()
        else:
            self.new_game_list_to_show = sorted(self.new_game_list_to_show)

    # 目录发出信号
    # 显示新内容
    def new_func_show_by_index(self,id_1,id_2):
        print("")
        print("show by index")
        print("id_1: ",id_1)
        print("id_2: ",id_2)

        # 记录
        self.new_remember_index_id_1 = id_1
        self.new_remember_index_id_2 = id_2
        self.new_search_flag = False
        
        ###
        self.beginResetModel()
        
        self.new_func_clear_all_data()

        # 取值
        self.new_game_list_to_show = get_id_list_from_index_and_filter(id_1,id_2) # set
        #   取值,未过滤时，都是 传地址地来的。 set or list
        #   经过 过滤后，用 all_set 过滤，再减去用户设定的过滤项，传地址过来的，只有可能会剩下 all_set （过滤项为空时） 。 set
        #   在下面 排序时，注意不要修改
        #   这里得到的都是 set 类型，需要的是 list , 正好也不容易被修改

        # 排序
        self.new_func_for_sort()

        # 数量信号
        self.new_func_numbers_changed()



        ###
        self.endResetModel()

        # 发送信号
        self.new_signal_time_for_choose_remember_game.emit()
    
    # 列表搜索，显示搜索结果
    def new_func_show_search_result(self,search_string,use_re=False,ignore_case=True,search_columns=tuple()):
        print("")
        print("show search result")

        self.beginResetModel()

        self.new_func_clear_all_data()

        id_1 = self.new_remember_index_id_1
        id_2 = self.new_remember_index_id_2
        self.new_search_flag = True

        # 取值，搜索范围
        temp_game_ids =  get_id_list_from_index_and_filter(id_1,id_2) 
        
        # 搜索
        self.new_game_list_to_show = func_for_search(search_string,search_object_list=[temp_game_ids,],use_re=use_re,ignore_case=ignore_case,search_columns=search_columns)
        
        # 排序
        self.new_func_for_sort()

        # 数量信号
        self.new_func_numbers_changed()

        self.endResetModel()

        # 发送信号
        self.new_signal_time_for_choose_remember_game.emit()

    def new_func_clear_all_data(self):
        print("clear data")
        self.new_game_list_to_show = []

    def new_func_cancel_search(self):
        if not self.new_search_flag:
            return
        
        self.new_search_flag = False

        id_1,id_2 = self.new_remember_index_id_1,self.new_remember_index_id_2
        self.new_func_show_by_index(id_1,id_2)
    
    def new_func_numbers_changed(self):
        game_list_number = len(self.new_game_list_to_show)
        self.singalGamelistNumberChanged.emit(game_list_number)

    def new_func_get_id_and_item_by_index(self, index):
        row = index.row()
        game_id = self.new_game_list_to_show[row]
        return game_id, machine_dict[ game_id ] 

    def new_func_get_item_id_by_index(self, index):
        row = index.row()
        game_id = self.new_game_list_to_show[row]
        return game_id

    def new_func_get_index_by_game_id(self,game_id,):
        result = QModelIndex()

        if not game_id:
            return result
        
        if not self.new_game_list_to_show:
            return result
        
        try:
            row = self.new_game_list_to_show.index(game_id)
        except:
            return result
        
        return self.index(row)

    # 删除一个游戏，从表格菜单中选择删除
    def new_func_remove_one_item_by_index(self,index):
        if not index_edit_mode:
            return

        id_1,id_2 = self.new_remember_index_id_1,self.new_remember_index_id_2
        if not id_1:
            return
        if id_1 not in editable_index_files:
            return

        if index.isValid():

            game_id = self.new_func_get_item_id_by_index(index)

            ###################
            # 目录文件，删除
            misc_funcs.delect_one_item_from_external_index(game_id,id_1,id_2)

            ###################
            # 重置列表
            self.new_signal_need_reload_gamelist.emit()
    #

class Delegate_for_Model_of_image(QStyledItemDelegate):
    def __init__(self, parent=None, margin=5):
        super().__init__(parent)

    def paint(self, painter, option, index):
        if not index.isValid():
            return

        painter.save()
        painter.setRenderHint(QPainter.RenderHint.SmoothPixmapTransform)

        # 1. 绘制选中/悬停背景 (保持原生风格)
        if option.state & QStyle.State_Selected:
            painter.fillRect(option.rect, option.palette.highlight())
        #elif option.state & QStyle.State_MouseOver:
        #    painter.fillRect(option.rect, option.palette.alternateBase())

        # 2. 获取数据
        the_image = index.data(Qt.DecorationRole)
        the_text = index.data(Qt.DisplayRole)

        if the_image is None:
            pass
        else:
            pixmap = the_image
            # 计算缩放尺寸
            original_width = pixmap.width()
            original_height = pixmap.height()
            if (original_width == image_width_for_image_table) and (original_height == image_height_for_image_table):
                x0 = option.rect.left()
                y0 = option.rect.top()
                painter.drawPixmap(x0 , y0 ,image_width_for_image_table,image_height_for_image_table,pixmap)
            else:
                # 计算缩放比例
                ratio_w = image_width_for_image_table / original_width
                ratio_h = image_height_for_image_table / original_height
                # 选择较小的比例以保持宽高比
                scale = min(ratio_w, ratio_h)
                # 新的尺寸
                new_width = int(original_width * scale)
                new_height = int(original_height * scale)
                if new_width > image_width_for_image_table:   new_width = image_width_for_image_table
                if new_height > image_height_for_image_table: new_height = image_height_for_image_table            
                # 顶点位置 偏移量 x,y
                x = int((image_width_for_image_table - new_width) / 2)
                y = int((image_height_for_image_table - new_height) / 2)
                if x < 0: x=0
                if y < 0: y=0

                x0 = option.rect.left()
                y0 = option.rect.top()
                #print(new_width,new_height)
                painter.drawPixmap(x0 + x, y0 + y,new_width,new_height,pixmap)

        if the_text:

            # 文本区域从图标下方开始
            #print()
            #print(option.rect)
            text_rect = QRect(option.rect)
            text_rect.setHeight(text_height_for_image_table)
            #print(text_rect)
            text_rect.translate( 0 , image_height_for_image_table )
            #the_offset = 3
            #if text_rect.width() > the_offset:
            #    text_rect.setWidth(text_rect.width() - the_offset)
            #    text_rect.translate( the_offset , 0 )
            #print(text_rect)

            # 5. 绘制文本 (自动换行)
            if the_text:
                # 设置文字颜色
                if option.state & QStyle.State_Selected:
                    painter.setPen(option.palette.highlightedText().color())
                else:
                    painter.setPen(option.palette.text().color())
                #painter.drawText(text_rect, Qt.AlignHCenter | Qt.AlignVCenter | Qt.TextSingleLine, the_text)
                #painter.drawText(text_rect, Qt.AlignVCenter | Qt.TextSingleLine, the_text)
                metrics = QFontMetrics(painter.font())
                elided_text = metrics.elidedText(the_text, Qt.TextElideMode.ElideRight, text_rect.width()) 
                painter.drawText(text_rect, Qt.AlignHCenter | Qt.AlignVCenter | Qt.TextSingleLine, elided_text) 

        painter.restore()

    def sizeHint(self, option, index):
        """为每个项目计算合适的尺寸"""
        if not index.isValid():
            return QSize(0, 0)
        
        return QSize(image_width_for_image_table, image_height_for_image_table + text_height_for_image_table)

class Model_for_image(QAbstractListModel): # QAbstractItemModel
    singalGamelistNumberChanged = Signal(int)
    new_signal_time_for_choose_remember_game = Signal() 
    new_signal_need_reload_gamelist = Signal()

    def __init__(self,*args,**kwargs):
        super().__init__(*args,**kwargs)
        self.setObjectName("modelForImage")

        self.new_game_list_to_show = []

        self.new_remember_index_id_1 = ""
        self.new_remember_index_id_2 = ""
        self.new_search_flag = False

        #
        self.new_zip_file_path = ""
        self.new_zip_opened_file = None
        self.new_zip_path = None

    def new_func_get_image_from_folders(self,game_id):
        # not finished
        # not used

        if not game_id:
            return None
        
        image_folder_path = the_variables.extra_image_zip_path["extra_image_folder_path/image_"+str(the_variables.image_dockwidget_numbers)]

        if not image_folder_path:
            return None

        pass

    def new_func_get_image_from_zip(self,game_id):
        if not game_id:
            return None
        
        if not self.new_zip_path:
            return None
        
        image_data = None

        image_file_path = game_id+".png"
        file_path_in_zip = self.new_zip_path / image_file_path
        if file_path_in_zip.exists() and file_path_in_zip.is_file():
            try:
                image_data = file_path_in_zip.read_bytes()
            except:
                image_data = None
        else:# 再找一下主版本
            if game_id in clone_set:
                parent_id = clone_to_parent[game_id]

                image_file_path = parent_id+".png"
                file_path_in_zip = self.new_zip_path / image_file_path
                if file_path_in_zip.exists() and file_path_in_zip.is_file():
                    try:
                        image_data = file_path_in_zip.read_bytes()
                    except:
                        image_data = None

        if image_data:
            pixmap=QPixmap()
            if pixmap.loadFromData(image_data,format="PNG") :
                if not pixmap.isNull():
                    return pixmap

        return None

    # 显示此列表时，打开 zip 文件
    # 隐藏此列表时，关闭 zip 文件
    # central widget 里 操作
    def new_func_open_zip(self,):

        zip_file_path = the_variables.extra_image_zip_path["extra_image_zip_path/image_"+str(the_variables.image_dockwidget_numbers)]

        if not zip_file_path:
            return

        if not os.path.isfile(zip_file_path):
            return

        try:
            self.new_zip_opened_file = zipfile.ZipFile(zip_file_path, mode='r',  allowZip64=True,)
            self.new_zip_file_path = zip_file_path
            self.new_zip_path = zipfile.Path(self.new_zip_opened_file)
            print("open zip file :",self.new_zip_file_path)
        except:
            self.new_zip_file_path = ""
            self.new_zip_opened_file = None
            self.new_zip_path = None

            exc_type, exc_value, exc_traceback = sys.exc_info()
            print(traceback.print_exception(exc_type, exc_value, exc_traceback))            

    def new_func_close_zip(self):
        if self.new_zip_opened_file is not None:
            try:
                self.new_zip_opened_file.close()
                print("close zip file :",self.new_zip_file_path)
                self.new_zip_opened_file = None
                self.new_zip_file_path = ""
                self.new_zip_path = None
            except:
                print("close zip file error")

                exc_type, exc_value, exc_traceback = sys.exc_info()
                print(traceback.print_exception(exc_type, exc_value, exc_traceback))

    def data(self, index, role=Qt.DisplayRole):
        if role == Qt.DisplayRole:
            # translation_column_index
            game_id = self.new_game_list_to_show[index.row()]
            return game_id + " - " +  machine_dict[game_id][translation_column_index]

        elif role == Qt.DecorationRole:
            
            return self.new_func_get_image_from_zip( self.new_game_list_to_show[index.row()] )

        elif role == Qt.ToolTipRole:
            return self.data(index,)
    
    def rowCount(self, parent ):
        return len(self.new_game_list_to_show)

    @the_timer
    def new_func_for_sort(self,column=None,reverse=None):
        #if reverse is None:
        #    reverse = the_variables.sort_reverse
        #if column is None:
        #    column = the_variables.sort_column
        #
        #sort_key_func = get_sort_func(column,reverse)
        #
        #if isinstance(self.new_game_list_to_show,list):
        #    self.new_game_list_to_show.sort( key = sort_key_func,reverse = reverse, )
        #else:
        #    self.new_game_list_to_show= sorted( self.new_game_list_to_show, key = sort_key_func,reverse = reverse, )
        if isinstance(self.new_game_list_to_show,list):
            self.new_game_list_to_show.sort()
        else:
            self.new_game_list_to_show = sorted(self.new_game_list_to_show)

    # 目录发出信号
    # 显示新内容
    def new_func_show_by_index(self,id_1,id_2):
        print("")
        print("show by index")
        print("id_1: ",id_1)
        print("id_2: ",id_2)

        # 记录
        self.new_remember_index_id_1 = id_1
        self.new_remember_index_id_2 = id_2
        self.new_search_flag = False
        
        ###
        self.beginResetModel()
        
        self.new_func_clear_all_data()

        # 取值
        self.new_game_list_to_show = get_id_list_from_index_and_filter(id_1,id_2) # set
        #   取值,未过滤时，都是 传地址地来的。 set or list
        #   经过 过滤后，用 all_set 过滤，再减去用户设定的过滤项，传地址过来的，只有可能会剩下 all_set （过滤项为空时） 。 set
        #   在下面 排序时，注意不要修改
        #   这里得到的都是 set 类型，需要的是 list , 正好也不容易被修改

        # 排序
        self.new_func_for_sort()

        # 数量信号
        self.new_func_numbers_changed()



        ###
        self.endResetModel()

        # 发送信号
        self.new_signal_time_for_choose_remember_game.emit()
    
    # 列表搜索，显示搜索结果
    def new_func_show_search_result(self,search_string,use_re=False,ignore_case=True,search_columns=tuple()):
        print("")
        print("show search result")

        self.beginResetModel()

        self.new_func_clear_all_data()

        id_1 = self.new_remember_index_id_1
        id_2 = self.new_remember_index_id_2
        self.new_search_flag = True

        # 取值，搜索范围
        temp_game_ids =  get_id_list_from_index_and_filter(id_1,id_2) 
        
        # 搜索
        self.new_game_list_to_show = func_for_search(search_string,search_object_list=[temp_game_ids,],use_re=use_re,ignore_case=ignore_case,search_columns=search_columns)
        
        # 排序
        self.new_func_for_sort()

        # 数量信号
        self.new_func_numbers_changed()

        self.endResetModel()

        # 发送信号
        self.new_signal_time_for_choose_remember_game.emit()

    def new_func_clear_all_data(self):
        print("clear data")
        self.new_game_list_to_show = []

    def new_func_cancel_search(self):
        if not self.new_search_flag:
            return
        
        self.new_search_flag = False

        id_1,id_2 = self.new_remember_index_id_1,self.new_remember_index_id_2
        self.new_func_show_by_index(id_1,id_2)
    
    def new_func_numbers_changed(self):
        game_list_number = len(self.new_game_list_to_show)
        self.singalGamelistNumberChanged.emit(game_list_number)

    def new_func_get_id_and_item_by_index(self, index):
        row = index.row()
        game_id = self.new_game_list_to_show[row]
        return game_id, machine_dict[ game_id ] 

    def new_func_get_item_id_by_index(self, index):
        row = index.row()
        game_id = self.new_game_list_to_show[row]
        return game_id

    def new_func_get_index_by_game_id(self,game_id,):
        result = QModelIndex()

        if not game_id:
            return result
        
        if not self.new_game_list_to_show:
            return result
        
        try:
            row = self.new_game_list_to_show.index(game_id)
        except:
            return result
        
        return self.index(row)

    # 删除一个游戏，从表格菜单中选择删除
    def new_func_remove_one_item_by_index(self,index):
        if not index_edit_mode:
            return

        id_1,id_2 = self.new_remember_index_id_1,self.new_remember_index_id_2
        if not id_1:
            return
        if id_1 not in editable_index_files:
            return

        if index.isValid():

            game_id = self.new_func_get_item_id_by_index(index)

            ###################
            # 目录文件，删除
            misc_funcs.delect_one_item_from_external_index(game_id,id_1,id_2)

            ###################
            # 重置列表
            self.new_signal_need_reload_gamelist.emit()
    #

#########################
#########################
#########################
# index_list = []
# index_has_children = dict()
class Model_for_index(QAbstractItemModel):
    def __init__(self,):
        super().__init__()

        self.new_search_flag = False
        self.new_search_string = ""
        self.new_search_use_re = False

    def data(self, index, role=Qt.DisplayRole):
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
        elif role == Qt.ToolTipRole:
            return self.data(index,)
            
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

    def new_func_get_index_id_by_index(self, index): # return id_1,id_2
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
    
    def new_func_if_index_file_is_editable(self, index):
        if index.isValid():
            internal_id = index.internalId()

            if internal_id == 1:
                id_1 = index_list[index.row()]
                if id_1 in editable_index_files:
                    return True
            elif internal_id > 1:
                parent_row = internal_id -2
                id_1 = index_list[parent_row]
                #id_2 = index_has_children[id_1][index.row()]
            
                if id_1 in editable_index_files:
                    return True
        
        return False

    def new_func_find_item(self,index_id_1,index_id_2): # return QModelIndex
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

    def new_func_search_index(self, search_string, use_re=False): 
        global index_list,index_has_children

        self.new_search_flag = True
        self.new_search_string = search_string
        self.new_search_use_re = use_re


        self.beginResetModel()

        index_list ,index_has_children = func_for_index_search(search_string,use_re=use_re)

        self.endResetModel()

    def new_func_cancel_search(self): 
        #print("cancel search")

        self.new_func_clear_search_flag()

        global index_list,index_has_children,index_list_backup,index_has_children_backup

        if index_list_backup is index_list:
            if index_has_children_backup is index_has_children:
                print("index,same as backup, do nothing")
                return

        self.beginResetModel()

        index_list = index_list_backup
        index_has_children = index_has_children_backup

        self.endResetModel()

    def new_func_refresh_index(self):
        # 置顶、取消置顶、隐藏、取消隐藏 后，需要更新数据
        # 正常状态 、 搜索状态
        self.beginResetModel()
        rebuild_index()
        if self.new_search_flag:
            self.new_func_search_index(self.new_search_string , self.new_search_use_re)
        self.endResetModel()

    def new_func_clear_search_flag(self):
        self.new_search_flag = False
        self.new_search_string = ""
        self.new_search_use_re = False


# editable_index_list
# editable_index_has_children = dict()
class Model_for_index_chooser(QAbstractItemModel):
    def __init__(self,):
        super().__init__()

    def data(self, index, role):
        if not index.isValid():
            return None;

        if role == Qt.DisplayRole:
            if index.column() == 0:
                internal_id = index.internalId()
                if internal_id == 1:
                    file_path = editable_index_list[index.row()]
                    the_text = os.path.basename(file_path)
                    return the_text
                elif internal_id > 1:
                    parent_row = internal_id -2
                    parent_id = editable_index_list[parent_row]
                    if parent_id in editable_index_has_children:
                        the_text =  editable_index_has_children[parent_id][index.row()]
                        return the_text
            elif index.column() == 1: # 文件路径
                internal_id = index.internalId()
                if internal_id == 1:
                    file_path = editable_index_list[index.row()]
                    #file_path = os.path.abspath(file_path)
                    return file_path
                elif internal_id > 1:
                    parent_row = internal_id -2
                    parent_id = editable_index_list[parent_row]
                    if parent_id in editable_index_has_children:
                        the_text =  editable_index_has_children[parent_id][index.row()]
                        return the_text
            
    def headerData(self,section,orientation,role ):
        if role == Qt.DisplayRole:
            if orientation == Qt.Horizontal:
                if section == 0:
                    return "目录"
                elif section == 1:
                    return "文件路径"
            if orientation == Qt.Vertical:
                return str(section)

    def rowCount(self, parent ):

        if parent==QModelIndex():
            return len(editable_index_list)
        else :
            if parent.internalId() == 1 :
                parent_id = editable_index_list[parent.row()]
                if parent_id in editable_index_has_children:
                    return len( editable_index_has_children[parent_id] )
            
        return 0

    def columnCount(self, parent ):  
        # 相同长度
        return 2
        
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

    def new_func_get_index_id_by_index(self, index): # return id_1,id_2
        id_1,id_2="",""
        
        if index.isValid():
            internal_id = index.internalId()
            if internal_id == 1:
                id_1 = editable_index_list[index.row()]
            elif internal_id > 1:
                parent_row = internal_id -2
                id_1 = editable_index_list[parent_row]
                id_2 = editable_index_has_children[id_1][index.row()]
                
        return id_1,id_2


if __name__ == "__main__":
    pass
