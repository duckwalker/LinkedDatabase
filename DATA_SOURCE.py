import json
import requests
import datetime
import mysql.connector
# from Xlent_AGV_Data_Server import *
# from Machine_Data import *
from pydantic import BaseModel
from typing import Union


class Item(BaseModel):
    machine_name: str  # String (Machine_Name)
    status: str  # Machine Running, Machine Stop, Machine Alarm, Machine Idle
    uph: int  # int
    cycle_time: float  # minute
    up_time: float  # minute
    down_time: float  # minute
    idle_time: float  # minute
    run_time: float  # minute
    error_count: int  # int
    update_time: str  # day/month/year, hour/minute/second

class x_core_setting(BaseModel):
    machine_name: str  # String (Machine_Name)
    data: dict

class Tasking_Item(BaseModel):
    machine_name: str  # String (Machine_Name)
    module: str
    task: str

class URL_INFO(BaseModel):
    url: str
    description: str
    type: str
    method: str

class USER_INFO(BaseModel):
    user_name: str
    password: str
    role: str
    description: str

class Testing_perpose(BaseModel):
    name: Union[str, None] = ""
    # name: str
    role: str

class machine_data_server:
    def __init__(self, database_ip: str, database_user: str, database_password: str, database_name: str):
        self.s_request = requests.Session()
        self.database_host = database_ip
        self.database_user = database_user
        self.database_password = database_password
        self.database_name = database_name

    def database_login(self):
        return mysql.connector.connect(host=self.database_host, user=self.database_user, password=self.database_password,
                                               database=self.database_name)

    def machine_count(self):
        agv_database = self.database_login()
        db_cursor = agv_database.cursor()
        db_cursor.execute("SHOW TABLES")
        table = []
        for i in db_cursor:
            table.append(i[0])
        return table

    def calculation(self, item):
        # cycle_time
        # uph
        # run_time
        # down_time
        #
        #
        if not (float(item['cycle_time']) == 0 or not (float(item['uph']) == 0)):
            ideal_run_rate = 60 / (float(item['cycle_time']) * 60)
            operation_time = float(item['run_time']) - float(item['down_time'])
            item["availability"] = operation_time / float(item['up_time'])
            item["performance"] = (float(item['uph']) / operation_time / ideal_run_rate)
            item["quality"] = int(item['uph']) / int(item['uph'])
        else:
            item["availability"] = 0
            item["performance"] = 0
            item["quality"] = 0

    def save_machine_database(self, table_name, item):
        print(item)
        # URL, DESCRIPTION, TYPE, METHOD,description
        item_list = []
        # for z in item:
        #     item_list.append(item[z])
        # item_list = ",".join(map(str, item_list))
        # print(item_list)
        database = self.database_login()
        item = json.loads(item)
        while True:
            db_cursor = database.cursor()
            db_cursor.execute("SHOW TABLES")
            table = []
            for i in db_cursor:
                table.append(i[0])
            if table_name in table:
                sql = f"INSERT INTO {table_name} (URL,DESCRIPTION,TYPE,METHOD) VALUES('{item['url']}', '{item['description']}', '{item['type']}', '{item['method']}') ON DUPLICATE KEY UPDATE description = '{item['description']}', type = '{item['type']}', method = '{item['method']}'"
                # INSERT INTO control_api(id, URL, DESCRIPTION, TYPE)  VALUES(3,"test", "Fadl", "666") ON DUPLICATE KEY UPDATE URL = "Fadl", DESCRIPTION = "88", TYPE ="Get";
                # val = (item['url'], item['description'], item['type'])
                db_cursor.execute(sql) # val
                database.commit()
                break
            else:
                db_cursor.execute(
                    f"CREATE TABLE {table_name}( URL VARCHAR(100) PRIMARY KEY ,DESCRIPTION VARCHAR(200),TYPE VARCHAR(50),METHOD VARCHAR(50))")

    def machine_grab_data(self, table_name: str, host: bool = False):
        agv_database = self.database_login()
        while True:
            db_cursor = agv_database.cursor()
            db_cursor.execute("SHOW TABLES")
            table = []
            for z in db_cursor:
                table.append(z[0])

            if table_name in table:
                db_cursor.execute(f"Describe {table_name}")
                table_data = []
                for y in db_cursor:
                    table_data.append(y[0])
                db_cursor.fetchall()
                db_cursor.execute(f"select * from {table_name}")
                full_data = []
                data = {}
                for i in db_cursor:
                    for x in range(len(i)):
                        data[table_data[x].lower()] = i[x]
                        print(table_data[x].lower(), i[x])
                    full_data.append(data)
                    data = {}
                return full_data
            else:
                break

    def delete_row(self, table_name, item):
        database = self.database_login()
        item = json.loads(item)
        while True:
            db_cursor = database.cursor()
            db_cursor.execute("SHOW TABLES")
            table = []
            for i in db_cursor:
                table.append(i[0])
            if table_name in table:
                #sql = f"INSERT INTO {table_name} (URL,DESCRIPTION,TYPE) VALUES('{item['url']}', '{item['description']}','{item['type']}') ON DUPLICATE KEY UPDATE description = '{item['description']}', type = '{item['type']}'"
                # INSERT INTO control_api(id, URL, DESCRIPTION, TYPE)  VALUES(3,"test", "Fadl", "666") ON DUPLICATE KEY UPDATE URL = "Fadl", DESCRIPTION = "88", TYPE ="Get";
                # val = (item['url'], item['description'], item['type'])
                sql = f'DELETE from {table_name} where url = "{item["url"]}";'
                db_cursor.execute(sql)  # ,val)
                database.commit()
                break
            else:
                db_cursor.execute(
                    f"CREATE TABLE {table_name}( URL VARCHAR(100) PRIMARY KEY ,DESCRIPTION VARCHAR(200),TYPE VARCHAR(50))")

    def machine_grab_pass_data(self, machine_name: str, type: str = "hour", start_count: int = 0, end_count: int = 0, host: bool = False):
        agv_database = self.database_login()
        while True:
            db_cursor = agv_database.cursor()
            db_cursor.execute("SHOW TABLES")
            table = []
            for i in db_cursor:
                table.append(i[0])

            if machine_name in table:
                db_cursor.execute(f"Describe {machine_name}")
                table_data = []
                for x in db_cursor:
                    table_data.append(x[0])
                db_cursor.fetchall()
                full_info = {}
                total_hour = end_count - start_count
                total_hour += 1
                result = []
                for i in range(total_hour):
                    db_cursor.execute(f"select * from {machine_name} where {type} = {start_count + i} ORDER BY id DESC LIMIT 1")
                    for x in db_cursor:
                        result = x
                    db_cursor.fetchall()
                    full_data = {}
                    if result != []:
                        for y in range(len(table_data)):
                            full_data[table_data[y].lower()] = result[y]
                        if host == False:
                            data = {"machine_name": full_data['name'].upper(), "status": full_data['status'],
                                     "uph": full_data['uph'], "cycle_time": full_data["cycle_time"],
                                     "up_time": full_data["up_time"], "down_time": full_data["down_time"],
                                     "idle_time": full_data["idle_time"], "run_time": full_data["run_time"],
                                     "error_count": full_data["error_count"],
                                     "update_time": f"{full_data['day']}/{full_data['month']}/{full_data['year']} {full_data['hour']}:{full_data['minute']}:{full_data['second']}",
                                     "ip": full_data['ip_address'],
                                     "x-core": full_data['x_core']}  # 09/05/2022 09:39:37
                            full_info[start_count + i] = data
                    else:
                        data = {"machine_name": None, "status": None,
                                "uph": None, "cycle_time": None,
                                "up_time": None, "down_time": None,
                                "idle_time": None, "run_time": None,
                                "error_count": None,
                                "update_time": None,
                                "ip": None,
                                "x-core": None}  # 09/05/2022 09:39:37
                        full_info[start_count + i] = data
                return full_info
            else:
                break

    def search_ip_in_database(self, machine_name: str):
        agv_database = self.database_login()
        while True:
            db_cursor = agv_database.cursor()
            table = []
            db_cursor.execute(f"select IP_ADDRESS from {machine_name} ORDER BY id DESC LIMIT 1")

            for x in db_cursor:
                result = x
            db_cursor.fetchall()
            return result[0]

    def request(self, web: str):
        reply = self.s_request.get(url=web, timeout=1)
        reply = reply.json()
        return reply

    def dev(self, machine_ip, item):
        agv_database = self.database_login()
        item = json.loads(item)
        if ((float(item['cycle_time']) > 0.00) and (float(item['uph']) > 0.00)):
            ideal_run_rate = 60 / (float(item['cycle_time']) * 60)
            operation_time = float(item['run_time']) - float(item['down_time'])
            item["availability"] = operation_time / float(item['up_time'])
            item["performance"] = (float(item['uph']) / operation_time / ideal_run_rate)
            item["quality"] = int(item['uph']) / int(item['uph'])
        else:
            item["availability"] = 0
            item["performance"] = 0
            item["quality"] = 0
        item['x-core'] = True
        while True:
            db_cursor = agv_database.cursor()
            db_cursor.execute("SHOW TABLES")
            table = []
            for i in db_cursor:
                table.append(i[0])
            if item['machine_name'].lower() in table:
                machine_last_data = self.machine_grab_data(item['machine_name'])
                if machine_last_data['status'].lower() != item['status'].lower() and 'error' in item[
                    'status'].lower():
                    item['error_count'] = machine_last_data['error_count'] + 1
                else:
                    item['error_count'] = machine_last_data['error_count']
                current_time = datetime.datetime.now()
                sql = f"INSERT INTO {item['machine_name'].lower()} (DAY,MONTH,YEAR,HOUR,MINUTE,SECOND,NAME,STATUS,UP_TIME,DOWN_TIME,IDLE_TIME,RUN_TIME,CYCLE_TIME,UPH,ERROR_COUNT,AVAILABILITY,PERFORMANCE,QUALITY,IP_ADDRESS,X_CORE) VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)"
                val = (
                current_time.day, current_time.month, current_time.year, current_time.hour, current_time.minute,
                current_time.second, item['machine_name'], item['status'], item['up_time'], item['down_time'],
                item['idle_time'], item['run_time'], item['cycle_time'], item['uph'], item['error_count'],
                item["availability"], item["performance"], item["quality"], machine_ip, item["x-core"])
                db_cursor.execute(sql, val)
                agv_database.commit()
                break
            else:
                db_cursor.execute(
                    f"CREATE TABLE {item['machine_name'].lower()}(ID int PRIMARY KEY AUTO_INCREMENT ,DAY int UNSIGNED ,MONTH int UNSIGNED,YEAR int UNSIGNED,HOUR int UNSIGNED,MINUTE int UNSIGNED,SECOND int UNSIGNED , NAME VARCHAR(50),STATUS VARCHAR(50), UP_TIME float UNSIGNED, DOWN_TIME float UNSIGNED, IDLE_TIME float UNSIGNED, RUN_TIME float UNSIGNED, STOP_TIME float UNSIGNED, CYCLE_TIME float UNSIGNED, UPH int UNSIGNED, ERROR_COUNT int UNSIGNED, MTBA float UNSIGNED, MTBF float UNSIGNED,QUALITY float UNSIGNED, AVAILABILITY float UNSIGNED, PERFORMANCE float UNSIGNED,IP_ADDRESS VARCHAR(50),X_CORE BOOLEAN)")

class user_server:

    def __init__(self, database_ip: str, database_user: str, database_password: str, database_name: str):
        self.s_request = requests.Session()
        self.database_host = database_ip
        self.database_user = database_user
        self.database_password = database_password
        self.database_name = database_name

    def database_login(self):
        return mysql.connector.connect(host=self.database_host, user=self.database_user, password=self.database_password,
                                               database=self.database_name)

    def machine_count(self):
        agv_database = self.database_login()
        db_cursor = agv_database.cursor()
        db_cursor.execute("SHOW TABLES")
        table = []
        for i in db_cursor:
            table.append(i[0])
        return table

    def calculation(self, item):
        # cycle_time
        # uph
        # run_time
        # down_time
        #
        #
        if not (float(item['cycle_time']) == 0 or not (float(item['uph']) == 0)):
            ideal_run_rate = 60 / (float(item['cycle_time']) * 60)
            operation_time = float(item['run_time']) - float(item['down_time'])
            item["availability"] = operation_time / float(item['up_time'])
            item["performance"] = (float(item['uph']) / operation_time / ideal_run_rate)
            item["quality"] = int(item['uph']) / int(item['uph'])
        else:
            item["availability"] = 0
            item["performance"] = 0
            item["quality"] = 0

    def save_machine_database(self, table_name, item):
        # URL, DESCRPITION, TYPE, METHOD
        item_list = []
        # for z in item:
        #     item_list.append(item[z])
        # item_list = ",".join(map(str, item_list))
        # print(item_list)
        database = self.database_login()
        item = json.loads(item)
        while True:
            db_cursor = database.cursor()
            db_cursor.execute("SHOW TABLES")
            table = []
            for i in db_cursor:
                table.append(i[0])
            if table_name in table:
                sql = f"INSERT INTO {table_name} (USER_NAME,PASSWORD,ROLE,DESCRIPTION) VALUES('{item['user_name']}', '{item['password']}', '{item['role']}','{item['description']}') ON DUPLICATE KEY UPDATE password = '{item['password']}', role = '{item['role']}', description= '{item['description']}'"
                # INSERT INTO control_api(id, URL, DESCRIPTION, TYPE)  VALUES(3,"test", "Fadl", "666") ON DUPLICATE KEY UPDATE URL = "Fadl", DESCRIPTION = "88", TYPE ="Get";
                # val = (item['url'], item['description'], item['type'])
                db_cursor.execute(sql)                                  # val
                database.commit()
                break
            else:
                db_cursor.execute(
                    f"CREATE TABLE {table_name}(USER_NAME VARCHAR(100) PRIMARY KEY ,PASSWORD VARCHAR(200),ROLE VARCHAR(50),DESCRIPTION VARCHAR(200))")

    def machine_grab_data(self, table_name: str, host: bool = False):
        agv_database = self.database_login()
        while True:
            db_cursor = agv_database.cursor()
            db_cursor.execute("SHOW TABLES")
            table = []
            for z in db_cursor:
                table.append(z[0])

            if table_name in table:
                db_cursor.execute(f"Describe {table_name}")
                table_data = []
                for y in db_cursor:
                    table_data.append(y[0])
                db_cursor.fetchall()
                db_cursor.execute(f"select * from {table_name}")
                full_data = []
                data = {}
                for i in db_cursor:
                    for x in range(len(i)):
                        data[table_data[x].lower()] = i[x]
                        print(table_data[x].lower(), i[x])
                    full_data.append(data)
                    data = {}
                return full_data
            else:
                break

    def delete_row(self, table_name, item):
        database = self.database_login()
        item = json.loads(item)

        db_cursor = database.cursor()
        db_cursor.execute("SHOW TABLES")
        table = []
        for i in db_cursor:
            table.append(i[0])
        if table_name in table:
            #sql = f"INSERT INTO {table_name} (URL,DESCRIPTION,TYPE) VALUES('{item['url']}', '{item['description']}','{item['type']}') ON DUPLICATE KEY UPDATE description = '{item['description']}', type = '{item['type']}'"
            # INSERT INTO control_api(id, URL, DESCRIPTION, TYPE)  VALUES(3,"test", "Fadl", "666") ON DUPLICATE KEY UPDATE URL = "Fadl", DESCRIPTION = "88", TYPE ="Get";
            # val = (item['url'], item['description'], item['type'])
            sql = f'DELETE from {table_name} where user_name = "{item["user_name"]}";'
            db_cursor.execute(sql)  # ,val)
            database.commit()


    def machine_grab_pass_data(self, machine_name: str, type: str = "hour", start_count: int = 0, end_count: int = 0, host: bool = False):
        agv_database = self.database_login()
        while True:
            db_cursor = agv_database.cursor()
            db_cursor.execute("SHOW TABLES")
            table = []
            for i in db_cursor:
                table.append(i[0])

            if machine_name in table:
                db_cursor.execute(f"Describe {machine_name}")
                table_data = []
                for x in db_cursor:
                    table_data.append(x[0])
                db_cursor.fetchall()
                full_info = {}
                total_hour = end_count - start_count
                total_hour += 1
                result = []
                for i in range(total_hour):
                    db_cursor.execute(f"select * from {machine_name} where {type} = {start_count + i} ORDER BY id DESC LIMIT 1")
                    for x in db_cursor:
                        result = x
                    db_cursor.fetchall()
                    full_data = {}
                    if result != []:
                        for y in range(len(table_data)):
                            full_data[table_data[y].lower()] = result[y]
                        if host == False:
                            data = {"machine_name": full_data['name'].upper(), "status": full_data['status'],
                                     "uph": full_data['uph'], "cycle_time": full_data["cycle_time"],
                                     "up_time": full_data["up_time"], "down_time": full_data["down_time"],
                                     "idle_time": full_data["idle_time"], "run_time": full_data["run_time"],
                                     "error_count": full_data["error_count"],
                                     "update_time": f"{full_data['day']}/{full_data['month']}/{full_data['year']} {full_data['hour']}:{full_data['minute']}:{full_data['second']}",
                                     "ip": full_data['ip_address'],
                                     "x-core": full_data['x_core']}  # 09/05/2022 09:39:37
                            full_info[start_count + i] = data
                    else:
                        data = {"machine_name": None, "status": None,
                                "uph": None, "cycle_time": None,
                                "up_time": None, "down_time": None,
                                "idle_time": None, "run_time": None,
                                "error_count": None,
                                "update_time": None,
                                "ip": None,
                                "x-core": None}  # 09/05/2022 09:39:37
                        full_info[start_count + i] = data
                return full_info
            else:
                break

    def search_ip_in_database(self, machine_name: str):
        agv_database = self.database_login()
        while True:
            db_cursor = agv_database.cursor()
            table = []
            db_cursor.execute(f"select IP_ADDRESS from {machine_name} ORDER BY id DESC LIMIT 1")

            for x in db_cursor:
                result = x
            db_cursor.fetchall()
            return result[0]

    def request(self, web: str):
        reply = self.s_request.get(url=web, timeout=1)
        reply = reply.json()
        return reply

    def dev(self, machine_ip, item):
        agv_database = self.database_login()
        item = json.loads(item)
        if ((float(item['cycle_time']) > 0.00) and (float(item['uph']) > 0.00)):
            ideal_run_rate = 60 / (float(item['cycle_time']) * 60)
            operation_time = float(item['run_time']) - float(item['down_time'])
            item["availability"] = operation_time / float(item['up_time'])
            item["performance"] = (float(item['uph']) / operation_time / ideal_run_rate)
            item["quality"] = int(item['uph']) / int(item['uph'])
        else:
            item["availability"] = 0
            item["performance"] = 0
            item["quality"] = 0
        item['x-core'] = True
        while True:
            db_cursor = agv_database.cursor()
            db_cursor.execute("SHOW TABLES")
            table = []
            for i in db_cursor:
                table.append(i[0])
            if item['machine_name'].lower() in table:
                machine_last_data = self.machine_grab_data(item['machine_name'])
                if machine_last_data['status'].lower() != item['status'].lower() and 'error' in item[
                    'status'].lower():
                    item['error_count'] = machine_last_data['error_count'] + 1
                else:
                    item['error_count'] = machine_last_data['error_count']
                current_time = datetime.datetime.now()
                sql = f"INSERT INTO {item['machine_name'].lower()} (DAY,MONTH,YEAR,HOUR,MINUTE,SECOND,NAME,STATUS,UP_TIME,DOWN_TIME,IDLE_TIME,RUN_TIME,CYCLE_TIME,UPH,ERROR_COUNT,AVAILABILITY,PERFORMANCE,QUALITY,IP_ADDRESS,X_CORE) VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)"
                val = (
                current_time.day, current_time.month, current_time.year, current_time.hour, current_time.minute,
                current_time.second, item['machine_name'], item['status'], item['up_time'], item['down_time'],
                item['idle_time'], item['run_time'], item['cycle_time'], item['uph'], item['error_count'],
                item["availability"], item["performance"], item["quality"], machine_ip, item["x-core"])
                db_cursor.execute(sql, val)
                agv_database.commit()
                break
            else:
                db_cursor.execute(
                    f"CREATE TABLE {item['machine_name'].lower()}(ID int PRIMARY KEY AUTO_INCREMENT ,DAY int UNSIGNED ,MONTH int UNSIGNED,YEAR int UNSIGNED,HOUR int UNSIGNED,MINUTE int UNSIGNED,SECOND int UNSIGNED , NAME VARCHAR(50),STATUS VARCHAR(50), UP_TIME float UNSIGNED, DOWN_TIME float UNSIGNED, IDLE_TIME float UNSIGNED, RUN_TIME float UNSIGNED, STOP_TIME float UNSIGNED, CYCLE_TIME float UNSIGNED, UPH int UNSIGNED, ERROR_COUNT int UNSIGNED, MTBA float UNSIGNED, MTBF float UNSIGNED,QUALITY float UNSIGNED, AVAILABILITY float UNSIGNED, PERFORMANCE float UNSIGNED,IP_ADDRESS VARCHAR(50),X_CORE BOOLEAN)")
