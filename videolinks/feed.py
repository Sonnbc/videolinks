from DBHelper import DBSession
from videolinks.models import Video, User, VideoVote
from sqlalchemy.sql import func
import redis
from time import sleep

class Feed():
  MAX_VIDEOS_PER_TOPIC = 150
  MAX_VIDEOS = 1000
  VIDEOS_PER_HASH = 1000

  def __init__(self):
    self._redis = redis.Redis("localhost")

  @property  
  def redis_connection(self):
    return self._redis  

  def build_feed(self, user_id, start, end, *topics):
    #sort by votes count, unnormalized
    hottest = hottest_videos(topics)

    #each item is (video, score, vote by this user)
    videos = [ ( DBHelper.get_video(x[0]), 
                 x[1], 
                 DBHelper.vote_by_user(user_id)
               )
               for x in hottest[start:end]
             ]
    return videos

  def hottest_videos(self, topics):
    r = self.redis_connection

    #retrieve MAX_VIDEOS_PER_TOPIC items from each topic. Each item will be
    #(video_id, score)
    hot = {x: r.zrange(self.zname(x), 0, self.MAX_VIDEOS_PER_TOPIC, 
      desc=True, withscores=True, score_cast_func=int)
      for x in topics}

    #merge videos from all topics
    hot = sorted([(int(video[0]), video[1])
                  for topic_id in hot for video in hot[topic_id]],
            key=lambda x: x[1], reverse=True)
    return hot[:self.MAX_VIDEOS]

  def update_video_score(self, video_id, topic_id, change):
    r = self.redis_connection
    hname, key = self.compose_index(video_id, topic_id)
    r.hincrby(hname, key, change)

  def zname(self, topic_id):
    return "feed.topic." + str(topic_id)

  def compose_index(self, video_id, topic_id):
    hname = "feed.vhash." + str(video_id / self.VIDEOS_PER_HASH)
    key =  str(video_id % self.VIDEOS_PER_HASH) + ".topic_id." + str(topic_id)
    return hname, key

  def decompose_index(self, hname, key):
    h = hname.split(".")
    k = key.split(".")
    video_id = int(h[2])*self.VIDEOS_PER_HASH + int(k[0])
    topic_id = int(k[2])
    return video_id, topic_id
  
  def consume_video_score(self, relax_per_iteration):
    r = self.redis_connection
    while True:
      for hname in r.keys("feed.vhash*"):
        for key in r.hkeys(hname):
          pipe = r.pipeline()
          pipe.hget(hname, key)
          pipe.hdel(hname, key)
          result = pipe.execute()

          value = result[0]
          video_id, topic_id = self.decompose_index(hname, key)
          r.zincrby(self.zname(topic_id), video_id, value)

      sleep(relax_per_iteration)

if __name__ == '__main__':
  feed = Feed()
  feed.consume_video_score(1)  


