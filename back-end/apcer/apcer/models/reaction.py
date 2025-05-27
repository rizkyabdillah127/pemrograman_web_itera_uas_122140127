# models/reaction.py
from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, UniqueConstraint
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from .meta import Base # Sesuaikan import Base jika path berbeda

class Reaction(Base):
    __tablename__ = 'reactions'

    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey('users.id'), nullable=False)
    post_id = Column(Integer, ForeignKey('posts.id'), nullable=False)
    type = Column(String(20), default='like', nullable=False) # Bisa diperluas jika ada tipe reaksi lain
    created_at = Column(DateTime, server_default=func.now())

    # Pastikan satu user hanya bisa mereaksi satu postingan sekali
    __table_args__ = (UniqueConstraint('user_id', 'post_id', name='_user_post_uc'),)

    # Relasi: Reaksi dibuat oleh satu user, untuk satu postingan
    user = relationship('User', back_populates='reactions')
    post = relationship('Post', back_populates='reactions')

    def __repr__(self):
        return f"<Reaction(id={self.id}, user_id={self.user_id}, post_id={self.post_id}, type='{self.type}')>"