from .meta import *

class Topic(Base):
  __tablename__ = 'topics'
  id = Column(Integer, primary_key=True)
  name = Column(String(50), nullable=False, unique=True)
  description = Column(Text)