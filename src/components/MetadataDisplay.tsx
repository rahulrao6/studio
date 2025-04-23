"use client";

import React from "react"; // Import React
import { Badge } from "@/components/ui/badge";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { ScrollArea } from "@/components/ui/scroll-area";
import { Accordion, AccordionContent, AccordionItem, AccordionTrigger } from "@/components/ui/accordion";
import { Separator } from "@/components/ui/separator";

interface MetadataDisplayProps {
  results: any;
  documentText: string;
}

const CardDescription = React.forwardRef<
  HTMLDivElement,
  React.HTMLAttributes<HTMLDivElement>
>(({ className, ...props }, ref) => (
  <div
    ref={ref}
    className={cn("text-sm text-muted-foreground", className)}
    {...props}
  />
))
CardDescription.displayName = "CardDescription";

function cn(...inputs: (string | undefined | null)[]): string {
  return inputs.filter(Boolean).join(' ');
}

export const MetadataDisplay: React.FC<MetadataDisplayProps> = ({ results, documentText }) => {
  return (
    <Card>
      <CardHeader>
        <CardTitle>Contract Analysis Results</CardTitle>
        <CardDescription>
          Detailed metadata and risk analysis of the contract.
        </CardDescription>
      </CardHeader>
      <CardContent>
        {results ? (
          <ScrollArea className="h-[600px] w-full">
            <div className="mb-6">
              <h2 className="text-lg font-semibold mb-2">Executive Summary</h2>
              <p className="mb-4">{results.executiveSummary.overall}</p>

              <h3 className="text-md font-semibold mb-2">Section Summaries</h3>
              {results.executiveSummary.sections.map((section: any, index: number) => (
                <div key={index} className="mb-4">
                  <h4 className="font-semibold">{section.sectionTitle}</h4>
                  <p>{section.summary}</p>
                  {section.highestRiskClause && (
                    <p className="text-sm italic mt-1">
                      Highest Risk Clause: {section.highestRiskClause}
                    </p>
                  )}
                </div>
              ))}
            </div>

            <Separator className="my-4" />

            <div className="mb-6">
              <h2 className="text-lg font-semibold mb-2">Contract Metadata</h2>
              <div className="grid gap-4">
                <div>
                  <h3 className="text-md font-semibold">Effective Date</h3>
                  <p>{results.metadata.effectiveDate || "Not specified"}</p>
                </div>

                <div>
                  <h3 className="text-md font-semibold">Renewal Deadline</h3>
                  <p>{results.metadata.renewalDeadline || "Not specified"}</p>
                </div>

                <div>
                  <h3 className="text-md font-semibold">Opt-Out Deadline</h3>
                  <p>{results.metadata.optOutDeadline || "Not specified"}</p>
                </div>

                <div>
                  <h3 className="text-md font-semibold">Governing Law</h3>
                  <p>{results.metadata.governingLaw || "Not specified"}</p>
                </div>

                <div>
                  <h3 className="text-md font-semibold">Venue</h3>
                  <p>{results.metadata.venue || "Not specified"}</p>
                </div>

                <div>
                  <h3 className="text-md font-semibold">Parties</h3>
                  {results.metadata.parties.length > 0 ? (
                    <ul className="list-disc pl-5">
                      {results.metadata.parties.map((party: string, index: number) => (
                        <li key={index}>{party}</li>
                      ))}
                    </ul>
                  ) : (
                    <p>No parties found.</p>
                  )}
                </div>

                <div>
                  <h3 className="text-md font-semibold">SLA References</h3>
                  {results.metadata.slaReferences && results.metadata.slaReferences.length > 0 ? (
                    <ul className="list-disc pl-5">
                      {results.metadata.slaReferences.map((sla: string, index: number) => (
                        <li key={index}>{sla}</li>
                      ))}
                    </ul>
                  ) : (
                    <p>No SLA references found.</p>
                  )}
                </div>
              </div>
            </div>

            <Separator className="my-4" />

            <div className="mb-6">
              <h2 className="text-lg font-semibold mb-2">Definitions</h2>
              {Object.keys(results.metadata.definitions).length > 0 ? (
                <Accordion type="single" collapsible>
                  {Object.entries(results.metadata.definitions).map(([term, definition], index) => (
                    <AccordionItem key={index} value={`definition-${index}`}>
                      <AccordionTrigger>{term}</AccordionTrigger>
                      <AccordionContent>{definition}</AccordionContent>
                    </AccordionItem>
                  ))}
                </Accordion>
              ) : (
                <p>No definitions found.</p>
              )}
            </div>

            <Separator className="my-4" />

            <div className="mb-6">
              <h2 className="text-lg font-semibold mb-2">Risk Analysis</h2>
              <div className="mb-4">
                <h3 className="text-md font-semibold">Overall Risk Score</h3>
                <Badge variant="secondary">{results.overallRiskScore}</Badge>
                <h3 className="text-md font-semibold mt-2">Regulatory Compliance Score</h3>
                <Badge variant="secondary">{results.regulatoryComplianceScore}</Badge>
              </div>
              {results.riskItems.length > 0 ? (
                <Accordion type="single" collapsible>
                  {results.riskItems.map((clause: any, index: number) => (
                    <AccordionItem key={index} value={`clause-${index}`}>
                      <AccordionTrigger>
                        Clause {index + 1} - {clause.riskCategory}
                      </AccordionTrigger>
                      <AccordionContent>
                        <p className="mb-2">
                          <strong>Clause Text:</strong> {clause.clauseText}
                        </p>
                        <p className="mb-2">
                          <strong>Confidence Score:</strong> {clause.confidenceScore}
                        </p>
                        <p className="mb-2">
                          <strong>Suggested Fix:</strong> {clause.suggestedFix}
                        </p>
                        <p className="mb-2">
                          <strong>Clarifying Question:</strong> {clause.clarifyingQuestion}
                        </p>
                        <p className="mb-2">
                          <strong>Industry Prevalence:</strong> {clause.industryPrevalence}
                        </p>
                      </AccordionContent>
                    </AccordionItem>
                  ))}
                </Accordion>
              ) : (
                <p>No risk clauses found.</p>
              )}
            </div>

            <Separator className="my-4" />

            <div>
              <h2 className="text-lg font-semibold mb-2">Negotiation Points</h2>
              {results.negotiationPoints.length > 0 ? (
                <ul className="list-disc pl-5">
                  {results.negotiationPoints.map((point: string, index: number) => (
                    <li key={index}>{point}</li>
                  ))}
                </ul>
              ) : (
                <p>No negotiation points found.</p>
              )}
            </div>
          </ScrollArea>
        ) : (
          <p>No metadata to display.</p>
        )}
      </CardContent>
    </Card>
  );
};
