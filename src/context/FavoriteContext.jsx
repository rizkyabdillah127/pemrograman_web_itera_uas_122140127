import { createContext, useContext, useEffect, useState } from "react";

const FavoriteContext = createContext();
export const useFavorite = () => useContext(FavoriteContext);

export const FavoriteProvider = ({ children }) => {
  const [favorites, setFavorites] = useState([]);
  const [loaded, setLoaded] = useState(false);

  useEffect(() => {
    const saved = localStorage.getItem("favorites");
    if (saved) {
      setFavorites(JSON.parse(saved));
    }
    setLoaded(true); // ⬅️ Tambahkan ini
  }, []);

  // ⏫ Load from localStorage saat awal
  useEffect(() => {
    const saved = localStorage.getItem("favorites");
    if (saved) {
      console.log("✅ Load from localStorage:", JSON.parse(saved));
      setFavorites(JSON.parse(saved));
    }
  }, []);

  // ⏬ Simpan ke localStorage setiap kali berubah
  useEffect(() => {
    console.log("💾 Save to localStorage:", favorites);
    localStorage.setItem("favorites", JSON.stringify(favorites));
  }, [favorites]);

  const addToFavorites = (post) => {
    setFavorites((prev) => [...prev, post]);
  };

  const removeFromFavorites = (id) => {
    setFavorites((prev) => prev.filter((post) => post.id !== id));
  };

  const isFavorited = (id) => {
    return favorites.some((post) => post.id === id);
  };

  return (
    <FavoriteContext.Provider
      value={{
        favorites,
        addToFavorites,
        removeFromFavorites,
        isFavorited,
        loaded, // ⬅️ Jangan lupa
      }}
    >
      {children}
    </FavoriteContext.Provider>
  );
};
