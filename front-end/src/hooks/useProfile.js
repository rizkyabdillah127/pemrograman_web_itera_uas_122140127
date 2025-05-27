// hooks/useProfile.js
import { useCallback } from "react";

const API_URL = "http://localhost:6543";

export function useProfile() {
  const getProfile = useCallback(async () => {
    const res = await fetch(`${API_URL}/me`, {
      credentials: "include",
    });
    return res.ok ? await res.json() : null;
  }, []);

  const updateProfile = async (payload) => {
    const res = await fetch(`${API_URL}/me`, {
      method: "PUT",
      headers: { "Content-Type": "application/json" },
      credentials: "include",
      body: JSON.stringify(payload),
    });
    return res.ok;
  };

  const deleteAccount = async () => {
    const res = await fetch(`${API_URL}/me`, {
      method: "DELETE",
      credentials: "include",
    });
    return res.ok;
  };

  return { getProfile, updateProfile, deleteAccount };
}
