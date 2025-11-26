import { useLocation, Link } from "react-router-dom";
import { useEffect } from "react";
import { Shield } from "lucide-react";
import { Button } from "@/components/ui/button";

const NotFound = () => {
  const location = useLocation();

  useEffect(() => {
    console.error("404 Error: User attempted to access non-existent route:", location.pathname);
  }, [location.pathname]);

  return (
    <div className="min-h-screen bg-gradient-to-b from-background to-secondary/30 flex items-center justify-center p-4">
      <div className="text-center space-y-6">
        <div className="inline-flex items-center gap-3 mb-4">
          <div className="p-3 bg-gradient-to-br from-primary to-accent rounded-lg">
            <Shield className="h-8 w-8 text-white" />
          </div>
        </div>
        <h1 className="text-6xl font-bold bg-gradient-to-r from-primary to-accent bg-clip-text text-transparent">
          404
        </h1>
        <p className="text-xl text-muted-foreground">
          Page not found
        </p>
        <Link to="/">
          <Button className="bg-gradient-to-r from-primary to-accent hover:opacity-90 transition-opacity">
            Return to Home
          </Button>
        </Link>
      </div>
    </div>
  );
};

export default NotFound;
