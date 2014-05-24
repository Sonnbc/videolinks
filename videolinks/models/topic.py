from .meta import *

from .user import User

class Topic(Base):
  __tablename__ = 'topics'
  id = Column(Integer, primary_key=True)
  name = Column(String(50), nullable=False, unique=True)
  description = Column(Text)

  subscriptions = relationship("TopicSubscription", backref="topic",
    cascade="all, delete, delete-orphan")

class TopicSubscription(Base):
  __tablename__ = "topicsubscriptions"
  user_id = Column(String(50), ForeignKey(User.id), 
    primary_key=True)
  topic_id = Column(String(50), ForeignKey(Topic.id),
    primary_key=True)
