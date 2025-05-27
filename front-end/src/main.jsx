import { StrictMode } from "react";
import { createRoot } from "react-dom/client";
import "@/index.css";
import App from "@/App.jsx";
import { BrowserRouter, Routes, Route } from "react-router-dom";
import Login from "@/pages/login/index.jsx";
import Register from "@/pages/register/index.jsx";
import IndexNotFound from "@/pages/not-found";
import { Toaster } from "sonner";
import PostListPage from "@/pages/post";
import ProfilePage from "@/pages/profile";
import PostDetailPage from "./pages/post/show";
import SavedPostsPage from "./pages/saved";
import MyPostsPage from "./pages/mypost";

createRoot(document.getElementById("root")).render(
  <StrictMode>
    <BrowserRouter>
      <Routes>
        <Route path="/" element={<App />} />
        <Route path="/login" element={<Login />} />
        <Route path="/register" element={<Register />} />
        <Route path="*" element={<IndexNotFound />} />

        <Route path="/posts" element={<PostListPage />} />
        <Route path="/post/:id" element={<PostDetailPage />} />
        <Route path="/saved" element={<SavedPostsPage />} />
        <Route path="/my-post" element={<MyPostsPage />} />
        <Route path="/profile" element={<ProfilePage />} />
      </Routes>

      <Toaster />
    </BrowserRouter>
  </StrictMode>
);
