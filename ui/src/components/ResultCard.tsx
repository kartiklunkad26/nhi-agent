import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { Shield, Key, Cloud } from "lucide-react";

interface ResultCardProps {
  title: string;
  type: "vault" | "aws" | "api-key";
  description: string;
  status?: "active" | "expired" | "inactive";
  lastAccessed?: string;
}

export const ResultCard = ({ title, type, description, status, lastAccessed }: ResultCardProps) => {
  const icons = {
    vault: Shield,
    aws: Cloud,
    "api-key": Key,
  };

  const statusColors = {
    active: "bg-green-500/10 text-green-600 border-green-500/20",
    expired: "bg-red-500/10 text-red-600 border-red-500/20",
    inactive: "bg-gray-500/10 text-gray-600 border-gray-500/20",
  };

  const Icon = icons[type];

  return (
    <Card className="hover:shadow-lg transition-all duration-300 hover:border-primary/50">
      <CardHeader>
        <div className="flex items-start justify-between">
          <div className="flex items-center gap-3">
            <div className="p-2 bg-gradient-to-br from-primary/10 to-accent/10 rounded-lg">
              <Icon className="h-5 w-5 text-primary" />
            </div>
            <div>
              <CardTitle className="text-lg">{title}</CardTitle>
              <CardDescription className="mt-1">{description}</CardDescription>
            </div>
          </div>
          {status && (
            <Badge variant="outline" className={statusColors[status]}>
              {status}
            </Badge>
          )}
        </div>
      </CardHeader>
      {lastAccessed && (
        <CardContent>
          <p className="text-sm text-muted-foreground">Last accessed: {lastAccessed}</p>
        </CardContent>
      )}
    </Card>
  );
};
