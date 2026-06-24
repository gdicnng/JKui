import os


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