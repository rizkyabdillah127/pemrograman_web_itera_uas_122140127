# models/post.py
from sqlalchemy import Column, Integer, Text, DateTime, ForeignKey, Boolean
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from .meta import Base # Sesuaikan import Base jika path berbeda

class Post(Base):
    __tablename__ = 'posts'

    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey('users.id'), nullable=False)
    content = Column(Text, nullable=False)
    created_at = Column(DateTime, server_default=func.now())
    updated_at = Column(DateTime, onupdate=func.now()) # Otomatis update saat record diubah
    is_deleted = Column(Boolean, default=False, nullable=False)

    # Relasi: Postingan dimiliki oleh satu user
    user = relationship('User', back_populates='posts')

    # Relasi: Satu postingan bisa punya banyak reaksi, simpanan, komentar
    reactions = relationship('Reaction', back_populates='post', lazy=True)
    saved_by = relationship('SavedPost', back_populates='post', lazy=True)
    comments = relationship('Comment', back_populates='post', lazy=True)


    def __repr__(self):
        return f"<Post(id={self.id}, user_id={self.user_id}, created_at='{self.created_at.strftime('%Y-%m-%d')}')>"