import Header from "@/components/Header";
import Footer from "@/components/Footer";
import { Integrations as IntegrationsComponent } from "@/components/Integrations";

const IntegrationsPage = () => {
  return (
    <div className="relative min-h-screen flex flex-col">
      <Header />
      <main className="flex-1 pt-24 pb-20 container mx-auto px-6">
        <div className="max-w-7xl mx-auto">
          <IntegrationsComponent />
        </div>
      </main>
      <Footer />
    </div>
  );
};

export default IntegrationsPage;
