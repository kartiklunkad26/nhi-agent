import { User } from "lucide-react";
import { useAuth } from "@/contexts/AuthContext";
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from "@/components/ui/select";

export const UserSelector = () => {
  const { currentUser, setCurrentUser, availableUsers } = useAuth();

  return (
    <div className="flex items-center gap-3 px-4 py-2 bg-secondary/30 rounded-lg border border-border/50">
      <User className="h-4 w-4 text-muted-foreground" />
      <Select value={currentUser || ""} onValueChange={setCurrentUser}>
        <SelectTrigger className="w-[200px] h-8 text-sm border-border/50 bg-background/50">
          <SelectValue placeholder="Select IAM user" />
        </SelectTrigger>
        <SelectContent>
          {availableUsers.map((user) => (
            <SelectItem key={user} value={user} className="text-sm">
              {user}
            </SelectItem>
          ))}
        </SelectContent>
      </Select>
    </div>
  );
};
