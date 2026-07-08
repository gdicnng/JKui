import sqlite3
import os
import time
import pickle
    # pickle.dumps()
    # pickle.loads()

import the_files
#the_files.extra_database_file

import ui_models

import extra_file_history
import extra_file_history_2
import extra_file_mameinfo
import extra_file_gameinit
import extra_file_command_english
import extra_file_command



conn=None
table_name="extra"

# history.xml_path              history.xml                         v
# history.dat_path              history.dat                         v
# command.dat_path              command.dat                         v
# command_english.dat_path      command_english.dat                 v
# mameinfo.dat_path             mameinfo.dat                        v
# messinfo.dat_path             messinfo.dat                        v
# gameinit.dat_path             gameinit.dat                        v
# sysinfo.dat_path              sysinfo.dat                         x   这个好像现在没有了

columns=[

        "id",                                                # string ，mame_id,mess_id,source(mameinof.dat 中有)

        "history",                             # string
        "history_reuse",                        # sting , game_id
        
        "history_dat",                     # string
        "history_dat_reuse",

        "command",                          # dict {int:list[str]} ,int 正好计数用，得转 pickle 存储
        "command_reuse",

        "command_english",                  # 同上，格式差不太多
        "command_english_reuse",

        "mameinfo",                         # string
        "mameinfo_reuse",

        "messinfo",                         # messinfo 格式 与 mameinfo 一样
        "messinfo_reuse",

        "gameinit",                         # string
        "gameinit_reuse",
        ]



def connect_database():
    global conn
    try:
        conn = sqlite3.connect(the_files.extra_database_file)
        #conn.row_factory = sqlite3.Row
    except:
        conn = None

def table_exists(conn, table_name):
    cursor = conn.cursor()
    cursor.execute(
        "SELECT 1 FROM sqlite_master WHERE type='table' AND name=?",
        (table_name,)
    )
    result = cursor.fetchone() is not None
    cursor.close()
    return result

def get_all_tables(conn):
    cursor = conn.cursor()
    cursor.execute("""
        SELECT name FROM sqlite_master 
        WHERE type='table'
    """)
    tables = [row[0] for row in cursor.fetchall()]
    cursor.close()
    return tables

def create_table(conn):
    temp_column_str =[]
    for column in columns:
        if column  in ["command","command_english"]:
            temp_column_str.append(f"{column} BLOB DEFAULT NULL ")
        else:
            temp_column_str.append(f"{column} TEXT DEFAULT '' ")

    cursor = conn.cursor()
    cursor.execute(f"""
        CREATE TABLE IF NOT EXISTS {table_name} (
        {', '.join(columns) },
        PRIMARY KEY (id)
    )
    """)
    conn.commit()
    cursor.close()

def delete_table():
    if conn is None:
        connect_database()
    
    cursor = conn.cursor()
    cursor.execute(f"""
        DROP TABLE IF EXISTS {table_name}
    """)
    conn.commit()
    cursor.close()

def update_text(conn, column_name, reuse_column_name,content_dict,reuse_dict):
    if not table_exists(conn, table_name):
        create_table(conn)
    
    # 清空
    cursor = conn.cursor()
    cursor.execute(f"""
        UPDATE {table_name} SET {column_name}='',{reuse_column_name}=''
    """)
    conn.commit()

    # 更新 content_dict
    cursor.execute(f"""
        SELECT id FROM {table_name}
    """)
    game_id_in_table = set([row[0] for row in cursor.fetchall()])    
    for id,content in content_dict.items():
        if id in game_id_in_table:
            cursor.execute(f"""
                UPDATE {table_name} SET {column_name}=? 
                WHERE id=?
            """,(content,id))
        else:
            cursor.execute(f"""
                INSERT INTO {table_name}  ( id,{column_name} )
                VALUES (?,?) 
            """,(id,content) )
    conn.commit()

    # 更新 reuse_dict
    cursor.execute(f"""
        SELECT id FROM {table_name}
    """)
    game_id_in_table = set([row[0] for row in cursor.fetchall()])        
    for id,reuse in reuse_dict.items():
        if id in game_id_in_table:
            cursor.execute(f"""
                UPDATE {table_name} SET {reuse_column_name}=?
                WHERE id=?
            """,(reuse,id))
        else:
            cursor.execute(f"""
                INSERT INTO {table_name}  ( id,{reuse_column_name} )
                VALUES (?,?) 
            """,(id,reuse) )
    conn.commit()
    cursor.close()


def update_binary_data(conn, column_name, reuse_column_name,content_dict,reuse_dict):
    if not table_exists(conn, table_name):
        create_table(conn)
    
    # 清空
    cursor = conn.cursor()
    cursor.execute(f"""
        UPDATE {table_name} SET {column_name}=NULL,{reuse_column_name}=NULL 
    """)
    conn.commit()

    # 更新 content_dict
    cursor.execute(f"""
        SELECT id FROM {table_name}
    """)
    game_id_in_table = set([row[0] for row in cursor.fetchall()])    
    for id,content in content_dict.items():
        binary_content = pickle.dumps(content)
        if id in game_id_in_table:
            cursor.execute(f"""
                UPDATE {table_name} SET {column_name}=? 
                WHERE id=?
            """,(binary_content,id))
        else:
            cursor.execute(f"""
                INSERT INTO {table_name}  ( id,{column_name} )
                VALUES (?,?) 
            """,(id,binary_content) )
    conn.commit()

    # 更新 reuse_dict
    cursor.execute(f"""
        SELECT id FROM {table_name}
    """)
    game_id_in_table = set([row[0] for row in cursor.fetchall()])        
    for id,reuse in reuse_dict.items():
        if id in game_id_in_table:
            cursor.execute(f"""
                UPDATE {table_name} SET {reuse_column_name}=?
                WHERE id=?
            """,(reuse,id))
        else:
            cursor.execute(f"""
                INSERT INTO {table_name}  ( id,{reuse_column_name} )
                VALUES (?,?) 
            """,(id,reuse) )
    conn.commit()
    cursor.close()

#########################################
#########################################

def get_item_by_id(cursor,game_id,column_name):
    cursor.execute(f"""
        SELECT {column_name}
        FROM {table_name}
        WHERE id=?
    """,(game_id,))
    result =  cursor.fetchone()
    if result:
        return result[0]    # 结果也可能为空，空字符串 或 None
    else:
        return None
    
def get_item_and_reuse_by_id(cursor,game_id,column_name,reuse_column_name):
    cursor.execute(f"""
        SELECT {column_name},{reuse_column_name}
        FROM {table_name}
        WHERE id=?
    """,(game_id,))
    return cursor.fetchone()


def get_content_bak(cursor,game_id,column_name,reuse_column_name):
    
    #def get_extra_content(cursor,game_id)
    # 获取内容
    history = get_item_by_id(cursor,game_id,column_name)
    if history:
        return history
    
    # 如果没有内容，查询 reuse_column_name，再获取内容
    reuse_id = get_item_by_id(cursor,game_id,reuse_column_name)
    if reuse_id:
        history = get_item_by_id(cursor,reuse_id,column_name)
        if history:
            return history
    
    # 如果没有内容，如果是子版本，查询主版本
    if game_id in ui_models.clone_to_parent:
        parent_id = ui_models.clone_to_parent[game_id]
        return func_for_get_history(cursor,parent_id,column_name,reuse_column_name)

def make_func_for_get_content_bak(column_name,reuse_column_name):
    
    def get_extra_content(cursor,game_id):
        # 获取内容
        result = get_item_by_id(cursor,game_id,column_name)
        if result:
            return result
        
        # 如果没有内容，查询 reuse_column_name，再获取内容
        reuse_id = get_item_by_id(cursor,game_id,reuse_column_name)
        if reuse_id:
            result = get_item_by_id(cursor,reuse_id,column_name)
            if result:
                return result
        
        # 如果没有内容，如果是子版本，查询主版本
        if game_id in ui_models.clone_to_parent:
            parent_id = ui_models.clone_to_parent[game_id]
            
            # 获取内容
            result = get_item_by_id(cursor,parent_id,column_name)
            if result:
                return result
            
            # 如果没有内容，查询 reuse_column_name，再获取内容
            reuse_id = get_item_by_id(cursor,parent_id,reuse_column_name)
            if reuse_id:
                result = get_item_by_id(cursor,reuse_id,column_name)
                if result:
                    return result
    
    return get_extra_content
        
def make_func_for_get_content(column_name,reuse_column_name):
    
    def get_extra_content(cursor,game_id):
        # 获取内容
        result = get_item_and_reuse_by_id(cursor,game_id,column_name,reuse_column_name)
        if result is not None:
            text_content,reuse_id = result
            if text_content:   # 如果有内容
                return text_content
            else:     # 如果没有内容，查询 reuse_column_name，再获取内容
                if reuse_id:
                    #print("try reuse id",reuse_id)
                    result = get_item_by_id(cursor,reuse_id,column_name)
                    if result:
                        return result
        
        
        # 如果没有内容，如果是子版本，查询主版本
        
        if game_id in ui_models.clone_to_parent:
            #print("try parent")
            parent_id = ui_models.clone_to_parent[game_id]
            
            result = get_item_and_reuse_by_id(cursor,parent_id,column_name,reuse_column_name)
            if result is not None:
                text_content,reuse_id = result
                if text_content:   # 如果有内容
                    return text_content
                else:     # 如果没有内容，查询 reuse_column_name，再获取内容
                    if reuse_id:
                        result = get_item_by_id(cursor,reuse_id,column_name)
                        if result:
                            return result
    return get_extra_content
        

func_for_get_history     =make_func_for_get_content("history","history_reuse")
func_for_get_history_dat =make_func_for_get_content("history_dat","history_dat_reuse")
func_for_get_mameinfo    =make_func_for_get_content("mameinfo","mameinfo_reuse")
func_for_get_messinfo    =make_func_for_get_content("messinfo","messinfo_reuse")
func_for_get_gameinit    =make_func_for_get_content("gameinit","gameinit_reuse")
#func_for_get_command             =make_func_for_get_content("command","command_reuse")  
#func_for_get_command_english     =make_func_for_get_content("command_english","command_english_reuse")
# 参数 (cursor,game_id)



#########################################
#########################################

def update_history(conn,file_path,parent_set=set()):
    if not os.path.isfile(file_path):
        return
    
    content_dict,reuse_dict = extra_file_history.read_file(file_path,parent_set)
    
    update_text(conn, "history", "history_reuse", content_dict, reuse_dict)

def update_history_2(conn,file_path,parent_set=set()):
    if not os.path.isfile(file_path):
        return
    
    content_dict,reuse_dict = extra_file_history_2.read_file(file_path,parent_set)
    
    update_text(conn, "history_dat", "history_dat_reuse", content_dict, reuse_dict)    

def update_mameinfo(conn,file_path,parent_set=set()):
    if not os.path.isfile(file_path):
        return
    
    content_dict,reuse_dict = extra_file_mameinfo.read_file(file_path,parent_set)
    
    update_text(conn, "mameinfo", "mameinfo_reuse", content_dict, reuse_dict)

def update_messinfo(conn,file_path,parent_set=set()):
    if not os.path.isfile(file_path):
        return
    
    # 同 messinfo
    content_dict,reuse_dict = extra_file_mameinfo.read_file(file_path,parent_set)
    
    update_text(conn, "messinfo", "messinfo_reuse", content_dict, reuse_dict)

def update_gameinit(conn,file_path,parent_set=set()):
    if not os.path.isfile(file_path):
        return
    
    content_dict,reuse_dict = extra_file_gameinit.read_file(file_path,parent_set)
    
    update_text(conn, "gameinit", "gameinit_reuse", content_dict, reuse_dict)

def update_command(conn,file_path,parent_set=set()):
    if not os.path.isfile(file_path):
        return
    
    content_dict,reuse_dict = extra_file_command.read_command_dat_and_replace(file_path,parent_set)
    
    update_binary_data(conn, "command", "command_reuse", content_dict, reuse_dict)

def update_command_english(conn,file_path,parent_set=set()):
    if not os.path.isfile(file_path):
        return
    
    content_dict,reuse_dict = extra_file_command_english.read_command_dat_and_replace(file_path,parent_set)
    
    update_binary_data(conn, "command_english", "command_english_reuse", content_dict, reuse_dict)

if __name__ == "__main__":
    db_file=the_files.extra_database_file
    conn = sqlite3.connect(db_file)
    
    
    if not table_exists(conn, table_name):
        create_table(conn)    

    print()
    result = get_all_tables(conn,)
    print("tables",result)
    print() 

    start_time = time.time()
    update_history(conn,r"c:\MAME\_code\JKui\dats\history.xml")
    update_history_2(conn,r"c:\MAME\_code\JKui\history.dat")
    update_mameinfo(conn,r"c:\MAME\_code\JKui\dats\mameinfo.dat")
    update_messinfo(conn,r"c:\MAME\_code\JKui\dats\messinfo.dat")
    update_gameinit(conn,r"c:\MAME\_code\JKui\dats\gameinit.dat")
    update_command(conn,r"c:\MAME\_code\JKui\command.dat")
    update_command_english(conn,r"c:\MAME\_code\JKui\dats\command.dat")
    
    end_time = time.time()
    print(f"update_history time: {end_time - start_time}")
