import argparse
import sys
import os
import random
import datetime
import string
import transaction # Pastikan ini diimpor

from pyramid.paster import bootstrap, setup_logging
from sqlalchemy.exc import OperationalError

# Import helper functions dari models/__init__.py
from ..models import get_engine, get_session_factory, get_tm_session
from ..models.meta import Base # Import Base untuk create_all()
from ..models.user import User
from ..models.post import Post
from ..models.reaction import Reaction
from ..models.saved_post import SavedPost
from ..models.comment import Comment


# Fungsi bantu untuk menghasilkan data acak (tidak berubah)
def generate_random_string(length=10):
    """Menghasilkan string acak."""
    characters = string.ascii_letters + string.digits
    return ''.join(random.choice(characters) for i in range(length))

def generate_random_paragraph(min_sentences=3, max_sentences=10):
    """Menghasilkan paragraf acak sederhana."""
    sentences = []
    for _ in range(random.randint(min_sentences, max_sentences)):
        words = []
        for __ in range(random.randint(5, 15)): # Jumlah kata per kalimat
            word = generate_random_string(random.randint(3, 8)).lower()
            words.append(word)
        sentence = ' '.join(words) + random.choice(['.', '!', '?'])
        sentences.append(sentence.capitalize())
    return ' '.join(sentences)

def generate_random_date_time(start_date, end_date):
    """Menghasilkan datetime acak antara dua tanggal."""
    time_between_dates = end_date - start_date
    random_seconds = random.randrange(int(time_between_dates.total_seconds()))
    return start_date + datetime.timedelta(seconds=random_seconds)


def setup_models(dbsession):
    """
    Menginisialisasi tabel-tabel database dan menambahkan data dummy.
    """
    # Base.metadata.create_all(dbsession.bind) tetap di sini sesuai instruksi sebelumnya
    print("Membuat semua tabel berdasarkan model...")
    Base.metadata.create_all(dbsession.bind)
    print("Tabel berhasil dibuat (atau sudah ada).")

    # --- Bagian Insert Data Mock Awal untuk Apcer (tidak berubah) ---
    print("\n--- Memeriksa dan Menambahkan Data Mock Apcer ---")

    # Tentukan rentang tanggal untuk data mock
    end_date = datetime.datetime.now()
    start_date_users = end_date - datetime.timedelta(days=365) # 1 tahun lalu
    start_date_posts = end_date - datetime.timedelta(days=180) # 6 bulan lalu
    start_date_reactions = end_date - datetime.timedelta(days=90) # 3 bulan lalu
    start_date_comments = end_date - datetime.timedelta(days=60) # 2 bulan lalu
    start_date_saved_posts = end_date - datetime.timedelta(days=30) # 1 bulan lalu

    # 1. Tambahkan Users Mock
    if dbsession.query(User).count() == 0:
        print("Menambahkan user mock...")
        mock_users = []
        for i in range(1, 11): # 10 user mock
            user = User(
                email=f"{generate_random_string(15)}@apcer.com", # Email anonim terenkripsi
                username=f"Anonim #{i}",
                created_at=generate_random_date_time(start_date_users, end_date)
            )
            user.set_password("password123") # Password sama untuk kemudahan testing
            mock_users.append(user)
        dbsession.add_all(mock_users)
        dbsession.flush() # Flush untuk mendapatkan ID user agar bisa digunakan di Post dll.
        print(f"Berhasil menambahkan {len(mock_users)} user mock.")
    else:
        print("Tabel 'users' sudah berisi data, melewati penambahan user mock.")

    # Ambil user yang sudah ada untuk relasi
    existing_users = dbsession.query(User).all()
    if not existing_users:
        print("Tidak ada user yang tersedia untuk membuat post, reaksi, atau komentar. Tambahkan user terlebih dahulu.")
        return # Keluar jika tidak ada user

    # 2. Tambahkan Posts Mock
    if dbsession.query(Post).count() == 0:
        print("Menambahkan post mock...")
        mock_posts = []
        for _ in range(30): # 30 post mock
            user = random.choice(existing_users)
            post = Post(
                user_id=user.id,
                content=generate_random_paragraph(),
                created_at=generate_random_date_time(start_date_posts, end_date)
            )
            mock_posts.append(post)
        dbsession.add_all(mock_posts)
        dbsession.flush() # Flush untuk mendapatkan ID post
        print(f"Berhasil menambahkan {len(mock_posts)} post mock.")
    else:
        print("Tabel 'posts' sudah berisi data, melewati penambahan post mock.")

    existing_posts = dbsession.query(Post).all()
    if not existing_posts:
        print("Tidak ada post yang tersedia untuk reaksi atau komentar. Tambahkan post terlebih dahulu.")
        return

    # 3. Tambahkan Reactions (Likes) Mock
    if dbsession.query(Reaction).count() == 0:
        print("Menambahkan reaksi mock...")
        mock_reactions = []
        reacted_pairs = set()

        for _ in range(50): # 50 reaksi mock
            user = random.choice(existing_users)
            post = random.choice(existing_posts)

            if (user.id, post.id) not in reacted_pairs:
                reaction = Reaction(
                    user_id=user.id,
                    post_id=post.id,
                    type='like',
                    created_at=generate_random_date_time(start_date_reactions, end_date)
                )
                mock_reactions.append(reaction)
                reacted_pairs.add((user.id, post.id))
        dbsession.add_all(mock_reactions)
        print(f"Berhasil menambahkan {len(mock_reactions)} reaksi mock.")
    else:
        print("Tabel 'reactions' sudah berisi data, melewati penambahan reaksi mock.")

    # 4. Tambahkan Comments Mock
    if dbsession.query(Comment).count() == 0:
        print("Menambahkan komentar mock...")
        mock_comments = []
        for _ in range(40): # 40 komentar mock
            user = random.choice(existing_users)
            post = random.choice(existing_posts)
            comment = Comment(
                user_id=user.id,
                post_id=post.id,
                content=generate_random_paragraph(min_sentences=1, max_sentences=3),
                created_at=generate_random_date_time(start_date_comments, end_date)
            )
            mock_comments.append(comment)
        dbsession.add_all(mock_comments)
        print(f"Berhasil menambahkan {len(mock_comments)} komentar mock.")
    else:
        print("Tabel 'comments' sudah berisi data, melewati penambahan komentar mock.")

    # 5. Tambahkan Saved Posts Mock
    if dbsession.query(SavedPost).count() == 0:
        print("Menambahkan saved posts mock...")
        mock_saved_posts = []
        saved_pairs = set()

        for _ in range(20): # 20 saved post mock
            user = random.choice(existing_users)
            post = random.choice(existing_posts)

            if (user.id, post.id) not in saved_pairs:
                saved_post = SavedPost(
                    user_id=user.id,
                    post_id=post.id,
                    saved_at=generate_random_date_time(start_date_saved_posts, end_date)
                )
                mock_saved_posts.append(saved_post)
                saved_pairs.add((user.id, post.id))
        dbsession.add_all(mock_saved_posts)
        print(f"Berhasil menambahkan {len(mock_saved_posts)} saved posts mock.")
    else:
        print("Tabel 'saved_posts' sudah berisi data, melewati penambahan saved posts mock.")


def parse_args(argv):
    parser = argparse.ArgumentParser(
        description='Script untuk menginisialisasi database aplikasi Apcer dan menambahkan data mock.',
        formatter_class=argparse.RawDescriptionHelpFormatter
    )
    parser.add_argument(
        'config_uri',
        help='File konfigurasi Pyramid, contoh: development.ini',
    )
    return parser.parse_args(argv[1:])


def main(argv=sys.argv):
    args = parse_args(argv)
    setup_logging(args.config_uri)
    env = bootstrap(args.config_uri)

    # Dapatkan settings dari env yang di-bootstrap
    settings = env['request'].registry.settings
    db_url = settings.get('sqlalchemy.url')
    if not db_url:
        print("Pengaturan 'sqlalchemy.url' tidak ditemukan di konfigurasi.", file=sys.stderr)
        sys.exit(1)

    # Dapatkan engine dari settings
    engine = get_engine(settings) # Menggunakan helper dari apcer.models

    # Dapatkan session factory dari engine
    session_factory = get_session_factory(engine) # Menggunakan helper dari apcer.models

    try:
        # Gunakan transaction.manager sebagai context manager untuk sesi
        with transaction.manager:
            # Dapatkan dbsession yang terikat dengan transaction manager
            dbsession = get_tm_session(session_factory, transaction.manager)

            # Panggil fungsi setup_models untuk membuat tabel dan mengisi data mock
            setup_models(dbsession)

            # transaction.commit() akan dipanggil otomatis saat keluar dari 'with transaction.manager'
            # jika tidak ada error. Namun, memanggilnya eksplisit juga bisa.
            # transaction.commit() # Ini redundan jika dalam with block, tapi tidak merusak.
            print("Inisialisasi database dan penambahan data mock selesai.")

    except OperationalError as e:
        print(f'''
Pyramid mengalami masalah saat menggunakan database SQL Anda. Masalah ini
mungkin disebabkan oleh salah satu hal berikut:

1. Server database Anda mungkin tidak berjalan. Pastikan server database
   yang dirujuk oleh pengaturan "sqlalchemy.url" di file "{os.path.basename(args.config_uri)}" Anda
   sedang berjalan.
2. Koneksi database mungkin tidak valid atau kredensial salah.

Detail Error: {e}
''', file=sys.stderr)
        sys.exit(1)
    except Exception as e:
        print(f"Terjadi kesalahan saat menginisialisasi database: {e}", file=sys.stderr)
        transaction.abort() # Abort transaksi pada error lainnya
        import traceback
        traceback.print_exc(file=sys.stderr)
        sys.exit(1)