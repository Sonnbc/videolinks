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

from .DBHelper import (
  DBSession, 
  get_user,
  get_video
  )


@view_config(route_name='home', renderer='templates/home.pt')
def frontpage(request):
  add_video_url = request.route_url('add_video')
  all_videos = DBSession.query(Video).all()
  return {'videos': all_videos, 'add_video': add_video_url,
      'logged_in': request.authenticated_userid}

@view_config(route_name='add_video', renderer='templates/add_video.pt',
  permission='add_video')
def add_video(request):
  if 'form.submitted' in request.params:
    title = request.params['title']
    description = request.params['description']
    url = request.params['url']
    handler = request.authenticated_userid
    user = get_user(handler)
    if not user:
      raise Exception("User not found. This is impossible!")

    if title and description and url:
      video = Video(title=title, description=description, url=url,
        owner=user)
      DBSession.add(video)
    return HTTPFound(location=request.route_url('home'))
    
  save_url = request.route_url('add_video')
  video = Video(title='', description='', url='')
  return {'video':video, 'save_url':save_url}

@view_config(route_name='delete_video', permission='delete_video')
def delete_video(request):
  video_id = request.matchdict['video_id']
  video = get_video(video_id)
  DBSession.delete(video)
  return HTTPFound(location = request.route_url('home'))

@view_config(route_name='login', renderer='templates/login.pt')
@forbidden_view_config(renderer='templates/login.pt')
def login(request):
    login_url = request.route_url('login')
    referrer = request.url
    if referrer == login_url:
        referrer = '/' # never use the login form itself as came_from
    came_from = request.params.get('came_from', referrer)
    message = ''
    login = ''
    password = ''
    if 'form.submitted' in request.params:
        login = request.params['login']
        password = request.params['password']
        user = get_user(login)
        if user and user.authenticate(password):
            headers = remember(request, login)
            return HTTPFound(location = came_from,
                             headers = headers)
        message = 'Failed login'

    return dict(
        message = message,
        url = request.application_url + '/login',
        came_from = came_from,
        login = login,
        password = password,
        )

@view_config(route_name='logout')
def logout(request):
    headers = forget(request)
    return HTTPFound(location = request.route_url('home'),
                     headers = headers)



