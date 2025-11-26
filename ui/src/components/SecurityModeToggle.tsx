import { Shield, Lock, AlertTriangle } from "lucide-react";
import { useSecurity } from "@/contexts/SecurityContext";
import { Button } from "@/components/ui/button";
import {
  Tooltip,
  TooltipContent,
  TooltipProvider,
  TooltipTrigger,
} from "@/components/ui/tooltip";

export const SecurityModeToggle = () => {
  const { secureMode, setSecureMode } = useSecurity();

  return (
    <TooltipProvider>
      <Tooltip>
        <TooltipTrigger asChild>
          <Button
            variant={secureMode ? "default" : "outline"}
            size="sm"
            onClick={() => setSecureMode(!secureMode)}
            className={`gap-2 ${
              secureMode
                ? "bg-green-600 hover:bg-green-700 text-white"
                : ""
            }`}
          >
            {secureMode ? (
              <>
                <Lock className="h-4 w-4" />
                Secure Mode
              </>
            ) : (
              <>
                <AlertTriangle className="h-4 w-4" />
                Admin Mode
              </>
            )}
          </Button>
        </TooltipTrigger>
        <TooltipContent>
          <p className="max-w-xs text-sm">
            {secureMode
              ? "Using user-specific credentials with minimal IAM permissions. Click to switch to admin mode."
              : "Using admin credentials - can see all identities. Click to switch to secure mode."}
          </p>
        </TooltipContent>
      </Tooltip>
    </TooltipProvider>
  );
};
