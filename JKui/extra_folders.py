import os
import glob


all_dict = dict()


# 分类列表
#
# 读取外部目录数据


# by source
def get_external_index_data(folders_path,file_extension=".ini"):
    
    # 去掉 双引号
    folders_path = folders_path.replace(r'"',"")

    # 分类列表文件  
    ini_files = {} # 初始化
        # keys,为 （相对/绝对）路径 + 文件名 ，
        # values ，为 文件名，不含路径
    # 分类列表，具体信息
    external_index_data = {} # 初始化
        # keys,为 （相对/绝对）路径 + 文件名 ，
        # values ，为 为一个 {}
            # keys,为子分类名，
            # values,为，分类游戏，集合 ,后来 转为 list 格式了
    # 查找 文件
    for x in folders_path.split(';') :
        ini_files.update( folders_search_ini( x ,file_extension=file_extension) )
    
    
    # 计算分类列表 具体信息
    for x in ini_files:
        temp = read_folder_ini(x) ## 
        if temp is None:
            # 格式错误，只检查了个别错误
            pass
        else: 
            #external_index_data[x] = {} 
            external_index_data[x] = temp  
    
    return external_index_data



def folders_search_ini(path,file_extension=".ini"):
    # 搜索 ini 文件
    
    # 扩展名
    ext = r'*' + file_extension
        # *.ini
        # *.sl_ini
    
    
    search_str = os.path.join(path, ext)
    #print( search_str )
    
    result = glob.glob( search_str )
    #print( result )
    
    temp_dict ={ }
    
    #os.path.basename(path)
    #去掉路径，只显示文件名
    for n in range( len(result) ):
        path_and_name = result[n] 
        basename = os.path.basename( result[n] )
        temp_dict[path_and_name] = {} # 新建一个 dict
        temp_dict[path_and_name] = basename

    # temp_dict 的键值为 文件名 （不含路径）
    # 每一个素中
    # { xxx\yyy\z.ini : z.ini}
    # 可能是相对路径，可能是绝对路径
    return temp_dict

def folders_save(file_name,data):
    
    f = open(file_name, 'wt',encoding='utf_8_sig')
    
    print(r"[FOLDER_SETTINGS]",file=f)
    if "FOLDER_SETTINGS" in data:
        for x in sorted( data["FOLDER_SETTINGS"] ):
            print(x,file=f)
    print("",file=f)
    
    print(r"[ROOT_FOLDER]",file=f)
    if "ROOT_FOLDER" in data:
        for x in sorted( data["ROOT_FOLDER"] ) :
            print(x,file=f)
    print("",file=f)

    for x in sorted( data.keys() ):
        if x not in ("FOLDER_SETTINGS","ROOT_FOLDER"):
            temp = r"[" + x + r"]"
            print(temp,file=f)

            for y in sorted(data[x]):
                print(y,file=f)

            print("",file=f)
    
    f.close()

def read_folder_ini(file_name):
    global all_dict
    # all_dict 
    # 元素：game_id:game_id
    # 用于过滤，相同字符串，有可能使用一个地址，节省空间

    
    lines = None

    try:
        file = open( file_name , mode = 'rt', encoding = 'utf_8_sig', )
        lines = file.readlines()
        file.close()
    except:
        lines = None
    

    temp_dict = {}
    mark = None # 分类 标题
    mark_list = []
    

    content = lines

    if content is None:
        return None # 之前 读取 文本 出错
    
        
    #index_counter = 0
    for line in content:
        
        line=line.strip()
        
        # 空行
        if not line:
            continue
        
        # 标题 行
        # [ 开头, ]结尾
        if line.startswith(r"[") and line.endswith(r"]"):

                mark = line[1:-1]

                # FOLDER_SETTINGS
                if mark.strip().lower() == "folder_settings":
                    mark="FOLDER_SETTINGS"
                
                # ROOT_FOLDER
                if mark.strip().lower() == "root_folder":
                    mark="ROOT_FOLDER"

                if mark == "": # 空值
                    mark = "-"
                
                mark_list.append(mark)
                if mark not in temp_dict: # 第一次，出始化
                    temp_dict[mark] = []
                continue
        
        # 内容行
        if mark==None:
            return None
            # 格式出错，内容出现在标题前
        else:
            game_id =line.lower() # 转为小写
            
            if game_id in all_dict: 
                temp_dict[mark].append( all_dict[game_id] )
            else:
                temp_dict[mark].append( game_id )
    
    # 格式错误
    #
    # 没有 "FOLDER_SETTINGS" ，mameui 也行
    # mameui 大写
    #
    # 没有 "ROOT_FOLDER" ，mameui 也行
    # mameui 大写
    #
    # 空文件，mameui 也行，也可以添加新游戏在其中
    #
    # 没有任何分类，直接列表，kof97、kov……，mameui报错
    #   
    
    # 如果没有
    # 添加一个空的
    if "FOLDER_SETTINGS" not in temp_dict:
        temp_dict["FOLDER_SETTINGS"] =  []
    
    # 如果没有
    # 添加一个空的    
    if "ROOT_FOLDER" not in temp_dict:
        temp_dict["ROOT_FOLDER"] =  []
        
    return temp_dict



