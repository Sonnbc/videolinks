from DBHelper import DBSession

from .models import (
  Video,
  User,
  VideoVote
  )

from sqlalchemy.sql import func

def get_feed(user_handler):
  #sort by votes count
  #TODO: try to be more efficient. perhaps 1 SQL call only?
  all_videos = DBSession.query(Video).all()

  votes = {
    x.id: 
        (
          DBSession.query(VideoVote).filter_by(
            video_id=x.id, vote_count=1).count(),
          y.vote_count if y else 0
        )
    for x in all_videos    
    for y in 
      [ DBSession.query(VideoVote).filter_by(
            user_handler=user_handler, video_id=x.id, vote_count=1).first() ]
  }
    
  print "This is votes: ", votes
  all_videos = sorted(all_videos, key=lambda x: votes[x.id][0], reverse=True)
  print [(x.id, votes[x.id]) for x in all_videos]
  all_videos = [
    (x, votes[x.id][0], votes[x.id][1]) for x in all_videos
  ]
  print all_videos
  return all_videos