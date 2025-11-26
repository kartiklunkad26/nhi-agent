import { FileText, User, Shield } from "lucide-react";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";

export interface AuditEntry {
  timestamp: Date;
  action: string;
  user: string;
  secureMode: boolean;
}

interface AuditLogProps {
  entries: AuditEntry[];
  currentMode: boolean; // true = secure mode, false = insecure mode
}

export const AuditLog = ({ entries, currentMode }: AuditLogProps) => {
  // Filter entries to only show current mode
  const currentModeEntries = entries.filter(e => e.secureMode === currentMode);

  if (currentModeEntries.length === 0) {
    return null;
  }

  return (
    <Card className="max-w-6xl mx-auto mt-8">
      <CardHeader>
        <CardTitle className="flex items-center gap-2">
          <FileText className={`h-5 w-5 ${currentMode ? 'text-green-600' : 'text-orange-600'}`} />
          {currentMode ? 'Part 2 Demo Audit Log' : 'Part 1 Demo Audit Log'}
        </CardTitle>
      </CardHeader>
      <CardContent>
        <div className="space-y-2">
          {currentModeEntries.map((entry, index) => (
            <div
              key={index}
              className={`flex items-start gap-3 p-3 rounded-lg ${
                currentMode
                  ? 'bg-green-50 dark:bg-green-950 border border-green-200 dark:border-green-800'
                  : 'bg-orange-50 dark:bg-orange-950 border border-orange-200 dark:border-orange-800'
              }`}
            >
              <div className="flex items-center gap-2 min-w-[180px] text-sm text-muted-foreground">
                {new Date(entry.timestamp).toLocaleTimeString()}
              </div>
              <div className="flex-1 flex items-start gap-2">
                {currentMode ? (
                  <>
                    <Shield className="h-4 w-4 text-green-600 mt-0.5" />
                    <div className="text-sm">
                      <span className="font-semibold text-green-700 dark:text-green-400">
                        {entry.user} + NHI Agent
                      </span>
                      <span className="text-muted-foreground"> performed: </span>
                      <span className="font-medium">{entry.action}</span>
                    </div>
                  </>
                ) : (
                  <>
                    <User className="h-4 w-4 text-orange-600 mt-0.5" />
                    <div className="text-sm">
                      <span className="font-semibold text-orange-700 dark:text-orange-400">
                        {entry.user}
                      </span>
                      <span className="text-muted-foreground"> performed: </span>
                      <span className="font-medium">{entry.action}</span>
                    </div>
                  </>
                )}
              </div>
            </div>
          ))}
        </div>
      </CardContent>
    </Card>
  );
};
