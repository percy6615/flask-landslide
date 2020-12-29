from ..tools.sync_tool import singleton
from app.database.mysql_engine import MySQLs



@singleton
class GlobalInMem:
    # getInstance

    def __init__(self):
        self.usersDic = None
        self.groupsDic = None
        self.missionid = None

    def handleUserList(self):
        all = MySQLs().get_dict_data_sql('select * from disaster_userlist ')
        self.usersDic = dict()
        self.groupsDic = dict()
        self.missionid = set()
        for a in all:
            if a['sourcetype'] == 'user':
                self.usersDic[a['senderid']] = a
            elif a['sourcetype'] == 'group':
                self.groupsDic[a['senderid']] = a
        missions = MySQLs().get_dict_data_sql('select distinct mission_id from wraproject.pump_mission_list ')
        for m in missions:
            self.missionid.add(m['mission_id'])
        return self

    def setRedis(self):
        print()

    def getUserList(self):
        return self.usersDic

    def getGroupList(self):
        return self.groupsDic

    def getMissionid(self):
        return self.missionid

    def updateDataBaseUser(self, senderid, groupname):
        return MySQLs().run(
            "update disaster_userlist set webflag = 1, groupname='%(groupname)s' where senderid='%(senderid)s' and sourcetype = 'user'" % (
                {"senderid": senderid, "groupname": groupname}))
