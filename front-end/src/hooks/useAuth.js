import { useCallback, useState } from "react";
import Cookies from "js-cookie";

const API_URL = "http://localhost:6543";

export function useAuth() {
  const [user, setUser] = useState(() => {
    const cookieUser = Cookies.get("user");
    return cookieUser ? JSON.parse(cookieUser) : null;
  });

  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);

  // 🔐 Login
  const login = async (email, password) => {
    setLoading(true);
    setError(null);

    try {
      const res = await fetch(`${API_URL}/login`, {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        credentials: "include",
        body: JSON.stringify({ email, password }),
      });

      const data = await res.json();

      if (!res.ok || !data.success) {
        setError(data.message || "Login failed");
        setLoading(false);
        return false;
      }

      setUser(data.user);
      Cookies.set("user", JSON.stringify(data.user));
      setLoading(false);
      window.location.href = "/posts";
      return true;
    } catch (err) {
      setError("An unexpected error occurred.");
      setLoading(false);
      return false;
    }
  };

  // ✍️ Register Anonim
  const register = async () => {
    setLoading(true);
    setError(null);

    try {
      const res = await fetch(`${API_URL}/register`, {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        credentials: "include",
      });

      const data = await res.json();

      if (!res.ok || !data.success) {
        setError(data.message || "Registration failed");
        setLoading(false);
        return { success: false };
      }

      setUser(data.user);
      Cookies.set("user", JSON.stringify(data.user));
      setLoading(false);
      return { success: true, email: data.email, password: data.password };
    } catch (err) {
      setError("An unexpected error occurred.");
      setLoading(false);
      return { success: false };
    }
  };

  // 🚪 Logout
  const logout = async () => {
    await fetch(`${API_URL}/logout`, {
      method: "POST",
      credentials: "include",
    });

    setUser(null);
    Cookies.remove("auth_tkt");
    Cookies.remove("user");
    window.location.href = "/login";
  };

  // 🔎 Check Session: mengecek cookies `auth_tkt` dan `user`
  const checkSession = useCallback(() => {
    const authToken = Cookies.get("auth_tkt");
    const userCookie = Cookies.get("user");

    const isValid = !!authToken && !!userCookie;
    return {
      isValid,
      user: isValid ? JSON.parse(userCookie) : null,
    };
  }, []);

  return {
    user,
    loading,
    error,
    login,
    register,
    logout,
    isAuthenticated: !!user,
    checkSession,
  };
}
