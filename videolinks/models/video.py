from .meta import *
from pyramid.security import Allow

class Video(Base):
  __tablename__ = 'videos'
  id = Column(Integer, primary_key=True)
  url = Column(Text, nullable=False)
  title = Column(String(200), nullable=False)
  description = Column(Text)
  extra = Column(PickleType)
  owner_id = Column(Integer, ForeignKey('users.id'))
  owner = relationship("User")

  votes = relationship("VideoVote", backref="video", 
    cascade="all, delete, delete-orphan")

  topic_id = Column(Integer, ForeignKey('topics.id'), nullable=False)
  topic = relationship("Topic", backref="videos")

  @property
  def __acl__(self):
    acls = [ (Allow, self.owner_id, 'delete_video') ]
    return acls

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