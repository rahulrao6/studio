"use client";

import { useState, useCallback } from "react";
import { Button } from "@/components/ui/button";
import { Textarea } from "@/components/ui/textarea";

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
      <Textarea
        placeholder="Paste contract text here..."
        className="w-full h-48 mb-4"
        value={documentText}
        onChange={handleTextChange}
      />
      <Button onClick={handleUpload}>Upload</Button>
    </div>
  );
};
