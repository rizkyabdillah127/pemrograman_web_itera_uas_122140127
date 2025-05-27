import { useEffect, useState } from "react";
import { useProfile } from "@/hooks/useProfile";
import DashboardLayout from "@/layouts/dashboard-layout";
import ProfileForm from "@/components/form/ProfileForm";
import { Loader2 } from "lucide-react";
import { toast } from "sonner";
import DeleteAccountDialog from "@/components/dialog/DeleteAccountDialog";

export default function ProfilePage() {
  const { getProfile, updateProfile, deleteAccount } = useProfile();
  const [profile, setProfile] = useState(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const fetchProfile = async () => {
      try {
        setLoading(true);
        const data = await getProfile();
        if (data?.success) {
          setProfile(data.user);
        } else {
          toast.error("Gagal memuat profil");
        }
      } catch (err) {
        toast.error("Terjadi kesalahan saat mengambil data profil.");
      } finally {
        setLoading(false);
      }
    };

    fetchProfile();
  }, [getProfile]);

  const handleSubmit = async (formData) => {
    const success = await updateProfile(formData);
    if (success) {
      toast.success("Profil berhasil diperbarui");
      setProfile({ ...profile, ...formData });
    } else {
      toast.error("Gagal memperbarui profil");
    }
  };

  const handleDelete = async () => {
    const success = await deleteAccount();
    if (success) {
      toast.success("Akun berhasil dihapus");
      setTimeout(() => {
        window.location.href = "/login";
      }, 1000);
    } else {
      toast.error("Gagal menghapus akun");
    }
  };

  if (loading) {
    return (
      <DashboardLayout>
        <div className="flex justify-center items-center py-10 text-gray-600">
          <Loader2 className="animate-spin w-5 h-5 mr-2" />
          Memuat profil...
        </div>
      </DashboardLayout>
    );
  }

  if (!profile) {
    return (
      <DashboardLayout>
        <div className="text-center py-10 text-red-600">
          Gagal memuat data profil.
        </div>
      </DashboardLayout>
    );
  }

  return (
    <DashboardLayout>
      <div className="p-6 space-y-8">
        <h1 className="text-2xl font-bold mb-4 text-gray-800">Profil Saya</h1>

        <ProfileForm initialData={profile} onSubmit={handleSubmit} />

        <DeleteAccountDialog onConfirm={handleDelete} />
      </div>
    </DashboardLayout>
  );
}
