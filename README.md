## 📝 Praktikum UTS: Aplikasi Web Posting dengan Fitur Favorite & Search

### 👤 Identitas

- **Nama:** Rizky Abdillah
- **NIM:** 122140127
- **Mata Kuliah:** Pemrograman Web
- **Jenis Praktikum:** UTS

---

## 🎯 Tujuan UTS

- Membangun aplikasi React yang mampu menampilkan daftar postingan dari API `dummyjson.com/posts`
- Menyediakan fitur:
  - **Infinite scroll** pada beranda
  - **Detail post**
  - **Menambahkan ke favorit (localStorage)**
  - **Pencarian berdasarkan judul dan tag**
  - **Toast notifikasi**
  - **Routing dan navigasi**

---

## ✅ Pemenuhan Kriteria

### 1. **Menampilkan data dari API menggunakan `fetch` atau `useEffect`**

- ✅ Terpenuhi di file `useFetch.js`, digunakan di `Home.jsx`, `Search.jsx`, dan `PostDetail.jsx`.

  Contoh:

  ```js
  const { data, loading, error } = useFetch(
    `https://dummyjson.com/posts?limit=${LIMIT}&skip=${skip}`
  );
  ```

---

### 2. **Menggunakan `react-router-dom` dan membuat lebih dari 2 halaman**

- ✅ Terpenuhi di `App.jsx`, digunakan:
  - `/` → Home
  - `/post/:id` → Post Detail
  - `/favorite` → Favorit
  - `/search` → Search
  - `*` → Not Found

---

### 3. **Menggunakan Props antar komponen**

- ✅ Komponen `PostCard.jsx` menerima props dari parent (`Home`, `Search`, dll)

  Contoh:

  ```js
  <PostCard key={item.id} {...item} />
  ```

---

### 4. **Menggunakan `useState` dan `useEffect`**

- ✅ Digunakan di `Home.jsx`, `PostDetail.jsx`, dan hook `useFetch.js`.

  Contoh penggunaan:

  ```js
  const [post, setPost] = useState(null);
  useEffect(() => {
    fetch(`https://dummyjson.com/posts/${id}`);
  }, [id]);
  ```

---

### 5. **Menggunakan `localStorage` untuk menyimpan data favorit**

- ✅ Dikelola di `FavoriteContext.jsx`:

  - Load dari localStorage
  - Simpan setiap perubahan favorit

  Contoh:

  ```js
  useEffect(() => {
    localStorage.setItem("favorites", JSON.stringify(favorites));
  }, [favorites]);
  ```

---

### 6. **Menggunakan Context API**

- ✅ Digunakan 2 Context:
  - `FavoriteContext.jsx` → menyimpan & mengelola state favorit
  - `ToastContext.jsx` → menampilkan notifikasi toast global

---

### 7. **Menggunakan TailwindCSS**

- ✅ Terlihat dari class Tailwind seperti `bg-gray-200`, `rounded-xl`, `hover:underline`, dsb, digunakan di semua komponen UI.

---

### 8. **Menggunakan Event Handling (`onClick`, `onChange`, dll)**

- ✅ Contoh:
  - Toggle favorit: `onClick={handleToggleFavorite}`
  - Filter tag: `onClick={() => handleTagClick(tag)}`
  - Search input: `onChange={(e) => updateParams("search", e.target.value)}`

---

### 9. **Membuat Komponen Sendiri Minimal 2**

- ✅ Kamu membuat lebih dari 2:
  - `PostCard`
  - `Navbar`
  - `Footer`
  - `GlobalToast`
  - `PostCardSkeleton`

---

### 10. **Membuat Custom Hook**

- ✅ `hooks/useFetch.js` adalah custom hook untuk pengambilan data.

---

### 11. **Menggunakan fitur Conditional Rendering**

- ✅ Contoh di `FavoritePage`:
  ```js
  {
    favorites.length === 0 ? (
      <p className="text-center text-gray-500">Belum ada post favorit.</p>
    ) : (
      favorites.map((post) => <PostCard key={post.id} {...post} />)
    );
  }
  ```

---

### 12. **Menggunakan Form Input & Select**

- ✅ Di `Search.jsx`:
  - Input search: `<input type="text" ... />`
  - Tag filter: `<select>...</select>`

---

## 💡 Catatan Teknis Tambahan

- **Infinite Scroll** diterapkan di `Home.jsx` menggunakan `IntersectionObserver`.
- **Toast Notification** ditampilkan menggunakan `GlobalToast` dan Context.
- **Routing yang rapi** menggunakan `MainLayout` yang membungkus semua halaman.
- **Efek loading** menggunakan `PostCardSkeleton`.
- **Search dan Filter** sangat optimal dengan fitur kombinasi pencarian dan pagination.

---
# pemrograman_web_itera_uas_122140127
