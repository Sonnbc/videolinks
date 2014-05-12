from sqlalchemy import (
  Column,
  Index,
  Integer,
  Text,
  String,
  PickleType,
  ForeignKey,
  DateTime
  )

from sqlalchemy.ext.declarative import (
  declarative_base,
  )

from sqlalchemy.orm import (
  relationship,
  synonym
  )

from pyramid.security import (
  Allow,
  Everyone,
  Authenticated,
  ALL_PERMISSIONS
  )

import hashlib, uuid

Base = declarative_base()

class RootFactory(dict):
  __acl__ = [ (Allow, 'g:admin', ALL_PERMISSIONS) ]

  
  def __init__(self, request):
    self.request = request
    self['videos'] = VideoFactory(self, 'videos')

class VideoFactory(object):
  __acl__ = [ (Allow, Authenticated, 'add_video'),
              (Allow, Authenticated, 'vote_video')]

  def __init__(self, parent, name):
    self.__parent__ = parent
    self.__name__ = name

  def __getitem__(self, key):
    import DBHelper
    video = DBHelper.get_video(key)
    print "VideoFactory __getitem__()", video
    print "owner:", video.owner.handler
    if video is None:
      raise KeyError
    
    video.__parent__ = self
    video.__name__ = key
    return video  

class Video(Base):
  __tablename__ = 'videos'
  id = Column(Integer, primary_key=True)
  url = Column(Text, nullable=False)
  title = Column(String(200), nullable=False)
  description = Column(Text)
  extra = Column(PickleType)
  owner_handler = Column(Integer, ForeignKey('users.handler'))
  owner = relationship("User")

  votes = relationship("VideoVote", backref="video", 
    cascade="all, delete, delete-orphan")

  @property
  def __acl__(self):
    acls = [ (Allow, self.owner_handler, 'delete_video') ]
    return acls

class User(Base):
  __tablename__ = 'users'
  __hashed_password = Column(Integer, nullable=False)

  handler = Column(String(50), primary_key=True)
  
  @property
  def password(self):
     raise Exception("Retrieving password is not possible")
  
  @password.setter
  def password(self, value):
      self.__hashed_password = hash(value)  

  password = synonym('__hashed_password', descriptor=password)

  def authenticate(self, password):
    return self.__hashed_password == hash(password)

  salt = '622bbf45325e40eb92c31a1e9349af04' #TODO: change this  
  def hash(self, value):
    return hashlib.sha512(value + salt).hexdigest()

  votes = relationship("VideoVote", backref="user", 
    cascade="all, delete, delete-orphan")

class VideoVote(Base):
  __tablename__ = "videovotes"
  user_handler = Column(String(50), ForeignKey('users.handler'), 
    primary_key=True)
  video_id = Column(Integer, ForeignKey('videos.id'),
    primary_key=True)

  vote_time = Column(DateTime)

  #vote count is either 1 (upvote), 0 (no vote), or -1 (downvote)
  #we want vote_time to be the first time the user votes on a video
  #to avoid user unvoting and revoting a video to change vote_time
  vote_count = Column(Integer)
