export default function Footer() {
  const currentYear = new Date().getFullYear();

  return (
    <footer className="py-6 px-6 bg-transparent">
      <div className="max-w-7xl mx-auto text-center text-sm opacity-80">
        <p>© {currentYear} Anonymous. All rights reserved.</p>
      </div>
    </footer>
  );
}
