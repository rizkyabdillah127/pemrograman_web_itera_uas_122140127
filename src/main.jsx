import { StrictMode } from "react";
import { createRoot } from "react-dom/client";
import "./index.css";
import App from "./App.jsx";
import { FavoriteProvider } from "./context/FavoriteContext.jsx";
import { ToastProvider } from "./context/ToastContext.jsx";
import GlobalToast from "./components/GlobalToast.jsx";

createRoot(document.getElementById("root")).render(
  <StrictMode>
    <ToastProvider>
      <FavoriteProvider>
        <App />
        <GlobalToast />
      </FavoriteProvider>
    </ToastProvider>
  </StrictMode>
);
