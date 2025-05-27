# APCER - Apa Cerita

APCER adalah sebuah aplikasi web yang memungkinkan pengguna untuk berbagi cerita atau postingan secara anonim. Pengguna dapat berinteraksi dengan postingan, seperti memberi reaksi (like), menyimpan postingan, dan memberikan komentar. Aplikasi ini berfokus pada kemudahan berbagi tanpa beban identitas.

## Overview Aplikasi

Aplikasi APCER dibangun dengan arsitektur *monorepo* yang memisahkan *front-end* dan *back-end*.
* **Front-end**: Dibangun menggunakan React.js dengan Vite.js sebagai *build tool*, dan styling menggunakan Tailwind CSS dengan komponen dari Shadcn UI. Pengelolaan *state* dan *fetch* data dilakukan melalui *custom hooks*.
* **Back-end**: Dibangun menggunakan *framework* Pyramid (Python) dengan SQLAlchemy sebagai ORM untuk interaksi database. Database yang digunakan adalah PostgreSQL.

## Fitur-fitur Utama

Berikut adalah fitur-fitur utama yang tersedia dalam aplikasi APCER:

### Autentikasi
* **Registrasi Anonim**: Pengguna dapat mendaftar tanpa perlu memberikan informasi pribadi yang sensitif. Sistem akan secara otomatis menghasilkan username "Anonim #[number]" dan email unik, serta password untuk pengguna.
* **Login**: Pengguna dapat masuk menggunakan email dan password yang diberikan saat registrasi.
* **Logout**: Pengguna dapat keluar dari akun mereka.
* **Profil Saya**: Pengguna dapat melihat dan memperbarui username serta email mereka. Mereka juga dapat menghapus akun secara permanen.

### Postingan
* **Melihat Semua Postingan**: Pengguna dapat melihat daftar semua postingan yang tersedia, diurutkan berdasarkan waktu pembuatan terbaru.
* **Melihat Detail Postingan**: Pengguna dapat melihat detail lengkap dari suatu postingan, termasuk konten, informasi pembuat, jumlah like, status like dan tersimpan oleh pengguna saat ini, serta daftar komentar.
* **Membuat Postingan**: Pengguna yang terautentikasi dapat membuat postingan baru dengan konten teks.
* **Postingan Saya**: Pengguna dapat melihat daftar postingan yang mereka buat sendiri.
* **Mengedit Postingan**: Pemilik postingan dapat mengedit konten postingan mereka.
* **Menghapus Postingan**: Pemilik postingan dapat menghapus (soft delete) postingan mereka.

### Interaksi Postingan
* **Reaksi (Like)**: Pengguna dapat memberikan "like" pada postingan. Jika sudah di-like, aksi yang sama akan menghapus like tersebut (toggle).
* **Menyimpan Postingan**: Pengguna dapat menyimpan postingan ke daftar mereka. Jika sudah tersimpan, aksi yang sama akan menghapus dari daftar simpanan (toggle).
* **Komentar**: Pengguna dapat menambahkan komentar pada postingan.

## Struktur Tabel Database

Aplikasi ini menggunakan beberapa tabel utama untuk menyimpan data, yang didefinisikan sebagai model SQLAlchemy:

### `users`
* `id` (Integer, Primary Key)
* `email` (String, Unique, Not Null): Email unik untuk identifikasi, terutama untuk akun anonim yang dihasilkan otomatis.
* `password_hash` (String, Not Null): Hash password menggunakan bcrypt.
* `username` (String, Unique, Not Null): Username pengguna, dihasilkan otomatis untuk akun anonim.
* `created_at` (DateTime): Waktu pembuatan akun.
* `last_login_at` (DateTime): Waktu terakhir pengguna login.

### `posts`
* `id` (Integer, Primary Key)
* `user_id` (Integer, Foreign Key ke `users.id`, Not Null): Pengguna yang membuat postingan.
* `content` (Text, Not Null): Isi teks dari postingan.
* `created_at` (DateTime): Waktu postingan dibuat.
* `updated_at` (DateTime): Waktu terakhir postingan diperbarui (otomatis).
* `is_deleted` (Boolean, Default False, Not Null): Flag untuk *soft delete* postingan.

### `reactions`
* `id` (Integer, Primary Key)
* `user_id` (Integer, Foreign Key ke `users.id`, Not Null): Pengguna yang memberikan reaksi.
* `post_id` (Integer, Foreign Key ke `posts.id`, Not Null): Postingan yang diberi reaksi.
* `type` (String, Default 'like', Not Null): Tipe reaksi (saat ini hanya 'like').
* `created_at` (DateTime): Waktu reaksi diberikan.
* `UniqueConstraint` (`user_id`, `post_id`): Memastikan satu pengguna hanya dapat memberikan satu reaksi pada satu postingan.

### `saved_posts`
* `id` (Integer, Primary Key)
* `user_id` (Integer, Foreign Key ke `users.id`, Not Null): Pengguna yang menyimpan postingan.
* `post_id` (Integer, Foreign Key ke `posts.id`, Not Null): Postingan yang disimpan.
* `saved_at` (DateTime): Waktu postingan disimpan.
* `UniqueConstraint` (`user_id`, `post_id`): Memastikan satu pengguna hanya dapat menyimpan satu postingan sekali.

### `comments`
* `id` (Integer, Primary Key)
* `post_id` (Integer, Foreign Key ke `posts.id`, Not Null): Postingan tempat komentar dibuat.
* `user_id` (Integer, Foreign Key ke `users.id`, Not Null): Pengguna yang membuat komentar.
* `content` (Text, Not Null): Isi teks dari komentar.
* `created_at` (DateTime): Waktu komentar dibuat.
* `updated_at` (DateTime): Waktu terakhir komentar diperbarui (otomatis).
* `is_deleted` (Boolean, Default False, Not Null): Flag untuk *soft delete* komentar.

## Struktur Folder

Aplikasi ini dibagi menjadi dua bagian utama: `front-end` dan `back-end`, masing-masing dengan struktur foldernya sendiri.

### Struktur Folder `back-end`
```
back-end/
├── apcer/                      # Proyek Pyramid utama
│   ├── alembic/                # Direktori untuk migrasi database Alembic
│   │   ├── versions/           # Skrip migrasi database
│   ├── apcer/                  # Source code aplikasi Pyramid
│   │   ├── models/             # Definisi model SQLAlchemy (User, Post, Comment, Reaction, SavedPost)
│   │   ├── scripts/            # Skrip utilitas, seperti initialize_db.py untuk mengisi data dummy
│   │   ├── views/              # Logika handler untuk setiap endpoint API (auth, post, comment, reaction, user)
│   │   ├── init.py             # Konfigurasi aplikasi Pyramid, termasuk rute, otentikasi, dan CORS
│   │   ├── routes.py           # Definisi rute URL untuk setiap endpoint API
│   │   ├── security.py         # Kebijakan otentikasi dan otorisasi
│   │   ├── cors.py             # Middleware CORS untuk menangani permintaan lintas asal
│   │   └── tests.py            # Unit dan integrasi test untuk backend
│   ├── development.ini         # File konfigurasi untuk lingkungan pengembangan
│   ├── production.ini          # File konfigurasi untuk lingkungan produksi
│   ├── setup.py                # File setup instalasi Python package
│   └── ...                     # File dan direktori lain (seperti static, templates, pytest.ini, dsb.)
```

### Struktur Folder `front-end`
```
front-end/
├── public/                     # Aset statis seperti favicon, dll.
├── src/
│   ├── assets/                 # Aset seperti gambar, ikon, dll.
│   ├── components/             # Komponen React yang dapat digunakan kembali
│   │   ├── ui/                 # Komponen UI dari Shadcn UI (button, input, dialog, dll.)
│   │   ├── card/               # Komponen spesifik seperti PostCard
│   │   ├── dialog/             # Komponen dialog kustom seperti DeleteAccountDialog
│   │   └── ...                 # Komponen lain seperti Navbar, Footer, ProfileForm, ApcerHero
│   ├── hooks/                  # Custom React Hooks untuk logika bisnis dan fetching data (useAuth, usePosts, useComments, dll.)
│   ├── layouts/                # Layout halaman (AuthLayout, DashboardLayout, MainLayout)
│   ├── lib/                    # Fungsi utilitas (misal: cn untuk Tailwind CSS)
│   ├── pages/                  # Halaman utama aplikasi (Login, Register, Posts, Profile, Saved, MyPost, NotFound, PostDetail)
│   ├── App.jsx                 # Komponen root aplikasi React
│   ├── main.jsx                # Entry point utama aplikasi React (render root component dan setup React Router)
│   └── index.css               # File CSS global (Tailwind CSS imports dan custom styles)
├── index.html                  # File HTML utama
├── package.json                # Metadata proyek dan daftar dependensi npm
├── vite.config.js              # Konfigurasi Vite (alias path, plugin React & Tailwind)
└── ...                         # File dan direktori lain (seperti jsconfig.json, eslint.config.js, README.md)
```

## Endpoint API (Back-end)

Berikut adalah daftar *endpoint* API yang disediakan oleh *back-end* Pyramid:

### Auth & User
* `POST /register`: Registrasi pengguna anonim.
* `POST /login`: Login pengguna.
* `POST /logout`: Logout pengguna.
* `GET /me`: Mendapatkan detail profil pengguna yang sedang login.
* `PUT /me`: Memperbarui profil pengguna yang sedang login.
* `DELETE /me`: Menghapus akun pengguna yang sedang login.

### Posts
* `GET /posts`: Mendapatkan daftar semua postingan (termasuk status `isLiked` dan `isSaved` jika pengguna terautentikasi).
* `POST /posts/create`: Membuat postingan baru.
* `GET /posts/{id}`: Mendapatkan detail postingan spesifik berdasarkan ID.
* `GET /posts/mine`: Mendapatkan daftar postingan yang dibuat oleh pengguna yang sedang login.
* `PUT /posts/{id}/edit`: Mengedit postingan berdasarkan ID.
* `DELETE /posts/{id}/delete`: Menghapus (soft delete) postingan berdasarkan ID.

### Interactions
* `POST /posts/{post_id}/react`: Mengubah status like pada postingan.
* `POST /posts/{post_id}/save`: Mengubah status simpan pada postingan.
* `POST /posts/{post_id}/comments`: Menambahkan komentar pada postingan.

## Cara Menjalankan Aplikasi

Pastikan Anda memiliki Python 3, `pip`, `npm` (atau `yarn`), dan PostgreSQL terinstal di sistem Anda.

### 1. Setup Backend

1.  **Navigasi ke Direktori Backend**:
    ```bash
    cd back-end/apcer
    ```

2.  **Buat Virtual Environment**:
    ```bash
    python3 -m venv env
    ```

3.  **Aktifkan Virtual Environment**:
    * **Linux/macOS**:
        ```bash
        source env/bin/activate
        ```
    * **Windows (Command Prompt)**:
        ```bash
        env\Scripts\activate.bat
        ```
    * **Windows (PowerShell)**:
        ```bash
        .\env\Scripts\Activate.ps1
        ```

4.  **Install Dependencies**:
    ```bash
    pip install --upgrade pip setuptools
    pip install -e ".[testing]"
    ```

5.  **Konfigurasi Database (PostgreSQL)**:
    Pastikan server PostgreSQL Anda berjalan. Edit `development.ini` untuk mengatur koneksi database Anda. Secara *default*, file tersebut menggunakan:
    ```ini
    sqlalchemy.url = postgresql+psycopg2://apcer-user:apcer-password@localhost:5432/postgres
    ```
    Anda mungkin perlu membuat *user* dan *database* `apcer-user` dan `postgres` di PostgreSQL, atau ubah *string* koneksi sesuai konfigurasi Anda.

6.  **Migrasi Database dengan Alembic**:
    ```bash
    env/bin/alembic -c development.ini revision --autogenerate -m "init"
    env/bin/alembic -c development.ini upgrade head
    ```

7.  **Isi Data Dummy (Opsional, untuk pengembangan)**:
    ```bash
    env/bin/initialize_apcer_db development.ini
    ```

8.  **Jalankan Server Backend**:
    ```bash
    env/bin/pserve development.ini
    ```
    Server *backend* akan berjalan di `http://localhost:6543`.

### 2. Setup Frontend

1.  **Navigasi ke Direktori Frontend**:
    ```bash
    cd front-end
    ```

2.  **Install Dependencies**:
    ```bash
    npm install
    ```

3.  **Jalankan Aplikasi Frontend**:
    ```bash
    npm run dev
    ```
    Aplikasi *front-end* akan berjalan di `http://localhost:5173`.

### 3. Mengakses Aplikasi

Setelah kedua server berjalan, Anda dapat mengakses aplikasi melalui *browser* Anda di `http://localhost:5173`.
