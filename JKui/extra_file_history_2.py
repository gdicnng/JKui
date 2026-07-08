import re


"""
history.dat
老格式
很久以前有个 中文版 history.dat

格式：

# 开头，注释
  文件开头有些注释以 
  后面有少量注释

$info=game_id1,game_id2
$bio
...内容...
$end

"""



def read_file(file_name,parent_set=set()):

    #$info=xxx,xxx,xxx
    #^\$info\=(\S.*?)\s*$
    
    # $bio
    # $end
    
    content_dict={}
    reuse_dict={}

    with open( file_name, 'rt',encoding='utf_8_sig',errors='replace') as text_file:
        
        str_ids = r'^\$info\=(\S.*?)\s*$'
        p_ids=re.compile(str_ids,)
        
        str_comment= r'^#'
        p_comment=re.compile(str_comment,)
        
        str_start= r'^\$bio'
        p_start=re.compile(str_start,)

        str_end = r'^\$end'
        p_end=re.compile(str_end,)
        

        new_text = []
        content = ""
        game_name_list = []
        content_start = False
        
        count = 0
        for line in text_file:
            count += 1
            
            # 注释
            m_comment = p_comment.search(line)
            if m_comment:
                if not content_start: 
                    # 文件开头部分的 是 注释 ；后面的，或许有可能不是注释。
                    # 暂时就这么滴吧
                    continue
            
            # id
            m_ids=p_ids.search(line)
            if m_ids:
                game_name_list = m_ids.group(1).split(",")
                #print( game_name_list )

                #if len(game_name_list) >1:
                #    print(game_name_list)
                continue
            
            # 开始
            m_start=p_start.search(line)
            if m_start:
                new_text = []
                content_start = True
                continue

            # 结束
            m_end=p_end.search(line)# 找到结束点
            if m_end:

                # 排序，将 第一个出现的 主版本 放在 首位
                if len(game_name_list) > 1:
                    for n in range(len(game_name_list)):
                        if game_name_list[n] in parent_set:
                            if n == 0:
                                break
                            else:
                                game_name_list[0], game_name_list[n] = game_name_list[n], game_name_list[0]
                                break
                if new_text:
                    if game_name_list:
                        content = "".join(new_text)
                        content_dict[game_name_list[0]] = content
                        for game_name in game_name_list[1:]:
                            reuse_dict[game_name] = game_name_list[0]
                    else:
                        print("history.dat,maybe error ???","$end",count)

                    
                # 清空
                content = ""
                new_text = []
                game_name_list = []
                content_start = False

                continue

            new_text.append(line)
        
        
    return content_dict, reuse_dict

if __name__ == "__main__":
    import pickle

    file_name = r"c:\MAME\_code\JJui_C\history.dat"
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