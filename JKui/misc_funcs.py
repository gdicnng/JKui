import os
import zipfile
import re
import shutil
import time
import io

import ui_models


def get_abspath_for_mame_and_working_directory(mame_exe_path_old="", mame_working_directory_old=""):
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

def get_abspath_for_exe_path_and_working_directory(exe_path_old="", working_directory_old=""):
    # 用户设定

    # 如果是相对路径，转换
    # 先转换  working_directory
    # exe_path 相对于  working_directory 再转换，
    # 如果 exe_path 为单文件名，检查是否是命令行中的程序

    exe_path = ""
    working_directory = ""

    # 都是绝对路径
    if os.path.isabs( exe_path_old ) and os.path.isfile( exe_path_old ):
        exe_path = exe_path_old
        working_directory = working_directory_old
        return exe_path, working_directory
    
    # exe 为绝对路径
    if os.path.isabs( exe_path_old ):
        exe_path = exe_path_old

        if working_directory_old:
            working_directory = os.path.abspath( working_directory_old )
        return exe_path, working_directory
    
    # exe 不是绝对路径
    else:
        if working_directory_old:
            working_directory = os.path.abspath( working_directory_old )

        # 相对路径拼接
        temp_file_path = os.path.join(working_directory_old,exe_path_old) 

        # 不含分隔路径符号
        # 有可能使用了命令行中的程序
        if os.path.split(exe_path_old)[0] == "": 
            
            if shutil.which(temp_file_path) is None:
                # 拼接的路径，不可执行
                
                # 检查 是否是 命令行中已有程序
                # 也可能是当前目录下文件名的缩写 比如 mame.exe 缩写为 mame ；这样虽然找不到路径，但可以执行
                if shutil.which(exe_path_old) is not None:
                    exe_path = exe_path_old
                    # 这种不用转换为绝对路径
                    return exe_path, working_directory

        # 其它情况
        exe_path = os.path.abspath( temp_file_path ) 
        return exe_path, working_directory


def scan_game_files_only_check_if_file_exists_work(mame_working_directory,rompath,merged=False):
    #time.sleep(5)
    def get_roms_folder_list(rompath):
        
        roms_folder_list = []
        
        if rompath:
            rompath = rompath.replace(r'"',"") # 去掉双引号
        
        for x in rompath.split(r';'):
            if x:
                #######
                # rompath ，记录的相对路径，是相对于模拟器的
                ### ###
                # 还有一种情况
                # 路径里有变量：$HOME/mame/roms
                    ####
                    # 有变量的，到底有几种格式？
                
                # 情况1，如果有变量，展开，
                temp_path = x
                try:
                    temp_path = os.path.expandvars( x )
                except:
                    temp_path = x

                if os.path.isabs( temp_path ): # 如果是，绝对路径，不用转换
                    roms_folder_list.append( temp_path )
                else: # 如果是，相对路径，转换
                    y = os.path.join(mame_working_directory,temp_path)
                    roms_folder_list.append( y )
        return roms_folder_list

    def get_files_names_in_rompath(merged = False,roms_folder_list=None):
        # 仅检查文件 存在 与否
        # 不深度检查文件的 正确性、完整性
        # *.zip 、*.7x 、文件夹
        temp=[]
        
        if roms_folder_list is None:
            roms_folder_list = []
        
        for a_folder in roms_folder_list:
            if not os.path.isdir(a_folder):
                continue
            
            (dirpath, dirnames, filenames) = next( os.walk(a_folder) )
            
            # 文件夹
            for name in dirnames:
                temp.append( name.lower() )
            
            # zip or 7z
            for name in filenames:
                
                name_lower=name.lower()
                
                if name_lower.endswith(r".zip") :
                    temp.append(name_lower[0:-4]) # .zip
                elif name_lower.endswith(r".7z"):
                    temp.append(name_lower[0:-3]) # .7z
                    
        
        temp_set = set( temp )
        
        temp_set = ui_models.all_set & temp_set
        
        # merged
        if merged :
            # 现有的主版
            the_parent = temp_set & ui_models.parent_set
            
            # 其中，有副版本的
            the_parent = the_parent & set( ui_models.parent_to_clone.keys() )
            
            # 关联的副版本
            the_colne = []
            for x in the_parent:
                the_colne.extend( ui_models.parent_to_clone[x] )
            the_colne = set( the_colne )
            
            # 合并
            the_result = temp_set | the_colne
            return  the_result
        
        # split
        else:
            return temp_set

    rompath_folder_list = get_roms_folder_list(rompath)
    for a_folder in rompath_folder_list:
        print(a_folder)
    result = get_files_names_in_rompath(merged,rompath_folder_list)
    print("numbers :",len(result))
    return result


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
# 编辑
def set_id_list_for_external_index(the_id_list,id_1,id_2=""):
    if type(the_id_list) is not list:
        the_id_list = list( the_id_list )
    
    the_index = ui_models.external_index
    
    # 第一层 "ROOT_FOLDER"
    def for_level_1(the_id_list,id_1):
        if id_1 in the_index:
            the_index[id_1]["ROOT_FOLDER"] = the_id_list
    
    # 第二层
    def for_level_2(the_id_list,id_1,id_2):
        if id_1 in the_index:
            the_index[id_1][id_2] = the_id_list
    
    if not id_2:
        for_level_1(the_id_list , id_1)
    else:
        for_level_2(the_id_list , id_1 , id_2)
# 编辑 删一个
def delect_one_item_from_external_index(game_id,id_1,id_2=""):
    if not game_id:
        return

    old_items = get_id_list_from_external_index(id_1,id_2) # 不过滤
    old_items = set(old_items)

    if game_id in old_items:
        old_items.remove(game_id)

        old_items = list(old_items)

        set_id_list_for_external_index(old_items,id_1,id_2)

        # 记录
        ui_models.index_files_be_edited.add(id_1)

        return True
# 编辑 删
def delect_items_from_external_index(game_id_set,id_1,id_2=""):
    if not game_id_set:
        return

    if isinstance(game_id_set,str):
        game_id_set = set()
        game_id_set.add(game_id_set)

    if not isinstance(game_id_set,set):
        game_id_set = set(game_id_set)

    old_items = get_id_list_from_external_index(id_1,id_2) # 不过滤
    old_items = set(old_items)
    old_len = len(old_items)

    old_items -= game_id_set

    new_len = len(old_items)

    if new_len != old_len:

        old_items = list(old_items)

        set_id_list_for_external_index(old_items,id_1,id_2)

        # 记录
        ui_models.index_files_be_edited.add(id_1)

        return True
# 编辑 添加
def add_items_to_external_index(game_id_set,id_1,id_2=""): # set
    if not game_id_set:
        return

    if isinstance(game_id_set,str):
        game_id_set = set()
        game_id_set.add(game_id_set)

    if not isinstance(game_id_set,set):
        game_id_set = set(game_id_set)

    old_items = get_id_list_from_external_index(id_1,id_2) # 不过滤
    old_items = set(old_items)
    old_len = len(old_items)

    old_items.update(game_id_set) # 添加

    new_len = len(old_items)

    if new_len != old_len:
        old_items = list(old_items)

        set_id_list_for_external_index(old_items,id_1,id_2)

        # 记录
        ui_models.index_files_be_edited.add(id_1)

        return True


# 外部目录，列出，范围以外的 项目



def load_icons_from_zip(icon_zip_path,all_set=None):
    if all_set is None:
        all_set = set()
    
    # 读取所有文件，二进制数据
    result = dict()

    if not os.path.isfile(icon_zip_path):
        return result

    io_data = io.BytesIO()
    
    try:
        file = open(icon_zip_path, 'rb')
        io_data.write(file.read())
        io_data.seek(0)
        file.close()
    except:
        return result
    
    if all_set:
        limitation = True
    else:
        limitation = False

    zip_ref = zipfile.ZipFile(io_data, 'r')
    
    for file_name in zip_ref.namelist():
        if "/" in file_name:
            continue
        
        if not file_name.endswith(".ico"):
            continue

        id_name = file_name[:-4]
        
        if limitation:
            if id_name in all_set:
                try:
                    with zip_ref.open(file_name,mode="r") as f:
                        data = f.read()
                        result[id_name] = data
                except:
                    pass

        else:
            try:
                with zip_ref.open(file_name,mode="r") as f:
                    data = f.read()
                    result[id_name] = data
            except:
                pass

    try:
        zip_ref.close()
        io_data.close()
    except:
        pass

    if result:
        print()
        print("load icons from zip",len(result))

    return result


def update_filter_set(gamelist_filter):

    result = set()

    items=set()

    if type(gamelist_filter) == str:
        gamelist_filter = gamelist_filter.strip()
        if gamelist_filter:
            for item in gamelist_filter.split(","):
                item = item.strip()
                if item:
                    items.add(item)

    result_list = []
    for item in items:
        print(item)
        if item in ("status preliminary","status good","status imperfect"):
            id_1,id_2 = item.split(" ")
            game_list = ui_models.get_id_list_from_index(id_1,id_2)
            print(len(game_list))
            result_list.append(game_list)
        else:
            id_1 = item
            game_list = ui_models.get_id_list_from_index(id_1)
            print(len(game_list))
            result_list.append(game_list)

    result.update(*tuple(result_list))

    
    print(len(result),"----------")
    result = result & ui_models.all_set
    ui_models.filter_set = result
    print("update filter_set",len(result))

