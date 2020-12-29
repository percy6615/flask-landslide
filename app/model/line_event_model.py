from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, scoped_session
from sqlalchemy import Column, Integer, String, Sequence

from app.database.mysql_engine import create_ng_mysql

engine = create_ng_mysql()

db_session = scoped_session(sessionmaker(autocommit=False, autoflush=False, bind=engine))
Base = declarative_base()
Base.query = db_session.query_property()


class LineEventData(Base):
    __tablename__ = 'disaster_userlist'
    senderid = Column(String(256), Sequence('user_id'), primary_key=True)
    status = Column(Integer, unique=True, nullable=False)
    sourcetype = Column(String(256), unique=True, nullable=False)
    epochsecond = Column(Integer, unique=False, nullable=False)
    eventstype = Column(String(256), unique=True, nullable=False)
    displayname = Column(String(256), unique=False, nullable=False)
    phone = Column(String(256), unique=True, nullable=False)
    unitname = Column(String(256), unique=False, nullable=False)
    roomid = Column(String(256), unique=True, nullable=False)
    groupid = Column(String(256), unique=False, nullable=False)
    displayurl = Column(String(256), unique=True, nullable=False)
    channeltoken = Column(String(256), unique=False, nullable=False)
    replytoken = Column(String(256), unique=True, nullable=False)
    userid = Column(String(256), unique=False, nullable=False)
    groupname = Column(String(256), unique=True, nullable=False)
    webflag = Column(Integer, unique=False, nullable=False)

    def to_dict(self):  # 將數據轉為字典
        dictionary = self.__dict__
        if "_sa_instance_state" in dictionary:
            del dictionary["_sa_instance_state"]
        return dictionary

    def __repr__(self):  # 讓print這個物件的時候，看起來好看
        return '<User %r>' % self.username
