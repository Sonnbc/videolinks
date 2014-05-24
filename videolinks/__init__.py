from pyramid.config import Configurator
from sqlalchemy import engine_from_config

from models import Base
from .DBHelper import DBSession


from pyramid.authentication import AuthTktAuthenticationPolicy
from pyramid.authorization import ACLAuthorizationPolicy
from videolinks.DBHelper import groupfinder

def add_route(config):
    config.add_route('home', '/')
    config.add_route('add_video', '/add_video',
        traverse='/videos')
    config.add_route('delete_video', '/delete_video/{video_id}', 
        traverse='/videos/{video_id}')

    config.add_route('login', '/login')
    config.add_route('logout', '/logout')
    config.add_route('register', '/register')

    config.add_route('vote_video', '/vote_video/{video_id}/{vote}',
        traverse='/videos')

    config.add_route('subscribe_topic', '/subscribe_topic/{topic_id}')
    config.add_route('unsubscribe_topic', '/unsubscribe_topic/{topic_id}')


def main(global_config, **settings):
    """ This function returns a Pyramid WSGI application.
    """
    engine = engine_from_config(settings, 'sqlalchemy.')
    DBSession.configure(bind=engine)
    Base.metadata.bind = engine

    authn_policy = AuthTktAuthenticationPolicy(
        'sosecret', callback=groupfinder, hashalg='sha512')
    authz_policy = ACLAuthorizationPolicy()

    config = Configurator(settings=settings, 
        root_factory='videolinks.models.RootFactory')
    config.set_authentication_policy(authn_policy)
    config.set_authorization_policy(authz_policy)

    config.include('pyramid_chameleon')
    
    config.add_static_view('static', 'static', cache_max_age=3600)
    add_route(config)
    
    config.scan()
    return config.make_wsgi_app()
