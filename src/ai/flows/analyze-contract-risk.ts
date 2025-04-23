'use server';
/**
 * @fileOverview Analyzes contract documents and identifies potential risks, key dates, parties, and definitions.
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
      remediationSuggestion: z.string().describe('A suggested redline to mitigate the risk.'),
      clarifyingQuestion: z.string().describe('A clarifying question to ask about the clause.'),
    })
  ).describe('A list of clauses identified as potentially risky.'),
  keyDates: z.array(z.string().describe('Key dates identified in the contract related to risk.')).describe('Key dates related to risk'),
  parties: z.array(z.string().describe('Parties identified in the contract.')).describe('Parties involved in the contract.'),
  definitions: z.record(z.string(), z.string()).describe('A dictionary of definitions found in the contract.'),
  effectiveDate: z.string().optional().describe('The effective date of the contract, if found.'),
  executiveSummary: z.object({
    overall: z.string().describe('Overall plain-English summary of the contract risk.'),
    sections: z.array(z.object({
      sectionTitle: z.string(),
      summary: z.string()
    })).describe('Plain-English summaries per section of the contract.')
  }).describe('Executive summaries of the contract.'),
  regulatoryComplianceScore: z.number().describe('A score (0-100) indicating the contract\'s compliance with relevant regulations.'),
});
export type AnalyzeContractRiskOutput = z.infer<typeof AnalyzeContractRiskOutputSchema>;

export async function analyzeContractRisk(input: AnalyzeContractRiskInput): Promise<AnalyzeContractRiskOutput> {
  return analyzeContractRiskFlow(input);
}

const extractContractMetadata = ai.defineTool({
  name: 'extractContractMetadata',
  description: 'Extracts key metadata from a contract document, including key dates, parties involved, and definitions.',
  inputSchema: z.object({
    contractText: z.string().describe('The text of the contract to analyze.'),
  }),
  outputSchema: z.object({
    keyDates: z.array(z.string().describe('Key dates identified in the contract.')),
    parties: z.array(z.string().describe('Parties identified in the contract.')),
    definitions: z.record(z.string(), z.string()).describe('A dictionary of definitions found in the contract.'),
    effectiveDate: z.string().optional().describe('The effective date of the contract, if found.'),
  }),
}, async input => {
  const metadata = await getDocumentMetadata(input.contractText);
  return {
    keyDates: metadata.detectedDates,
    parties: metadata.parties,
    definitions: { /* TODO: Implement extraction of definitions */ },
    effectiveDate: metadata.effectiveDate,
  };
});

const generateExecutiveSummary = ai.defineTool({
  name: 'generateExecutiveSummary',
  description: 'Generates an executive summary of the contract, both overall and per section.',
  inputSchema: z.object({
    contractText: z.string().describe('The text of the contract to analyze.'),
  }),
  outputSchema: z.object({
    overall: z.string().describe('Overall plain-English summary of the contract risk.'),
    sections: z.array(z.object({
      sectionTitle: z.string(),
      summary: z.string()
    })).describe('Plain-English summaries per section of the contract.')
  }),
}, async input => {
  // TODO: Implement the logic to generate executive summaries.
  return {
    overall: 'Overall risk is moderate. Key areas to review are...',
    sections: [{ sectionTitle: 'Payment Terms', summary: 'Payment terms are standard.' }]
  };
});

const assessRegulatoryCompliance = ai.defineTool({
  name: 'assessRegulatoryCompliance',
  description: 'Assesses the contract\'s compliance with relevant regulations.',
  inputSchema: z.object({
    contractText: z.string().describe('The text of the contract to analyze.'),
  }),
  outputSchema: z.number().describe('A score (0-100) indicating the contract\'s compliance with relevant regulations.'),
}, async input => {
  // TODO: Implement the logic to assess regulatory compliance.
  return 75; // Example compliance score
});

const prompt = ai.definePrompt({
  name: 'analyzeContractRiskPrompt',
  tools: [extractContractMetadata, generateExecutiveSummary, assessRegulatoryCompliance],
  input: {
    schema: z.object({
      documentText: z.string().describe('The text content of the contract document.'),
    }),
  },
  output: {
    schema: AnalyzeContractRiskOutputSchema,
  },
  prompt: `You are an expert legal analyst specializing in identifying risks within contracts.

  Analyze the following contract text and identify potential risks. Provide an overall risk score (0-100) and highlight specific clauses that are considered risky, along with their risk categories and confidence scores. For each risky clause, generate a recommended redline to mitigate the risk and a clarifying question to ask about the clause.

  Contract Text: {{{documentText}}}

  Here are some risk patterns to look for: auto-renewal, force majeure, and security obligations.

  Use the extractContractMetadata tool to identify key dates, parties involved, and definitions within the contract.
  Use the generateExecutiveSummary tool to create an overall and per-section plain-English summary.
  Use the assessRegulatoryCompliance tool to get a regulatory compliance score.

  Include all extracted metadata and summaries in the output.

  Format your output as a JSON object matching the schema above.`,
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
  return {
    ...output!,
    riskClauses: output!.riskClauses.map(clause => ({
      ...clause,
      remediationSuggestion: 'Consider narrowing the scope of this clause...', // Example suggestion
      clarifyingQuestion: 'What specific scenarios does this clause intend to cover?' // Example question
    }))
  };
});
