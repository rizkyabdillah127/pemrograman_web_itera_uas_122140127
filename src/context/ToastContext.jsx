import { createContext, useContext, useState } from "react";

const ToastContext = createContext();

export const useToast = () => useContext(ToastContext);

export const ToastProvider = ({ children }) => {
  const [toast, setToast] = useState({ visible: false, message: "" });

  const showToast = (message) => {
    setToast({ visible: true, message });

    // Auto hide setelah 2.5 detik
    setTimeout(() => {
      setToast({ visible: false, message: "" });
    }, 2500);
  };

  return (
    <ToastContext.Provider value={{ toast, showToast }}>
      {children}
    </ToastContext.Provider>
  );
};
