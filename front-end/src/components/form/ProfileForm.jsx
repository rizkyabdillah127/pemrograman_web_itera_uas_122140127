import PropTypes from "prop-types";
import { useState, useEffect } from "react";
import { Button } from "@/components/ui/button";

export default function ProfileForm({ initialData, onSubmit }) {
  const [formData, setFormData] = useState(null);

  useEffect(() => {
    if (initialData) {
      setFormData({
        username: initialData.username || "",
        email: initialData.email || "",
      });
    }
  }, [initialData]);

  if (!formData) return null;

  const handleChange = (e) =>
    setFormData((prev) => ({
      ...prev,
      [e.target.name]: e.target.value,
    }));

  const handleSubmit = (e) => {
    e.preventDefault();
    onSubmit(formData);
  };

  return (
    <form
      onSubmit={handleSubmit}
      className="relative overflow-hidden border border-gray-200/5 rounded-2xl p-6 shadow-sm bg-transparent"
    >
      {/* Grain effect background layer */}
      <div className="absolute inset-0 z-0 bg-[url('https://grainy-gradients.vercel.app/noise.svg')] bg-cover opacity-5 pointer-events-none" />

      {/* Form content */}
      <div className="relative z-10 space-y-5">
        <div>
          <label className="block text-sm font-medium text-gray-700">
            Username
          </label>
          <input
            type="text"
            name="username"
            value={formData.username}
            onChange={handleChange}
            required
            placeholder="Masukkan username"
            className="mt-1 w-full px-3 py-2 rounded-md border border-gray-300 bg-white/80 backdrop-blur-sm focus:outline-none focus:ring-2 focus:ring-primary focus:border-transparent text-gray-800 placeholder:text-gray-400"
          />
        </div>

        <div>
          <label className="block text-sm font-medium text-gray-700">
            Email
          </label>
          <input
            type="email"
            name="email"
            value={formData.email}
            onChange={handleChange}
            required
            placeholder="Masukkan email"
            className="mt-1 w-full px-3 py-2 rounded-md border border-gray-300 bg-white/80 backdrop-blur-sm focus:outline-none focus:ring-2 focus:ring-primary focus:border-transparent text-gray-800 placeholder:text-gray-400"
          />
        </div>

        <Button type="submit" className="w-full">
          Simpan Perubahan
        </Button>
      </div>
    </form>
  );
}

ProfileForm.propTypes = {
  initialData: PropTypes.shape({
    username: PropTypes.string,
    email: PropTypes.string,
  }),
  onSubmit: PropTypes.func.isRequired,
};
