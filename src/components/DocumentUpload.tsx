"use client";

import { useState, useCallback } from "react";
import { Button } from "@/components/ui/button";
import { Textarea } from "@/components/ui/textarea";
import { Label } from "@/components/ui/label";

interface DocumentUploadProps {
  onDocumentUpload: (text: string) => void;
}

export const DocumentUpload: React.FC<DocumentUploadProps> = ({ onDocumentUpload }) => {
  const [documentText, setDocumentText] = useState("");

  const handleTextChange = useCallback((event: React.ChangeEvent<HTMLTextAreaElement>) => {
    setDocumentText(event.target.value);
  }, []);

  const handleUpload = () => {
    onDocumentUpload(documentText);
  };

  return (
    <div>
      <Label htmlFor="contract-text">Paste Contract Text Here</Label>
      <Textarea
        id="contract-text"
        placeholder="Enter contract text..."
        className="w-full h-48 mb-4"
        value={documentText}
        onChange={handleTextChange}
      />
      <Button onClick={handleUpload}>Upload</Button>
    </div>
  );
};
