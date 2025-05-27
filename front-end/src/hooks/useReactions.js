const API_URL = "http://localhost:6543";

export function useReactions() {
  const toggleReaction = async (postId) => {
    const res = await fetch(`${API_URL}/posts/${postId}/react`, {
      method: "POST",
      credentials: "include",
    });
    return res.ok;
  };

  return { toggleReaction };
}
