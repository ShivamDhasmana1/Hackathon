import { useState, useRef, useEffect } from "react";
import { Camera, Check } from "lucide-react";
import { Button } from "@/components/ui/button";

interface SelfieCaptureProps {
  onCapture: (blob: Blob) => void;
  capturedImage: string | null;
}

const SelfieCapture = ({ onCapture, capturedImage }: SelfieCaptureProps) => {
  const videoRef = useRef<HTMLVideoElement>(null);
  const canvasRef = useRef<HTMLCanvasElement>(null);
  const [stream, setStream] = useState<MediaStream | null>(null);
  const [cameraReady, setCameraReady] = useState(false);
  const [error, setError] = useState<string | null>(null);

  // Initialize camera on component mount
  useEffect(() => {
    startCamera();
    return () => {
      stopCamera();
    };
  }, []);

  const startCamera = async () => {
    try {
      const mediaStream = await navigator.mediaDevices.getUserMedia({
        video: { facingMode: "user", width: { ideal: 1280 }, height: { ideal: 720 } },
      });
      
      if (videoRef.current) {
        videoRef.current.srcObject = mediaStream;
        setStream(mediaStream);
        setCameraReady(true);
        setError(null);
      }
    } catch (err) {
      console.error("Error accessing camera:", err);
      setError("Unable to access camera. Please grant camera permissions.");
    }
  };

  const stopCamera = () => {
    if (stream) {
      stream.getTracks().forEach((track) => track.stop());
      setStream(null);
      setCameraReady(false);
    }
  };

  const capturePhoto = () => {
    if (!videoRef.current || !canvasRef.current) return;

    const video = videoRef.current;
    const canvas = canvasRef.current;
    
    // Set canvas dimensions to match video
    canvas.width = video.videoWidth;
    canvas.height = video.videoHeight;

    // Draw video frame to canvas
    const ctx = canvas.getContext("2d");
    if (ctx) {
      ctx.drawImage(video, 0, 0, canvas.width, canvas.height);
      
      // Convert canvas to blob
      canvas.toBlob((blob) => {
        if (blob) {
          onCapture(blob);
          stopCamera(); // Stop camera after capture
        }
      }, "image/jpeg", 0.95);
    }
  };

  const retake = () => {
    onCapture(null as any);
    startCamera();
  };

  return (
    <div className="space-y-4">
      <div className="bg-muted/50 border border-border rounded-lg p-4 mb-4">
        <div className="flex items-start gap-3">
          <Camera className="w-5 h-5 text-primary flex-shrink-0 mt-0.5" />
          <div className="text-sm">
            <p className="font-medium text-foreground mb-1">Liveness Check Instructions</p>
            <ul className="text-muted-foreground space-y-1">
              <li>• Look straight into the camera</li>
              <li>• Ensure your face is well-lit and clearly visible</li>
              <li>• Blink once before capturing to confirm liveness</li>
            </ul>
          </div>
        </div>
      </div>

      {error && (
        <div className="bg-destructive/10 border border-destructive text-destructive rounded-lg p-4 text-sm">
          {error}
        </div>
      )}

      <div className="relative rounded-xl overflow-hidden bg-muted border border-border">
        {!capturedImage ? (
          <>
            <video
              ref={videoRef}
              autoPlay
              playsInline
              muted
              className="w-full h-auto max-h-[400px] object-cover"
            />
            <canvas ref={canvasRef} className="hidden" />
            
            {cameraReady && (
              <div className="absolute bottom-4 left-1/2 -translate-x-1/2">
                <Button
                  type="button"
                  onClick={capturePhoto}
                  size="lg"
                  className="bg-primary hover:bg-primary/90 shadow-[var(--shadow-button)]"
                >
                  <Camera className="w-5 h-5 mr-2" />
                  Capture Selfie
                </Button>
              </div>
            )}

            {!cameraReady && !error && (
              <div className="absolute inset-0 flex items-center justify-center bg-muted">
                <div className="text-center">
                  <div className="inline-block animate-spin rounded-full h-8 w-8 border-b-2 border-primary mb-2"></div>
                  <p className="text-sm text-muted-foreground">Starting camera...</p>
                </div>
              </div>
            )}
          </>
        ) : (
          <div className="relative">
            <img
              src={capturedImage}
              alt="Captured selfie"
              className="w-full h-auto max-h-[400px] object-cover"
            />
            <div className="absolute top-4 right-4 bg-success text-success-foreground rounded-full p-2 shadow-lg">
              <Check className="w-6 h-6" />
            </div>
            <div className="absolute bottom-4 left-1/2 -translate-x-1/2">
              <Button
                type="button"
                onClick={retake}
                variant="secondary"
                size="lg"
              >
                Retake Photo
              </Button>
            </div>
          </div>
        )}
      </div>
    </div>
  );
};

export default SelfieCapture;
