import { Button } from "@/components/ui/button";
import { Link } from "react-router-dom";

const Hero = () => {
  return (
    <section className="relative min-h-[85vh] flex items-center justify-center overflow-hidden bg-background">
      <div className="relative z-10 container mx-auto px-6 py-20">
        <div className="max-w-5xl mx-auto text-center space-y-8">
          {/* Main headline */}
          <h1 className="text-6xl md:text-7xl lg:text-8xl font-bold tracking-tight text-foreground leading-[1.1] animate-in fade-in slide-in-from-bottom-4 duration-700">
            Securing Non-Human
            <br />
            Identities. Everywhere.
          </h1>
          
          {/* Subtitle */}
          <p className="text-lg md:text-xl text-muted-foreground animate-in fade-in slide-in-from-bottom-6 duration-700 delay-150 max-w-3xl mx-auto leading-relaxed">
            Secure API Keys, Secrets, Tokens, Service Accounts, and AI Agents across Cloud, SaaS, and On-Premise environments
          </p>
          
          {/* CTA Button */}
          <div className="flex items-center justify-center pt-4 animate-in fade-in slide-in-from-bottom-8 duration-700 delay-300">
            <Link to="/dashboard">
              <Button size="xl" className="gap-2 text-base px-8 py-6 h-auto">
                Get Started
              </Button>
            </Link>
          </div>
          
          {/* Trust badges */}
          <div className="pt-16 animate-in fade-in slide-in-from-bottom-10 duration-700 delay-500">
            <p className="text-sm font-medium text-muted-foreground uppercase tracking-wider mb-8">
              Trusted by world-recognized brands
            </p>
            <div className="flex flex-wrap items-center justify-center gap-x-12 gap-y-8 opacity-60 grayscale">
              <div className="text-2xl font-bold tracking-tight">AWS</div>
              <div className="text-2xl font-bold tracking-tight">Azure</div>
              <div className="text-2xl font-bold tracking-tight">Google Cloud</div>
              <div className="text-2xl font-bold tracking-tight">OpenAI</div>
              <div className="text-2xl font-bold tracking-tight">GitHub</div>
            </div>
          </div>
        </div>
      </div>
    </section>
  );
};

export default Hero;
