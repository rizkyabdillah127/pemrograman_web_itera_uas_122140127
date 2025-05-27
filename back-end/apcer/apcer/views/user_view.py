from pyramid.view import view_config
from pyramid.response import Response
from pyramid.httpexceptions import HTTPBadRequest
from ..models.user import User
import json

def json_response(data, status=200):
    return Response(
        body=json.dumps(data, default=str),
        content_type='application/json; charset=utf-8',
        status=status
    )

@view_config(route_name='auth.me', renderer='json', permission='view')
def me_view(request):
    """
    Mendukung GET, PUT, DELETE untuk profil user yang sedang login.
    """
    user_id = request.authenticated_userid
    if not user_id:
        return json_response({'success': False, 'message': 'Unauthorized'}, status=401)

    dbsession = request.dbsession
    user = dbsession.query(User).filter_by(id=user_id).first()
    if not user:
        return json_response({'success': False, 'message': 'User not found'}, status=404)

    # Handle GET
    if request.method == 'GET':
        return json_response({
            'success': True,
            'user': {
                'id': user.id,
                'email': user.email,
                'username': user.username,
                'created_at': user.created_at.isoformat(),
                'last_login_at': user.last_login_at.isoformat() if user.last_login_at else None
            }
        })

    # Handle PUT (Update)
    elif request.method == 'PUT':
        try:
            payload = request.json_body
        except Exception:
            return json_response({'success': False, 'message': 'Invalid JSON'}, status=400)

        username = payload.get('username')
        email = payload.get('email')

        if not username or not email:
            return json_response({'success': False, 'message': 'Username and email are required'}, status=400)

        # Optional: validasi email/username tidak duplikat dari user lain
        duplicate_user = dbsession.query(User).filter(
            User.id != user.id,
            (User.email == email) | (User.username == username)
        ).first()
        if duplicate_user:
            return json_response({'success': False, 'message': 'Username atau email sudah digunakan'}, status=400)

        user.username = username
        user.email = email
        return json_response({'success': True, 'message': 'Profil berhasil diperbarui'})

    # Handle DELETE
    elif request.method == 'DELETE':
        dbsession.delete(user)
        return json_response({'success': True, 'message': 'Akun telah dihapus'})

    # Method tidak diizinkan
    return json_response({'success': False, 'message': 'Method not allowed'}, status=405)
