const API_URL = "http://localhost:6543";

export function useSavedPosts() {
  const toggleSave = async (postId) => {
    const res = await fetch(`${API_URL}/posts/${postId}/save`, {
      method: "POST",
      credentials: "include",
    });
    return res.ok;
  };

  return { toggleSave };
}
