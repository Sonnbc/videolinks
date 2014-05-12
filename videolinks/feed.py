import DBHelper

from .models import (
  Video,
  User,
  VideoVote
  )

def get_feed(user_handler):
  #sort by votes count
  #TODO: try to be more efficient. perhaps 1 SQL call only?
  all_videos = DBHelper.DBSession.query(Video).all()
  votes = {x.id: DBHelper.DBSession.query(
    VideoVote).filter_by(video_id=x.id, vote_count=1).count()
    for x in all_videos}
  print votes
  all_videos = sorted(all_videos, key=lambda x: votes[x.id], reverse=True)
  return all_videos