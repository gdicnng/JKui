import re

import extra_file_command



"""
command.dat
    英文版

    https://www.progettosnaps.net/command/
    


    
    
格式：
$info=game_id1,game_id2,……
$cmd
...内容... 
$end


内容中的分段形式：
- 子标题1 -
─────────────────────────────────────────────────────────────────────────
行1……
行2……
……

- 子标题2 -
─────────────────────────────────────────────────────────────────────────
行1……
行2……
……

"""


# 未分段
def read_command_dat_0(file_name,parent_set=set()):
    
    content_dict={}
    reuse_dict={}

    with open( file_name, 'rt',encoding='utf_8_sig',errors='replace') as text_file:
        
        #str_ids = r'^\$info\=(\S.*?)\s*$'
        str_ids = r'^\$info\=(.*?)\s*$' # 最后一个，它给了个空值
        p_ids=re.compile(str_ids,)
        
        str_comment= r'^#'
        p_comment=re.compile(str_comment,)
        
        str_start= r'^\$cmd'
        p_start=re.compile(str_start,)

        str_end = r'^\$end'
        p_end=re.compile(str_end,)
        

        game_name_list = []
        content_start = False
        
        line_count = 0 
        for line in text_file:
            line_count += 1
            
            m_comment = p_comment.search(line)
            if m_comment:
                if not content_start: 
                    continue
            
            # id
            m_ids=p_ids.search(line)
            if m_ids:
                game_name_list = m_ids.group(1).split(",")
                #print( game_name_list )
                
                # 排序，将 第一个出现的 主版本 放在 首位
                if len(game_name_list) > 1:
                    for n in range(len(game_name_list)):
                        if game_name_list[n] in parent_set:
                            if n == 0:
                                break
                            else:
                                game_name_list[0], game_name_list[n] = game_name_list[n], game_name_list[0]
                                break
                # content_dict
                #  初始化
                content_dict[game_name_list[0]] = []
                # reuse_dict
                if game_name_list:
                    for game_name in game_name_list[1:]:
                        reuse_dict[game_name] = game_name_list[0]
                
                continue
            
            m_start = p_start.search(line)
            if m_start:
                content_start = True
                continue
            
            m_end = p_end.search(line)
            if m_end:
                content_start = False
                continue

            if content_start:
                if game_name_list:
                    content_dict[game_name_list[0]].append(line)
        
        
    return content_dict, reuse_dict
# 分段  等
def read_command_dat(file_name,parent_set=set()):
   
    # 分段

    content_dict, reuse_dict = read_command_dat_0(file_name,parent_set)

    title_str_re=r"\- (.+) \-.*\n(─{8,})" # 两行 ：第一行 标题；第二行 分隔线
    p_title = re.compile(title_str_re)

    for game_id in content_dict:
        value = content_dict[game_id] # list of str
        temp_dict = {}

        # 找到标题所在的 行
        title_index_list=[]
        title_list=[]
        if len(value) > 2:

            first_line  = value[0]
            index_number_of_second_line = 1

            while(index_number_of_second_line < len(value) ):

                second_line = value[index_number_of_second_line]

                m = p_title.search(first_line + second_line)
                if m:
                    title_list.append( m.group(1) )
                    title_index_list.append(index_number_of_second_line - 1)
                
                first_line = second_line
                index_number_of_second_line += 1
        
        if not title_list:
            # 没有标题
            # 0 
            temp_dict[0] = value
        else:
            # 有标题

            # 0
            if title_index_list[0] != 0:
                # 第一个标题 不是 第一行
                temp_dict[0] = value[ : title_index_list[0] ]

            # 1+
            for n in range(len(title_list)):

                title_count = n + 1
                # 从 1 开始

                title_index = title_index_list[n]

                if n == len(title_list) - 1: 
                    # 是最后一个标题
                    temp_dict[title_count] = value[ title_index : ]
                else:
                    # 不是最后一个标题
                    title_index_2 = title_index_list[n+1]
                    temp_dict[title_count] = value[ title_index : title_index_2  ] 
        content_dict[game_id] = temp_dict
    
    return content_dict, reuse_dict


def read_command_dat_and_replace(file_name,parent_set=set()):
    content_dict,reuse_dict = read_command_dat( file_name ,parent_set )
    for game_name in content_dict:
        for count in content_dict[game_name]:
            content_dict[game_name][count] = extra_file_command.replace_content(content_dict[game_name][count])
    return content_dict, reuse_dict

if __name__ == "__main__":
    pickle_file_name = r"c:\MAME\_code\JKui\.JKui\cache_data.pickle"
    command_file_path=r"c:\MAME\_code\JKui\command_english.dat"
    output_file_path=r"temp.txt"
    output_file_path_2=r"temp_2.txt"
    output_file_path_3=r"temp_3.txt"
    output_file_path_4=r"temp_4.txt"

    import pickle
    with open(pickle_file_name, "rb") as f:
        data = pickle.load(f)
    
    parent_set =data["set_data"]["parent_set"]

    content_dict,reuse_dict = read_command_dat_0( command_file_path ,parent_set )
    with open(output_file_path, "wt",encoding="utf-8",errors="ignore") as f:
        for game_name in content_dict:
            f.write("\n")
            f.write("****************\n")
            f.write(game_name + "\n")
            f.write("".join(content_dict[game_name]))
            #print(game_name,content_dict[game_name],"\n")
    with open(output_file_path_2, "wt",encoding="utf-8",errors="ignore") as f:
        for game_name in reuse_dict:
            f.write(game_name + "\t")
            f.write(reuse_dict[game_name] + "\n")

    content_dict,reuse_dict = read_command_dat( command_file_path ,parent_set )
    with open(output_file_path_3, "wt",encoding="utf-8",errors="ignore") as f:
        for game_name in content_dict:
            f.write("\n")
            f.write("****************\n")
            f.write(game_name + "\n")
            for n in content_dict[game_name]:
                f.write(str(n) + "*"*20 + "\n")
                f.write("".join(content_dict[game_name][n]))
            
    with open(output_file_path_4, "wt",encoding="utf-8",errors="ignore") as f:
        for game_name in reuse_dict:
            f.write(game_name + "\t")
            f.write(reuse_dict[game_name] + "\n")




