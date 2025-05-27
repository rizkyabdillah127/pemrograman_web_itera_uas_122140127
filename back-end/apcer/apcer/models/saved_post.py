# models/saved_post.py
from sqlalchemy import Column, Integer, DateTime, ForeignKey, UniqueConstraint
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from .meta import Base # Sesuaikan import Base jika path berbeda

class SavedPost(Base):
    __tablename__ = 'saved_posts'

    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey('users.id'), nullable=False)
    post_id = Column(Integer, ForeignKey('posts.id'), nullable=False)
    saved_at = Column(DateTime, server_default=func.now())

    # Pastikan satu user hanya bisa menyimpan satu postingan sekali
    __table_args__ = (UniqueConstraint('user_id', 'post_id', name='_user_saved_post_uc'),)

    # Relasi: SavedPost dibuat oleh satu user, untuk satu postingan
    user = relationship('User', back_populates='saved_posts')
    post = relationship('Post', back_populates='saved_by')

    def __repr__(self):
        return f"<SavedPost(id={self.id}, user_id={self.user_id}, post_id={self.post_id})>"