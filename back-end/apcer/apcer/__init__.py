from pyramid.config import Configurator
from pyramid.session import SignedCookieSessionFactory
from pyramid.authentication import AuthTktAuthenticationPolicy
from pyramid.authorization import ACLAuthorizationPolicy
from sqlalchemy import engine_from_config
from .models.meta import Base
from .models.meta import Session  # ⬅️ WAJIB untuk aktifkan request.dbsession
from .security import get_user_id, RootFactory
from pyramid.renderers import JSON
from .cors import cors_tween_factory

def main(global_config, **settings):
    config = Configurator(settings=settings)

    config.add_tween('.cors_tween_factory')
    config.add_renderer('json', JSON(indent=4))

    engine = engine_from_config(settings, 'sqlalchemy.')
    Base.metadata.bind = engine
    config.include('pyramid_tm')
    config.include('pyramid_retry')
    config.include('pyramid_sqlalchemy')

    my_session_factory = SignedCookieSessionFactory('itsaseekreet')
    config.set_session_factory(my_session_factory)

    authn_policy = AuthTktAuthenticationPolicy(
        secret=settings['auth.secret'],
        callback=get_user_id,
        hashalg='sha512',
        timeout=86400,
        reissue_time=7200
    )
    authz_policy = ACLAuthorizationPolicy()
    config.set_authentication_policy(authn_policy)
    config.set_authorization_policy(authz_policy)
    config.set_root_factory(RootFactory)

    config.add_renderer('.jinja2', 'pyramid_jinja2.renderer_factory')
    config.include('pyramid_jinja2')
    config.add_jinja2_renderer('.html')

    config.include('.models')
    config.include('.routes')
    config.scan()

    return config.make_wsgi_app()
