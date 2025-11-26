import { useState } from "react";
import { SearchBar } from "@/components/SearchBar";
import { ResultsTable } from "@/components/ResultsTable";
import { Integrations } from "@/components/Integrations";
import { Shield, Search, Settings2 } from "lucide-react";
import { useToast } from "@/hooks/use-toast";
import { searchIdentities, type IdentityResult } from "@/lib/api";
import vault42Logo from "@/assets/vault42-logo.png";
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs";

const Index = () => {
  const { toast } = useToast();
  const [isSearching, setIsSearching] = useState(false);
  const [hasSearched, setHasSearched] = useState(false);
  const [searchResults, setSearchResults] = useState<IdentityResult[]>([]);
  const [searchError, setSearchError] = useState<string | null>(null);

  const handleSearch = async (query: string) => {
    setIsSearching(true);
    setHasSearched(true);
    setSearchError(null);
    setSearchResults([]);

    try {
      const response = await searchIdentities(query, null, false);
      setSearchResults(response.results);

      if (response.results.length === 0) {
        toast({
          title: "No results found",
          description: "Try a different search query.",
        });
      }
    } catch (error: any) {
      console.error("Search error:", error);
      setSearchError(error.message || "Failed to search identities");
      toast({
        variant: "destructive",
        title: "Search failed",
        description: error.message || "An error occurred while searching. Make sure the API server is running and credentials are configured in .env",
      });
    } finally {
      setIsSearching(false);
    }
  };

  return (
    <div className="min-h-screen" style={{ background: 'var(--gradient-hero)' }}>
      <Tabs defaultValue="search" className="w-full">
        <header className="border-b border-border/40 bg-background/60 backdrop-blur-xl sticky top-0 z-10 shadow-sm">
          <div className="container mx-auto px-4 py-4">
            <div className="flex items-center justify-between">
              <div className="flex items-center gap-3">
                <img
                  src={vault42Logo}
                  alt="NexusID"
                  className="h-10 w-10 rounded-lg"
                />
                <h1 className="text-2xl font-bold bg-gradient-to-r from-primary to-accent bg-clip-text text-transparent">
                  NexusID
                </h1>
              </div>
              <TabsList className="bg-background/80">
                <TabsTrigger value="search" className="flex items-center gap-2">
                  <Search className="h-4 w-4" />
                  Search
                </TabsTrigger>
                <TabsTrigger value="integrations" className="flex items-center gap-2">
                  <Settings2 className="h-4 w-4" />
                  Integrations
                </TabsTrigger>
              </TabsList>
            </div>
          </div>
        </header>

        <main className="container mx-auto px-4 py-8">
          <TabsContent value="search" className="space-y-8 mt-0">
            <section>
              <div className="text-center mb-8 space-y-6">
                <h2 className="text-2xl md:text-3xl font-normal tracking-tight leading-tight" style={{ fontFamily: 'Comic Sans MS, cursive' }}>
                  manage all NHIs here
                </h2>
              </div>

              <SearchBar onSearch={handleSearch} isLoading={isSearching} />
            </section>

            {hasSearched && (
              <section className="animate-fade-in max-w-6xl mx-auto">
                <div className="mb-10">
                  <h3 className="text-3xl font-bold mb-2">Search Results</h3>
                  <p className="text-lg text-muted-foreground">
                    {isSearching
                      ? "Searching..."
                      : searchError
                      ? "Search failed"
                      : `Found ${searchResults.length} identities`}
                  </p>
                </div>

                {isSearching ? (
                  <div className="space-y-4">
                    {[1, 2, 3, 4].map((i) => (
                      <div
                        key={i}
                        className="h-20 bg-gradient-to-br from-card to-card/50 rounded-xl border border-border animate-pulse"
                      />
                    ))}
                  </div>
                ) : searchError ? (
                  <div className="p-6 border border-destructive/50 rounded-xl bg-destructive/10">
                    <div className="flex items-start gap-3">
                      <Shield className="h-6 w-6 text-destructive mt-1" />
                      <div>
                        <p className="text-lg font-semibold text-destructive mb-2">Search Failed</p>
                        <p className="text-foreground">{searchError}</p>
                        <p className="text-sm text-muted-foreground mt-3">
                          Make sure you've configured your credentials in the .env file and that the API server is running on port 8000.
                        </p>
                      </div>
                    </div>
                  </div>
                ) : searchResults.length > 0 ? (
                  <ResultsTable results={searchResults} />
                ) : (
                  <div className="p-8 border border-border/50 rounded-xl bg-card">
                    <div className="text-center">
                      <Shield className="h-12 w-12 mx-auto mb-4 text-muted-foreground" />
                      <h3 className="text-xl font-semibold mb-2">No Results Found</h3>
                      <p className="text-muted-foreground">
                        Try a different search query or check your AWS credentials configuration.
                      </p>
                    </div>
                  </div>
                )}
              </section>
            )}
          </TabsContent>

          <TabsContent value="integrations" className="mt-0">
            <Integrations />
          </TabsContent>
        </main>

        <footer className="border-t border-border/40 py-10 mt-20 bg-background/40 backdrop-blur-sm">
          <div className="container mx-auto px-4 text-center text-sm text-muted-foreground">
            <p className="font-medium">NexusID • NHI Management</p>
          </div>
        </footer>
      </Tabs>
    </div>
  );
};

export default Index;
