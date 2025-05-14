import { useToast } from "../context/ToastContext";

const GlobalToast = () => {
  const { toast } = useToast();

  if (!toast.visible) return null;

  return (
    <div className="fixed top-4 left-1/2 -translate-x-1/2 bg-emerald-700 text-white px-4 py-2 rounded shadow-md animate-slide-in z-50">
      {toast.message}
    </div>
  );
};

export default GlobalToast;
