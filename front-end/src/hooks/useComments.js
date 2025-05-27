const API_URL = "http://localhost:6543";

export function useComments() {
  const addComment = async (postId, content) => {
    const form = new FormData();
    form.append("content", content);

    try {
      const res = await fetch(`${API_URL}/posts/${postId}/comments`, {
        method: "POST",
        credentials: "include",
        body: form,
      });

      const data = await res.json();

      if (res.ok && data.success) {
        return data.comment; // kembalikan komentar baru
      } else {
        console.error(data.message);
        return null;
      }
    } catch (err) {
      console.error("Gagal mengirim komentar:", err);
      return null;
    }
  };

  return { addComment };
}
