"use client";

import { useState } from "react";
import { DocumentUpload } from "@/components/DocumentUpload";
import { MetadataDisplay } from "@/components/MetadataDisplay";
import { Button } from "@/components/ui/button";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { analyzeContractRisk } from "@/ai/flows/analyze-contract-risk";
import { Toaster } from "@/components/ui/toaster";

export default function Home() {
  const [documentText, setDocumentText] = useState<string | null>(null);
  const [analysisResults, setAnalysisResults] = useState<any | null>(null);

  const handleDocumentUpload = (text: string) => {
    setDocumentText(text);
    setAnalysisResults(null); // Clear previous results
  };

  const handleAnalyze = async () => {
    if (documentText) {
      try {
        const results = await analyzeContractRisk({ documentText });
        setAnalysisResults(results);
      } catch (error) {
        console.error("Error analyzing contract:", error);
        // Handle error appropriately (e.g., display an error message)
      }
    }
  };

  return (
    <div className="container mx-auto p-4">
      <Toaster />
      <h1 className="text-2xl font-semibold mb-4">ContractIQ</h1>
      <div className="grid gap-4 grid-cols-1 md:grid-cols-2">
        <Card>
          <CardHeader>
            <CardTitle>Document Upload</CardTitle>
          </CardHeader>
          <CardContent>
            <DocumentUpload onDocumentUpload={handleDocumentUpload} />
            {documentText && (
              <Button onClick={handleAnalyze} className="mt-4">
                Analyze Contract
              </Button>
            )}
          </CardContent>
        </Card>
        <Card>
          <CardHeader>
            <CardTitle>Analysis Results</CardTitle>
          </CardHeader>
          <CardContent>
            {analysisResults ? (
              <p>Analysis Results available in Metadata Display</p>
            ) : (
              <p>No analysis results yet. Upload a document and click Analyze.</p>
            )}
          </CardContent>
        </Card>
      </div>
      <div className="mt-4">
        {analysisResults && (
          <MetadataDisplay results={analysisResults} documentText={documentText || ''} />
        )}
      </div>
    </div>
  );
}
