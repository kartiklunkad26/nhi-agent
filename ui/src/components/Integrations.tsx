import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import { Cloud, Shield, CheckCircle2, Settings } from "lucide-react";

interface Integration {
  id: string;
  name: string;
  provider: string;
  status: "connected" | "disconnected";
  description: string;
  icon: React.ReactNode;
  lastSync?: Date;
}

const mockIntegrations: Integration[] = [
  {
    id: "1",
    name: "AWS IAM",
    provider: "Amazon Web Services",
    status: "connected",
    description: "Collect and analyze IAM users, roles, groups, and access keys from your AWS account.",
    icon: <Cloud className="h-6 w-6" />,
    lastSync: new Date(Date.now() - 1000 * 60 * 15), // 15 minutes ago
  },
];

export function Integrations() {
  const formatLastSync = (date?: Date) => {
    if (!date) return "Never";
    const now = new Date();
    const diff = now.getTime() - date.getTime();
    const minutes = Math.floor(diff / 1000 / 60);
    const hours = Math.floor(minutes / 60);
    const days = Math.floor(hours / 24);

    if (days > 0) return `${days} day${days > 1 ? 's' : ''} ago`;
    if (hours > 0) return `${hours} hour${hours > 1 ? 's' : ''} ago`;
    if (minutes > 0) return `${minutes} minute${minutes > 1 ? 's' : ''} ago`;
    return "Just now";
  };

  return (
    <div className="space-y-6">
      <div>
        <h2 className="text-3xl font-bold tracking-tight mb-2">Integrations</h2>
        <p className="text-muted-foreground">
          Manage your cloud provider integrations and identity sources
        </p>
      </div>

      <div className="grid gap-6 md:grid-cols-2 lg:grid-cols-3">
        {mockIntegrations.map((integration) => (
          <Card key={integration.id} className="relative overflow-hidden">
            <div className="absolute top-0 right-0 w-32 h-32 bg-gradient-to-bl from-primary/10 to-transparent rounded-bl-full" />

            <CardHeader>
              <div className="flex items-start justify-between">
                <div className="p-3 bg-gradient-to-br from-primary/20 to-accent/20 rounded-lg">
                  {integration.icon}
                </div>
                <Badge
                  variant={integration.status === "connected" ? "default" : "secondary"}
                  className="flex items-center gap-1"
                >
                  {integration.status === "connected" && (
                    <CheckCircle2 className="h-3 w-3" />
                  )}
                  {integration.status === "connected" ? "Connected" : "Disconnected"}
                </Badge>
              </div>

              <CardTitle className="mt-4">{integration.name}</CardTitle>
              <CardDescription className="text-xs">{integration.provider}</CardDescription>
            </CardHeader>

            <CardContent className="space-y-4">
              <p className="text-sm text-muted-foreground">
                {integration.description}
              </p>

              {integration.lastSync && (
                <div className="text-xs text-muted-foreground">
                  Last synced: {formatLastSync(integration.lastSync)}
                </div>
              )}

              <div className="flex gap-2">
                <Button size="sm" variant="outline" className="flex-1">
                  <Settings className="h-4 w-4 mr-2" />
                  Configure
                </Button>
                {integration.status === "connected" && (
                  <Button size="sm" variant="outline">
                    Sync Now
                  </Button>
                )}
              </div>
            </CardContent>
          </Card>
        ))}

        {/* Add New Integration Card */}
        <Card className="border-dashed hover:border-primary/50 transition-colors cursor-pointer">
          <CardHeader className="h-full flex flex-col items-center justify-center text-center py-12">
            <div className="p-4 bg-muted rounded-full mb-4">
              <Shield className="h-8 w-8 text-muted-foreground" />
            </div>
            <CardTitle className="text-lg">Add Integration</CardTitle>
            <CardDescription className="mt-2">
              Connect a new cloud provider or identity source
            </CardDescription>
            <Button variant="outline" className="mt-4">
              Browse Integrations
            </Button>
          </CardHeader>
        </Card>
      </div>
    </div>
  );
}
