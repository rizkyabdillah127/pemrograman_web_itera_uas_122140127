import { useState, useEffect } from "react";
import { Link } from "react-router-dom";
import { Button } from "@/components/ui/button";
import { useAuth } from "@/hooks/useAuth";

export default function Navbar() {
  const [isOpen, setIsOpen] = useState(false);
  const { checkSession } = useAuth();
  const [isAuthenticated, setIsAuthenticated] = useState(false);

  useEffect(() => {
    const { isValid } = checkSession();
    setIsAuthenticated(isValid);
  }, [checkSession]);

  return (
    <header
      className={`fixed z-50 top-0 left-0 w-full text-secondary-foreground`}
    >
      <div className="max-w-7xl mx-auto flex justify-between items-center px-4 py-3 md:px-6">
        <Link
          to="/"
          className="text-xl md:text-2xl font-bold text-secondary-foreground"
        >
          Apcer
        </Link>

        <div className="hidden md:flex items-center gap-2">
          {!isAuthenticated ? (
            <>
              <Button
                asChild
                variant="ghost"
                className="text-secondary-foreground hover:bg-primary/[0.8] hover:text-secondary-foreground"
              >
                <Link to="/login">Masuk</Link>
              </Button>
              <Button
                asChild
                className="bg-primary-foreground text-primary hover:bg-primary-foreground/90"
              >
                <Link to="/register">Daftar</Link>
              </Button>
            </>
          ) : (
            <Button
              asChild
              className="bg-primary-foreground text-primary hover:bg-primary-foreground/90"
            >
              <Link to="/posts">Posts Dashboard</Link>
            </Button>
          )}
        </div>

        <button
          onClick={() => setIsOpen(!isOpen)}
          className="md:hidden focus:outline-none text-secondary-foreground"
        >
          <svg
            className="h-6 w-6"
            fill="none"
            stroke="currentColor"
            viewBox="0 0 24 24"
          >
            {isOpen ? (
              <path
                strokeLinecap="round"
                strokeLinejoin="round"
                strokeWidth={2}
                d="M6 18L18 6M6 6l12 12"
              />
            ) : (
              <path
                strokeLinecap="round"
                strokeLinejoin="round"
                strokeWidth={2}
                d="M4 6h16M4 12h16M4 18h16"
              />
            )}
          </svg>
        </button>
      </div>

      {isOpen && (
        <nav className="md:hidden bg-primary/90 backdrop-blur-md pb-4 pt-2 border-t border-primary-foreground/[0.1]">
          <ul className="flex flex-col gap-2 px-4">
            {!isAuthenticated ? (
              <>
                <li>
                  <Button
                    asChild
                    onClick={() => setIsOpen(false)}
                    className="w-full justify-start text-left bg-primary-foreground text-primary hover:bg-primary-foreground/90"
                  >
                    <Link to="/login">Masuk</Link>
                  </Button>
                </li>
                <li>
                  <Button
                    asChild
                    className="w-full justify-start text-left bg-primary-foreground text-primary hover:bg-primary-foreground/90"
                    onClick={() => setIsOpen(false)}
                  >
                    <Link to="/register">Daftar</Link>
                  </Button>
                </li>
              </>
            ) : (
              <li>
                <Button
                  asChild
                  className="w-full justify-start text-left bg-primary-foreground text-primary hover:bg-primary-foreground/90"
                  onClick={() => setIsOpen(false)}
                >
                  <Link to="/posts">Posts Dashboard</Link>
                </Button>
              </li>
            )}
          </ul>
        </nav>
      )}
    </header>
  );
}
