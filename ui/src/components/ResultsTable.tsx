import { Badge } from "@/components/ui/badge";
import { Shield, Key, Cloud, AlertTriangle, Info } from "lucide-react";
import {
  Table,
  TableBody,
  TableCell,
  TableHead,
  TableHeader,
  TableRow,
} from "@/components/ui/table";

interface ResultItem {
  title: string;
  type: "vault" | "aws" | "api-key" | "error" | "info";
  description: string;
  status?: "active" | "expired" | "inactive" | "error" | "info";
  lastAccessed?: string;
}

interface ResultsTableProps {
  results: ResultItem[];
}

export const ResultsTable = ({ results }: ResultsTableProps) => {
  const icons = {
    vault: Shield,
    aws: Cloud,
    "api-key": Key,
    error: AlertTriangle,
    info: Info,
  };

  const typeLabels = {
    vault: "Vault",
    aws: "AWS",
    "api-key": "API Key",
    error: "Error",
    info: "Info",
  };

  const statusColors = {
    active: "bg-green-500/10 text-green-600 border-green-500/20",
    expired: "bg-red-500/10 text-red-600 border-red-500/20",
    inactive: "bg-gray-500/10 text-gray-600 border-gray-500/20",
    error: "bg-red-500/10 text-red-600 border-red-500/20",
    info: "bg-blue-500/10 text-blue-600 border-blue-500/20",
  };

  return (
    <div className="relative overflow-hidden rounded-xl border border-border/50 bg-card shadow-[0_4px_20px_hsl(var(--foreground)/0.06)]">
      <div className="overflow-x-auto">
        <Table>
          <TableHeader>
            <TableRow className="border-b border-border/50 hover:bg-transparent">
              <TableHead className="font-semibold text-foreground">Type</TableHead>
              <TableHead className="font-semibold text-foreground">Name</TableHead>
              <TableHead className="font-semibold text-foreground">Description</TableHead>
              <TableHead className="font-semibold text-foreground">Status</TableHead>
              <TableHead className="font-semibold text-foreground text-right">Last Accessed</TableHead>
            </TableRow>
          </TableHeader>
          <TableBody>
            {results.map((result, index) => {
              const Icon = icons[result.type];
              return (
                <TableRow
                  key={index}
                  className="border-b border-border/50 last:border-0 hover:bg-gradient-to-r hover:from-primary/5 hover:to-accent/5 transition-all duration-200"
                >
                  <TableCell className="font-medium">
                    <div className="flex items-center gap-3">
                      <div className="p-2 bg-gradient-to-br from-primary/10 to-accent/10 rounded-lg">
                        <Icon className="h-4 w-4 text-primary" />
                      </div>
                      <span className="text-sm font-medium">{typeLabels[result.type]}</span>
                    </div>
                  </TableCell>
                  <TableCell className="font-semibold text-foreground">
                    {result.title}
                  </TableCell>
                  <TableCell className="text-muted-foreground max-w-md">
                    {result.description}
                  </TableCell>
                  <TableCell>
                    {result.status && (
                      <Badge variant="outline" className={statusColors[result.status]}>
                        {result.status}
                      </Badge>
                    )}
                  </TableCell>
                  <TableCell className="text-muted-foreground text-right">
                    {result.lastAccessed}
                  </TableCell>
                </TableRow>
              );
            })}
          </TableBody>
        </Table>
      </div>
    </div>
  );
};
