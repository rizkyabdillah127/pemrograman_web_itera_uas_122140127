# views/reaction_views.py
from pyramid.view import view_config
from pyramid.httpexceptions import HTTPFound, HTTPForbidden
from pyramid.security import Authenticated
from sqlalchemy.exc import IntegrityError
from ..models.reaction import Reaction
from ..models.saved_post import SavedPost
from ..models.post import Post

@view_config(route_name='posts.react', request_method='POST', permission='react')
def react_post(request):
    """
    Menangani reaksi (like/unlike) pada postingan.
    """
    post_id = request.matchdict['post_id']
    user_id = request.authenticated_userid

    if not user_id:
        request.session.flash('Anda harus login untuk memberikan reaksi.', queue='error')
        return HTTPForbidden()

    dbsession = request.dbsession
    
    # Cek apakah post ada DAN tidak dihapus
    post = dbsession.query(Post).filter_by(id=post_id).first()
    # MODIFIKASI: Menambahkan kondisi post.is_deleted
    if not post or post.is_deleted:
        request.session.flash('Postingan tidak ditemukan.', queue='error')
        return HTTPFound(location=request.route_url('home'))

    existing_reaction = dbsession.query(Reaction).filter_by(
        user_id=user_id, post_id=post_id, type='like'
    ).first()

    if existing_reaction:
        dbsession.delete(existing_reaction)
        request.session.flash('Anda batal menyukai postingan ini.', queue='info')
    else:
        new_reaction = Reaction(
            user_id=user_id,
            post_id=post_id,
            type='like'
        )
        dbsession.add(new_reaction)
        request.session.flash('Anda menyukai postingan ini!', queue='info')

    return HTTPFound(location=request.route_url('posts.detail', id=post_id))

@view_config(route_name='posts.save', request_method='POST', permission='react')
def save_post(request):
    """
    Menangani menyimpan/menghapus postingan dari daftar simpanan user.
    """
    post_id = request.matchdict['post_id']
    user_id = request.authenticated_userid

    if not user_id:
        request.session.flash('Anda harus login untuk menyimpan postingan.', queue='error')
        return HTTPForbidden()

    dbsession = request.dbsession

    # Cek apakah post ada DAN tidak dihapus
    post = dbsession.query(Post).filter_by(id=post_id).first()
    # MODIFIKASI: Menambahkan kondisi post.is_deleted
    if not post or post.is_deleted:
        request.session.flash('Postingan tidak ditemukan.', queue='error')
        return HTTPFound(location=request.route_url('home'))

    existing_saved = dbsession.query(SavedPost).filter_by(
        user_id=user_id, post_id=post_id
    ).first()

    if existing_saved:
        dbsession.delete(existing_saved)
        request.session.flash('Anda menghapus postingan dari daftar simpanan.', queue='info')
    else:
        new_saved = SavedPost(
            user_id=user_id,
            post_id=post_id
        )
        dbsession.add(new_saved)
        request.session.flash('Anda menyimpan postingan ini!', queue='info')
    
    return HTTPFound(location=request.route_url('posts.detail', id=post_id))