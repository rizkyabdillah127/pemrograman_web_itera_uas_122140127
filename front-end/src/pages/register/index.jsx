import { Link, useNavigate } from "react-router-dom";
import { Button } from "@/components/ui/button";
import AuthLayout from "@/layouts/auth-layout";
import { useState, useEffect } from "react";
import { useAuth } from "@/hooks/useAuth";
import { Loader2 } from "lucide-react";
import { toast } from "sonner";
import {
  Dialog,
  DialogContent,
  DialogDescription,
  DialogHeader,
  DialogTitle,
} from "@/components/ui/dialog";

export default function Register() {
  const { register, error: authError } = useAuth();
  const navigate = useNavigate();

  const [processing, setProcessing] = useState(false);
  const [error, setError] = useState(null);

  const [showCredentialsDialog, setShowCredentialsDialog] = useState(false);
  const [generatedCredentials, setGeneratedCredentials] = useState({
    email: "",
    password: "",
  });

  useEffect(() => {
    let timer;
    if (showCredentialsDialog) {
      timer = setTimeout(() => {
        setShowCredentialsDialog(false);
        navigate("/posts");
      }, 10000);
    }
    return () => clearTimeout(timer);
  }, [showCredentialsDialog, navigate]);

  const handleRegisterClick = async () => {
    setProcessing(true);
    setError(null);

    try {
      const result = await register();

      if (!result || !result.success) {
        const errMsg = authError || "Registration failed. Please try again.";
        toast.error(errMsg);
        setError(errMsg);
        return;
      }

      setGeneratedCredentials({
        email: result.email,
        password: result.password,
      });
      setShowCredentialsDialog(true);
    } catch (err) {
      const fallback = "Registration error occurred.";
      const message = err?.message || fallback;
      toast.error(message);
      setError(message);
    } finally {
      setProcessing(false);
    }
  };

  const handleCopyCredentials = async () => {
    const credentialsText = `email: ${generatedCredentials.email}\npassword: ${generatedCredentials.password}`;
    try {
      await navigator.clipboard.writeText(credentialsText);
      toast.success("Credentials successfully copied to clipboard!");
    } catch (err) {
      toast.error("Copy failed. Please try again.");
    }
  };

  return (
    <AuthLayout
      title="Register Anonymously"
      description="Click the button below to create an anonymous account."
    >
      <div className="flex flex-col gap-6">
        <div className="grid gap-4">
          {error && <p className="text-sm text-red-500">{error}</p>}

          <Button
            type="button"
            className="mt-2 w-full"
            onClick={handleRegisterClick}
            disabled={processing}
          >
            {processing && (
              <span className="animate-spin mr-2">
                <Loader2 className="h-4 w-4" />
              </span>
            )}
            Daftar Sekarang
          </Button>
        </div>

        <div className="text-muted-foreground text-center text-sm">
          Already have an account?{" "}
          <Link to="/login" tabIndex={6}>
            Log in
          </Link>
        </div>
      </div>

      <Dialog
        open={showCredentialsDialog}
        onOpenChange={setShowCredentialsDialog}
      >
        <DialogContent className="sm:max-w-[425px] rounded-lg shadow-xl p-6 bg-white">
          <DialogHeader>
            <DialogTitle className="text-2xl font-bold text-gray-900">
              Registration Successful!
            </DialogTitle>
            <DialogDescription className="text-gray-600">
              Your anonymous account has been created. Please copy these
              credentials, as they will disappear in 10 seconds.
            </DialogDescription>
          </DialogHeader>
          <div className="grid gap-4 py-4">
            <div className="bg-gray-100 p-4 rounded-md border border-gray-200">
              <p className="text-sm font-medium text-gray-700">Email:</p>
              <p className="font-mono text-base text-gray-800 break-all">
                {generatedCredentials.email}
              </p>
            </div>
            <div className="bg-gray-100 p-4 rounded-md border border-gray-200">
              <p className="text-sm font-medium text-gray-700">Password:</p>
              <p className="font-mono text-base text-gray-800 break-all">
                {generatedCredentials.password}
              </p>
            </div>
            <Button onClick={handleCopyCredentials} className="w-full mt-2">
              Copy Credentials
            </Button>
          </div>
        </DialogContent>
      </Dialog>
    </AuthLayout>
  );
}
