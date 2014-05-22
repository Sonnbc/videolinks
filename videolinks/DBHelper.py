from videolinks.models import (
  User, 
  Video,
  VideoVote,
  Topic
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

def groupfinder(handler, request):
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

def get_user_from_id(userid):
  return get_user(id=userid)  

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

def vote_video(user_handler, video_id, vote_kind):
  vote_kind = int(vote_kind)
  #don't allow downvote for now
  if vote_kind not in [0, 1]:
    return

  try:
    vote = DBSession.query(VideoVote).filter_by(
      user_handler=user_handler, video_id=video_id).one()
    vote.vote_count = vote_kind
  except exc.NoResultFound:
    vote = VideoVote(user_handler=user_handler, video_id=video_id,
      vote_time=datetime.now(), vote_count=vote_kind)
    DBSession.add(vote)




