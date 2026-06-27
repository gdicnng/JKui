import os

import ui_models




def get_mame_path_and_working_directory(mame_exe_path_old="", mame_working_directory_old=""):
    # 值保存在 qsettings 里，内容再从这里过一遍

    mame_exe_path = ""
    mame_working_directory = ""

    # 如果存在此文件，设为绝对值
    # 如果不存在此文件，当成 ，它 在 系统 环境变量 里
    if os.path.isfile( mame_exe_path_old ):
        mame_exe_path = os.path.abspath( mame_exe_path_old )
    else:
        mame_exe_path = mame_exe_path_old
    
    # 工作文件夹，如果已设置
    if os.path.isdir( mame_working_directory_old ):
        mame_working_directory = os.path.abspath( mame_working_directory_old )
    else:
        # 工作文件夹，如果没有设置，自动设置为 mame 所在文件夹
        if os.path.isfile( mame_exe_path_old ):
            temp                   = os.path.dirname( mame_exe_path_old )
            mame_working_directory = os.path.abspath( temp )
    
    return mame_exe_path, mame_working_directory


# internal_index
def get_id_list_from_internal_index(id_1,id_2="",):
    
    the_index = ui_models.internal_index
    
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
    
    if not id_2:
        return for_level_1(id_1)
    else:
        return for_level_2(id_1,id_2)
# external_index
def get_id_list_from_external_index(id_1,id_2="",):
    
    the_index = ui_models.external_index
    
    # 第一层 "ROOT_FOLDER"
    def for_level_1(id_1):
        temp = [] # 可能为 list 也可能为 set
        if id_1 in the_index:
            if "ROOT_FOLDER" in the_index[id_1]:
                temp = the_index[id_1]["ROOT_FOLDER"]
        return temp
    
    # 第二层
    def for_level_2(id_1,id_2):
        temp = [] # 可能为 list 也可能为 set
        if id_1 in the_index:
            if id_2 in the_index[id_1]:
                temp = the_index[id_1][id_2]
        return temp
    
    if not id_2:
        return for_level_1(id_1)
    else:
        return for_level_2(id_1,id_2)
# external_index_by_source      mame
def get_id_list_from_external_index_by_source(id_1,id_2=""):
    the_index = ui_models.external_index_by_source
    internal_index = ui_models.internal_index
    
    # 第一层 "ROOT_FOLDER"
    def for_level_1(id_1):
        temp = [] 
        if id_1 in the_index:
            if "ROOT_FOLDER" in the_index[id_1]:
                temp = the_index[id_1]["ROOT_FOLDER"]
        return temp
    
    # 第二层
    def for_level_2(id_1,id_2):
        temp = [] 
        if id_1 in the_index:
            if id_2 in the_index[id_1]:
                temp = the_index[id_1][id_2]
        return temp
    
    if not id_2 :
        temp_list = for_level_1(id_1)
    else:
        temp_list = for_level_2(id_1,id_2)
    
    the_source_list=[] # 以源代码分类
    
    the_item_list=[] # 将去除的 一些 项目
    
    for x in temp_list:
        if x.startswith("- ") or x.startswith("-\t"):
            the_item_list.append( x[2:].lower().strip() )
        else:
            the_source_list.append(x)
    
    
    the_id_list = []
    
    # 1
    for the_source in set(the_source_list) :
        id_1="sourcefile"
        id_2=the_source
        the_id_list.extend( get_id_list_from_internal_index(id_1,id_2) )
    
    # 2 减掉
    if the_id_list and the_item_list:
        the_id_list = set(the_id_list) - set(the_item_list)

    
    return the_id_list #  list 或 set

