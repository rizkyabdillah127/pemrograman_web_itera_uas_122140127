def includeme(config):
    # Static view
    config.add_static_view('static', 'static', cache_max_age=3600)
    config.add_route('home', '/')  # Beranda utama

    # -------------------------
    # 🔐 AUTH ROUTES
    # -------------------------
    config.add_route('register', '/register')
    config.add_route('login', '/login')
    config.add_route('logout', '/logout')
    config.add_route('auth.me', '/me')  # GET, PUT, DELETE profil pengguna

    # -------------------------
    # 📄 POST ROUTES
    # -------------------------
    config.add_route('posts.list', '/posts')                    # GET all posts
    config.add_route('posts.create', '/posts/create')           # POST create post
    config.add_route('posts.detail', '/posts/{id:\d+}')         # GET detail post
    config.add_route('posts.mine', '/posts/mine')               # ✅ GET posts milik user (baru)
    
    # -------------------------
    # ✏ UPDATE / DELETE POST
    # -------------------------
    config.add_route('posts.edit', '/posts/{id:\d+}/edit')       # PUT
    config.add_route('posts.delete', '/posts/{id:\d+}/delete')   # DELETE

    # -------------------------
    # ❤ REACTIONS & SAVED POSTS
    # -------------------------
    config.add_route('posts.react', '/posts/{post_id:\d+}/react')  # POST toggle like
    config.add_route('posts.save', '/posts/{post_id:\d+}/save')    # POST toggle save

    # -------------------------
    # 💬 COMMENTS
    # -------------------------
    config.add_route('posts.comments', '/posts/{post_id:\d+}/comments')  # POST add comment