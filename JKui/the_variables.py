software_name = "JKui"

user_settings = None # 记录 用户配置文件 ，QSettings

image_dockwidget_numbers = 20

command_line_options_for_emulator_to_export_data = ["-listxml", "-dtd"]

current_id = None

locale_original = None 
# 获取当前语言区域 locale.setlocale(locale.LC_ALL)  

sort_column = 0
sort_reverse = False
sort_colums_use_locale = []
sort_use_locale = False

index_id_1 = ""
index_id_2 = ""

# 游戏列表 列标题 翻译
columns_translation = {
        "id"          :"缩写",
        "year"        :"年代",
        "sourcefile"  :"源代码",
        "manufacturer":"制造商",
        "cloneof"     :"主版本",
        "translation" :"游戏名(译)",
        "description" :"游戏名",
        "status"      :"模拟状态",
        "savestate"   :"存档状态",
        }

# 目录列表，翻译 
index_translation = {
        'all_set'           :'所有列表',
        'available_set'     :'拥有列表',
        'unavailable_set'   :'未拥有列表',
        'parent_set'        :'主版本',
        'clone_set'         :'副版本',
        'bios'              :'bios',
        'device'            :'device',
        'mechanical'        :'mechanical',
        'softwarelist'      :'software list',
        'chd'               :'chd',
        'sample'            :'sample',
        'year'              :'年代',
        'manufacturer'      :'制造商',
        'sourcefile'        :'源代码',
        'status'            :'模拟状态',
        'savestate'         :"存盘状态",
        'dump'              :"dump 问题",
        'sound channels'    :"声音 通道",
        'chip cpu'          :"芯片 cpu",
        'chip audio'        :"芯片 audio",
        'input players'     :"输入 玩家",
        'input control'     :"输入 控制",
        'display number'    :"显示 数量",
        'display type'      :"显示 种类",
        'display refresh'   :"显示 刷新率",
        'display rotate'    :"显示 旋转",
        'display resolution':"显示 分辨率",

        #'only_sample_set':'仅需 sample，无需 rom、chd',
        #'no_roms':'无需 rom、chd',
        #'no_rom_chd_sample':'无需 rom、chd、sample',
        }

# 目录 默认排序
index_order = ( 
        'all_set',
        'available_set',
        'unavailable_set',
        'parent_set',
        'clone_set',
        
        'bios',
        'device',
        
        'chd',
        'sample',
        
        'mechanical',
        
        'softwarelist',
        
        #'no_roms',
        #'only_sample_set',
        #'no_rom_chd_sample',
        
        'year',
        'manufacturer',
        'sourcefile',
        'status',
        'savestate',
        'dump',
        'sound channels',
        
        'chip cpu',
        'chip audio',
        
        'input players',
        'input control',
        'display number',
        'display type',
        'display refresh',
        'display rotate',
        'display resolution',

                )


extra_image_folder_path={
    #  "extra_image_folder_path/image_1": "titles",

}
extra_image_zip_path={
    # "extra_image_zip_path/image_1": "titles.zip",
    
}
def update_extra_path():
    # 程序启动时，更新一下
    # 修改路径时，更新一下

    global extra_image_folder_path
    global extra_image_zip_path

    for n in range(1,image_dockwidget_numbers+1):

        temp_text = "extra_image_folder_path/image_"+str(n)
        extra_image_folder_path[temp_text] = ""
        try:
            result = user_settings.value(temp_text)
            if not result: # 可能是 None
                result = ""
            extra_image_folder_path[temp_text] = result
        except:
            pass


        temp_text = "extra_image_zip_path/image_"+str(n)
        extra_image_zip_path[temp_text] = ""
        try:
            result = user_settings.value(temp_text)
            if not result: # 可能是 None
                result = ""
            extra_image_zip_path[temp_text] = result
        except:
            pass

    print()
    for k,v in extra_image_folder_path.items():
        print(k,v)
    print()
    for k,v in extra_image_zip_path.items():
        print(k,v)
