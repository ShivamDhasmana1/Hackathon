import { useState } from "react";
import { Shield, Loader2 } from "lucide-react";
import { Button } from "@/components/ui/button";
import { Card } from "@/components/ui/card";
import { toast } from "sonner";
import StepIndicator from "./StepIndicator";
import IDUpload from "./IDUpload";
import SelfieCapture from "./SelfieCapture";
import DecisionResult from "./DecisionResult";

// API base URL - update this to your backend URL
const API_BASE_URL = "https://sociogenetic-babblingly-darien.ngrok-free.dev";

interface Decision {
  status: "approved" | "manual_review" | "rejected";
  auto_approve: boolean;
  risk_level: "low" | "medium" | "high";
  summary: string;
  reasons: string[];
}

interface AnalysisResponse {
  request_id: string;
  decision: Decision;
}

const KYCWizard = () => {
  const [currentStep, setCurrentStep] = useState(1);
  const [idDocument, setIdDocument] = useState<File | null>(null);
  const [selfieBlob, setSelfieBlob] = useState<Blob | null>(null);
  const [selfiePreview, setSelfiePreview] = useState<string | null>(null);
  const [isSubmitting, setIsSubmitting] = useState(false);
  const [result, setResult] = useState<AnalysisResponse | null>(null);

  const handleIdSelect = (file: File) => {
    setIdDocument(file);
    if (file) {
      // Auto-advance to next step after small delay
      setTimeout(() => setCurrentStep(2), 300);
    }
  };

  const handleSelfieCapture = (blob: Blob) => {
    setSelfieBlob(blob);
    
    // Create preview URL from blob
    if (blob) {
      const url = URL.createObjectURL(blob);
      setSelfiePreview(url);
    } else {
      setSelfiePreview(null);
    }
  };

  const handleSubmit = async () => {
    if (!idDocument || !selfieBlob) {
      toast.error("Please complete all steps before submitting");
      return;
    }

    setIsSubmitting(true);

    try {
      // Prepare FormData
      const formData = new FormData();
      formData.append("id_document", idDocument);
      formData.append("selfie", selfieBlob, "selfie.jpg");

      // Make API call
      const response = await fetch(`${API_BASE_URL}/analyze_kyc`, {
        method: "POST",
        body: formData,
      });

      if (!response.ok) {
        throw new Error(`API Error: ${response.status} ${response.statusText}`);
      }

      const data: AnalysisResponse = await response.json();
      
      // Set result and show success toast
      setResult(data);
      toast.success("Verification completed successfully!");
      
    } catch (error) {
      console.error("Error submitting KYC:", error);
      toast.error(
        "Something went wrong during verification. Please try again or contact support."
      );
    } finally {
      setIsSubmitting(false);
    }
  };

  const handleReset = () => {
    setCurrentStep(1);
    setIdDocument(null);
    setSelfieBlob(null);
    setSelfiePreview(null);
    setResult(null);
  };

  // Show result if available
  if (result) {
    return (
      <div className="space-y-6">
        <DecisionResult requestId={result.request_id} decision={result.decision} />
        <div className="text-center">
          <Button onClick={handleReset} variant="outline" size="lg">
            Start New Verification
          </Button>
        </div>
      </div>
    );
  }

  return (
    <Card className="p-8 max-w-3xl mx-auto shadow-[var(--shadow-card)]">
      <StepIndicator currentStep={currentStep} totalSteps={2} />

      <div className="space-y-6">
        {/* Step 1: ID Upload */}
        <div className={currentStep === 1 ? "block" : "hidden"}>
          <div className="text-center mb-6">
            <h2 className="text-2xl font-bold text-foreground mb-2">
              Upload Your ID Document
            </h2>
            <p className="text-muted-foreground">
              Please provide a clear photo of your government-issued ID
            </p>
          </div>
          <IDUpload onFileSelect={handleIdSelect} selectedFile={idDocument} />
        </div>

        {/* Step 2: Selfie Capture */}
        <div className={currentStep === 2 ? "block" : "hidden"}>
          <div className="text-center mb-6">
            <h2 className="text-2xl font-bold text-foreground mb-2">
              Capture Your Selfie
            </h2>
            <p className="text-muted-foreground">
              Take a live photo to verify your identity
            </p>
          </div>
          <SelfieCapture
            onCapture={handleSelfieCapture}
            capturedImage={selfiePreview}
          />
        </div>

        {/* Navigation Buttons */}
        <div className="flex items-center justify-between pt-6 border-t border-border">
          <Button
            type="button"
            variant="outline"
            onClick={() => setCurrentStep(Math.max(1, currentStep - 1))}
            disabled={currentStep === 1 || isSubmitting}
          >
            Back
          </Button>

          {currentStep < 2 ? (
            <Button
              type="button"
              onClick={() => setCurrentStep(2)}
              disabled={!idDocument}
            >
              Continue
            </Button>
          ) : (
            <Button
              type="button"
              onClick={handleSubmit}
              disabled={!idDocument || !selfieBlob || isSubmitting}
              className="min-w-[200px]"
            >
              {isSubmitting ? (
                <>
                  <Loader2 className="w-4 h-4 mr-2 animate-spin" />
                  Verifying...
                </>
              ) : (
                <>
                  <Shield className="w-4 h-4 mr-2" />
                  Submit for Verification
                </>
              )}
            </Button>
          )}
        </div>
      </div>
    </Card>
  );
};

export default KYCWizard;
