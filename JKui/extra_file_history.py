import xml.etree.ElementTree

"""
    history.xml
        https://www.arcade-history.com
    
    规则

    Information for the mainlist entries:
    
    <entry>
     <systems>
      <system name="rom_name">
      <system name="rom_name2">
      <system name="rom_name3">
     </systems>
     <text>information to show</text>
    </entry>
    
    
    
    Information for the softlist entries:
    
    <entry>
     <software>
      <item list="softlist_name" name="rom_name">
      <item list="softlist_name" name="rom_name2">
      <item list="softlist_name2" name="rom_name">
     </software>
     <text>information to show</text>
    </entry>
    
    
    
    
    Special case (when an entry appears in both softlist & mainlist):
    
    <entry>
     <systems>
      <system name="rom_name">
     </systems>
     <software>
      <item list="softlist_name" name="rom_name">
     </software>
     <text>information to show</text>
    </entry>

"""

def read_file( file_name ,parent_set=set() ):

    text = ''
    flag = False
    count = 0

    content_dict={}
    reuse_dict={}

    for (event, elem) in xml.etree.ElementTree.iterparse(file_name,events=("end",) ) :
        #if event == 'end': # 找到结束标记
        if elem.tag=="entry":
            count += 1

            game_name_list = []
            content = ""

            for child in elem:
                if child.tag == "systems" :
                    for grandchild in child:
                        game_name_list.append(grandchild.attrib["name"])
                        
                if child.tag == "text" :
                        content = child.text

            # 排序，将 第一个出现的 主版本 放在 首位
            if len(game_name_list) > 1:
                for n in range(len(game_name_list)):
                    if game_name_list[n] in parent_set:
                        if n == 0:
                            break
                        else:
                            game_name_list[0], game_name_list[n] = game_name_list[n], game_name_list[0]
                            break
            
            if game_name_list:
                content_dict[game_name_list[0]] = content
                for game_name in game_name_list[1:]:
                    reuse_dict[game_name] = game_name_list[0]

            elem.clear()

    #print(count)
    return content_dict,reuse_dict 



if __name__ == "__main__":
    import pickle

    file_name = r"c:\MAME\_code\JJui_C\history.xml"
    pickle_file_name = r"c:\MAME\_code\JKui\.JKui\cache_data.pickle"

    with open(pickle_file_name, "rb") as f:
        data = pickle.load(f)
    
    parent_set =data["set_data"]["parent_set"]

    content_dict,reuse_dict = read_file( file_name ,parent_set )

    with open("temp.txt", "wt",encoding="utf-8",errors="ignore") as f:
        for game_name in content_dict:
            f.write("\n")
            f.write("****************\n")
            f.write(game_name + "\n")
            f.write(content_dict[game_name] + "\n")
    with open("temp_2.txt", "wt",encoding="utf-8",errors="ignore") as f:
        for game_name in reuse_dict:
            f.write(game_name + "\t")
            f.write(reuse_dict[game_name] + "\n")