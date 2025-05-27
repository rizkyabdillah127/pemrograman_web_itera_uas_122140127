import { useEffect, useState } from "react";
import DashboardLayout from "@/layouts/dashboard-layout";
import { usePosts } from "@/hooks/usePosts";
import { Loader2, Trash2, Pencil, ArrowRight } from "lucide-react";
import { toast } from "sonner";
import {
  AlertDialog,
  AlertDialogTrigger,
  AlertDialogContent,
  AlertDialogHeader,
  AlertDialogTitle,
  AlertDialogFooter,
  AlertDialogCancel,
  AlertDialogAction,
} from "@/components/ui/alert-dialog";
import { Button } from "@/components/ui/button";
import { Textarea } from "@/components/ui/textarea";
import { Link } from "react-router-dom";

export default function MyPostsPage() {
  const { getMyPosts, updatePost, deletePost } = usePosts();
  const [myPosts, setMyPosts] = useState([]);
  const [loading, setLoading] = useState(true);
  const [editData, setEditData] = useState(null);
  const [editValue, setEditValue] = useState("");

  useEffect(() => {
    const fetchMyPosts = async () => {
      setLoading(true);
      const posts = await getMyPosts();
      if (Array.isArray(posts)) setMyPosts(posts);
      setLoading(false);
    };
    fetchMyPosts();
  }, [getMyPosts]);

  const handleEdit = async () => {
    const success = await updatePost(editData.id, editValue);
    if (success) {
      toast.success("Postingan berhasil diperbarui");
      setMyPosts((prev) =>
        prev.map((p) =>
          p.id === editData.id ? { ...p, content: editValue } : p
        )
      );
    } else {
      toast.error("Gagal memperbarui postingan");
    }
    setEditData(null);
  };

  const handleDelete = async (id) => {
    const success = await deletePost(id);
    if (success) {
      toast.success("Postingan berhasil dihapus");
      setMyPosts((prev) => prev.filter((p) => p.id !== id));
    } else {
      toast.error("Gagal menghapus postingan");
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

  return (
    <DashboardLayout>
      <div className="p-6 space-y-6">
        <h1 className="text-2xl font-bold text-gray-800">
          Kelola Postingan Saya
        </h1>

        {loading ? (
          <div className="flex justify-center items-center text-gray-600">
            <Loader2 className="animate-spin w-5 h-5 mr-2" />
            Memuat postingan...
          </div>
        ) : myPosts.length === 0 ? (
          <p className="text-gray-500 text-sm">
            Belum ada postingan yang dibuat.
          </p>
        ) : (
          <ul className="space-y-4">
            {myPosts.map((post) => (
              <li
                key={post.id}
                className="relative rounded-xl bg-transparent border border-gray-200/50 hover:border-gray-300 transition overflow-hidden"
              >
                <div className="absolute inset-0 z-0 pointer-events-none bg-[url('https://grainy-gradients.vercel.app/noise.svg')] opacity-5" />

                <div className="relative z-10 p-5 space-y-2">
                  <h3 className="font-semibold text-gray-800">
                    {post.content}
                  </h3>
                  <p className="text-sm text-gray-500">
                    Dibuat pada {formatToJakartaTime(post.createdAt)}
                  </p>
                  <div className="flex gap-4 text-sm mt-1 text-gray-600">
                    <div>{post.likesCount} suka</div>
                    <div>{post.commentsCount} komentar</div>
                  </div>

                  <div className="my-4">
                    <Link
                      to={`/post/${post.id}`}
                      className="text-sm text-primary hover:underline flex items-center gap-1"
                    >
                      Lihat detail postingan <ArrowRight className="w-4 h-4" />
                    </Link>
                  </div>

                  <div className="flex gap-3 mt-3">
                    {/* 🔧 Edit */}
                    <AlertDialog open={editData?.id === post.id}>
                      <AlertDialogTrigger asChild>
                        <Button
                          variant="ghost"
                          onClick={() => {
                            setEditData({ id: post.id });
                            setEditValue(post.content);
                          }}
                        >
                          <Pencil className="w-4 h-4 mr-1" />
                          Edit
                        </Button>
                      </AlertDialogTrigger>
                      <AlertDialogContent>
                        <AlertDialogHeader>
                          <AlertDialogTitle>Edit Postingan</AlertDialogTitle>
                        </AlertDialogHeader>
                        <Textarea
                          value={editValue}
                          onChange={(e) => setEditValue(e.target.value)}
                          rows={5}
                        />
                        <AlertDialogFooter>
                          <AlertDialogCancel onClick={() => setEditData(null)}>
                            Batal
                          </AlertDialogCancel>
                          <AlertDialogAction onClick={handleEdit}>
                            Simpan
                          </AlertDialogAction>
                        </AlertDialogFooter>
                      </AlertDialogContent>
                    </AlertDialog>

                    {/* 🗑️ Delete */}
                    <AlertDialog>
                      <AlertDialogTrigger asChild>
                        <Button variant="ghost">
                          <Trash2 className="w-4 h-4 mr-1" />
                          Hapus
                        </Button>
                      </AlertDialogTrigger>
                      <AlertDialogContent>
                        <AlertDialogHeader>
                          <AlertDialogTitle>
                            Yakin ingin menghapus postingan ini?
                          </AlertDialogTitle>
                        </AlertDialogHeader>
                        <AlertDialogFooter>
                          <AlertDialogCancel>Batal</AlertDialogCancel>
                          <AlertDialogAction
                            onClick={() => handleDelete(post.id)}
                          >
                            Hapus
                          </AlertDialogAction>
                        </AlertDialogFooter>
                      </AlertDialogContent>
                    </AlertDialog>
                  </div>
                </div>
              </li>
            ))}
          </ul>
        )}
      </div>
    </DashboardLayout>
  );
}
