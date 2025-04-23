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
  const [isLoading, setIsLoading] = useState(false);

  const handleDocumentUpload = (text: string) => {
    setDocumentText(text);
    setAnalysisResults(null); // Clear previous results
  };

  const handleAnalyze = async () => {
    if (documentText) {
      setIsLoading(true);
      try {
        const results = await analyzeContractRisk({ documentText });
        setAnalysisResults(results);
      } catch (error) {
        console.error("Error analyzing contract:", error);
        // Handle error appropriately (e.g., display an error message)
      } finally {
        setIsLoading(false);
      }
    }
  };

  return (
    <div className="container mx-auto p-4">
      <Toaster />
      <h1 className="text-3xl font-semibold mb-4 text-center">ContractIQ</h1>
      <div className="grid gap-6 grid-cols-1 md:grid-cols-2">
        <Card>
          <CardHeader>
            <CardTitle>Document Upload</CardTitle>
          </CardHeader>
          <CardContent>
            <DocumentUpload onDocumentUpload={handleDocumentUpload} />
            <Button onClick={handleAnalyze} className="mt-4" disabled={isLoading}>
              {isLoading ? "Analyzing..." : "Analyze Contract"}
            </Button>
          </CardContent>
        </Card>
        {analysisResults && (
          <Card>
            <CardHeader>
              <CardTitle>Analysis Results</CardTitle>
            </CardHeader>
            <CardContent>
              <MetadataDisplay results={analysisResults} documentText={documentText || ''} />
            </CardContent>
          </Card>
        )}
      </div>
    </div>
  );
}
