from abc import ABC
from linebot.models import FollowEvent, JoinEvent, SourceGroup, SourceRoom
from app.model.message_interface import MessageInterface

#user
class FollowEventHandle(MessageInterface, ABC):
    def __init__(self, event, profile, channel_access_token):
        self.channel_access_token = channel_access_token
        if event is not None:
            self.event = event
            self.eventType = event.type
            self.eventTimestamp = event.timestamp
            self.eventSourceUserId = event.source.user_id
            self.eventSourceSenderId = event.source.sender_id
            self.eventSourceType = event.source.type
            if isinstance(event, FollowEvent):
                self.replyToken = event.reply_token
        if profile is not None:
            self.profileDisplayName = profile.display_name
            self.profileUrl = profile.picture_url

    def to_json(self):
        return {'data': [{'senderid': self.eventSourceSenderId, 'status': 0, 'sourcetype': self.eventSourceType,
                          'epochsecond': self.eventTimestamp, 'eventstype': self.eventType,
                          'displayname': self.profileDisplayName,
                          'phone': None, 'unitname': None, 'roomid': None,
                          'groupid': None, 'displayurl': self.profileUrl,
                          'channeltoken': self.channel_access_token, 'replytoken': self.replyToken,
                          'userid': self.eventSourceUserId, 'groupname': None, 'webflag': 0}]}

    def setCheckEventExistSql(self):
        checkSql = 'select 1 from disaster_userlist where eventstype=\'follow\' and userid=\'' + self.eventSourceUserId + '\' and channeltoken=\'' + self.channel_access_token + '\''
        return checkSql

    def setDeleteEventSql(self):
        delSql = "delete from disaster_userlist where userid = '%(eventSourceUserId)s' and channeltoken = '%(channel_access_token)s'" % (
            {"eventSourceUserId": self.eventSourceUserId, "channel_access_token": self.channel_access_token})
        return delSql, self.eventSourceUserId

#group
class JoinEventHandle(MessageInterface, ABC):
    def __init__(self, event, summary, channel_access_token):
        self.channel_access_token = channel_access_token
        if event is not None:
            self.event = event
            self.eventType = event.type
            self.eventTimestamp = event.timestamp
            self.eventSourceRoomId = None
            self.eventSourceGroupId = None
            self.eventSourceType = event.source.type
            self.eventSourceUserId = event.source.user_id
            self.eventSourceSendId = event.source.sender_id
            if isinstance(event.source, SourceGroup):
                self.eventSourceGroupId = event.source.group_id
            elif isinstance(event.source, SourceRoom):
                self.eventSourceRoomId = event.source.room_id
            if isinstance(event, JoinEvent):
                self.replyToken = event.reply_token
        if summary is not None:
            self.groupName = summary.group_name
            self.profileUrl = summary.picture_url

    def to_json(self):
        return {'data': [{'senderid': self.eventSourceSendId, 'status': 0, 'sourcetype': self.eventSourceType,
                          'epochsecond': self.eventTimestamp, 'eventstype': self.eventType,
                          'displayname': None,
                          'phone': None, 'unitname': None, 'roomid': self.eventSourceRoomId,
                          'groupid': self.eventSourceGroupId, 'displayurl': self.profileUrl,
                          'channeltoken': self.channel_access_token, 'replytoken': self.replyToken,
                          'userid': self.eventSourceUserId, 'groupname': self.groupName,'webflag': -1}]}

    def setCheckEventExistSql(self):
        checkSql = 'select 0'
        if self.eventSourceGroupId is not None:
            checkSql = 'select 1 from disaster_userlist where eventstype=\'join\' and groupid=\'' + self.eventSourceGroupId + '\' and channeltoken=\'' + self.channel_access_token + '\''
        elif self.eventSourceRoomId is not None:
            checkSql = 'select 1 from disaster_userlist where eventstype=\'join\' and roomid=\'' + self.eventSourceRoomId + '\' and channeltoken=\'' + self.channel_access_token + '\''
        return checkSql

    def setDeleteEventSql(self):
        delSql = 'select 0'
        eventId = ''
        if self.eventSourceGroupId is not None:
            eventId = self.eventSourceGroupId
            delSql = "delete from disaster_userlist where groupid = '%(eventSourceGroupId)s' and channeltoken = '%(" \
                     "channel_access_token)s'" % (
                {"eventSourceGroupId": self.eventSourceGroupId, "channel_access_token": self.channel_access_token})
        elif self.eventSourceRoomId is not None:
            eventId = self.eventSourceRoomId
            delSql = "delete from disaster_userlist where roomid = '%(eventSourceRoomId)s' and channeltoken = '%(" \
                     "channel_access_token)s'" % (
                {"eventSourceRoomId": self.eventSourceRoomId, "channel_access_token": self.channel_access_token})
        return delSql,eventId

