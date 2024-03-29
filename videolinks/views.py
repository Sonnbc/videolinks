from pyramid.response import Response
from pyramid.view import view_config, forbidden_view_config
from pyramid.security import remember, forget
from pyramid.httpexceptions import HTTPFound, HTTPNotFound

from sqlalchemy.exc import DBAPIError

from .models import Video, User
import DBHelper
from DBHelper import DBSession
from feed import Feed


@view_config(route_name='home', renderer='templates/home.pt')
def frontpage(request):
  add_video_url = request.route_url('add_video')
  user_id = request.authenticated_userid
  user = DBHelper.get_user_from_id(user_id)
  topics = DBHelper.get_all_topics()
  topic_ids = [x.id for x in topics]

  feed = Feed()
  all_videos = feed.build_feed(user_id, topic_ids)
  return {'videos': all_videos, 'logged_in': user, 'topics':topics}

@view_config(route_name='add_video', renderer='templates/add_video.pt',
  permission='add_video')
def add_video(request):
  save_url = request.route_url('add_video')
  topics = DBHelper.get_all_topics()
  video = Video(title='', description='', url='', topic_id=0)
  message = None

  if 'form.submitted' in request.params:
    title = request.params['title']
    description = request.params['description']
    url = request.params['url']
    topic_id = request.params['topic']
    user_id = request.authenticated_userid

    video = Video(title=title, description=description, url=url,
        owner_id=user_id, topic_id=topic_id)
    if DBHelper.add_video(video):
      feed = Feed()
      feed.update_video_score(video_id, topic_id, 0)
      return HTTPFound(location=request.route_url('home'))
    else:
      message = "Error while adding video"

  return {'video':video, 'save_url':save_url, 
      'topics':topics, 'message':message}

@view_config(route_name='delete_video', permission='delete_video')
def delete_video(request):
  video_id = request.matchdict['video_id']
  video = DBHelper.get_video(video_id)
  DBSession.delete(video)
  return HTTPFound(location = request.route_url('home'))

@view_config(route_name='register', renderer='templates/register.pt')
def register(request):
  handler = ''
  password = ''
  message = ''
  if 'form.submitted' in request.params:
    handler = request.params['handler']
    password = request.params['password']
    user = DBHelper.add_user(handler, password)
    if user:
      headers = remember(request, user.id)
      return HTTPFound(location=request.route_url('home'),
                      headers = headers)
    else:    
      message = "Username taken"

  return dict(
    message = message,
    url = request.application_url + '/register',
    handler = handler,
    password = password
    )  

@view_config(route_name='login', renderer='templates/login.pt')
@forbidden_view_config(renderer='templates/login.pt')
def login(request):
  login_url = request.route_url('login')
  referrer = request.url
  if referrer == login_url:
    # never use the login form itself as came_from
    referrer = request.route_url('home') 
  came_from = request.params.get('came_from', referrer)
  message = ''
  handler = ''
  password = ''
  if 'form.submitted' in request.params:
    handler = request.params['handler']
    password = request.params['password']
    user = DBHelper.get_user_from_handler(handler)
    print user.id, user.handler
    if user and user.authenticate(password):
      headers = remember(request, user.id)
      return HTTPFound(location = came_from,
                       headers = headers)
    message = 'Failed login'

  return dict(
    message = message,
    url = request.application_url + '/login',
    came_from = came_from,
    handler = handler,
    password = password,
    )

@view_config(route_name='logout')
def logout(request):
  headers = forget(request)
  return HTTPFound(location = request.route_url('home'),
                   headers = headers)

@view_config(route_name='vote_video', renderer='json')
def vote_video(request):
  user_id = request.authenticated_userid
  vote = request.matchdict['vote']
  video_id = int(request.matchdict['video_id'])
  topic_id = DBHelper.get_video(video_id).topic_id
  change = DBHelper.vote_video(user_id, video_id, vote)
  feed = Feed()
  feed.update_video_score(video_id, topic_id, change)

  return {'change': change}

@view_config(route_name='subscribe_topic')
def subscribe_topic(request):
  user_id = request.authenticated_userid
  topic_id = request.matchdict['topic_id']
  DBHelper.subscribe_topic(user_id, topic_id)

  return last_location_or_home(request)

@view_config(route_name='unsubscribe_topic')
def unsubscribe_topic(request):
  user_id = request.authenticated_userid
  topic_id = request.matchdict['topic_id']
  DBHelper.unsubscribe_topic(user_id, topic_id)

  return last_location_or_home(request)  

def last_location_or_home(request):
  referrer = request.referrer
  if (not referrer) or referrer == request.url:
    referrer = request.route_url('home')

  return HTTPFound(location = referrer)




