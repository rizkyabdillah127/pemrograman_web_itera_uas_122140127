from pyramid.view import view_config
from pyramid.response import Response
from pyramid.httpexceptions import HTTPForbidden
from ..models.comment import Comment
from ..models.post import Post
import json

def json_response(data, status=200):
    return Response(
        body=json.dumps(data, default=str),
        content_type='application/json; charset=utf-8',
        status=status
    )

@view_config(route_name='posts.comments', request_method='POST', renderer='json', permission='comment')
def add_comment(request):
    post_id = request.matchdict['post_id']
    user_id = request.authenticated_userid
    content = request.params.get('content')

    if not user_id:
        return json_response({'success': False, 'message': 'Unauthorized'}, status=401)

    if not content:
        return json_response({'success': False, 'message': 'Isi komentar tidak boleh kosong'}, status=400)

    dbsession = request.dbsession

    # Cek apakah postingan ada
    post = dbsession.query(Post).filter_by(id=post_id).first()
    if not post:
        return json_response({'success': False, 'message': 'Postingan tidak ditemukan'}, status=404)

    new_comment = Comment(
        user_id=user_id,
        post_id=post_id,
        content=content
    )
    dbsession.add(new_comment)
    dbsession.flush()

    return json_response({
        'success': True,
        'comment': {
            'id': new_comment.id,
            'content': new_comment.content,
            'created_at': new_comment.created_at.isoformat(),
            'user': {
                'id': new_comment.user.id,
                'username': new_comment.user.username,
                'email': new_comment.user.email
            }
        }
    })
