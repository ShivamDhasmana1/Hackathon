import { CheckCircle, AlertCircle, Clock, ShieldCheck } from "lucide-react";
import { Card } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";

interface Decision {
  status: "approved" | "manual_review" | "rejected";
  auto_approve: boolean;
  risk_level: "low" | "medium" | "high";
  summary: string;
  reasons: string[];
}

interface DecisionResultProps {
  requestId: string;
  decision: Decision;
}

const DecisionResult = ({ requestId, decision }: DecisionResultProps) => {
  const getStatusConfig = () => {
    switch (decision.status) {
      case "approved":
        return {
          icon: <CheckCircle className="w-12 h-12" />,
          color: "text-success",
          bgColor: "bg-success/10",
          borderColor: "border-success/20",
          label: "Approved",
          badgeVariant: "default" as const,
        };
      case "manual_review":
        return {
          icon: <Clock className="w-12 h-12" />,
          color: "text-warning",
          bgColor: "bg-warning/10",
          borderColor: "border-warning/20",
          label: "Manual Review Required",
          badgeVariant: "secondary" as const,
        };
      case "rejected":
        return {
          icon: <AlertCircle className="w-12 h-12" />,
          color: "text-destructive",
          bgColor: "bg-destructive/10",
          borderColor: "border-destructive/20",
          label: "Rejected",
          badgeVariant: "destructive" as const,
        };
    }
  };

  const getRiskBadgeColor = () => {
    switch (decision.risk_level) {
      case "low":
        return "bg-success/10 text-success border-success/20";
      case "medium":
        return "bg-warning/10 text-warning border-warning/20";
      case "high":
        return "bg-destructive/10 text-destructive border-destructive/20";
    }
  };

  const statusConfig = getStatusConfig();

  return (
    <Card className="p-8 max-w-2xl mx-auto shadow-[var(--shadow-card)] border-2">
      <div className="text-center mb-6">
        <div
          className={`inline-flex p-4 rounded-full mb-4 ${statusConfig.bgColor} ${statusConfig.color}`}
        >
          {statusConfig.icon}
        </div>
        <h2 className="text-3xl font-bold mb-2 text-foreground">
          {statusConfig.label}
        </h2>
        <p className="text-muted-foreground mb-4">{decision.summary}</p>
        <div className="flex items-center justify-center gap-3 flex-wrap">
          <Badge variant={statusConfig.badgeVariant} className="text-sm px-3 py-1">
            {statusConfig.label}
          </Badge>
          <Badge
            variant="outline"
            className={`text-sm px-3 py-1 ${getRiskBadgeColor()}`}
          >
            {decision.risk_level.toUpperCase()} Risk
          </Badge>
        </div>
      </div>

      <div className="space-y-4 mb-6">
        <div className="bg-muted/50 rounded-lg p-4">
          <h3 className="text-sm font-semibold text-muted-foreground mb-3 flex items-center gap-2">
            <ShieldCheck className="w-4 h-4" />
            Verification Timeline
          </h3>
          <div className="space-y-2">
            {[
              "Document uploaded and validated",
              "Face verification completed",
              "Liveness check performed",
              `Decision: ${statusConfig.label}`,
            ].map((step, index) => (
              <div key={index} className="flex items-center gap-3">
                <div className="w-2 h-2 rounded-full bg-primary"></div>
                <p className="text-sm text-foreground">{step}</p>
              </div>
            ))}
          </div>
        </div>

        {decision.reasons.length > 0 && (
          <div className="bg-card border border-border rounded-lg p-4">
            <h3 className="text-sm font-semibold text-foreground mb-3">
              Details
            </h3>
            <ul className="space-y-2">
              {decision.reasons.map((reason, index) => (
                <li
                  key={index}
                  className="text-sm text-muted-foreground flex items-start gap-2"
                >
                  <span className="text-primary mt-1">•</span>
                  <span>{reason}</span>
                </li>
              ))}
            </ul>
          </div>
        )}
      </div>

      <div className="pt-4 border-t border-border">
        <p className="text-xs text-muted-foreground text-center">
          Request ID: <span className="font-mono">{requestId}</span>
        </p>
      </div>
    </Card>
  );
};

export default DecisionResult;
