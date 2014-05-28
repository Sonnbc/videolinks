from ..feed import Feed
import subprocess
from multiprocessing import Pool
from random import shuffle, randint
import traceback
from time import sleep

class TestFeed:
  def clean_redis(self):
    r = self.feed.redis_connection
    for x in r.keys("vhash*"):
      r.delete(x)
    for x in r.keys("topic*"):
      r.delete(x)

  def setUp(self):
    self.feed = Feed()
    self.clean_redis()
    self.consumer = subprocess.Popen(['python', 'feed.py'])
  
  def tearDown(self):
    self.consumer.kill()
    #self.clean_redis()

  def test_compose_index_1(self):
    video_id, topic_id = 123, 45
    a = self.feed.compose_index(video_id, topic_id)
    
    assert(self.feed.compose_index(video_id, topic_id) == 
      ("vhash.0", "123.topic_id.45"))
    assert((video_id, topic_id) == self.feed.decompose_index(*a))


  def test_compose_index_2(self):
    video_id, topic_id = 123456, 78
    a = self.feed.compose_index(video_id, topic_id)

    assert(self.feed.compose_index(video_id, topic_id) == 
      ("vhash.123", "456.topic_id.78"))
    assert((video_id, topic_id) == self.feed.decompose_index(*a))

  def test_feed(self):
    num_videos = 2000
    num_topics = 10
    get_topic = lambda x: x % num_topics
    iterations = 1

    args = [(x, get_topic(x)) for x in range(num_videos)*iterations]
    shuffle(args)
    pool = Pool(processes=40)

    #Why not pool.map()? See explanation here:
    #http://stackoverflow.com/questions/1408356/keyboard-interrupts-with-pythons-multiprocessing-pool
    pool.map_async(vote, args).get(9999999)

    #wait for the consumer to collect everything
    sleep(5)

    topics = set([get_topic(x) for x in range(num_videos)])
    hot = self.feed.hottest_videos(topics)
    correct_videos = reversed(
      range(num_videos - Feed.MAX_VIDEOS, num_videos))
    correct_videos = [(x, x*iterations) for x in correct_videos]
    assert(hot == correct_videos)
  
def vote(arg):
  video_id, topic_id = arg
  feed = Feed()
  #vote video_id times for video_id
  for i in xrange(video_id):
    feed.update_video_score(video_id, topic_id, 1)    



