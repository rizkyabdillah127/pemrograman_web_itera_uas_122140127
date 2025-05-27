from pyramid.view import view_config
from pyramid.response import Response
from pyramid.httpexceptions import HTTPNotFound
from sqlalchemy.orm import joinedload
from ..models.user import User
from ..models.post import Post
from ..models.reaction import Reaction
from ..models.comment import Comment
from ..models.saved_post import SavedPost
import json

def json_response(data, status=200):
    return Response(
        body=json.dumps(data, default=str),
        content_type='application/json; charset=utf-8',
        status=status
    )


@view_config(route_name='posts.list', renderer='json', request_method='GET', permission='view')
def list_posts(request):
    dbsession = request.dbsession
    posts = dbsession.query(Post).options(joinedload(Post.user)) \
        .filter(Post.is_deleted == False).order_by(Post.created_at.desc()).all()

    current_user_id = request.authenticated_userid
    results = []

    for post in posts:
        likes = dbsession.query(Reaction).filter_by(post_id=post.id, type='like').count()
        comments = dbsession.query(Comment).filter_by(post_id=post.id, is_deleted=False).count()

        is_liked = False
        is_saved = False
        if current_user_id:
            is_liked = dbsession.query(Reaction).filter_by(
                user_id=current_user_id, post_id=post.id, type='like'
            ).first() is not None
            is_saved = dbsession.query(SavedPost).filter_by(
                user_id=current_user_id, post_id=post.id
            ).first() is not None

        results.append({
            "id": post.id,
            "username": post.user.username,
            "createdAt": post.created_at.isoformat(),
            "content": post.content,
            "likesCount": likes,
            "commentsCount": comments,
            "isLiked": is_liked,
            "isSaved": is_saved,
        })
        
    return json_response(results)


@view_config(route_name='posts.create', renderer='json', request_method='POST', permission='create')
def create_post(request):
    content = request.params.get('content')
    if not content:
        return json_response({'success': False, 'message': 'Konten tidak boleh kosong'}, status=400)

    dbsession = request.dbsession
    new_post = Post(
        user_id=request.authenticated_userid,
        content=content
    )
    dbsession.add(new_post)
    dbsession.flush()

    return json_response({'success': True, 'message': 'Post created', 'post_id': new_post.id})


@view_config(route_name='posts.detail', renderer='json', request_method='GET', permission='view')
def post_detail(request):
    post_id = request.matchdict.get('id')
    dbsession = request.dbsession

    post = dbsession.query(Post).options(joinedload(Post.user)) \
        .filter_by(id=post_id, is_deleted=False).first()

    if not post:
        return json_response({'success': False, 'message': 'Postingan tidak ditemukan'}, status=404)

    comments = dbsession.query(Comment).options(joinedload(Comment.user)) \
        .filter_by(post_id=post.id, is_deleted=False).order_by(Comment.created_at.asc()).all()

    post_likes = dbsession.query(Reaction).filter_by(post_id=post.id, type='like').count()

    current_user_id = request.authenticated_userid
    is_liked = is_saved = False
    if current_user_id:
        is_liked = dbsession.query(Reaction).filter_by(
            user_id=current_user_id, post_id=post.id, type='like'
        ).first() is not None
        is_saved = dbsession.query(SavedPost).filter_by(
            user_id=current_user_id, post_id=post.id
        ).first() is not None

    return json_response({
        'id': post.id,
        'content': post.content,
        'created_at': post.created_at.isoformat(),
        'user': {
            'id': post.user.id,
            'username': post.user.username,  # ✅ GANTI DARI 'name' KE 'username'
            'email': post.user.email
        },
        'likes_count': post_likes,
        'is_liked_by_current_user': is_liked,
        'is_saved_by_current_user': is_saved,
        'comments': [{
            'id': c.id,
            'content': c.content,
            'created_at': c.created_at.isoformat(),
            'user': {
                'id': c.user.id,
                'username': c.user.username,  # ✅ GANTI DARI 'name' KE 'username'
                'email': c.user.email
            }
        } for c in comments]
    })

@view_config(route_name='posts.mine', renderer='json', request_method='GET', permission='view')
def my_posts(request):
    user_id = request.authenticated_userid
    if not user_id: 
        return json_response({'success': False, 'message': 'Unauthorized'}, status=401)

    dbsession = request.dbsession
    posts = dbsession.query(Post).filter_by(user_id=user_id, is_deleted=False).order_by(Post.created_at.desc()).all()

    results = []
    for post in posts:
        likes = dbsession.query(Reaction).filter_by(post_id=post.id, type='like').count()
        comments = dbsession.query(Comment).filter_by(post_id=post.id, is_deleted=False).count()

        results.append({
            "id": post.id,
            "content": post.content,
            "createdAt": post.created_at.isoformat(),
            "likesCount": likes,
            "commentsCount": comments,
        })

    return json_response(results)


@view_config(route_name='posts.edit', renderer='json', request_method='PUT')
def edit_post(request):
    post_id = request.matchdict.get('id')
    user_id = request.authenticated_userid
    dbsession = request.dbsession

    post = dbsession.query(Post).filter_by(id=post_id, is_deleted=False).first()
    if not post:
        return json_response({'success': False, 'message': 'Post tidak ditemukan'}, status=404)

    if post.user_id != user_id:
        return json_response({'success': False, 'message': 'Akses ditolak'}, status=403)

    try:
        body = request.json_body
        content = body.get('content')
        if not content:
            return json_response({'success': False, 'message': 'Konten tidak boleh kosong'}, status=400)
        
        post.content = content
        dbsession.flush()
        return json_response({'success': True, 'message': 'Post berhasil diperbarui'})
    except Exception as e:
        return json_response({'success': False, 'message': f'Kesalahan: {str(e)}'}, status=500)


@view_config(route_name='posts.delete', renderer='json', request_method='DELETE')
def delete_post(request):
    post_id = request.matchdict.get('id')
    user_id = request.authenticated_userid
    dbsession = request.dbsession

    post = dbsession.query(Post).filter_by(id=post_id, is_deleted=False).first()
    if not post:
        return json_response({'success': False, 'message': 'Post tidak ditemukan'}, status=404)

    if post.user_id != user_id:
        return json_response({'success': False, 'message': 'Akses ditolak'}, status=403)

    post.is_deleted = True
    dbsession.flush()

    return json_response({'success': True, 'message': 'Post berhasil dihapus'})
