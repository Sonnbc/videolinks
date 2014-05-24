from .meta import *
import hashlib, uuid

class User(Base):
  __tablename__ = 'users'
  __hashed_password = Column(Integer, nullable=False)

  id = Column(Integer, primary_key=True)
  handler = Column(String(50), unique=True)
  
  ####################################################################
  ## security
  ####################################################################
  @property
  def password(self):
     raise Exception("Retrieving password is not possible")
  
  @password.setter
  def password(self, value):
      self.__hashed_password = hash(value)  

  password = synonym('__hashed_password', descriptor=password)

  def authenticate(self, password):
    return self.__hashed_password == hash(password)

  salt = '622bbf45325e40eb92c31a1e9349af04' #TODO: change this  
  def hash(self, value):
    return hashlib.sha512(value + salt).hexdigest()

  ####################################################################  

  votes = relationship("VideoVote", backref="user", 
    cascade="all, delete, delete-orphan")
  subscriptions = relationship("TopicSubscription", backref="user",
    cascade="all, delete, delete-orphan")