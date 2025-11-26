import Header from "@/components/Header";
import Footer from "@/components/Footer";
import { Plus } from "lucide-react";
import { Button } from "@/components/ui/button";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { useState } from "react";
import { SearchBar } from "@/components/SearchBar";
import { ResultsTable } from "@/components/ResultsTable";
import { useAuth } from "@/contexts/AuthContext";
import { useSecurity } from "@/contexts/SecurityContext";
import { searchIdentities, type IdentityResult } from "@/lib/api";
import { useToast } from "@/hooks/use-toast";

const Dashboard = () => {
  const [hasIntegration, setHasIntegration] = useState(true); // Set to true to show main dashboard
  const [isLoading, setIsLoading] = useState(false);
  const [results, setResults] = useState<IdentityResult[]>([]);
  const [lastQuery, setLastQuery] = useState<string>("");
  const { currentUser } = useAuth();
  const { secureMode } = useSecurity();
  const { toast } = useToast();

  const handleSearch = async (query: string) => {
    setIsLoading(true);
    setLastQuery(query);

    try {
      const response = await searchIdentities(query, currentUser, secureMode);
      setResults(response.results);

      toast({
        title: "Search completed",
        description: `Found ${response.total} result${response.total !== 1 ? 's' : ''}`,
      });
    } catch (error) {
      console.error("Search failed:", error);
      toast({
        title: "Search failed",
        description: error instanceof Error ? error.message : "An error occurred",
        variant: "destructive",
      });
      setResults([]);
    } finally {
      setIsLoading(false);
    }
  };

  if (!hasIntegration) {
    return (
      <div className="relative min-h-screen">
        <Header />
        <main className="pt-24 pb-20 container mx-auto px-6">
          <div className="max-w-2xl mx-auto">
            <Card className="border-2 border-dashed border-border">
              <CardHeader className="text-center space-y-4">
                <div className="mx-auto w-16 h-16 rounded-full bg-primary/10 flex items-center justify-center">
                  <Plus className="h-8 w-8 text-primary" />
                </div>
                <CardTitle className="text-2xl">Setup Your First Integration</CardTitle>
                <CardDescription className="text-base">
                  Connect your cloud provider to start managing non-human identities
                </CardDescription>
              </CardHeader>
              <CardContent className="space-y-4">
                <Button
                  variant="search"
                  size="lg"
                  className="w-full"
                  onClick={() => setHasIntegration(true)}
                >
                  <Plus className="h-5 w-5 mr-2" />
                  Add Integration
                </Button>
                <div className="grid gap-3">
                  <Button variant="outline" className="justify-start" size="lg">
                    <img src="/placeholder.svg" alt="AWS" className="h-5 w-5 mr-3" />
                    Amazon Web Services (AWS)
                  </Button>
                  <Button variant="outline" className="justify-start" size="lg">
                    <img src="/placeholder.svg" alt="Azure" className="h-5 w-5 mr-3" />
                    Microsoft Azure
                  </Button>
                  <Button variant="outline" className="justify-start" size="lg">
                    <img src="/placeholder.svg" alt="GCP" className="h-5 w-5 mr-3" />
                    Google Cloud Platform
                  </Button>
                </div>
              </CardContent>
            </Card>
          </div>
        </main>
        <Footer />
      </div>
    );
  }

  return (
    <div className="relative min-h-screen">
      <Header />
      <main className="pt-24 pb-20 container mx-auto px-6">
        <div className="max-w-5xl mx-auto space-y-8">
          {/* Search bar */}
          <SearchBar onSearch={handleSearch} isLoading={isLoading} />

          {/* Results */}
          {results.length > 0 && (
            <Card>
              <CardHeader>
                <CardTitle>Search Results</CardTitle>
                <CardDescription>
                  {results.length} result{results.length !== 1 ? 's' : ''} for "{lastQuery}"
                  {secureMode && currentUser && (
                    <span className="ml-2 text-green-600 font-medium">
                      (Secure Mode - viewing as {currentUser})
                    </span>
                  )}
                </CardDescription>
              </CardHeader>
              <CardContent>
                <ResultsTable results={results} />
              </CardContent>
            </Card>
          )}

          {/* Empty state when no results */}
          {!isLoading && results.length === 0 && lastQuery && (
            <Card>
              <CardHeader>
                <CardTitle>No Results Found</CardTitle>
                <CardDescription>
                  No identities found for "{lastQuery}". Try a different query.
                </CardDescription>
              </CardHeader>
            </Card>
          )}

          {/* Initial state */}
          {!isLoading && results.length === 0 && !lastQuery && (
            <Card>
              <CardHeader>
                <CardTitle>Ready to Search</CardTitle>
                <CardDescription>
                  Use the search bar above to find service accounts, roles, and API keys across your AWS infrastructure.
                </CardDescription>
              </CardHeader>
              <CardContent>
                <div className="space-y-4">
                  <p className="text-sm text-muted-foreground">
                    Try queries like:
                  </p>
                  <ul className="list-disc list-inside space-y-2 text-sm text-muted-foreground">
                    <li>"Show me all users without MFA"</li>
                    <li>"List admin users"</li>
                    <li>"Find access keys older than 90 days"</li>
                    <li>"Are my access keys the oldest?"</li>
                  </ul>
                </div>
              </CardContent>
            </Card>
          )}
        </div>
      </main>
      <Footer />
    </div>
  );
};

export default Dashboard;
