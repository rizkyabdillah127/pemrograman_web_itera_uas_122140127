# security.py
from pyramid.authentication import AuthTktAuthenticationPolicy
from pyramid.authorization import ACLAuthorizationPolicy
from pyramid.security import Allow, Authenticated, Everyone, Deny, NO_PERMISSION_REQUIRED

# Fungsi untuk mendapatkan principal ID (biasanya user ID)
# Ini akan dipanggil oleh authentication policy
def get_user_id(userid, request):
    # userid yang dikirim adalah ID user yang disimpan di token/cookie
    # Di sini Anda bisa mengambil user dari database jika perlu
    # Untuk contoh ini, kita asumsikan userid adalah user.id yang sudah ada.
    return [f'user:{userid}']

# Fungsi untuk menentukan roles/permissions
# Ini akan dipanggil oleh authorization policy
class RootFactory:
    __acl__ = [
        # Semua orang (termasuk yang tidak login) bisa melihat post
        (Allow, Everyone, 'view'),
        (Allow, Authenticated, 'create'), # User login bisa buat post
        (Allow, Authenticated, 'react'),  # User login bisa like/save
        (Allow, Authenticated, 'comment'), # User login bisa comment

        # User yang adalah pemilik resource (post/comment) bisa edit/delete
        # (Allow, 'user:owner_id', 'edit'), # Contoh: jika Anda ingin cek pemilik
        # (Allow, 'user:owner_id', 'delete'), # Contoh: jika Anda ingin cek pemilik
    ]

    def __init__(self, request):
        self.request = request

# Konfigurasi di __init__.py aplikasi Pyramid Anda:
# config.set_authentication_policy(
#     AuthTktAuthenticationPolicy(
#         secret='supersecret', # Ganti dengan string acak yang kuat
#         callback=get_user_id,
#         hashalg='sha512',
#         timeout=86400, # Cookie berlaku 24 jam
#         reissue_time=7200 # Perbarui cookie setiap 2 jam jika aktif
#     )
# )
# config.set_authorization_policy(ACLAuthorizationPolicy())
# config.set_default_permission(NO_PERMISSION_REQUIRED) # Defaultnya tidak ada permission yang dibutuhkan
# config.set_root_factory(RootFactory)