const PostCardSkeleton = () => {
  return (
    <div className="border border-gray-200 rounded-2xl p-6 shadow-sm bg-[#f8f8f8] animate-pulse space-y-4">
      {/* Judul */}
      <div className="h-6 w-2/3 bg-gray-200 rounded" />

      {/* Body */}
      <div className="h-4 w-full bg-gray-200 rounded" />
      <div className="h-4 w-5/6 bg-gray-200 rounded" />
      <div className="h-4 w-4/6 bg-gray-200 rounded" />

      {/* Tags */}
      <div className="flex gap-2 mt-2">
        {[...Array(3)].map((_, i) => (
          <div key={i} className="h-6 w-16 bg-gray-200 rounded-full" />
        ))}
      </div>

      {/* Reactions */}
      <div className="flex gap-4 mt-2">
        <div className="h-4 w-14 bg-gray-200 rounded" />
        <div className="h-4 w-14 bg-gray-200 rounded" />
        <div className="h-4 w-14 bg-gray-200 rounded" />
      </div>

      {/* Footer actions */}
      <div className="flex justify-between items-center mt-4">
        <div className="h-5 w-24 bg-gray-200 rounded" />
        <div className="h-6 w-20 bg-gray-200 rounded-full" />
      </div>
    </div>
  );
};

export default PostCardSkeleton;
