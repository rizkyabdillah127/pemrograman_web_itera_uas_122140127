// src/pages/SavedPostsPage.jsx
import { useEffect, useState } from "react";
import { usePosts } from "@/hooks/usePosts";
import DashboardLayout from "@/layouts/dashboard-layout";
import PostCard from "@/components/card/post-card";
import { Loader2 } from "lucide-react";
import { Link } from "react-router-dom";

export default function SavedPostsPage() {
  const { getAllPosts } = usePosts();
  const [posts, setPosts] = useState([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const fetchSaved = async () => {
      setLoading(true);
      const all = await getAllPosts();
      const filtered = all.filter((p) => p.isSaved);
      setPosts(filtered);
      setLoading(false);
    };
    fetchSaved();
  }, [getAllPosts]);

  return (
    <DashboardLayout>
      <div className="p-6 space-y-6">
        <h1 className="text-2xl font-bold text-gray-800">
          Postingan Tersimpan
        </h1>

        {loading ? (
          <div className="flex justify-center items-center mt-4 text-gray-600">
            <Loader2 className="w-5 h-5 animate-spin" />
            <span className="ml-2">Memuat...</span>
          </div>
        ) : posts.length === 0 ? (
          <p className="text-sm text-gray-500">
            Belum ada postingan yang disimpan.
          </p>
        ) : (
          posts.map((post) => (
            <Link key={post.id} to={`/post/${post.id}`}>
              <PostCard
                username={post.username || "unknown"}
                createdAt={post.createdAt}
                content={post.content}
                likesCount={post.likesCount}
                commentsCount={post.commentsCount}
                isLiked={post.isLiked}
                isSaved={post.isSaved}
              />
            </Link>
          ))
        )}
      </div>
    </DashboardLayout>
  );
}
