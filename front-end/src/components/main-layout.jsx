import Navbar from "../components/navbar";
import Footer from "../components/footer";

export default function MainLayout({ children }) {
  return (
    <>
      <Navbar />
      <main className="relative py-20 mx-auto">{children}</main>
      <Footer />
    </>
  );
}
