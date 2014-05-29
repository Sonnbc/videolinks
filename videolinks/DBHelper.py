from videolinks.models import (
  User, 
  Video, VideoVote,
  Topic, TopicSubscription
  )

from sqlalchemy.orm import (
  scoped_session,
  sessionmaker,
  exc
  )

from zope.sqlalchemy import ZopeTransactionExtension
DBSession = scoped_session(sessionmaker(extension=ZopeTransactionExtension()))
from sqlalchemy.orm.exc import NoResultFound
from sqlalchemy.exc import SQLAlchemyError

from datetime import datetime

def groupfinder(user_id, request):
  return []

def add_user(handler, password):
  user = get_user_from_handler(handler)
  if not user:
    user = User(handler=handler, password=password)
    DBSession.add(user)
    DBSession.flush() #flush to populate id for user
    return user

  return False

def get_user(**f):
  try:
    user = DBSession.query(User).filter_by(**f).one()
    return user
  except NoResultFound:
    return None

def get_user_from_handler(handler):
  return get_user(handler=handler)

def get_user_from_id(user_id):
  return get_user(id=user_id)  

def get_video(id):
  try:
    video = DBSession.query(Video).filter_by(id=id).one()
    return video
  except NoResultFound:
    return None

def add_video(video):
  #TODO: move validation elsewhere
  if not (video.url and video.title and video.description):
    return False

  try:
    DBSession.add(video)
    return True
  except SQLAlchemyError:
    return False

def get_all_topics():
  topics = DBSession.query(Topic).all()
  return topics

def vote_video(user_id, video_id, vote_kind):
  #don't allow downvote for now
  #return the actual change in vote, ie: vote_kind - current vote

  #0: unvote, 1:upvote
  vote_kind = int(vote_kind)
  if vote_kind not in [0, 1]:
    return

  try:
    vote = DBSession.query(VideoVote).filter_by(
      user_id=user_id, video_id=video_id).one()
    res = vote_kind - vote.vote_count
    vote.vote_count = vote_kind
  except exc.NoResultFound:
    vote = VideoVote(user_id=user_id, video_id=video_id,
      vote_time=datetime.now(), vote_count=vote_kind)
    res = vote_kind
    DBSession.add(vote)

  return res

def vote_by_user(video_id, user_id):
  res = DBSession.query(VideoVote).filter_by(
    user_id=user_id, video_id=video_id, vote_count=1).first() or 0
  return res


def subscribe_topic(user_id, topic_id):
  subscription = TopicSubscription(user_id=user_id, topic_id=topic_id)
  DBSession.add(subscription)

def unsubscribe_topic(user_id, topic_id):
  DBSession.query(TopicSubscription).filter_by(
    user_id=user_id, topic_id=topic_id).delete()

######################################################################
## Sqlite: enforce foreign key
######################################################################
from sqlalchemy.engine import Engine
from sqlalchemy import event

@event.listens_for(Engine, "connect")
def set_sqlite_pragma(dbapi_connection, connection_record):
    cursor = dbapi_connection.cursor()
    cursor.execute("PRAGMA foreign_keys=ON")
    cursor.close()
######################################################################
