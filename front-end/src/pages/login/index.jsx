import { LoaderCircle } from "lucide-react";
import TextLink from "@/components/text-link";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import AuthLayout from "@/layouts/auth-layout";
import { useEffect, useState } from "react";
import { useAuth } from "@/hooks/useAuth";
import { toast } from "sonner";
import { Link, useNavigate } from "react-router-dom";

export default function Login({ status, canResetPassword }) {
  const { login, checkSession, loading } = useAuth();
  const navigate = useNavigate();

  const [data, setData] = useState({ email: "", password: "" });
  const [processing, setProcessing] = useState(false);
  const [error, setError] = useState(null);

  // 🔒 Auto-redirect jika sudah login
  useEffect(() => {
    const session = checkSession();

    if (session.isValid) {
      navigate("/posts");
    }
  }, [checkSession, navigate]);

  const handleChange = (e) => {
    const { name, value } = e.target;
    setData((prev) => ({ ...prev, [name]: value }));
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    setProcessing(true);
    setError(null);

    try {
      const success = await login(data.email, data.password);

      if (!success) {
        const message = "Email or password is incorrect.";
        toast.error(message);
        setError(message);
        return;
      }

      toast.success("Login successful!");
      navigate("/posts");
    } catch (err) {
      const message = "Login failed: " + (err.message || "Unexpected error");
      toast.error(message);
      setError(message);
    } finally {
      setProcessing(false);
    }
  };

  return (
    <AuthLayout
      title="Log in to your account"
      description="Enter your email and password below to log in"
    >
      <form className="flex flex-col gap-6" onSubmit={handleSubmit}>
        <div className="grid gap-4">
          {/* Email */}
          <div className="grid gap-1">
            <Label htmlFor="email">Email address</Label>
            <Input
              id="email"
              type="email"
              name="email"
              required
              autoFocus
              autoComplete="email"
              value={data.email}
              onChange={handleChange}
              disabled={processing}
              placeholder="email@example.com"
            />
          </div>

          {/* Password */}
          <div className="grid gap-1">
            <div className="flex items-center">
              <Label htmlFor="password">Password</Label>
              {canResetPassword && (
                <TextLink
                  href={route("password.request")}
                  className="ml-auto text-sm"
                >
                  Forgot password?
                </TextLink>
              )}
            </div>
            <Input
              id="password"
              type="password"
              name="password"
              required
              autoComplete="current-password"
              value={data.password}
              onChange={handleChange}
              disabled={processing}
              placeholder="Password"
            />
          </div>

          {/* Error Display */}
          {error && <p className="text-sm text-red-500">{error}</p>}

          {/* Submit Button */}
          <Button
            type="submit"
            className="mt-4 w-full"
            disabled={processing || loading}
          >
            {processing && (
              <span className="animate-spin mr-2">
                <LoaderCircle className="h-4 w-4" />
              </span>
            )}
            Log in
          </Button>
        </div>

        {/* Register Link */}
        <div className="text-muted-foreground text-center text-sm">
          Don't have an account? <Link to="/register">Create an account</Link>
        </div>
      </form>

      {/* Optional status message */}
      {status && (
        <div className="mt-4 text-center text-sm font-medium text-green-600">
          {status}
        </div>
      )}
    </AuthLayout>
  );
}
