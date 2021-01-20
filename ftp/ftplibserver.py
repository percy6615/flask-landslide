import hashlib
import os

from pyftpdlib.authorizers import DummyAuthorizer
from pyftpdlib.handlers import FTPHandler
from pyftpdlib.servers import FTPServer, ThreadedFTPServer

BASE_DIR = os.path.dirname(os.path.dirname(__file__))
BASE_HOME = os.path.join(BASE_DIR, 'home')
NAME_PWD = os.path.join(BASE_DIR, 'db', 'name_pwd')
USER_FILE = os.path.join(BASE_DIR, 'db')


class MyHandler(FTPHandler):

    def on_connect(self):
        print("%s:%s connected" % (self.remote_ip, self.remote_port))

    def on_disconnect(self):
        # do something when client disconnects
        print("on_disconnect")
        pass

    def on_login(self, username):
        # do something when user login
        print("on_login")
        pass

    def on_logout(self, username):
        # do something when user logs out
        print("on_logout")
        pass

    def on_file_sent(self, file):
        # do something when a file has been sent
        print("on_file_sent")
        pass

    def on_file_received(self, file):
        # do something when a file has been received

        print("on_file_received")
        pass

    def on_incomplete_file_sent(self, file):
        # do something when a file is partially sent
        print("on_incomplete_file_sent")
        pass

    def on_incomplete_file_received(self, file):
        # remove partially uploaded files
        print("on_incomplete_file_received")
        os.remove(file)


def main():
    authorizer = DummyAuthorizer()
    authorizer.add_user('user', '12345', './ftphome', perm='elradfmwMT')  # 新增使用者 引數:username,password,允許的路徑,許可權
    # authorizer.add_anonymous(os.getcwd())  # 這裡是允許匿名使用者,如果不允許刪掉此行即可
    # 例項化FTPHandler
    handler = MyHandler
    handler.authorizer = authorizer
    # 設定一個客戶端連結時的標語
    handler.banner = "pyftpdlib based ftpd ready."
    # handler.masquerade_address = '151.25.42.11'#指定偽裝ip地址
    # handler.passive_ports = range(60000, 65535)#指定允許的埠範圍
    address = ("0.0.0.0", 21)  # FTP一般使用21,20埠
    server = ThreadedFTPServer(('', 21), handler)

    # set a limit for connections
    server.max_cons = 256
    server.max_cons_per_ip = 5
    # 開啟伺服器
    server.serve_forever()


def md5(pwd):
    hash = hashlib.md5(bytes('xx7', encoding='utf-8'))
    hash.update(bytes(pwd, encoding='utf-8'))
    return hash.hexdigest()


if __name__ == '__main__':
    main()
