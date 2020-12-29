import random
from abc import ABCMeta, abstractmethod

from app import globalRegisterUser
from app.database.mysql_engine import MySQLs, create_ng_mysql
import pandas as pd
import time
# from sqlalchemy.orm import sessionmaker
engine = create_ng_mysql()

# db_session = sessionmaker(engine)

class MessageInterface(metaclass=ABCMeta):
    @abstractmethod
    def to_json(self):
        pass

    @abstractmethod
    def setCheckEventExistSql(self):
        pass

    @abstractmethod
    def setDeleteEventSql(self):
        pass

    def isCheckEventExist(self):
        checkSql = self.setCheckEventExistSql()
        try:
            tf = len(MySQLs().get(checkSql)) >= 1
        except None:
            print('check error to db event')
        return tf

    def deleteEvent(self):
        delSql, eventId = self.setDeleteEventSql()
        try:
            MySQLs().run(delSql)
            if eventId in globalRegisterUser:
                del globalRegisterUser[eventId]
        except None:
            print('delete error to db event')





