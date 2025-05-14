import { useFavorite } from "../context/FavoriteContext";
import PostCard from "../components/PostCard";

const FavoritePage = () => {
  const { favorites } = useFavorite();

  return (
    <div className="max-w-3xl mx-auto p-4 space-y-6">
      <h1 className="text-3xl font-bold text-center mb-6">Post Favorit ❤️</h1>

      {favorites.length === 0 ? (
        <p className="text-center text-gray-500">Belum ada post favorit.</p>
      ) : (
        favorites.map((post) => <PostCard key={post.id} {...post} />)
      )}
    </div>
  );
};

export default FavoritePage;
