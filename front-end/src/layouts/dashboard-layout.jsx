import { useLocation, Link, useNavigate } from "react-router-dom";
import {
  LayoutDashboard,
  FileText,
  UserCircle,
  Bookmark,
  LogOut,
} from "lucide-react";
import clsx from "clsx";
import { useEffect } from "react";
import { useAuth } from "@/hooks/useAuth";

// Navigasi utama
const navItems = [
  { label: "Postingan", path: "/posts", icon: FileText },
  { label: "Tersimpan", path: "/saved", icon: Bookmark },
  { label: "Profil", path: "/profile", icon: UserCircle },
  { label: "My Post", path: "/my-post", icon: FileText },
];

export default function DashboardLayout({ children }) {
  const location = useLocation();
  const navigate = useNavigate();
  const { checkSession, logout } = useAuth();

  useEffect(() => {
    const session = checkSession();
    if (!session.isValid) {
      navigate("/login");
    }
  }, [checkSession, navigate]);

  return (
    <div className="min-h-screen md:flex relative bg-gradient-to-br from-[#fdfbfb] to-[#ebedee] dark:from-gray-900 dark:to-gray-800">
      {/* Sidebar untuk tablet & desktop */}
      <aside className="hidden md:block md:w-64 md:py-6 md:px-4 md:backdrop-blur-lg md:bg-transparent">
        <div className="text-lg font-bold text-primary mb-8 px-2">Apcer</div>
        <nav className="space-y-2">
          {navItems.map(({ label, path, icon: Icon }) => {
            const isActive = location.pathname === path;
            return (
              <Link
                key={path}
                to={path}
                className={clsx(
                  "flex items-center gap-3 px-3 py-2 rounded-lg transition-colors",
                  isActive
                    ? "bg-primary/10 text-primary font-semibold"
                    : "text-muted-foreground hover:text-primary hover:bg-muted"
                )}
              >
                <Icon className="w-5 h-5" />
                {label}
              </Link>
            );
          })}
        </nav>

        {/* Tombol Logout */}
        <button
          onClick={logout}
          className="flex items-center gap-3 px-3 py-2 rounded-lg text-red-600 hover:bg-red-100 transition-colors mt-6"
        >
          <LogOut className="w-5 h-5" />
          Logout
        </button>
      </aside>

      {/* Konten Utama */}
      <main className="flex-1 pb-20">{children}</main>

      {/* Bottom Navigation untuk Mobile */}
      <nav className="fixed bottom-4 left-1/2 -translate-x-1/2 z-50 w-[95%] max-w-sm bg-white shadow-lg rounded-xl px-6 py-2 flex justify-around items-center border md:hidden">
        {navItems.map(({ label, path, icon: Icon }) => {
          const isActive = location.pathname === path;
          return (
            <Link
              key={path}
              to={path}
              className={clsx(
                "flex flex-col items-center text-xs",
                isActive
                  ? "text-primary font-medium"
                  : "text-muted-foreground hover:text-primary"
              )}
            >
              <Icon className="w-5 h-5 mb-0.5" />
              <span className="text-[11px]">{label}</span>
            </Link>
          );
        })}

        {/* Tombol Logout untuk Mobile */}
        <button
          onClick={logout}
          className="flex flex-col items-center text-xs text-red-600"
        >
          <LogOut className="w-5 h-5 mb-0.5" />
          <span className="text-[11px]">Logout</span>
        </button>
      </nav>
    </div>
  );
}
