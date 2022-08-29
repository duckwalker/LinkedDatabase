import datetime
import json
import time
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from DATA_SOURCE import *
import uvicorn
import uvicorn.logging
import uvicorn.loops
import uvicorn.loops.auto
import uvicorn.protocols
import uvicorn.protocols.http
import uvicorn.protocols.http.auto
import uvicorn.protocols.websockets
import uvicorn.protocols.websockets.auto
import uvicorn.lifespan
import uvicorn.lifespan.on
import platform
import socket
import requests
import threading
import logging

app = FastAPI(title="Database Connector")
s_request = requests.Session()

def setup_api():
    @app.post('/control_api/save')
    def save_api_setting(item: URL_INFO):
        item = item.json()
        return machine_data_source.save_machine_database("control_api", item)

    @app.get("/control_api/grab")
    def grab_api_setting():
        try:
            file = machine_data_source.machine_grab_data("control_api")
        except:
            f = open('json_seed.json')
            file = json.load(f)
            f.close()
        return file

    @app.post('/control_api/delete')
    def delete(item: URL_INFO):
        item = item.json()
        return machine_data_source.delete_row("control_api", item)

    @app.post('/user_login/save')
    def save_api_setting(item: USER_INFO):
        item = item.json()
        # @app.post('/control_api/save')
        # def save_api_setting():
        #     print("test")
        # item = item.json()
        # item = json.loads(item)
        # item = json.dumps(item)
        # print(item)
        return user_login.save_machine_database("user", item)

    @app.get("/user_login/grab")
    def grab_api_setting():
        try:
            file = user_login.machine_grab_data("user")
        except:
            f = open('user_seed.json')
            file = json.load(f)
            f.close()
        return file

    @app.post('/user_login/delete')
    def delete(item: USER_INFO):
        item = item.json()
        return user_login.delete_row("user", item)


class MyFilter(object):
    def __init__(self, level):
        self.__level = level

    def filter(self, logRecord):
        return logRecord.levelno <= self.__level

machine_data_source = machine_data_server("192.168.10.42", "control_system", "92189218", "control_api")
user_login = user_server("192.168.10.42", "control_system", "92189218", "control_api")
try:
    logger = logging.getLogger(str(datetime.datetime.now()))
    logger.setLevel(logging.INFO)
    handler = logging.FileHandler(
        f'mylog_{str(datetime.datetime.now().day)}-{str(datetime.datetime.now().month)}-{str(datetime.datetime.now().year)}.log')
    formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    handler.setFormatter(formatter)
    handler.addFilter(MyFilter(logging.INFO))
    logger.addHandler(handler)


    setup_api()
    ip_add = socket.gethostbyname(socket.gethostname())
    ip_add = '192.168.10.41'
    origins = ['*']
    app.add_middleware(CORSMiddleware, allow_origins=["*"],
                       allow_credentials=True, allow_methods=["*"], allow_headers=["*"])
    uvicorn.run(app, host=ip_add, port=8888)
except Exception as e:
    print(e)

