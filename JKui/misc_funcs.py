import os
import zipfile

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

def scan_game_files_only_check_if_file_exists_work(rompath,qsettings,merged=False):
    def get_roms_folder_list(rompath):
        
        settings = qsettings
        mame_path = settings.value("mame/path") 
        mame_working_directory = settings.value("mame/working_directory") 
        mame_path, mame_working_directory = get_abspath_for_mame_and_working_directory(mame_path, mame_working_directory)
        
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

def load_icons_from_zip(icon_zip_path,all_set=set()):
    # 读取所有文件，二进制数据
    result = dict()

    if not os.path.isfile(icon_zip_path):
        return result
    
    try:
        file = open(icon_zip_path, 'rb')
    except:
        return result
    
    if all_set:
        limitation = True
    else:
        limitation = False

    zip_ref = zipfile.ZipFile(file, 'r')
    
    for file_name in zip_ref.namelist():
        if "/" in file_name:
            continue
        
        if not file_name.endswith(".ico"):
            continue

        id_name = file_name.split(".")[0]
        
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
        file.close()
    except:
        pass

    if result:
        print()
        print("load icons from zip",len(result))

    return result

def update_filter_set(qsettings):

    settings = qsettings

    result = set()

    items=set()

    value = settings.value("gamelist/filter")
    if type(value) == str:
        value = value.strip()
        if value:
            for item in value.split(","):
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



    