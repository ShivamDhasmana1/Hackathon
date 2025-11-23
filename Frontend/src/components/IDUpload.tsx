import { useState, useRef } from "react";
import { Upload, FileCheck, X } from "lucide-react";
import { Button } from "@/components/ui/button";

interface IDUploadProps {
  onFileSelect: (file: File) => void;
  selectedFile: File | null;
}

const IDUpload = ({ onFileSelect, selectedFile }: IDUploadProps) => {
  const [preview, setPreview] = useState<string | null>(null);
  const fileInputRef = useRef<HTMLInputElement>(null);

  const handleChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    e.preventDefault();
    if (e.target.files && e.target.files[0]) {
      handleFile(e.target.files[0]);
    }
  };

  const handleFile = (file: File) => {
    // Validate file type
    if (!file.type.match(/image\/(jpeg|jpg|png)/)) {
      alert("Please upload a valid image file (JPG, JPEG, or PNG)");
      return;
    }

    // Validate file size (max 10MB)
    if (file.size > 10 * 1024 * 1024) {
      alert("File size must be less than 10MB");
      return;
    }

    onFileSelect(file);

    // Create preview
    const reader = new FileReader();
    reader.onload = (e) => {
      setPreview(e.target?.result as string);
    };
    reader.readAsDataURL(file);
  };

  const handleRemove = () => {
    setPreview(null);
    onFileSelect(null as any);
    if (fileInputRef.current) {
      fileInputRef.current.value = "";
    }
  };

  return (
    <div className="space-y-4">
      {!selectedFile ? (
        <div className="text-center">
          <input
            ref={fileInputRef}
            type="file"
            accept="image/jpeg,image/jpg,image/png"
            onChange={handleChange}
            className="hidden"
            id="id-upload"
          />
          <Button 
            type="button" 
            variant="outline" 
            size="lg"
            onClick={() => fileInputRef.current?.click()}
            className="w-full max-w-md"
          >
            <Upload className="w-5 h-5 mr-2" />
            Upload ID Document
          </Button>
          <p className="text-xs text-muted-foreground mt-3">
            Supports: JPG, JPEG, PNG (Max 10MB)
          </p>
        </div>
      ) : (
        <div className="border border-border rounded-xl p-4 bg-card">
          <div className="flex items-start gap-4">
            {preview && (
              <img
                src={preview}
                alt="ID preview"
                className="w-24 h-24 object-cover rounded-lg border border-border"
              />
            )}
            <div className="flex-1 min-w-0">
              <div className="flex items-center gap-2 mb-1">
                <FileCheck className="w-5 h-5 text-success flex-shrink-0" />
                <h4 className="font-semibold text-foreground truncate">
                  {selectedFile.name}
                </h4>
              </div>
              <p className="text-sm text-muted-foreground">
                {(selectedFile.size / 1024 / 1024).toFixed(2)} MB
              </p>
            </div>
            <Button
              type="button"
              variant="ghost"
              size="sm"
              onClick={handleRemove}
              className="flex-shrink-0"
            >
              <X className="w-4 h-4" />
            </Button>
          </div>
        </div>
      )}
    </div>
  );
};

export default IDUpload;
