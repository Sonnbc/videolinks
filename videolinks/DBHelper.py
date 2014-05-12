from .models import (
  User, 
  Video,
  VideoVote
  )

from sqlalchemy.orm import (
  scoped_session,
  sessionmaker
  )

from zope.sqlalchemy import ZopeTransactionExtension
DBSession = scoped_session(sessionmaker(extension=ZopeTransactionExtension()))
from sqlalchemy.orm.exc import NoResultFound

from datetime import datetime

def groupfinder(handler, request):
  return []

def get_user(handler):
  try:
    user = DBSession.query(User).filter_by(handler=handler).one()
    return user
  except NoResultFound, e:
    return None

def get_video(id):
  try:
    video = DBSession.query(Video).filter_by(id=id).one()
    return video
  except NoResultFound, e:
    return None

def vote_video(user_handler, video_id, vote_kind):
  vote_kind = int(vote_kind)
  #don't allow downvote for now
  if vote_kind not in [0, 1]:
    return

  vote = VideoVote(user_handler=user_handler, video_id=video_id,
    vote_time=datetime.now(), vote_count=vote_kind)
  DBSession.add(vote)




