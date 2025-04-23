// src/ai/flows/analyze-contract-risk.ts
'use server';
/**
 * @fileOverview Analyzes contract documents and identifies potential risks.
 *
 * - analyzeContractRisk - A function that analyzes contract risk.
 * - AnalyzeContractRiskInput - The input type for the analyzeContractRisk function.
 * - AnalyzeContractRiskOutput - The return type for the analyzeContractRisk function.
 */

import {ai} from '@/ai/ai-instance';
import {z} from 'genkit';
import {getDocumentMetadata} from '@/services/document-metadata';

const AnalyzeContractRiskInputSchema = z.object({
  documentText: z.string().describe('The text content of the contract document.'),
});
export type AnalyzeContractRiskInput = z.infer<typeof AnalyzeContractRiskInputSchema>;

const AnalyzeContractRiskOutputSchema = z.object({
  overallRiskScore: z.number().describe('The overall risk score of the contract (0-100).'),
  riskClauses: z.array(
    z.object({
      clauseText: z.string().describe('The text of the risky clause.'),
      riskCategory: z.string().describe('The category of risk associated with the clause.'),
      confidenceScore: z.number().describe('The confidence score (0-1) of the risk assessment.'),
    })
  ).
    describe('A list of clauses identified as potentially risky.'),
  keyDates: z.array(z.string().describe('Key dates identified in the contract related to risk.')).describe('Key dates related to risk'),
});
export type AnalyzeContractRiskOutput = z.infer<typeof AnalyzeContractRiskOutputSchema>;

export async function analyzeContractRisk(input: AnalyzeContractRiskInput): Promise<AnalyzeContractRiskOutput> {
  return analyzeContractRiskFlow(input);
}

const identifyKeyDates = ai.defineTool({
  name: 'identifyKeyDates',
  description: 'Identifies key dates within a contract that are related to potential risks.',
  inputSchema: z.object({
    contractText: z.string().describe('The text of the contract to analyze.'),
  }),
  outputSchema: z.array(z.string().describe('Key dates identified in the contract.')),
}, async input => {
  // TODO: Implement the logic to extract key dates from the contract text.
  // This could involve using regex, NLP techniques, or calling another service.
  return getDocumentMetadata(input.contractText).then(metadata => metadata.detectedDates);
});

const prompt = ai.definePrompt({
  name: 'analyzeContractRiskPrompt',
  tools: [identifyKeyDates],
  input: {
    schema: z.object({
      documentText: z.string().describe('The text content of the contract document.'),
    }),
  },
  output: {
    schema: z.object({
      overallRiskScore: z.number().describe('The overall risk score of the contract (0-100).'),
      riskClauses: z.array(
        z.object({
          clauseText: z.string().describe('The text of the risky clause.'),
          riskCategory: z.string().describe('The category of risk associated with the clause.'),
          confidenceScore: z.number().describe('The confidence score (0-1) of the risk assessment.'),
        })
      ).describe('A list of clauses identified as potentially risky.'),
      keyDates: z.array(z.string().describe('Key dates identified in the contract related to risk.')).describe('Key dates related to risk'),
    }),
  },
  prompt: `You are an expert legal analyst specializing in identifying risks within contracts.

  Analyze the following contract text and identify potential risks. Provide an overall risk score (0-100) and highlight specific clauses that are considered risky, along with their risk categories and confidence scores.

  Contract Text: {{{documentText}}}

  If there are key dates that are related to risk, call the identifyKeyDates tool to extract those dates.
  Then include the key dates in the output.

  Format your output as a JSON object matching the schema above.`, // Using Handlebars templating.
});

const analyzeContractRiskFlow = ai.defineFlow<
  typeof AnalyzeContractRiskInputSchema,
  typeof AnalyzeContractRiskOutputSchema
>({
  name: 'analyzeContractRiskFlow',
  inputSchema: AnalyzeContractRiskInputSchema,
  outputSchema: AnalyzeContractRiskOutputSchema,
}, async input => {
  const {output} = await prompt(input);
  return output!;
});

