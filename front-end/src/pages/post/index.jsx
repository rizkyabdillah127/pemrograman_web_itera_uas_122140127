import { useEffect, useRef, useState, useCallback } from "react";
import { usePosts } from "@/hooks/usePosts";
import PostCard from "@/components/card/post-card";
import { Loader2, Plus } from "lucide-react";
import DashboardLayout from "@/layouts/dashboard-layout";
import {
  AlertDialog,
  AlertDialogContent,
  AlertDialogHeader,
  AlertDialogFooter,
  AlertDialogTitle,
  AlertDialogCancel,
} from "@/components/ui/alert-dialog";
import { Button } from "@/components/ui/button";
import { Textarea } from "@/components/ui/textarea";
import { toast } from "sonner";
import { Link } from "react-router-dom";

export default function PostListPage() {
  const { getAllPosts, createPost } = usePosts();
  const [posts, setPosts] = useState([]);
  const [visibleCount, setVisibleCount] = useState(6);
  const [loading, setLoading] = useState(true);
  const [hasMore, setHasMore] = useState(true);
  const [open, setOpen] = useState(false);
  const [newContent, setNewContent] = useState("");
  const observerRef = useRef();

  const fetchPosts = useCallback(async () => {
    setLoading(true);
    const all = await getAllPosts();
    const sorted = Array.isArray(all)
      ? [...all].sort((a, b) => new Date(b.created_at) - new Date(a.created_at))
      : [];
    setPosts(sorted);
    setHasMore(sorted.length > visibleCount);
    setLoading(false);
  }, [getAllPosts, visibleCount]);

  useEffect(() => {
    fetchPosts();
  }, [fetchPosts]);

  const loadMore = () => {
    setVisibleCount((prev) => prev + 6);
  };

  const lastPostRef = useCallback(
    (node) => {
      if (loading) return;
      if (observerRef.current) observerRef.current.disconnect();

      observerRef.current = new IntersectionObserver((entries) => {
        if (entries[0].isIntersecting && hasMore) {
          loadMore();
        }
      });

      if (node) observerRef.current.observe(node);
    },
    [loading, hasMore]
  );

  const handleCreatePost = async () => {
    if (!newContent.trim()) {
      toast.error("Isi postingan tidak boleh kosong");
      return;
    }

    const success = await createPost(newContent);
    if (success) {
      toast.success("Postingan berhasil dibuat");
      setOpen(false);
      setNewContent("");
      fetchPosts(); // refresh data
    } else {
      toast.error("Gagal membuat postingan");
    }
  };

  const visiblePosts = posts.slice(0, visibleCount);

  return (
    <DashboardLayout>
      <div className="p-6 space-y-8">
        <div className="flex items-center justify-between">
          <h1 className="text-2xl font-bold text-gray-800">Explore Posts</h1>
          <Button onClick={() => setOpen(true)} className="gap-1">
            <Plus className="w-4 h-4" />
            Buat Postingan
          </Button>
        </div>

        {visiblePosts.map((post, index) => {
          const isLast = index === visiblePosts.length - 1;
          return (
            <Link
              key={post.id}
              ref={isLast ? lastPostRef : null}
              to={`/post/${post.id}`}
            >
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
          );
        })}

        {loading && (
          <div className="flex justify-center items-center mt-4 text-gray-600">
            <Loader2 className="w-5 h-5 animate-spin" />
            <span className="ml-2">Loading...</span>
          </div>
        )}

        {!loading && !hasMore && posts.length > 0 && (
          <p className="text-center text-sm text-gray-500">No more posts.</p>
        )}
      </div>

      {/* Alert Dialog untuk Form Posting */}
      <AlertDialog open={open} onOpenChange={setOpen}>
        <AlertDialogContent className="max-w-lg">
          <AlertDialogHeader>
            <AlertDialogTitle>Buat Postingan Baru</AlertDialogTitle>
          </AlertDialogHeader>
          <Textarea
            placeholder="Tulis sesuatu..."
            className="min-h-[120px]"
            value={newContent}
            onChange={(e) => setNewContent(e.target.value)}
          />
          <AlertDialogFooter className="mt-4">
            <AlertDialogCancel>Batal</AlertDialogCancel>
            <Button onClick={handleCreatePost}>Kirim</Button>
          </AlertDialogFooter>
        </AlertDialogContent>
      </AlertDialog>
    </DashboardLayout>
  );
}
