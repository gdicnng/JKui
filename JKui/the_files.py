import os
import pkgutil
import the_variables


current_working_directory = os.getcwd()

folder_temporary = os.path.join(current_working_directory, "." + the_variables.software_name)

user_config_file = os.path.join(folder_temporary, "JKui.ini")

folder_qss = os.path.join(folder_temporary, "qss")

data_file = os.path.join(folder_temporary ,"cache_data.bin") 

#文件的二进制数据
icon_for_mainwindow = pkgutil.get_data("my_resource", "icon_for_mainwindow.png")
icon_red = pkgutil.get_data("my_resource", r"icons_for_gamelist/red.png")
icon_green = pkgutil.get_data("my_resource", r"icons_for_gamelist/green.png")
icon_yellow = pkgutil.get_data("my_resource", r"icons_for_gamelist/yellow.png")
icon_black = pkgutil.get_data("my_resource", r"icons_for_gamelist/black.png")
#print(type(icon_red))
#<class 'bytes'>



if __name__ == "__main__" :
    # locals()
    # or
    # dir()
    
    temp = locals()
    #print()
    #print(temp)
    
    the_keys=sorted(temp.keys())
    #print()
    #print( the_keys )
    
    print()
    for x in the_keys:
        if x.startswith("_"):
            pass
        elif type(temp[x])==str:
            print(x.ljust(45),end="")
            print(' ',end='')
            print(temp[x])
