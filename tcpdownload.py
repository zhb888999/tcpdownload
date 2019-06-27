#!/usr/bin/python3
# -*- coding: utf-8 -*-
# Author @mking
# Description @ tcodownload.py
# CreateTime @ 2019-06-27 18:32:36

from threading import Thread
from socket import socket, SOL_SOCKET, SO_REUSEPORT
import os
import time

"""
Tcp文件下载API,用于建立简单的文件下载服务器和客户端程序

Server类可以简单的创建一个Tcp下载服务端,server_ip和
server_port参数为需要绑定的服务器IP地址及端口号,通过
start()方法可以启动服务,支持多任务.

Client类可以和server建立连接并下载文件,server_ip和
server_port参数为服务器ip地址和服务器端口口号,
filename参数为需要下载的文件名,通过client()方法可以启动下载.

默认端口号为9091,服务器提供的下载文件需要和Server程序位于同一
目录
"""


class Server(socket):
    __quest_list = list()
    server_ip_port = ()

    def __init__(self, server_ip="", server_port=9091):
        socket.__init__(self)
        self.server_ip_port = (server_ip, server_port)

    def add_list(self, connect_socket, connect_ip_port, filename):
        user_struct = {"connect_socket": connect_socket,
                       "connect_ip_port": connect_ip_port,
                       "filename": filename,
                       "begin_time": time.strftime("%a, %d %b %Y %H:%M:%S",
                                                   time.gmtime())}
        self.__quest_list.append(user_struct)

    def send_file(self, **kwargs):
        filesize = os.path.getsize(kwargs["filename"])
        print("客户需要下载的文件名及大小:%s %.2fMB"
              % (kwargs["filename"], filesize/(1024*1024)))
        kwargs["connect_socket"].send(str(filesize).encode('utf-8'))
        with open(kwargs["filename"], 'rb') as file:
            print("开始发送!!!!!!")
            while True:
                messg = file.read(1024)
                if messg:
                    kwargs["connect_socket"].send(messg)
                else:
                    print("文件发送成功!")
                    break

    def server(self, **kwargs):
        print(f"当前连接的IP是{kwargs['connect_ip_port']}")
        if kwargs["filename"] in os.listdir():
            self.send_file(**kwargs)
            kwargs["connect_socket"].close()
        else:
            kwargs["connect_socket"].send("0".encode('utf-8'))
            kwargs["connect_socket"].close()
            print("用户请求的文件%s不存在,已断开连接!" % kwargs["filename"])

    def start(self):
        self.setsockopt(SOL_SOCKET, SO_REUSEPORT, True)
        self.bind((self.server_ip_port))
        self.listen(128)
        while True:
            connect_socket, connect_ip_port = self.accept()
            filename = connect_socket.recv(1024).decode('utf-8')
            self.add_list(connect_socket, connect_ip_port, filename)
            Thread(target=self.server,
                   kwargs=self.__quest_list[-1],
                   daemon=True).start()
            for quest in self.__quest_list:
                print("%s:%s:%s"
                      % (quest["connect_ip_port"][0],
                         quest["filename"],
                         quest["begin_time"]))


class Client(socket):
    def __init__(self, server_ip="", server_port=9091, filename=""):
        super().__init__()
        self.server_ip_port = (server_ip, server_port)
        self.filename = filename
        self.filesize = 0

    def show_speed(self):
        while True:
            if os.path.exists(self.filename):
                speed = (os.path.getsize(self.filename)/self.filesize)*100
                print("\r已下载%d%%" % speed, end="")
                if os.path.getsize(self.filename) == self.filesize:
                    break
                time.sleep(0.1)

    def client(self):
        self.connect(self.server_ip_port)
        self.send(self.filename.encode('utf-8'))
        self.filesize = int(self.recv(1024).decode('utf-8'))
        if self.filesize:
            print("下载文件名及大小为:%s %.2fMB"
                  % (self.filename, self.filesize/(1024*1024)))
            Thread(target=self.show_speed, daemon=True).start()
            with open(self.filename, 'wb') as file:
                while True:
                    messg = self.recv(1024)
                    if messg:
                        file.write(messg)
                    else:
                        break
        else:
            print("你要下载的文件不存在!")
        self.close()


if __name__ == '__main__':
    server = Server()
    server.start()

    # client = Client(server_ip="127.0.0.1", server_port=9091, fliename="test.txt")
    # client.client()
