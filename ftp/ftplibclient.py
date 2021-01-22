import ftplib
import os
from ftplib import FTP
import socket
from ftp import psftplib

# ftp = FTP()
# local = "localhost"
# # local = "192.168.4.200"
# ftp.connect(local, 21)  # localhost改成伺服器ip地址
# ftp.login(user='user', passwd='12345')
# ftp.set_pasv(False)


class FtpAddOns():
    PATH_CACHE = []

    def __init__(self, ftp_h):
        self.ftp_h = ftp_h

    def ftp_exists(self, path):
        '''path exists check function for ftp handler'''
        exists = None
        if path not in self.PATH_CACHE:
            try:
                self.ftp_h.cwd(path)
                exists = True
                self.PATH_CACHE.append(path)
            except ftplib.error_perm as e:
                if str(e.args).count('550'):
                    exists = False
        else:
            exists = True

        return exists

    def ftp_mkdirs(self, path, sep='/'):
        '''mkdirs function for ftp handler'''
        split_path = path.split(sep)

        new_dir = ''
        for server_dir in split_path:
            if server_dir:
                new_dir += sep + server_dir
                if not self.ftp_exists(new_dir):
                    try:
                        print('Attempting to create directory (%s) ...' % (new_dir),
                              self.ftp_h.mkd(new_dir))
                        print('Done!')
                    except Exception as e:
                        print('ERROR -- %s' % (str(e.args)))

def _get_local_files(local_dir, walk=True):
    '''Retrieve local files list
    result_list == a list of dictionaries with path and mtime keys. ex: {'path':<filepath>,'mtime':<file last modified time>}
    ignore_dirs == a list of directories to ignore, should not include the base_dir.
    ignore_files == a list of files to ignore.
    ignore_file_ext == a list of extentions to ignore.
    '''
    result_list = []

    ignore_dirs = ['CVS', '.svn']
    ignore_files = ['.project', '.pydevproject']
    ignore_file_ext = ['.pyc']

    base_dir = os.path.abspath(local_dir)

    for current_dir, dirs, files in os.walk(base_dir):
        for this_dir in ignore_dirs:
            if this_dir in dirs:
                dirs.remove(this_dir)

        sub_dir = current_dir.replace(base_dir, '')
        if not walk and sub_dir:
            break

        for this_file in files:
            if this_file not in ignore_files and os.path.splitext(this_file)[-1].lower() not in ignore_file_ext:
                filepath = os.path.join(current_dir, this_file)
                file_monitor_dict = {
                    'path': filepath,
                    'mtime': os.path.getmtime(filepath)
                }
                result_list.append(file_monitor_dict)
    return result_list

def upload_all(server,
               username,
               password,
               base_local_dir,
               base_remote_dir,
               files_to_update=None,
               encrypt=False,
               walk=True):
    '''Upload all files in a given directory to the given remote directory'''
    continue_on = False
    login_ok = False
    server_connect_ok = False

    base_local_dir = os.path.abspath(base_local_dir)
    base_remote_dir = os.path.normpath(base_remote_dir)

    if files_to_update:
        local_files = files_to_update
    else:
        local_files = _get_local_files(base_local_dir, walk)

    if local_files:
        if not encrypt:  # Use standard FTP
            ftp_h = ftplib.FTP()
        else:  # Use sftp
            ftp_h = psftplib.SFTP()

        try:
            ftp_h.connect(server, 21)
            server_connect_ok = True
        except socket.gaierror as e:
            print('ERROR -- Could not connect to (%s): %s' % (server, str(e.args)))
        except IOError as e:
            print('ERROR -- File not found: %s' % (str(e.args)))
        except socket.error as e:
            print('ERROR -- Could not connect to (%s): %s' % (server, str(e.args)))

        ftp_path_tools = FtpAddOns(ftp_h)

        if server_connect_ok:
            try:
                ftp_h.login(username, password)
                print('Logged into (%s) as (%s)' % (server, username))
                login_ok = True
            except ftplib.error_perm as e:
                print('ERROR -- Check Username/Password: %s' % (str(e.args)))
            except psftplib.ProcessTimeout as e:
                print('ERROR -- Check Username/Password (timeout): %s' % (str(e.args)))

            if login_ok:

                for file_info in local_files:
                    filepath = file_info['path']

                    path, filename = os.path.split(filepath)
                    remote_sub_path = path.replace(base_local_dir, '')
                    remote_path = path.replace(base_local_dir, base_remote_dir)
                    remote_path = remote_path.replace('\\', '/')  # Convert to unix style

                    if not ftp_path_tools.ftp_exists(remote_path):
                        ftp_path_tools.ftp_mkdirs(remote_path)

                    # Change to directory
                    try:
                        last = ftp_h.pwd()
                        ftp_h.cwd(remote_path)
                        now = ftp_h.pwd()
                        continue_on = True
                    except ftplib.error_perm as e:
                        print('ERROR -- %s' % (str(e.args)))
                    except psftplib.PsFtpInvalidCommand as e:
                        print('ERROR -- %s' % (str(e.args)))

                    if continue_on:
                        if os.path.exists(filepath):
                            f_h = open(filepath, 'rb')
                            filename = os.path.split(f_h.name)[-1]

                            display_filename = os.path.join(remote_sub_path, filename)
                            display_filename = display_filename.replace('\\', '/')

                            print('Sending (%s) ...' % (display_filename), )
                            send_cmd = 'STOR %s' % (filename)
                            try:
                                ftp_h.storbinary(send_cmd, f_h)
                                f_h.close()
                                print('Done!')
                            except Exception as e:
                                print('ERROR!')
                                print(str(e.args))

                        else:
                            print("WARNING -- File no longer exists, (%s)!" % (filepath))

                ftp_h.quit()
                print('Closing Connection')
    else:
        print('ERROR -- No files found in (%s)' % (base_local_dir))

    return continue_on

def uploadfile(ftp, remotepath, localpath):
    bufsize = 1024
    fp = open(localpath, 'rb')
    filenames = ftp.nlst()  # get filenames within the directory
    print(filenames)


    ftp.storbinary('STOR ' + remotepath, fp, bufsize)  # 上传文件
    ftp.set_debuglevel(0)
    fp.close()

# def uploadThis(path):
#     files = os.listdir(path)
#     os.chdir(path)
#     for f in files:
#         if os.path.isfile(f):
#             fh = open(f, 'rb')
#             ftp.storbinary('STOR %s' % f, fh)
#             fh.close()
#         elif os.path.isdir(f):
#             ftp.mkd(f)
#             ftp.cwd(f)
#             uploadThis(f)
#     ftp.cwd('..')
#     os.chdir('..')
myPath = r'./percy/sss/'
# uploadThis(myPath)
path = "./app/classification/keras/image/landslide_v20210112.h5/"

path = "D:/github/flask-landslide/app/classification/keras/image/landslide_v20210112.h5/"
path1= "./landslide_v20210112"
print(_get_local_files(local_dir=path))

# uploadfile(ftp, "/percy1/test1.txt", "test.txt")

upload_all(server="localhost",
               username="user",
               password = "12345",
               base_local_dir = path,
               base_remote_dir = path1,
               files_to_update=None,
               encrypt=False,
               walk=True)
