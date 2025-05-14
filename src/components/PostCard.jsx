import PropTypes from "prop-types";
import { Link, useNavigate } from "react-router-dom";
import { useFavorite } from "../context/FavoriteContext";
import { useToast } from "../context/ToastContext";
import { useCallback } from "react";

const PostCard = ({ id, title, body, tags, reactions, views }) => {
  const { addToFavorites, removeFromFavorites, isFavorited } = useFavorite();
  const { showToast } = useToast();
  const navigate = useNavigate();

  const isFav = isFavorited(id);

  const handleToggleFavorite = useCallback(() => {
    const post = { id, title, body, tags, reactions, views };

    if (isFav) {
      removeFromFavorites(id);
      showToast("❌ Dihapus dari favorit");
    } else {
      addToFavorites(post);
      showToast("❤️ Ditambahkan ke favorit");
    }
  }, [
    isFav,
    id,
    title,
    body,
    tags,
    reactions,
    views,
    removeFromFavorites,
    addToFavorites,
    showToast,
  ]);

  const handleTagClick = (tag) => {
    navigate(`/search?tag=${encodeURIComponent(tag)}`);
  };

  return (
    <div className="border border-gray-200 rounded-2xl p-6 shadow-sm bg-[#f8f8f8] relative hover:shadow-md transition">
      <h2 className="text-xl font-semibold text-primary mb-2">{title}</h2>
      <p className="mb-3 text-gray-700 text-sm leading-relaxed line-clamp-3">
        {body}
      </p>

      {/* Tags */}
      <div className="flex flex-wrap gap-2 text-sm mt-2">
        {tags.map((tag) => (
          <button
            key={tag}
            onClick={() => handleTagClick(tag)}
            className="btn-primary cursor-pointer px-3 py-1 rounded-full text-xs hover:opacity-90 transition"
          >
            #{tag}
          </button>
        ))}
      </div>

      {/* Reactions */}
      <div className="text-sm text-gray-500 mt-3 space-x-4">
        <span>👍 {reactions.likes}</span>
        <span>👎 {reactions.dislikes}</span>
        <span>👁️ {views}</span>
      </div>

      {/* Actions */}
      <div className="mt-5 flex justify-between items-center">
        <Link
          to={`/post/${id}`}
          className="text-sm text-primary hover:underline transition"
        >
          Lihat Detail →
        </Link>

        <button
          onClick={handleToggleFavorite}
          className={`text-sm px-3 py-1 rounded-full transition cursor-pointer ${
            isFav
              ? "bg-red-100 text-red-500 hover:bg-red-200"
              : "bg-gray-100 text-gray-600 hover:bg-gray-200"
          }`}
        >
          {isFav ? "❤️ Favorit" : "🤍 Tambah"}
        </button>
      </div>
    </div>
  );
};

PostCard.propTypes = {
  id: PropTypes.number.isRequired,
  title: PropTypes.string.isRequired,
  body: PropTypes.string.isRequired,
  tags: PropTypes.array.isRequired,
  reactions: PropTypes.shape({
    likes: PropTypes.number,
    dislikes: PropTypes.number,
  }),
  views: PropTypes.number,
};

export default PostCard;
