import { Link, useParams } from "react-router-dom";
import { useEffect, useState } from "react";
import { Heart, Bookmark, Loader2, ArrowLeft } from "lucide-react";
import DashboardLayout from "@/layouts/dashboard-layout";
import { useComments } from "@/hooks/useComments";
import { usePosts } from "@/hooks/usePosts";
import { useReactions } from "@/hooks/useReactions";
import { useSavedPosts } from "@/hooks/useSavedPosts";
import { toast } from "sonner";
import clsx from "clsx";

export default function PostDetailPage() {
  const { id } = useParams();
  const { getPostDetail } = usePosts();
  const { addComment } = useComments();
  const { toggleReaction } = useReactions();
  const { toggleSave } = useSavedPosts();

  const [post, setPost] = useState(null);
  const [comments, setComments] = useState([]);
  const [loading, setLoading] = useState(true);
  const [newComment, setNewComment] = useState("");
  const [showCount, setShowCount] = useState(3);
  const [likesCount, setLikesCount] = useState(0);
  const [isLiked, setIsLiked] = useState(false);
  const [isSaved, setIsSaved] = useState(false);

  useEffect(() => {
    const fetchDetail = async () => {
      try {
        setLoading(true);
        const data = await getPostDetail(id);
        if (data?.id) {
          setPost(data);
          setComments(data.comments || []);
          setLikesCount(data.likes_count || 0);
          setIsLiked(data.is_liked_by_current_user || false);
          setIsSaved(data.is_saved_by_current_user || false);
        } else {
          toast.error("Gagal memuat detail postingan");
        }
      } catch (err) {
        toast.error("Terjadi kesalahan saat memuat detail");
      } finally {
        setLoading(false);
      }
    };

    fetchDetail();
  }, [id, getPostDetail]);

  const handleAddComment = async () => {
    if (!newComment.trim()) return;

    const comment = await addComment(id, newComment);
    if (comment) {
      setComments((prev) => [...prev, comment]);
      setNewComment("");
      toast.success("Komentar ditambahkan");
    } else {
      toast.error("Gagal menambahkan komentar");
    }
  };

  const handleLike = async () => {
    const success = await toggleReaction(id);
    if (success) {
      setIsLiked(!isLiked);
      setLikesCount((prev) => (isLiked ? prev - 1 : prev + 1));
    } else {
      toast.error("Gagal menyukai postingan");
    }
  };

  const handleSave = async () => {
    const success = await toggleSave(id);
    if (success) {
      setIsSaved(!isSaved);
    } else {
      toast.error("Gagal menyimpan postingan");
    }
  };

  const formatToJakartaTime = (dateString) => {
    const date = new Date(dateString);
    date.setTime(date.getTime() + 7 * 60 * 60 * 1000); // Tambah 7 jam untuk WIB
    return date.toLocaleString("id-ID", {
      weekday: "long",
      year: "numeric",
      month: "long",
      day: "numeric",
      hour: "2-digit",
      minute: "2-digit",
      hour12: false,
    });
  };

  const formatCommentTime = (dateString) => {
    const date = new Date(dateString);
    date.setTime(date.getTime() + 7 * 60 * 60 * 1000); // Tambah 7 jam untuk WIB
    return date.toLocaleString("id-ID", {
      weekday: "short",
      year: "numeric",
      month: "short",
      day: "numeric",
      hour: "2-digit",
      minute: "2-digit",
      hour12: false,
    });
  };

  if (loading) {
    return (
      <DashboardLayout>
        <div className="flex justify-center items-center py-10 text-gray-600">
          <Loader2 className="animate-spin w-5 h-5 mr-2" />
          Memuat detail...
        </div>
      </DashboardLayout>
    );
  }

  if (!post) {
    return (
      <DashboardLayout>
        <div className="text-center py-10 text-red-600">
          Postingan tidak ditemukan.
        </div>
      </DashboardLayout>
    );
  }

  return (
    <DashboardLayout>
      <div className="p-6 relative overflow-hidden">
        {/* Grainy Background */}
        <div className="absolute inset-0 z-0 bg-[url('https://grainy-gradients.vercel.app/noise.svg')] opacity-5 pointer-events-none" />

        <div className="relative z-10 space-y-6">
          {/* Back */}
          <Link
            to="/posts"
            className="inline-flex gap-2 items-center text-gray-600 hover:text-gray-800"
          >
            <ArrowLeft className="w-4 h-4" />
            <span>Kembali ke daftar postingan</span>
          </Link>

          {/* Post content */}
          <div className="space-y-2">
            <h2 className="text-xl font-bold text-gray-800">{post.content}</h2>
            <p className="text-sm text-gray-500">
              Dibuat oleh @{post.user.username} pada{" "}
              {formatToJakartaTime(post.created_at)}
            </p>
          </div>

          <div className="flex items-center gap-4 pt-2 text-sm text-gray-600">
            <button
              onClick={handleLike}
              className={clsx(
                "flex items-center gap-1 hover:text-rose-600 transition",
                isLiked && "text-rose-600"
              )}
            >
              <Heart className="w-4 h-4" />
              {likesCount}
            </button>

            <button
              onClick={handleSave}
              className={clsx(
                "ml-auto flex items-center gap-1 hover:text-blue-600 transition",
                isSaved && "text-blue-600"
              )}
            >
              <Bookmark className="w-4 h-4" />
              {isSaved ? "Saved" : "Save"}
            </button>
          </div>

          <hr className="border-gray-300" />

          {/* Comment section */}
          <section className="space-y-4">
            <h3 className="text-lg font-semibold text-gray-700">Komentar</h3>

            {comments.length === 0 && (
              <p className="text-gray-500 text-sm">Belum ada komentar.</p>
            )}

            {comments.slice(0, showCount).map((c) => (
              <div
                key={c.id}
                className="border-b border-gray-200 pb-2 text-sm text-gray-800"
              >
                <p className="font-semibold">@{c.user.username}</p>
                <p className="text-gray-600">{c.content}</p>
                <p className="text-xs text-muted-foreground">
                  {formatCommentTime(c.created_at)}
                </p>
              </div>
            ))}

            {comments.length > showCount && (
              <button
                onClick={() => setShowCount((prev) => prev + 3)}
                className="text-primary text-sm hover:underline"
              >
                Lihat komentar lainnya
              </button>
            )}

            <div className="pt-4">
              <textarea
                className="w-full px-3 py-2 border rounded-md focus:outline-none focus:ring"
                rows={3}
                placeholder="Tulis komentar..."
                value={newComment}
                onChange={(e) => setNewComment(e.target.value)}
              ></textarea>
              <button
                onClick={handleAddComment}
                className="mt-2 bg-primary text-white px-4 py-2 rounded hover:bg-primary/90"
              >
                Kirim
              </button>
            </div>
          </section>
        </div>
      </div>
    </DashboardLayout>
  );
}
