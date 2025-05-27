import AuthLayoutTemplate from "@/layouts/auth-simple-layout";

export default function AuthLayout({ children, title, description, ...props }) {
  return (
    <AuthLayoutTemplate title={title} description={description} {...props}>
      {children}
    </AuthLayoutTemplate>
  );
}
