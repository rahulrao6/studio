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
              <h3 className="text-lg font-semibold">Key Dates:</h3>
              {results.keyDates.length > 0 ? (
                <ul className="list-disc pl-5">
                  {results.keyDates.map((date: string, index: number) => (
                    <li key={index}>{date}</li>
                  ))}
                </ul>
              ) : (
                <p>No key dates found.</p>
              )}
            </div>

            <div>
              <h3 className="text-lg font-semibold">Risk Clauses:</h3>
              {results.riskClauses.length > 0 ? (
                <Accordion type="single" collapsible>
                  {results.riskClauses.map((clause: any, index: number) => (
                    <AccordionItem key={index} value={`clause-${index}`}>
                      <AccordionTrigger>
                        Clause {index + 1} - {clause.riskCategory}
                      </AccordionTrigger>
                      <AccordionContent>
                        <p>{clause.clauseText}</p>
                        <p>Confidence Score: {clause.confidenceScore}</p>
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
