import { useParams, useNavigate } from "react-router-dom";
import { useEffect, useState } from "react";

const PostDetail = () => {
  const { id } = useParams();
  const navigate = useNavigate();
  const [post, setPost] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  useEffect(() => {
    fetch(`https://dummyjson.com/posts/${id}`)
      .then((res) => {
        if (!res.ok) throw new Error("Post tidak ditemukan");
        return res.json();
      })
      .then((data) => {
        setPost(data);
        setLoading(false);
      })
      .catch((err) => {
        setError(err.message);
        setLoading(false);
      });
  }, [id]);

  if (loading) {
    return (
      <div className="max-w-3xl mx-auto p-6 animate-pulse space-y-4">
        <div className="h-8 bg-gray-200 rounded w-2/3"></div>
        <div className="space-y-2">
          <div className="h-4 bg-gray-200 rounded w-full"></div>
          <div className="h-4 bg-gray-200 rounded w-5/6"></div>
          <div className="h-4 bg-gray-200 rounded w-4/6"></div>
        </div>
        <div className="flex gap-2 mt-4">
          <div className="h-6 w-20 bg-gray-200 rounded-full"></div>
          <div className="h-6 w-20 bg-gray-200 rounded-full"></div>
        </div>
      </div>
    );
  }

  if (error) {
    return <p className="text-center text-red-500 mt-6">{error}</p>;
  }

  return (
    <div className="max-w-3xl mx-auto p-6 space-y-4">
      <h1 className="text-3xl font-bold text-primary">{post.title}</h1>
      <p className="text-gray-700 text-sm leading-relaxed">{post.body}</p>

      {/* Tags */}
      <div className="flex flex-wrap gap-2 text-sm mt-2">
        {post.tags.map((tag) => (
          <button
            key={tag}
            onClick={() => handleTagClick(tag)}
            className="bg-primary text-white cursor-pointer px-3 py-1 rounded-full text-xs hover:opacity-90 transition"
          >
            #{tag}
          </button>
        ))}
      </div>

      <div className="text-sm text-gray-500 space-x-4">
        <span>👍 {post.reactions.likes}</span>
        <span>👎 {post.reactions.dislikes}</span>
        <span>👁️ {post.views} views</span>
      </div>

      <button
        onClick={() => navigate("/")}
        className="mt-6 px-4 py-2 rounded btn-primary mx-auto w-full cursor-pointer"
      >
        ← Kembali ke Beranda
      </button>
    </div>
  );
};

export default PostDetail;
