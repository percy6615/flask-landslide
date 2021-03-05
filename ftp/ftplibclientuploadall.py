import ftplib
import os
import socket


class FtpAddOns:
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


class FTPClientToDocker:
    def _get_local_files(self, local_dir, walk=True):
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
        name_dirs = []
        for current_dir, dirs, files in os.walk(base_dir):
            for this_dir in ignore_dirs:
                if this_dir in dirs:
                    dirs.remove(this_dir)

            sub_dir = current_dir.replace(base_dir, '')
            if not walk and sub_dir:
                break
            if current_dir not in name_dirs:
                file_monitor_dict = {
                    'path': current_dir,
                    'mtime': os.path.getmtime(current_dir),
                    'type': 'folder'
                }
                result_list.append(file_monitor_dict)
                name_dirs.append(current_dir)

            for this_file in files:
                if this_file not in ignore_files and os.path.splitext(this_file)[-1].lower() not in ignore_file_ext:
                    filepath = os.path.join(current_dir, this_file)
                    file_monitor_dict = {
                        'path': filepath,
                        'mtime': os.path.getmtime(filepath),
                        'type': 'file'
                    }
                    result_list.append(file_monitor_dict)
        return result_list

    def upload_all(self, server="192.168.4.200", port=621, username="user", password="12345",
                   base_local_dir="D:/github/flask-landslide/app/classification/keras/image/landslide_v20210112.h5/",
                   base_remote_dir="landslide_v20210112", files_to_update=None, walk=True):
        base_local_dir = os.path.abspath(base_local_dir)
        base_remote_dir = os.path.normpath(base_remote_dir)
        server_connect_ok = False
        if files_to_update:
            local_files = files_to_update
        else:
            local_files = self._get_local_files(base_local_dir, walk)

        ftp_h = ftplib.FTP()
        ftp_h.set_pasv(False)
        try:
            ftp_h.connect(server, port)
            server_connect_ok = True
        except socket.gaierror as e:
            print('ERROR -- Could not connect to (%s): %s' % (server, str(e.args)))
        except IOError as e:
            print('ERROR -- File not found: %s' % (str(e.args)))
        except socket.error as e:
            print('ERROR -- Could not connect to (%s): %s' % (server, str(e.args)))

        if len(local_files) > 0:
            ftp_path_tools = FtpAddOns(ftp_h)
            if server_connect_ok:
                try:
                    ftp_h.login(username, password)
                    print('Logged into (%s) as (%s)' % (server, username))
                    login_ok = True
                except ftplib.error_perm as e:
                    print('ERROR -- Check Username/Password: %s' % (str(e.args)))

            if login_ok:
                for file_info in local_files:
                    filepath = file_info['path']
                    path = None
                    filename = None
                    if file_info['type'] == 'file':
                        path, filename = os.path.split(filepath)
                    else:
                        path = file_info['path']

                    remote_sub_path = path.replace(base_local_dir, '')
                    remote_path = path.replace(base_local_dir, base_remote_dir)
                    remote_path = remote_path.replace('\\', '/')  # Convert to unix style
                    remote_path = "/" + remote_path

                    if not ftp_path_tools.ftp_exists(remote_path):
                        ftp_path_tools.ftp_mkdirs(remote_path)
                    try:
                        last = ftp_h.pwd()
                        ftp_h.cwd(remote_path)
                        now = ftp_h.pwd()
                        continue_on = True
                    except ftplib.error_perm as e:
                        print('ERROR -- %s' % (str(e.args)))

                    if continue_on and filename is not None:
                        f_h = open(filepath, 'rb')

                        display_filename = os.path.join(remote_sub_path, filename)
                        display_filename = display_filename.replace('\\', '/')
                        print(display_filename)
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
        else:
            print('ERROR -- No files found in (%s)' % (base_local_dir))
