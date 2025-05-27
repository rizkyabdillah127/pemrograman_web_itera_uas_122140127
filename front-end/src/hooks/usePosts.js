// ✅ hooks/usePosts.js
import { useCallback } from "react";

const API_URL = "http://localhost:6543";

export function usePosts() {
  const getAllPosts = useCallback(async () => {
    const res = await fetch(`${API_URL}/posts`, {
      credentials: "include",
    });
    return res.ok ? await res.json() : [];
  }, []);

  const getPostDetail = useCallback(async (id) => {
    const res = await fetch(`${API_URL}/posts/${id}`, {
      credentials: "include",
    });
    return res.ok ? await res.json() : null;
  }, []);

  const createPost = useCallback(async (content) => {
    const form = new FormData();
    form.append("content", content);
    const res = await fetch(`${API_URL}/posts/create`, {
      method: "POST",
      credentials: "include",
      body: form,
    });
    return res.ok;
  }, []);

  const getMyPosts = useCallback(async () => {
    const res = await fetch(`${API_URL}/posts/mine`, {
      credentials: "include",
    });
    return res.ok ? await res.json() : [];
  }, []);

  const updatePost = useCallback(async (id, content) => {
    const res = await fetch(`${API_URL}/posts/${id}/edit`, {
      method: "PUT",
      headers: { "Content-Type": "application/json" },
      credentials: "include",
      body: JSON.stringify({ content }),
    });

    const data = await res.json();
    return res.ok && data.success;
  }, []);

  const deletePost = useCallback(async (id) => {
    const res = await fetch(`${API_URL}/posts/${id}/delete`, {
      method: "DELETE",
      credentials: "include",
    });

    const data = await res.json();
    return res.ok && data.success;
  }, []);

  return {
    getAllPosts,
    getPostDetail,
    createPost,
    getMyPosts,
    updatePost,
    deletePost,
  };
}
