import AppLogoIcon from "@/components/app-logo-icon";
import { Link } from "react-router-dom";
import PropTypes from "prop-types";

function AuthSimpleLayout({ children, title, description }) {
  return (
    <div className="bg-background flex min-h-svh flex-col items-center justify-center gap-6 p-6 md:p-10">
      <div className="w-full max-w-sm">
        <div className="flex flex-col gap-8">
          <div className="flex flex-col items-center gap-4">
            <Link
              to="/"
              className="flex flex-col items-center gap-2 font-medium"
            >
              <h1>APCER</h1>

              <span className="sr-only">{title}</span>
            </Link>

            <div className="space-y-2 text-center">
              <h1 className="text-xl font-medium">{title}</h1>
              <p className="text-muted-foreground text-center text-sm">
                {description}
              </p>
            </div>
          </div>
          {children}
        </div>
      </div>
    </div>
  );
}

// Set prop types and default props
AuthSimpleLayout.propTypes = {
  title: PropTypes.string,
  description: PropTypes.string,
  children: PropTypes.node.isRequired,
};

AuthSimpleLayout.defaultProps = {
  title: "",
  description: "",
};

export default AuthSimpleLayout;
