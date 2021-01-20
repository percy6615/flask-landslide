import os
from ftplib import FTP

ftp = FTP()
local = "localhost"
# local = "192.168.4.200"
ftp.connect(local, 21)  # localhost改成伺服器ip地址
ftp.login(user='user', passwd='12345')
ftp.set_pasv(False)

# file_handle = open("test.txt",'wb').write
# ftp.retrbinary("RETR test.txt",file_handle,1024)#從伺服器上下載檔案 1024位元組一個塊
# ftp.set_debuglevel(0)
# ftp.close()


def uploadfile(ftp, remotepath, localpath):
    bufsize = 1024
    fp = open(localpath, 'rb')
    filenames = ftp.nlst()  # get filenames within the directory
    print(filenames)


    ftp.storbinary('STOR ' + remotepath, fp, bufsize)  # 上传文件
    ftp.set_debuglevel(0)
    fp.close()

def uploadThis(path):
    files = os.listdir(path)
    os.chdir(path)
    for f in files:
        if os.path.isfile(f):
            fh = open(f, 'rb')
            ftp.storbinary('STOR %s' % f, fh)
            fh.close()
        elif os.path.isdir(f):
            ftp.mkd(f)
            ftp.cwd(f)
            uploadThis(f)
    ftp.cwd('..')
    os.chdir('..')
myPath = r'./percy/sss/'
uploadThis(myPath)

# uploadfile(ftp, "/percy1/test1.txt", "test.txt")
