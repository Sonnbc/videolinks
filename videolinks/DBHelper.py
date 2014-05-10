from .models import (
  User, 
  Video
  )

from sqlalchemy.orm import (
  scoped_session,
  sessionmaker
  )

from zope.sqlalchemy import ZopeTransactionExtension
DBSession = scoped_session(sessionmaker(extension=ZopeTransactionExtension()))
from sqlalchemy.orm.exc import NoResultFound

def groupfinder(handler, request):
  print "groupfinder:", handler
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



