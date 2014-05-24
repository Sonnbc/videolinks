from pyramid.security import (
  Allow,
  Everyone,
  Authenticated,
  ALL_PERMISSIONS
  )

from .meta import *

class RootFactory(dict):
  __acl__ = [ (Allow, 'g:admin', ALL_PERMISSIONS) ]

  __acl__ += [(Allow, Authenticated, 'subscribe_topic'),
              (Allow, Authenticated, 'unsubscribe_topic')]

  
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
    from .. import DBHelper
    video = DBHelper.get_video(key)
    if video is None:
      raise KeyError
    
    video.__parent__ = self
    video.__name__ = key
    return video