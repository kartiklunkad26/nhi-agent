import { useState } from "react";
import { Search } from "lucide-react";
import { Input } from "@/components/ui/input";
import { Button } from "@/components/ui/button";

interface SearchBarProps {
  onSearch: (query: string) => void;
  isLoading?: boolean;
}

export const SearchBar = ({ onSearch, isLoading = false }: SearchBarProps) => {
  const [query, setQuery] = useState("");

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    if (query.trim()) {
      onSearch(query);
    }
  };

  return (
    <form onSubmit={handleSubmit} className="w-full max-w-4xl mx-auto">
      <div className="relative group mb-6">
        <div className="absolute -inset-1 bg-gradient-to-r from-primary to-accent rounded-2xl blur opacity-20 group-hover:opacity-30 transition duration-300"></div>
        <div className="relative flex gap-3 bg-card p-2 rounded-xl shadow-[0_4px_20px_hsl(var(--foreground)/0.06)] border border-border/50 hover:shadow-[0_10px_40px_hsl(var(--foreground)/0.1)] transition-all duration-300">
          <Input
            type="text"
            placeholder="Search for service accounts, roles, and API keys across AWS..."
            value={query}
            onChange={(e) => setQuery(e.target.value)}
            disabled={isLoading}
            className="flex-1 h-14 text-lg px-6 border-0 bg-transparent focus-visible:ring-0 focus-visible:ring-offset-0 placeholder:text-muted-foreground/60"
          />
          <Button
            type="submit"
            disabled={isLoading || !query.trim()}
            size="lg"
            className="h-14 px-8 bg-gradient-to-r from-primary to-accent hover:opacity-90 transition-all duration-300 shadow-[0_4px_20px_hsl(var(--primary)/0.25)] hover:shadow-[0_8px_30px_hsl(var(--primary)/0.35)]"
          >
            {isLoading ? (
              <>
                <div className="animate-spin mr-2 h-4 w-4 border-2 border-white border-t-transparent rounded-full" />
                Searching...
              </>
            ) : (
              <>
                <Search className="mr-2 h-5 w-5" />
                Search
              </>
            )}
          </Button>
        </div>
      </div>

      <div className="flex flex-wrap gap-2 justify-center items-center">
        <span className="text-sm font-medium text-muted-foreground mr-1">Try:</span>
        <button
          type="button"
          onClick={() => setQuery("list of users")}
          disabled={isLoading}
          className="px-4 py-2 text-sm font-medium text-foreground bg-secondary/50 hover:bg-secondary hover:border-primary/30 border border-transparent rounded-lg transition-all duration-200 disabled:opacity-50"
        >
          list of users
        </button>
        <button
          type="button"
          onClick={() => setQuery("list of access keys")}
          disabled={isLoading}
          className="px-4 py-2 text-sm font-medium text-foreground bg-secondary/50 hover:bg-secondary hover:border-primary/30 border border-transparent rounded-lg transition-all duration-200 disabled:opacity-50"
        >
          list of access keys
        </button>
        <button
          type="button"
          onClick={() => setQuery("are my access keys the oldest")}
          disabled={isLoading}
          className="px-4 py-2 text-sm font-medium text-foreground bg-secondary/50 hover:bg-secondary hover:border-primary/30 border border-transparent rounded-lg transition-all duration-200 disabled:opacity-50"
        >
          are my access keys the oldest
        </button>
      </div>
    </form>
  );
};
