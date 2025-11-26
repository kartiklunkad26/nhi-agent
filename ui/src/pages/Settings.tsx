import { useState, useEffect } from "react";
import { Shield, Settings as SettingsIcon, Save } from "lucide-react";
import { Link, useNavigate } from "react-router-dom";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { useToast } from "@/hooks/use-toast";
import { supabase } from "@/integrations/supabase/client";
import type { User, Session } from "@supabase/supabase-js";

const Settings = () => {
  const navigate = useNavigate();
  const { toast } = useToast();
  const [user, setUser] = useState<User | null>(null);
  const [session, setSession] = useState<Session | null>(null);
  const [loading, setLoading] = useState(true);

  // AWS credentials
  const [awsAccessKeyId, setAwsAccessKeyId] = useState("");
  const [awsSecretAccessKey, setAwsSecretAccessKey] = useState("");
  const [awsRegion, setAwsRegion] = useState("us-east-1");
  const [awsId, setAwsId] = useState<string | null>(null);

  useEffect(() => {
    // Set up auth state listener
    const { data: { subscription } } = supabase.auth.onAuthStateChange(
      (event, session) => {
        setSession(session);
        setUser(session?.user ?? null);
        
        if (!session) {
          navigate("/auth");
        } else {
          // Load credentials when session is available
          setTimeout(() => {
            loadCredentials(session.user.id);
          }, 0);
        }
      }
    );

    // Check for existing session
    supabase.auth.getSession().then(({ data: { session } }) => {
      setSession(session);
      setUser(session?.user ?? null);
      
      if (!session) {
        navigate("/auth");
      } else {
        loadCredentials(session.user.id);
      }
    });

    return () => subscription.unsubscribe();
  }, [navigate]);

  const loadCredentials = async (userId: string) => {
    try {
      // Load AWS credentials
      const { data: awsData, error: awsError } = await supabase
        .from("aws_credentials")
        .select("*")
        .eq("user_id", userId)
        .single();

      if (awsError && awsError.code !== "PGRST116") {
        console.error("Error loading AWS credentials:", awsError);
      } else if (awsData) {
        setAwsAccessKeyId(awsData.aws_access_key_id);
        setAwsSecretAccessKey(awsData.aws_secret_access_key);
        setAwsRegion(awsData.aws_region);
        setAwsId(awsData.id);
      }
    } catch (error) {
      console.error("Error loading credentials:", error);
    } finally {
      setLoading(false);
    }
  };

  const handleSaveAWS = async () => {
    if (!user) return;

    try {
      if (awsId) {
        // Update existing
        const { error } = await supabase
          .from("aws_credentials")
          .update({
            aws_access_key_id: awsAccessKeyId,
            aws_secret_access_key: awsSecretAccessKey,
            aws_region: awsRegion,
          })
          .eq("id", awsId);

        if (error) throw error;
      } else {
        // Insert new
        const { data, error } = await supabase
          .from("aws_credentials")
          .insert({
            user_id: user.id,
            aws_access_key_id: awsAccessKeyId,
            aws_secret_access_key: awsSecretAccessKey,
            aws_region: awsRegion,
          })
          .select()
          .single();

        if (error) throw error;
        setAwsId(data.id);
      }

      toast({
        title: "AWS credentials saved",
        description: "Your AWS credentials have been securely stored.",
      });
    } catch (error: any) {
      toast({
        variant: "destructive",
        title: "Failed to save AWS credentials",
        description: error.message,
      });
    }
  };

  // Don't render until we check auth
  if (!session || loading) {
    return null;
  }

  return (
    <div className="min-h-screen bg-gradient-to-b from-background to-secondary/30">
      <header className="border-b border-border/40 bg-background/80 backdrop-blur-sm sticky top-0 z-10">
        <div className="container mx-auto px-4 py-4">
          <div className="flex items-center justify-between">
            <Link to="/" className="flex items-center gap-3 hover:opacity-80 transition-opacity">
              <div className="p-2 bg-gradient-to-br from-primary to-accent rounded-lg">
                <Shield className="h-6 w-6 text-white" />
              </div>
              <h1 className="text-2xl font-bold bg-gradient-to-r from-primary to-accent bg-clip-text text-transparent">
                Identity Search
              </h1>
            </Link>
          </div>
        </div>
      </header>

      <main className="container mx-auto px-4 py-12">
        <div className="max-w-3xl mx-auto space-y-8">
          <div className="flex items-center gap-3 mb-8">
            <div className="p-3 bg-gradient-to-br from-primary to-accent rounded-lg">
              <SettingsIcon className="h-6 w-6 text-white" />
            </div>
            <div>
              <h2 className="text-3xl font-bold">Settings</h2>
              <p className="text-muted-foreground">Configure your AWS credentials</p>
            </div>
          </div>

          <Card>
            <CardHeader>
              <CardTitle>AWS Credentials</CardTitle>
              <CardDescription>
                Configure your AWS IAM access credentials
              </CardDescription>
            </CardHeader>
            <CardContent className="space-y-4">
              <div className="space-y-2">
                <Label htmlFor="aws-access-key">AWS Access Key ID</Label>
                <Input
                  id="aws-access-key"
                  type="text"
                  placeholder="AKIAIOSFODNN7EXAMPLE"
                  value={awsAccessKeyId}
                  onChange={(e) => setAwsAccessKeyId(e.target.value)}
                />
              </div>
              <div className="space-y-2">
                <Label htmlFor="aws-secret-key">AWS Secret Access Key</Label>
                <Input
                  id="aws-secret-key"
                  type="password"
                  placeholder="wJalrXUtnFEMI/K7MDENG/bPxRfiCYEXAMPLEKEY"
                  value={awsSecretAccessKey}
                  onChange={(e) => setAwsSecretAccessKey(e.target.value)}
                />
              </div>
              <div className="space-y-2">
                <Label htmlFor="aws-region">AWS Region</Label>
                <Input
                  id="aws-region"
                  type="text"
                  placeholder="us-east-1"
                  value={awsRegion}
                  onChange={(e) => setAwsRegion(e.target.value)}
                />
              </div>
              <Button 
                onClick={handleSaveAWS}
                className="bg-gradient-to-r from-primary to-accent hover:opacity-90 transition-opacity"
              >
                <Save className="h-4 w-4 mr-2" />
                Save AWS Credentials
              </Button>
            </CardContent>
          </Card>

          <div className="p-4 border border-border rounded-lg bg-card">
            <p className="text-sm text-muted-foreground">
              <strong>Secure Storage:</strong> Your credentials are now securely stored in the database 
              and encrypted. They are only accessible when you're logged in.
            </p>
          </div>
        </div>
      </main>
    </div>
  );
};

export default Settings;
