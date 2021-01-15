import hashlib
import os
import pickle
import socketserver

# from config import settings
import subprocess

BASE_DIR = os.path.dirname(os.path.dirname(__file__))
BASE_HOME = os.path.join(BASE_DIR, 'home')
NAME_PWD = os.path.join(BASE_DIR, 'db', 'name_pwd')
USER_FILE = os.path.join(BASE_DIR, 'db')

baseHome = BASE_HOME


class MyServer(socketserver.BaseRequestHandler):
    def recv_file(self):
        conn = self.request
        a = str(conn.recv(1024), encoding='utf-8')
        file_size, file_name = a.split(',')
        new_file_name = os.path.join(baseHome, file_name)
        if file_name in baseHome:  # 檢測文件是否已存在，涉及斷點續傳
            has_recv = os.stat(baseHome).st_size  # 計算臨時文件大小
            conn.sendall(bytes(has_recv, encoding='utf-8'))
            with open(new_file_name, 'ab') as f:  # 追加模式
                data = conn.recv(1024)
                f.write(data)
                has_recv += len(data)
        else:
            has_recv = 0
            conn.sendall(bytes('s', encoding='utf-8'))  # 客戶端收到字符串s，從0開始發送
            with open(new_file_name, 'wb') as f:
                while has_recv <= int(file_size):
                    data = conn.recv(1024)
                    f.write(data)
                    has_recv += len(data)

    def send_file(self, fileName):
        filePath = os.path.join(self.currDir, fileName)
        conn = self.request
        if os.path.exists(filePath):
            size = os.stat(filePath).st_size
            conn.sendall(bytes(str(size) + ',' + fileName, encoding='utf-8'))
            ret = conn.recv(1024)
            r = str(ret, encoding='utf-8')
            if r == 's':
                has_send = 0
            else:
                has_send = int(r)
            with open(filePath, 'rb') as f:
                f.seek(has_send)
                while has_send < size:
                    data = f.read(1024)
                    conn.sendall(data)
                    has_send += len(data)
                    conn.sendall(bytes('0', encoding='utf-8'))
        else:
            conn.sendall(bytes('0', encoding='utf-8'))

    def createDir(self, currDir, newName):
        mulu = os.path.join(baseHome, currDir)
        newFilePath = os.path.join(mulu, newName)
        if os.path.exists(newFilePath):
            return '2'
        else:
            ret = '0'
            try:
                os.makedirs(newFilePath)
                ret = '1'
            except OSError as e:
                ret = '0'
            return ret

    def command(self):
        conn = self.request
        a = conn.recv(1024)
        ret = str(a, encoding='utf-8')
        ret2 = subprocess.check_output(ret, shell=True)
        r = divmod(len(ret2), 1024)
        s = r[0] + 1
        conn.sendall(bytes(str(s), encoding='utf-8'))
        conn.recv(1024)
        conn.sendall(ret2)

    def md5(self, pwd):
        hash = hashlib.md5(bytes('xx7', encoding='utf-8'))
        hash.update(bytes(pwd, encoding='utf-8'))
        return hash.hexdigest()

    def login(self, username, pwd):
        if os.path.exists(NAME_PWD):
            s = pickle.load(open(NAME_PWD, 'rb'))
        if username in s:
            if s[username] == self.md5(pwd):
                return True
            else:
                return False
        else:
            return False

    def regist(self, username, pwd):
        conn = self.request
        s = {}
        if os.path.exists(NAME_PWD):
            s = pickle.load(open(NAME_PWD, 'rb'))
        if username in s:
            return False
        else:
            s[username] = self.md5(pwd)
            mulu = os.path.join(USER_FILE, username)
            os.makedirs(mulu)
            pickle.dump(s, open(NAME_PWD, 'wb'))
            return True

    def before(self, username, pwd, ret):
        conn = self.request
        if ret == '1':
            r = self.login(username, pwd)
            if r:
                conn.sendall(bytes('y', encoding='utf-8'))
            else:
                conn.sendall(bytes('n', encoding='utf-8'))
        elif ret == '2':
            r = self.regist(username, pwd)
            if r:
                conn.sendall(bytes('y', encoding='utf-8'))
            else:
                conn.sendall(bytes('n', encoding='utf-8'))

    def user_file(self, username):
        conn = self.request
        mulu = baseHome
        self.currDir = mulu
        conn.sendall(bytes(mulu, encoding='utf-8'))
        while True:
            if conn:
                b = conn.recv(1024)
                ret = str(b, encoding='utf-8')
                try:
                    a, b = ret.split(' ', 1)
                except Exception as e:
                    a = ret
                if a == 'cd':
                    if b == '..':
                        mulu = os.path.dirname(mulu)
                    else:
                        mulu = os.path.join(mulu, b)
                    self.currDir = mulu
                    conn.sendall(bytes(mulu, encoding='utf-8'))
                elif a == 'ls':
                    ls = os.listdir(mulu)
                    print(ls)
                    a = ','.join(ls)
                    if a == '':
                        a = '.'
                    conn.sendall(bytes(a, encoding='utf-8'))
                elif a == 'mkdir':
                    m = self.createDir(self.currDir, b)
                    conn.sendall(bytes(m, encoding='utf-8'))
                elif a == 'q':
                    break

    def handle(self):
        conn = self.request
        conn.sendall(bytes('welcome', encoding='utf-8'))
        b = conn.recv(1024)
        ret = str(b, encoding='utf-8')
        c = conn.recv(1024)
        r = str(c, encoding='utf-8')
        username, pwd = r.split(',')
        self.before(username, pwd, ret)
        self.user_file(username)
        while True:
            a = conn.recv(1024)
            ret = str(a, encoding='utf-8')
            if ret == '1':
                self.recv_file()
            elif ret == '2':
                self.command()
            elif ret[0:4] == 'get:':
                self.send_file(ret[4:])
            elif ret == 'q':
                break
            else:
                pass


if __name__ == '__main__':
    server = socketserver.ThreadingTCPServer(('', 9999), MyServer)
    server.serve_forever()
