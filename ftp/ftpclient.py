# !/usr/bin/env python
# -*-coding:utf-8 -*-

import os
import socket
import sys


def send_file(file_path):
    '''
    發送文件
   :param file_path:文件名
   :return:
   '''
    size = os.stat(file_path).st_size
    file_name = os.path.basename(file_path)
    obj.sendall(bytes(str(size) + ',' + file_name, encoding='utf-8'))
    ret = obj.recv(1024)
    r = str(ret, encoding='utf-8')
    if r == 's':  # 文件不存在，從頭開始傳
        has_send = 0
    else:  # 文件存在
        has_send = int(r)
    with open(file_path, 'rb') as f:
        f.seek(has_send)  # 定位到已經傳到的位置
        while has_send < size:
            data = f.read(1024)
            obj.sendall(data)
            has_send += len(data)
            sys.stdout.write('\r')  # 情況文件內容
            sys.stdout.write('已發送%s%%|%s' % (int(has_send / size * 100), (round(has_send / size * 40) * '|')))
            sys.stdout.flush()  # 強制刷出內存
    print('上傳成功！\n')


def recv_file(toPath, getFile):
        '''
        接收要下載的文件
        :param toPath: 本地要保存文件的存放路徑
        :param getFile: 要下載的文件名稱
        :return:
        '''
        obj.sendall(bytes('get:' + getFile, encoding='utf-8'))
        a = str(obj.recv(1024), encoding='utf-8')
        file_size, file_name = a.split(',')
        file_size = int(file_size)
        if file_size == 0:
            print('沒有找到此文件')
        else:
            new_file_name = os.path.join(toPath, file_name)
            if file_name in toPath:
                has_recv = os.stat(toPath).st_size
                obj.sendall(bytes(has_recv, encoding='utf-8'))
                with open(new_file_name, 'ab') as f:
                    while has_recv <= file_size:
                        data = obj.recv(1024)
                        f.write(data)
                        has_recv += len(data)
                        sys.stdout.write('\r')  # 情況文件內容
                        sys.stdout.write(
                            '已接收%s%%|%s' % (int(has_recv / file_size * 100), (round(has_recv / file_size * 40) * '|')))
                        sys.stdout.flush()  # 強制刷出內存
            else:
                has_recv = 0
                obj.sendall(bytes('s', encoding='utf-8'))
                with open(new_file_name, 'wb') as f:
                    while has_recv <= file_size:
                        data = obj.recv(1024)
                        f.write(data)
                        has_recv += len(data)
                        sys.stdout.write('\r')  # 情況文件內容
                        sys.stdout.write(
                            '已接收%s%%|%s' % (int(has_recv / file_size * 100), (round(has_recv / file_size * 40) * '|')))
                        sys.stdout.flush()  # 強制刷出內存
            print('接收成功！\n')


def command(command_name):
        '''
        執行命令
        :param command_name:
        :return:
        '''
        obj.sendall(bytes(command_name, encoding='utf-8'))
        ret = obj.recv(1024)  # 接受命令需要接受的次數
        obj.sendall(bytes('收到次數', encoding='utf-8'))
        r = str(ret, encoding='utf-8')
        for i in range(int(r)):  # 共需接收int(r)次
            ret = obj.recv(1024)  # 等待客戶端發送
            r = str(ret, encoding='GBK')
            print(r)


def login(username, pwd):
        '''
        登錄
        :param username: 用戶名
        :param pwd: 密碼
        :return: 是否登錄成功
        '''
        obj.sendall(bytes(username + ',' + pwd, encoding='utf-8'))
        ret = obj.recv(1024)
        r = str(ret, encoding='utf-8')
        if r == 'y':
            return True
        else:
            return False


def regist(username, pwd):
    '''
    注冊
    :param username: 用戶名
    :param pwd: 密碼
    :return: 是否注冊成功
    '''
    obj.sendall(bytes(username + ',' + pwd, encoding='utf-8'))
    ret = obj.recv(1024)
    r = str(ret, encoding='utf-8')
    if r == 'y':
        return True
    else:
        return False


def before(username, pwd):
    '''
    選擇注冊和登錄，並展示用戶的詳細目錄信息，支持cd和ls命令
    :param username: 用戶名
    :param pwd: 密碼
    :return:
    '''
    a = input('請選擇 1.登錄  2.注冊：')
    obj.sendall(bytes(a, encoding='utf-8'))
    # obj.recv()
    if a == '1':
        ret = login(username, pwd)
        if ret:
            print('登錄成功')
            return 1
        else:
            print('用戶名或密碼錯誤')
            return 0
    elif a == '2':
        ret = regist(username, pwd)
        if ret:
            print('注冊成功')
            return 1
        else:
            print('用戶名已存在')
            return 0


def user_file(username):
    # obj.sendall(bytes('打印用戶文件路徑', encoding='utf-8'))
    ret = obj.recv(1024)
    r = str(ret, encoding='utf-8')
    print(r)
    while True:
        a = input('輸入 cd切換目錄，ls查看目錄詳細信息，mkdir創建文件夾，q退出：')
        a = a.strip()
        obj.sendall(bytes(a, encoding='utf-8'))
        if a == 'q':
            break
        elif a[0:5] == 'mkdir':
            ret = obj.recv(1024)
            r = str(ret, encoding='utf-8')
            if r == '1':
                print('文件夾創建成功')
            elif r == '2':
                print('文件夾已存在！')
            else:
                print('創建失敗！')
        else:
            ret = obj.recv(1024)
            r = str(ret, encoding='utf-8')
            if len(r) == 1:  # 判斷是cd結果，還是ls的結果（ls只有一個子目錄，直接打印）
                print(r)
            else:
                li = r.split(',')
                for i in li:
                    print(i)


def main(username, pwd):
    ret = obj.recv(1024)
    r = str(ret, encoding='utf-8')
    print(r)
    result = before(username, pwd)  # 判斷登錄/注冊
    if result:
        user_file(username)
        while True:
            a = input('請選擇 1.傳文件 2.執行命令 3.收文件 q 退出：')
            obj.sendall(bytes(str(a), encoding='utf-8'))
            if a == '1':
                b = input('請輸入文件路徑：')
                if os.path.exists(b):
                    send_file(b)
                    obj.sendall(bytes('hhe', encoding='utf-8'))
            elif a == '2':
                b = input('請輸入command：')
                command(b)
            elif a == '3':
                b = input('請輸入存放路徑：')
                c = input('請輸入要獲取的文件：')
                recv_file(b, c)
            elif a == 'q':
                break
            else:
                print('輸入錯誤！')

    obj.close()


if __name__ == '__main__':
    obj = socket.socket()
    obj.connect(('192.168.4.142', 9999))
    username = input('請輸入用戶名：')
    pwd = input('請輸入密碼：')
    main(username, pwd)
