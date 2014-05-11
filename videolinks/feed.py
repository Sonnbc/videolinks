from random import shuffle

import DBHelper

from .models import (
  Video,
  User
  )

def get_feed(user_handler):
  #Just shuffle all videos and return
  all_videos = DBHelper.DBSession.query(Video).all()
  shuffle(all_videos)
  return all_videos