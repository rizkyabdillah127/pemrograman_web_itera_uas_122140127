import { Link } from "react-router-dom";

export default function IndexNotFound() {
  return (
    <div className="min-h-screen flex flex-col items-center justify-center bg-white dark:bg-black text-black dark:text-white text-center px-4">
      <h1 className="text-5xl font-extrabold mb-4">404</h1>
      <h2 className="text-2xl font-semibold mb-2">Page Not Found</h2>
      <p className="text-gray-600 dark:text-gray-400 mb-6 max-w-md">
        The page you are looking for doesn’t exist or has been moved.
      </p>

      <Link
        to="/"
        className="px-6 py-2 bg-black text-white dark:bg-white dark:text-black rounded-md border border-black dark:border-white transition hover:bg-white hover:text-black dark:hover:bg-black dark:hover:text-white"
      >
        Back to Home
      </Link>
    </div>
  );
}
