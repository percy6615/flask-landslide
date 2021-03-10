import os

import pymysql
from dotenv import load_dotenv
from sqlalchemy import create_engine

from app.tools import log_tool
from app.tools.sync_tool import synchronized, Singletonclass

logger = log_tool.logger
load_dotenv()


def create_ng_mysql():
    logger.info('configure database settings for pandas')
    mysql_host = os.getenv('mysql_host')
    mysql_pwd = os.getenv('mysql_pwd')
    mysql_username = os.getenv('mysql_username')
    mysql_port = os.getenv('mysql_port')
    mysql_database = os.getenv('mysql_database')
    uri = 'mysql+pymysql://' + mysql_username + ':' + mysql_pwd + '@' + mysql_host + ':' + mysql_port + '/' + mysql_database + '?charset=utf8mb4'
    engine = create_engine(uri)
    return engine


@Singletonclass.singleton
class MySQLs:
    # getInstance

    def __init__(self):
        self.conn = None
        self.cur = None
        self._conn()

    def _conn(self):
        logger.info('configure mysql database settings')
        mysql_host = os.getenv('mysql_host')
        mysql_pwd = os.getenv('mysql_pwd')
        mysql_username = os.getenv('mysql_username')
        mysql_port = os.getenv('mysql_port')
        mysql_database = os.getenv('mysql_database')
        self.conn = pymysql.connect(host=mysql_host, user=mysql_username, passwd=mysql_pwd, db=mysql_database,
                                    port=int(mysql_port), charset='utf8mb4')
        self.cur = self.conn.cursor()
        self.cur.execute('SET NAMES utf8')
        self.cur.execute("SET CHARACTER SET utf8")
        self.cur.execute("SET character_set_connection=utf8")

    @synchronized
    def run(self, sql):
        # logger.debug('execute mysql SQL {}'.format(sql))

        if self.conn is None:
            self._conn()
        elif not self.cur.connection:
            self._conn()
        try:
            result = self.cur.execute(sql)
            self.conn.commit()
            self._logout()
            return result
        except pymysql.Error as e:
            print('mysql conn get error ' + str(e))

    @synchronized
    def get(self, sql):
        # logger.info('retrieve data from mysql table')
        if self.conn is None:
            self._conn()
        elif not self.cur.connection:
            self._conn()
        try:
            self.cur.execute(sql)
            data = self.cur.fetchall()
            self.conn.commit()
            self._logout()
            return data  # return tuple
        except pymysql.Error as e:
            print('mysql conn get error ' + str(e))

    def _logout(self):
        try:
            if self.conn is not None:
                self.cur.close()
                self.conn.close()
            logger.info('log out from mysql database')
        except pymysql.Error as e:
            logger.warning('already logged out from Postgres database' + str(e))

    @staticmethod
    def get_index_dict(cur):
        index_dict = dict()
        index_dict_type = dict()
        index = 0
        for desc in cur.description:
            # pymysql.constants.FIELD_TYPE.get_info(desc[1])
            index_dict[desc[0]] = index
            index_dict_type[desc[0]] = desc[1]
            index = index + 1
        return index_dict, index_dict_type

    def get_dict_data_sql(self, sql):

        if self.conn is None:
            self._conn()
        elif not self.cur.connection:
            self._conn()
        self.cur.execute(sql)
        data = self.cur.fetchall()
        # self.conn.commit()
        index_dict, index_dict_type = self.get_index_dict(self.cur)
        res = []
        for datai in data:
            resi = dict()
            for indexi in index_dict:
                if datai[index_dict[indexi]] is None:
                    if index_dict_type[indexi] == pymysql.constants.FIELD_TYPE.VAR_STRING:
                        resi[indexi] = ''
                    elif index_dict_type[indexi] == pymysql.constants.FIELD_TYPE.DATETIME:
                        resi[indexi] = None
                else:
                    resi[indexi] = datai[index_dict[indexi]]
            res.append(resi)
        self._logout()
        return res

# class MysqlPool:
#     def __new__(cls, *args, **kwargs):
#         if cls._instance is None:
#             cls._instance = super().__new__(cls)
#         return cls._instance
#
#     def __init__(self):
#         self.conn = None
#         self.pool = None
#         self.cur = None
#     def _pool(self):
#         logger.info('configure mysql database settings')
#         mysql_host = os.getenv('mysql_host')
#         mysql_pwd = os.getenv('mysql_pwd')
#         mysql_username = os.getenv('mysql_username')
#         mysql_port = os.getenv('mysql_port')
#         mysql_database = os.getenv('mysql_database')
#         self.pool = Pool.connect(host=mysql_host, user=mysql_username, passwd=mysql_pwd, db=mysql_database,
#                                  port=mysql_port, autocommit=True)
#         self.pool.init()
#
#     def _conn(self):
#         self.conn = self.pool.get_conn()
#         self.cur = self.conn.cursor()
