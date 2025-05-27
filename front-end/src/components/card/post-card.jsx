import PropTypes from "prop-types";
import { Heart, MessageCircle, Bookmark } from "lucide-react";
import clsx from "clsx";

export default function PostCard({
  id,
  username,
  createdAt,
  content,
  likesCount,
  commentsCount,
  isLiked,
  isSaved,
}) {
  // Buat objek Date dari string createdAt
  const dateFromBackend = new Date(createdAt);

  // Tambahkan 6 jam
  // getTime() mengembalikan milidetik sejak epoch
  // 6 * 60 * 60 * 1000 = 6 jam dalam milidetik
  dateFromBackend.setTime(dateFromBackend.getTime() + 7 * 60 * 60 * 1000);

  // Opsi format untuk menampilkan tanggal dan waktu
  const displayOptions = {
    weekday: "long",
    year: "numeric",
    month: "long",
    day: "numeric",
    hour: "2-digit",
    minute: "2-digit",
    hour12: false, // Gunakan format 24 jam
    // Penting: Jika Anda sudah menambahkan 6 jam secara manual,
    // maka sebaiknya JANGAN atur timeZone di sini.
    // Biarkan toLocaleString menggunakan zona waktu lokal browser
    // atau jika backend Anda memang mengirim UTC,
    // offset 6 jam ini akan "mengarahkan" ke WIB dari UTC.
    // Jika masih ada masalah, baru pertimbangkan timeZone lagi.
  };

  return (
    <div className="relative rounded-xl bg-transparent border border-gray-200/50 hover:border-gray-300 transition overflow-hidden">
      {/* Grain effect */}
      <div className="absolute inset-0 z-0 pointer-events-none bg-[url('https://grainy-gradients.vercel.app/noise.svg')] opacity-5" />

      {/* Content */}
      <div className="relative z-10 p-5 space-y-3">
        <div className="flex justify-between items-center">
          <h3 className="font-semibold text-gray-800">@{username}</h3>
          <span className="text-sm text-gray-500">
            {/* Tampilkan tanggal yang sudah ditambahkan 6 jam */}
            {dateFromBackend.toLocaleString("id-ID", displayOptions)}
          </span>
        </div>

        <p className="text-gray-700 text-sm whitespace-pre-line">{content}</p>

        <div className="flex items-center gap-4 pt-2 text-sm text-gray-600">
          {/* Liked status only */}
          <div
            className={clsx(
              "flex items-center gap-1",
              isLiked ? "text-rose-600" : "text-gray-600"
            )}
          >
            <Heart className="w-4 h-4" />
            {likesCount}
          </div>

          {/* Comments count */}
          <div className="flex items-center gap-1">
            <MessageCircle className="w-4 h-4" />
            {commentsCount}
          </div>

          {/* Saved status only */}
          <div
            className={clsx(
              "ml-auto flex items-center gap-1",
              isSaved ? "text-blue-600" : "text-gray-600"
            )}
          >
            <Bookmark className="w-4 h-4" />
            {isSaved ? "Saved" : "Save"}
          </div>
        </div>
      </div>
    </div>
  );
}

PostCard.propTypes = {
  id: PropTypes.number.isRequired,
  username: PropTypes.string.isRequired,
  createdAt: PropTypes.string.isRequired,
  content: PropTypes.string.isRequired,
  likesCount: PropTypes.number.isRequired,
  commentsCount: PropTypes.number.isRequired,
  isLiked: PropTypes.bool,
  isSaved: PropTypes.bool,
};
