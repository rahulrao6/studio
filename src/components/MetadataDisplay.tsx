"use client";

import { Badge } from "@/components/ui/badge";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { ScrollArea } from "@/components/ui/scroll-area";
import { Accordion, AccordionContent, AccordionItem, AccordionTrigger } from "@/components/ui/accordion";

interface MetadataDisplayProps {
  results: any;
  documentText: string;
}

export const MetadataDisplay: React.FC<MetadataDisplayProps> = ({ results, documentText }) => {
  return (
    <Card>
      <CardHeader>
        <CardTitle>Contract Metadata</CardTitle>
      </CardHeader>
      <CardContent>
        {results ? (
          <>
            <div className="mb-4">
              <h3 className="text-lg font-semibold">Overall Risk Score:</h3>
              <Badge variant="secondary">{results.overallRiskScore}</Badge>
            </div>

            <div className="mb-4">
              <h3 className="text-lg font-semibold">Effective Date:</h3>
              <p>{results.metadata.effectiveDate || 'Not specified'}</p>
            </div>

            <div className="mb-4">
              <h3 className="text-lg font-semibold">Parties:</h3>
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

            <div className="mb-4">
              <h3 className="text-lg font-semibold">Definitions:</h3>
              {Object.keys(results.metadata.definitions).length > 0 ? (
                <Accordion type="single" collapsible>
                  {Object.entries(results.metadata.definitions).map(([term, definition], index) => (
                    <AccordionItem key={index} value={`definition-${index}`}>
                      <AccordionTrigger>
                        {term}
                      </AccordionTrigger>
                      <AccordionContent>
                        {definition}
                      </AccordionContent>
                    </AccordionItem>
                  ))}
                </Accordion>
              ) : (
                <p>No definitions found.</p>
              )}
            </div>

            <div className="mb-4">
              <h3 className="text-lg font-semibold">Key Dates:</h3>
              {results.metadata.renewalDeadline || results.metadata.optOutDeadline ? (
                <ul className="list-disc pl-5">
                  {results.metadata.renewalDeadline && <li>Renewal Deadline: {results.metadata.renewalDeadline}</li>}
                  {results.metadata.optOutDeadline && <li>Opt-Out Deadline: {results.metadata.optOutDeadline}</li>}
                </ul>
              ) : (
                <p>No key dates found.</p>
              )}
            </div>

            <div>
              <h3 className="text-lg font-semibold">Risk Clauses:</h3>
              {results.riskItems.length > 0 ? (
                <Accordion type="single" collapsible>
                  {results.riskItems.map((clause: any, index: number) => (
                    <AccordionItem key={index} value={`clause-${index}`}>
                      <AccordionTrigger>
                        Clause {index + 1} - {clause.riskCategory}
                      </AccordionTrigger>
                      <AccordionContent>
                        <p>{clause.clauseText}</p>
                        <p>Confidence Score: {clause.confidenceScore}</p>
                        <p>Suggested Fix: {clause.suggestedFix}</p>
                        <p>Clarifying Question: {clause.clarifyingQuestion}</p>
                        <p>Industry Prevalence: {clause.industryPrevalence}</p>
                      </AccordionContent>
                    </AccordionItem>
                  ))}
                </Accordion>
              ) : (
                <p>No risk clauses found.</p>
              )}
            </div>
          </>
        ) : (
          <p>No metadata to display.</p>
        )}
      </CardContent>
    </Card>
  );
};
