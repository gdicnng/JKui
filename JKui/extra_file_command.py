import sys
#import os
import re


"""
command.dat
    中文版

    https://bbs.xqemu.cn/thread-2147-1-1.html
    
    已失效 ： https://www.ppxclub.com/130735-1-1


    
    
格式：
$info=game_id1,game_id2,……
$cmd
...内容1... 
$end
$cmd
...内容2... 
$end
……

"""


replace_dict={
        # 参考  jjsnake 中文出招表，文件头
        # 参考补充 日文出扫表，文件头
        
        #   还需要再补充 mame 插件 data , button_char.lua 中的内容
        
        r"@A-button" : r"Ａ",
        r"@B-button" : r"Ｂ",
        r"@C-button" : r"Ｃ",
        r"@D-button" : r"Ｄ",
        r"@E-button" : r"Ｅ",
        r"@F-button" : r"Ｆ",
        r"@G-button" : r"Ｇ",
        r"@H-button" : r"Ｈ",
        r"@I-button" : r"Ｉ",
        r"@J-button" : r"Ｊ",
        r"@K-button" : r"Ｋ",
        r"@L-button" : r"Ｌ",
        r"@M-button" : r"Ｍ",
        r"@N-button" : r"Ｎ",
        r"@O-button" : r"Ｏ",
        r"@P-button" : r"Ｐ",
        r"@Q-button" : r"Ｑ",
        r"@R-button" : r"Ｒ",
        r"@S-button" : r"Ｓ",
        r"@T-button" : r"Ｔ",
        r"@U-button" : r"Ｕ",
        r"@V-button" : r"Ｖ",
        r"@W-button" : r"Ｗ",
        r"@X-button" : r"Ｘ",
        r"@Y-button" : r"Ｙ",
        r"@Z-button" : r"Ｚ", 
        
        r"^s"        : r"Ｓ", # Ｓ
        
        r"_A"        : r"Ａ",
        r"_B"        : r"Ｂ",
        r"_C"        : r"Ｃ",
        r"_D"        : r"Ｄ",
        
        r"_Z"        : r"Ｚ",

        r"_+"  : r"＋",#gb2312
        r"_."  : r"…",# 啥意思，不过 jjsnake 出扫表里没有
        r"_1"  : r"↙",
        r"_2"  : r"↓",
        r"_3"  : r"↘",
        r"_4"  : r"←",
        r"_5"  : r"⊙", # ??? ⊙⊕
        # 摇杆回中 ???
        # 摇杆回中，用哪个符号？⊙⊕
        # 两个
        # ⊙ U+2299 CIRCLED DOT OPERATOR : direct product, vector pointing out of page
        # ☉ ，U+2609 SUN : alchemical symbol for gold
        r"_6"  : r"→",
        r"_7"  : r"↖",
        r"_8"  : r"↑",
        r"_9"  : r"↗",
        r"_N"  : r"Ｎ", # # # # 
        
        r"@BALL"  : r"⊙",# ??? ☉☉⊕⊕
        
        r"_a" : r"①",# ① gb2312
        r"_b" : r"②",
        r"_c" : r"③",
        r"_d" : r"④",
        r"_e" : r"⑤",
        r"_f" : r"⑥",
        r"_g" : r"⑦",
        r"_h" : r"⑧",
        r"_i" : r"⑨",
        r"_j" : r"⑩",
        
        r"@decrease" : r"－",
        r"@increase" : r"＋",
        
        r"_S":r"开始键",
        r"^S":r"选择键",
        r"_P":r"拳",
        r"_K":r"脚",
        r"_G":r"防",
        r"^E":r"轻拳",
        r"^F":r"中拳",
        r"^G":r"重拳",
        r"^H":r"轻脚",
        r"^I":r"中脚",
        r"^J":r"重脚",
        r"^T":r"三脚同时输入",
        r"^U":r"三拳同时输入",
        r"^V":r"两脚同时输入",
        r"^W":r"两拳同时输入",
        
        r"@start"   : r"开始键",
        r"@select"  : r"选择键",
        r"@punch"   : r"拳",
        r"@kick"    : r"脚",
        r"@guard"   : r"防",
        r"@L-punch" : r"轻拳",
        r"@M-punch" : r"中拳",
        r"@S-punch" : r"重拳",
        r"@L-kick"  : r"轻脚",
        r"@M-kick"  : r"中脚",
        r"@S-kick"  : r"重脚",
        r"@3-kick"  : r"三脚同时输入",
        r"@3-punch" : r"三拳同时输入",
        r"@2-kick"  : r"两脚同时输入",
        r"@2-punch" : r"两拳同时输入",
        
        r"@custom1" : r"自定义①",# ① gb2312
        r"@custom2" : r"自定义②",
        r"@custom3" : r"自定义③",
        r"@custom4" : r"自定义④",
        r"@custom5" : r"自定义⑤",
        r"@custom6" : r"自定义⑥",
        r"@custom7" : r"自定义⑦",
        r"@custom8" : r"自定义⑧",
        r"@up"      : r"↑",
        r"@down"    : r"↓",
        r"@left"    : r"←",
        r"@right"   : r"→",
        r"@lever"   : r"Φ",# gb2312 ????? Φф
        r"@nplayer" : r"Pn", #
        r"@1player" : r"P1", #
        r"@2player" : r"P2", #
        r"@3player" : r"P3", #
        r"@4player" : r"P4", #
        r"@5player" : r"P5", #
        r"@6player" : r"P6", #
        r"@7player" : r"P7", #
        r"@8player" : r"P8", #
        
        # ※
        
        # ・  在 gb2312  ，但不在 gbk 中 ????? ，U+30FB KATAKANA MIDDLE DOT 片假名？
        # · gbk ,U+00B7 MIDDLE DOT : midpoint (in typography), Georgian comma, Greek middle dot (ano teleia)
        r"_`" : r"·",
        r"_@" : r"◎",#gb2312
        r"_)" : r"○",#gb2312 ：# ○，U+25CB WHITE CIRCLE# 还有个 零〇 长得一样
        r"_(" : r"●",#gb2312
        r"_*" : r"☆",#gb2312
        r"_&" : r"★",#gb2312
        r"_%" : r"△",#gb2312
        r"_$" : r"▲",#gb2312
        r"_#" : r"∷",
        # 回字形状
        # 双重 正方形，楷体里没有，换一个算了
        # gbk 里有这个： ，没有 ▣ ,▣ 25a3 
        #### jjsnake 出招表中，好像没有用这个，正好
        # 〓＃▓∷
        r"_]" : r"□",#gb2312
        r"_[" : r"■",#gb2312
        r"_{" : r"▽",       #gbk
        r"_}" : r"▼",       #gbk
        r"_<" : r"◇",#gb2312
        r"_>" : r"◆",#gb2312
        
        r"_|" : r"跳",
        r"_O" : r"按住", #?
        r"_-" : r"空中",
        r"_=" : r"下蹲",
        r"^-" : r"靠近",
        r"^=" : r"离开",
        r"_~" : r"蓄", #?
        r"^*" : r"连按", # Serious Tap ? # ボタン連打 ????  | ^* | @tap      |
        r"^?" : r"任意键",
        
        r"@jump"  : r"跳",
        r"@hold"  : r"按住", # # ??
        r"@air"   : r"空中",
        r"@sit"   : r"下蹲",
        r"@close" : r"靠近",
        r"@away"  : r"离开",
        r"@charge": r"蓄", # # ??
        r"@tap"   : r"连按",
        r"@button": r"任意键",
        
        r"_k" : r"→↘↓↙←", # ????? 这下面一大堆
        r"_l" : r"←↖↑↗→",
        r"_m" : r"←↙↓↘→",
        r"_n" : r"→↗↑↖←",
        r"_o" : r"→↘↓",
        r"_p" : r"↓↙←",
        r"_q" : r"←↖↑",
        r"_r" : r"↑↗→",
        r"_s" : r"←↙↓",
        r"_t" : r"↓↘→",
        r"_u" : r"→↗↑",
        r"_v" : r"↑↖←",
        r"_w" : r"从下开始顺时针一圈", # ??
        r"_x" : r"从上开始顺时针一圈", # ??
        r"_y" : r"从上开始逆时针一圈", # ??
        r"_z" : r"从下开始逆时针一圈", # ??
        r"_L" : r"→→",
        r"_M" : r"←←",
        r"_Q" : r"→↓↘",
        r"_R" : r"←↓↙",
        
        # → ← ↑ ↓↖ ↗ ↘ ↙ 
        r"@hcb" : r"→↘↓↙←",# half circle back
        r"@huf" : r"←↖↑↗→",
        r"@hcf" : r"←↙↓↘→", # half circle forward
        r"@hub" : r"→↗↑↖←",
        r"@qfd" : r"→↘↓",
        r"@qdb" : r"↓↙←",
        r"@qbu" : r"←↖↑",
        r"@quf" : r"↑↗→",
        r"@qbd" : r"←↙↓",
        r"@qdf" : r"↓↘→", # qcf ? quarter circle forward
        r"@qfu" : r"→↗↑",
        r"@qub" : r"↑↖←",
        r"@fdf" : r"从下开始顺时针一圈", # ??
        r"@fub" : r"从上开始顺时针一圈", # ??
        r"@fuf" : r"从上开始逆时针一圈", # ??
        r"@fdb" : r"从下开始逆时针一圈", # ??
        r"@xff" : r"→→",
        r"@xbb" : r"←←",
        r"@dsf" : r"→↓↘",
        r"@dsb" : r"←↓↙",

        r"_!" : r"→",
        r"^!" : r"└→",
        r"^1" : r"↙蓄",
        r"^2" : r"↓蓄",
        r"^3" : r"↘蓄",
        r"^4" : r"←蓄",
        r"^6" : r"→蓄",
        r"^7" : r"↖蓄",
        r"^8" : r"↑蓄",
        r"^9" : r"↗蓄",
        
        r"@-->" : r"→",
        r"@==>" : r"└→",
        
        # mame 插件 ,data,button_char.lua 补充
        r"@AIR" : r"空中",# @AIR
        r"@DIR" : r"DIR",# @DIR
        r"@MAX" : r"最大",# @MAX
        r"@TAP" : r"TAP",# @TAP ??????
        
        r"^M" : r"最大",# ^M   # MAX
        
        r"_?" : r"DIR",# _?
        r"_H" : r"Ｈ",# _H
        r"_X" : r"TAP",# _X ?????
        r"_^" : r"空中",# _^

        }

# 正则替换
original_string_iterable = replace_dict.keys()
re_string_iterable       = [re.escape(x) for x in original_string_iterable] # re.escape() 转义
re_string                = "|".join(re_string_iterable)
p=re.compile(re_string)
#
def replace_func_for_sub(match):
    return replace_dict.get(match[0],match[0])
#
def replace_content(lines):
    result=[]
    for line in lines:
        #re.sub(pattern, repl, string, count=0, flags=0)
        result.append( re.sub( p, replace_func_for_sub, line,) )
    return result

# 普通替换
def replace_content_bak(lines):
    result=[]
    for line in lines:
        for x in replace_dict: 
            line = line.replace(x,replace_dict[x])
        result.append(line)
    return result

#############################

def read_command_dat(file_name,parent_set=set()):
    # 已分段，但格式不是字符串，保存到 sqlite3 好像有点麻烦，用 pickle 保存
    
    # 每段内容，为 list, 其中单个 元素为 一行string
    
    content_dict={}
        # key : 0,1,2,3,.... 。分段从 1 开始；如果标题前有内容，从0开始
        # value : list[str]
    reuse_dict={}
        # key: game_id
        # value: game_id be reused

    with open( file_name, 'rt',encoding='utf_8_sig',errors='replace') as text_file:
        
        str_ids = r'^\$info\=(\S.*?)\s*$'
        p_ids=re.compile(str_ids,)
        
        str_comment= r'^#'
        p_comment=re.compile(str_comment,)
        
        str_start= r'^\$cmd'
        p_start=re.compile(str_start,)

        str_end = r'^\$end'
        p_end=re.compile(str_end,)
        

        new_text = []
        #content = ""
        game_name_list = []
        content_start = False
        
        count = 0 # 每个游戏内，计数
        line_count = 0 # 总行数
        for line in text_file:
            line_count += 1
            
            
            # 注释
            m_comment = p_comment.search(line)
            if m_comment:
                if not content_start: 
                    # 文件开头部分的 是 注释 ；后面的，gameinit 中，感觉有可能不是注释。
                    # 暂时就这么滴吧
                    continue
            
            # id
            m_ids=p_ids.search(line)
            if m_ids:
                count = 0 # 新游戏，重置计数
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
                content_dict[game_name_list[0]] = dict()
                # reuse_dict
                if game_name_list:
                    for game_name in game_name_list[1:]:
                        reuse_dict[game_name] = game_name_list[0]
                
                continue
            
            # 开始
            m_start=p_start.search(line)
            if m_start:
                count += 1
                #print(game_name_list,"start",count)
                new_text = []
                content_start = True
                continue

            # 结束
            m_end=p_end.search(line)# 找到结束点
            if m_end:
                if game_name_list:
                    #print(game_name_list[0],count)
                    if count in content_dict[game_name_list[0]]:# 已经有了，重复使用结束标记
                        print("command.dat,maybe error ???","$end",line_count)
                    else:
                        content_dict[game_name_list[0]][count] = new_text
                # 清空
                #content = ""
                new_text = []
                content_start = False

                continue
            
            if content_start:
                new_text.append(line)
        
        
    return content_dict, reuse_dict
#
def read_command_dat_and_replace(file_name,parent_set=set()):
    content_dict,reuse_dict = read_command_dat( file_name ,parent_set )
    for game_name in content_dict:
        for count in content_dict[game_name]:
            content_dict[game_name][count] = replace_content(content_dict[game_name][count])
    return content_dict, reuse_dict

#############################


if __name__ == "__main__":
    pickle_file_name = r"c:\MAME\_code\JKui\.JKui\cache_data.pickle"
    command_file_path=r"c:\MAME\_code\JKui\command.dat"
    output_file_path=r"temp.txt"
    output_file_path_2=r"temp_2.txt"

    import pickle
    with open(pickle_file_name, "rb") as f:
        data = pickle.load(f)
    
    parent_set =data["set_data"]["parent_set"]

    content_dict,reuse_dict = read_command_dat_and_replace( command_file_path ,parent_set )

    with open(output_file_path, "wt",encoding="utf-8",errors="ignore") as f:
        for game_name in content_dict:
            f.write("\n")
            f.write("****************\n")
            f.write(game_name + "\n")

            for n in sorted( content_dict[game_name].keys()):
                f.write(str(n)+ "\n")
                lines = content_dict[game_name][n]
                
                for line in lines:
                    f.write(line)

    with open(output_file_path_2, "wt",encoding="utf-8",errors="ignore") as f:
        for game_name in reuse_dict:
            f.write(game_name + "\t")
            f.write(reuse_dict[game_name] + "\n")    

