# views/auth.py
from pyramid.view import view_config
from pyramid.security import remember, forget, NO_PERMISSION_REQUIRED
from pyramid.httpexceptions import HTTPUnauthorized
from ..models.user import User
import uuid
import random
import string

def generate_random_string(length=12):
    characters = string.ascii_letters + string.digits + string.punctuation
    return ''.join(random.choice(characters) for _ in range(length))


@view_config(route_name='register', renderer='json', request_method='POST', permission=NO_PERMISSION_REQUIRED)
def api_register(request):
    dbsession = request.dbsession

    anon_email = f"{uuid.uuid4()}@apcer.com"
    next_user_number = dbsession.query(User).count() + 1
    username = f"Anonim #{next_user_number}"
    raw_password = generate_random_string(12)

    # Cek unik email/username
    if dbsession.query(User).filter_by(email=anon_email).first() or dbsession.query(User).filter_by(username=username).first():
        request.response.status = 400
        return {'success': False, 'message': 'Registrasi gagal. Email atau username sudah digunakan.'}

    new_user = User(email=anon_email, username=username)
    new_user.set_password(raw_password)
    dbsession.add(new_user)
    dbsession.flush()

    headers = remember(request, new_user.id)
    request.response.headerlist.extend(headers)

    return {
        'success': True,
        'message': 'Registrasi berhasil.',
        'email': anon_email,
        'password': raw_password,
        'user': {
            'id': new_user.id,
            'username': new_user.username
        }
    }


@view_config(route_name='login', renderer='json', request_method='POST', permission=NO_PERMISSION_REQUIRED)
def api_login(request):
    dbsession = request.dbsession
    try:
        data = request.json_body
        login_email = data.get('email')
        login_password = data.get('password')
    except Exception:
        request.response.status = 400
        return {'success': False, 'message': 'Permintaan tidak valid'}

    user = dbsession.query(User).filter_by(email=login_email).first()

    if user and user.check_password(login_password):
        headers = remember(request, user.id)
        request.response.headerlist.extend(headers)
        return {
            'success': True,
            'message': 'Login berhasil',
            'user': {
                'id': user.id,
                'username': user.username,
                'email': user.email
            }
        }
    else:
        request.response.status = 401
        return {'success': False, 'message': 'Email atau password salah'}


@view_config(route_name='logout', renderer='json', request_method='POST', permission=NO_PERMISSION_REQUIRED)
def api_logout(request):
    headers = forget(request)
    request.response.headerlist.extend(headers)
    return {'success': True, 'message': 'Logout berhasil'}
