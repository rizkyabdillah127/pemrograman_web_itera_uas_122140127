from pyramid.view import notfound_view_config
from pyramid.view import HTTPNotFound

@notfound_view_config(renderer='../templates/404.jinja2')
def notfound_view(request):
    request.response.status = 404
    return {}
