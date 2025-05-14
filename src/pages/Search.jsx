import { useSearchParams } from "react-router-dom";
import useFetch from "../hooks/useFetch";
import PostCard from "../components/PostCard";
import PostCardSkeleton from "../components/PostCardSkeleton";
import { useMemo } from "react";

const LIMIT = 10;

const Search = () => {
  const [searchParams, setSearchParams] = useSearchParams();

  const page = parseInt(searchParams.get("page")) || 1;
  const search = searchParams.get("search") || "";
  const selectedTag = searchParams.get("tag") || "";

  const { data, loading, error } = useFetch(
    `https://dummyjson.com/posts?limit=150`
  );

  const posts = data?.posts || [];

  const allTags = useMemo(() => {
    return [...new Set(posts.flatMap((p) => p.tags))];
  }, [posts]);

  const filtered = useMemo(() => {
    return posts.filter((post) => {
      const matchSearch = post.title
        .toLowerCase()
        .includes(search.toLowerCase());
      const matchTag = selectedTag ? post.tags.includes(selectedTag) : true;
      return matchSearch && matchTag;
    });
  }, [posts, search, selectedTag]);

  const totalPages = Math.ceil(filtered.length / LIMIT);
  const start = (page - 1) * LIMIT;
  const end = start + LIMIT;
  const paginated = filtered.slice(start, end);

  const updateParams = (key, value) => {
    const params = new URLSearchParams(searchParams);
    params.set(key, value);
    if (key !== "page") params.set("page", 1);
    setSearchParams(params);
  };

  const resetFilter = () => {
    setSearchParams({ page: 1 });
  };

  return (
    <div className="max-w-3xl mx-auto p-4 space-y-6">
      <h1 className="text-3xl font-bold text-center mb-4 text-primary">
        Pencarian Post 🔍
      </h1>

      {/* Search & Filter */}
      <div className="flex flex-col sm:flex-row gap-4 mb-2">
        <input
          type="text"
          placeholder="Cari berdasarkan judul..."
          className="flex-1 border px-3 py-2 rounded-xl shadow-sm bg-white text-black"
          value={search}
          onChange={(e) => updateParams("search", e.target.value)}
        />
        <select
          className="border px-3 py-2 rounded-xl shadow-sm bg-white text-black"
          value={selectedTag}
          onChange={(e) => updateParams("tag", e.target.value)}
        >
          <option value="">Semua Tag</option>

          {allTags.map((tag) => (
            <option key={tag} value={tag}>
              #{tag}
            </option>
          ))}
        </select>
      </div>

      {/* Reset Filter */}
      {(search || selectedTag) && (
        <button
          onClick={resetFilter}
          className="text-sm bg-[#121212] rounded-2xl text-white px-4 py-2 hover:bg-[#1f1f1f] transition"
        >
          Reset Filter ❌
        </button>
      )}

      {/* Loader & Error */}
      {loading && (
        <div className="space-y-4">
          {[...Array(3)].map((_, i) => (
            <PostCardSkeleton key={i} />
          ))}
        </div>
      )}

      {error && <div className="text-center text-red-500">{error}</div>}

      {/* List */}
      {!loading && paginated.length === 0 && (
        <p className="text-center text-gray-500">Tidak ada hasil.</p>
      )}

      {paginated.map((item) => (
        <PostCard key={item.id} {...item} />
      ))}

      {/* Pagination */}
      {!loading && totalPages > 1 && (
        <div className="flex justify-center gap-2 flex-wrap mt-6">
          <button
            onClick={() => updateParams("page", page - 1)}
            disabled={page === 1}
            className="px-3 py-1 rounded btn-primary border bg-[#121212] text-white hover:bg-[#1f1f1f] disabled:opacity-40"
          >
            Prev
          </button>

          {Array.from({ length: totalPages }, (_, i) => i + 1).map((num) => (
            <button
              key={num}
              onClick={() => updateParams("page", num)}
              className={`px-3 py-1 rounded border ${
                num === page
                  ? "bg-[#121212] text-white btn-primary"
                  : "bg-white text-black hover:bg-gray-100"
              }`}
            >
              {num}
            </button>
          ))}

          <button
            onClick={() => updateParams("page", page + 1)}
            disabled={page === totalPages}
            className="px-3 py-1 rounded border btn-primary bg-[#121212] text-white hover:bg-[#1f1f1f] disabled:opacity-40"
          >
            Next
          </button>
        </div>
      )}
    </div>
  );
};

export default Search;
