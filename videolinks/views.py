from pyramid.response import Response
from pyramid.view import (
    view_config,
    forbidden_view_config,
    )
from pyramid.security import (
    remember,
    forget,
    )

from sqlalchemy.exc import DBAPIError

from pyramid.httpexceptions import (
    HTTPFound,
    HTTPNotFound,
    )

from .models import (
  Video,
  User
  )

import DBHelper
from DBHelper import DBSession
import feed


@view_config(route_name='home', renderer='templates/home.pt')
def frontpage(request):
  add_video_url = request.route_url('add_video')
  all_videos = feed.get_feed(request.authenticated_userid)
  
  user_id = request.authenticated_userid
  user = DBHelper.get_user_from_id(user_id)

  topics = DBHelper.get_all_topics()

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

#TODO: this should not be a view handler (just REST)
#TODO: this is not really efficient (have to reload the whole referer page)
@view_config(route_name='vote_video')
def vote_video(request):
  handler = request.authenticated_userid
  vote = request.matchdict['vote']
  video_id = request.matchdict['video_id']
  DBHelper.vote_video(handler, video_id, vote)

  referrer = request.referrer
  this_url = request.route_url('vote_video', video_id=video_id, vote=vote)

  if (not referrer) or referrer == this_url:
    referrer = request.route_url('home')

  return HTTPFound(location = referrer)




