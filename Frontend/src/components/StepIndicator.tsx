import { Check } from "lucide-react";

interface StepIndicatorProps {
  currentStep: number;
  totalSteps: number;
}

const StepIndicator = ({ currentStep, totalSteps }: StepIndicatorProps) => {
  const steps = [
    { number: 1, label: "Upload ID" },
    { number: 2, label: "Capture Selfie" },
  ];

  return (
    <div className="flex items-center justify-center mb-8">
      {steps.map((step, index) => (
        <div key={step.number} className="flex items-center">
          <div className="flex flex-col items-center">
            <div
              className={`w-10 h-10 rounded-full flex items-center justify-center font-semibold transition-all duration-300 ${
                currentStep > step.number
                  ? "bg-success text-success-foreground"
                  : currentStep === step.number
                  ? "bg-primary text-primary-foreground shadow-[var(--shadow-button)]"
                  : "bg-secondary text-secondary-foreground"
              }`}
            >
              {currentStep > step.number ? (
                <Check className="w-5 h-5" />
              ) : (
                step.number
              )}
            </div>
            <span
              className={`mt-2 text-sm font-medium ${
                currentStep >= step.number
                  ? "text-foreground"
                  : "text-muted-foreground"
              }`}
            >
              {step.label}
            </span>
          </div>
          {index < steps.length - 1 && (
            <div
              className={`w-24 h-1 mx-4 rounded transition-all duration-300 ${
                currentStep > step.number ? "bg-success" : "bg-border"
              }`}
            />
          )}
        </div>
      ))}
    </div>
  );
};

export default StepIndicator;
