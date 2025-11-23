import { Shield, Lock, Zap } from "lucide-react";
import KYCWizard from "@/components/KYCWizard";

const Index = () => {
  return (
    <div className="min-h-screen bg-[var(--gradient-bg)]">
      {/* Header */}
      <header className="border-b border-border bg-card/50 backdrop-blur-sm sticky top-0 z-10">
        <div className="container mx-auto px-4 py-4">
          <div className="flex items-center justify-between">
            <div className="flex items-center gap-2">
              <Shield className="w-8 h-8 text-primary" />
              <h1 className="text-2xl font-bold bg-[var(--gradient-primary)] bg-clip-text text-transparent">
                SecureKYC
              </h1>
            </div>
            <div className="hidden md:flex items-center gap-6 text-sm text-muted-foreground">
              <div className="flex items-center gap-2">
                <Lock className="w-4 h-4" />
                <span>Bank-grade Security</span>
              </div>
              <div className="flex items-center gap-2">
                <Zap className="w-4 h-4" />
                <span>Instant Verification</span>
              </div>
            </div>
          </div>
        </div>
      </header>

      {/* Main Content */}
      <main className="container mx-auto px-4 py-12">
        {/* Hero Section */}
        <div className="text-center mb-12 max-w-3xl mx-auto">
          <h2 className="text-4xl md:text-5xl font-bold mb-4 text-foreground">
            AI-Powered KYC Verification
          </h2>
          <p className="text-lg text-muted-foreground mb-8">
            Secure, fast, and automated identity verification powered by advanced AI.
            Complete your onboarding in minutes with our streamlined process.
          </p>
          
          {/* Trust Indicators */}
          <div className="flex items-center justify-center gap-8 flex-wrap text-sm">
            <div className="flex items-center gap-2 text-muted-foreground">
              <div className="w-2 h-2 rounded-full bg-success"></div>
              <span>256-bit Encryption</span>
            </div>
            <div className="flex items-center gap-2 text-muted-foreground">
              <div className="w-2 h-2 rounded-full bg-success"></div>
              <span>GDPR Compliant</span>
            </div>
            <div className="flex items-center gap-2 text-muted-foreground">
              <div className="w-2 h-2 rounded-full bg-success"></div>
              <span>99.9% Uptime</span>
            </div>
          </div>
        </div>

        {/* KYC Wizard */}
        <KYCWizard />
      </main>
    </div>
  );
};

export default Index;
