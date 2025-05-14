import { Link } from "react-router-dom";

const Navbar = () => {
  return (
    <nav className="bg-[#121212] text-white p-4 shadow">
      <div className="max-w-6xl mx-auto flex flex-col md:flex-row gap-5 md:gap-0 justify-between items-center">
        <Link to="/" className="font-bold text-lg">
          📰 DummyPost
        </Link>

        <div className="space-x-4 text-sm">
          <Link to="/" className="hover:underline">
            Beranda
          </Link>
          <Link to="/search" className="hover:underline">
            Search
          </Link>
          <Link to="/favorite" className="hover:underline">
            Favorit
          </Link>
        </div>
      </div>
    </nav>
  );
};

export default Navbar;
