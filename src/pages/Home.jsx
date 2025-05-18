import { useEffect, useRef, useState } from "react";
import useFetch from "../hooks/useFetch";
import PostCard from "../components/PostCard";
import PostCardSkeleton from "../components/PostCardSkeleton";
import { useFavorite } from "../context/FavoriteContext";

const LIMIT = 3;

const Home = () => {
  const { loaded } = useFavorite();
  const [skip, setSkip] = useState(0);
  const [allPosts, setAllPosts] = useState([]);
  const loaderRef = useRef(null);

  //const { data, loading, error } = useFetch(
  //  `https://dummyjson.com/posts?limit=${LIMIT}&skip=${skip}` 
  //);

  useEffect(() => {
    if (data?.posts) {
      setAllPosts((prev) => [...prev, ...data.posts]);
    }
  }, [data]);

  useEffect(() => {
    if (loading) return;
    const observer = new IntersectionObserver(
      (entries) => {
        if (entries[0].isIntersecting && data?.total > allPosts.length) {
          setSkip((prev) => prev + LIMIT);
        }
      },
      { threshold: 1 }
    );
    const target = loaderRef.current;
    if (target) observer.observe(target);
    return () => {
      if (target) observer.unobserve(target);
    };
  }, [loading, data, allPosts]);

  return (
    <div className="max-w-3xl mx-auto p-4 space-y-6">
      <h1 className="text-3xl font-bold text-center mb-6">Daftar Post 📚</h1>

      {!loaded ? (
        <p className="text-center">Menyiapkan data favorit...</p>
      ) : (
        <>
          {allPosts.map((item) => (
            <PostCard key={item.id} {...item} />
          ))}

          {loading && (
            <div className="space-y-4">
              {[...Array(3)].map((_, i) => (
                <PostCardSkeleton key={i} />
              ))}
            </div>
          )}

          {error && <p className="text-center text-red-500">{error}</p>}
          <div ref={loaderRef}></div>
        </>
      )}
    </div>
  );
};

export default Home;
