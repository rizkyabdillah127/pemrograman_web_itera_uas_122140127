# models/user.py
from sqlalchemy import Column, Integer, String, DateTime
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
import bcrypt
from .meta import Base

class User(Base):
    __tablename__ = 'users'

    id = Column(Integer, primary_key=True)
    email = Column(String(255), unique=True, nullable=False)
    password_hash = Column(String(255), nullable=False) # Akan menyimpan hash bcrypt
    username = Column(String(50), unique=True, nullable=False)
    created_at = Column(DateTime, server_default=func.now())
    last_login_at = Column(DateTime)

    # Relasi: Satu user bisa punya banyak postingan, reaksi, simpanan, komentar
    posts = relationship('Post', back_populates='user', lazy=True)
    reactions = relationship('Reaction', back_populates='user', lazy=True)
    saved_posts = relationship('SavedPost', back_populates='user', lazy=True)
    comments = relationship('Comment', back_populates='user', lazy=True)

    def __repr__(self):
        return f"<User(id={self.id}, username='{self.username}', email='{self.email}')>"

    # Best Practice: Metode untuk hashing dan verifikasi password menggunakan bcrypt
    def set_password(self, password):
        # bcrypt.hashpw membutuhkan input bytes, jadi encode password
        hashed_password = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt())
        self.password_hash = hashed_password.decode('utf-8') # Simpan sebagai string

    def check_password(self, password):
        # bcrypt.checkpw juga membutuhkan input bytes untuk password dan hash
        # Pastikan password_hash di-encode kembali ke bytes
        return bcrypt.checkpw(password.encode('utf-8'), self.password_hash.encode('utf-8'))