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
  metadata: z.object({
    effectiveDate: z.string().optional().describe('The effective date of the contract, if found.'),
    renewalDeadline: z.string().optional().nullable().describe('The renewal deadline of the contract, if found.'),
    optOutDeadline: z.string().optional().nullable().describe('The opt-out deadline of the contract, if found.'),
    parties: z.array(z.string().describe('Parties identified in the contract.')).describe('Parties involved in the contract.'),
    governingLaw: z.string().optional().describe('The governing law of the contract, if specified.'),
    venue: z.string().optional().describe('The venue for dispute resolution, if specified.'),
    definitions: z.record(z.string(), z.string()).describe('A dictionary of definitions found in the contract.'),
    slaReferences: z.array(z.string()).optional().describe('SLA references, if any.'),
  }).describe('Comprehensive metadata of the contract.'),
  executiveSummary: z.object({
    overall: z.string().describe('Overall plain-English summary of the contract risk.'),
    sections: z.array(z.object({
      sectionTitle: z.string(),
      summary: z.string(),
      highestRiskClause: z.string().optional().describe('The highest-risk clause in the section.')
    })).describe('Plain-English summaries per section of the contract.')
  }).describe('Executive summaries of the contract.'),
  riskItems: z.array(
    z.object({
      clauseText: z.string().describe('The text of the risky clause.'),
      riskCategory: z.string().describe('The category of risk associated with the clause.'),
      confidenceScore: z.number().describe('The confidence score (0-1) of the risk assessment.'),
      suggestedFix: z.string().describe('A suggested redline to mitigate the risk.'),
      clarifyingQuestion: z.string().describe('A clarifying question to ask about the clause.'),
      industryPrevalence: z.string().describe('Comparison to industry prevalence (e.g., "More common than 80% of similar MSAs").'),
    })
  ).describe('A list of clauses identified as potentially risky, with remediation and questions.'),
  overallRiskScore: z.number().describe('The overall risk score of the contract (0-100).'),
  regulatoryComplianceScore: z.number().describe('A score (0-100) indicating the contract\'s compliance with relevant regulations.'),
  negotiationPoints: z.array(z.string()).describe('Key points for negotiation.'),
});
export type AnalyzeContractRiskOutput = z.infer<typeof AnalyzeContractRiskOutputSchema>;

export async function analyzeContractRisk(input: AnalyzeContractRiskInput): Promise<AnalyzeContractRiskOutput> {
  return analyzeContractRiskFlow(input);
}

const extractContractMetadata = ai.defineTool({
  name: 'extractContractMetadata',
  description: 'Extracts comprehensive metadata from a contract document.',
  inputSchema: z.object({
    contractText: z.string().describe('The text of the contract to analyze.'),
  }),
  outputSchema: z.object({
    effectiveDate: z.string().optional().describe('The effective date of the contract, if found.'),
    renewalDeadline: z.string().optional().nullable().describe('The renewal deadline of the contract, if found.'),
    optOutDeadline: z.string().optional().nullable().describe('The opt-out deadline of the contract, if found.'),
    parties: z.array(z.string().describe('Parties identified in the contract.')).describe('Parties involved in the contract.'),
    governingLaw: z.string().optional().describe('The governing law of the contract, if specified.'),
    venue: z.string().optional().describe('The venue for dispute resolution, if specified.'),
    definitions: z.record(z.string(), z.string()).describe('A dictionary of definitions found in the contract.'),
    slaReferences: z.array(z.string()).optional().describe('SLA references, if any.'),
  }),
}, async input => {
  const metadata = await getDocumentMetadata(input.contractText);
  // TODO: Implement extraction of definitions and SLA references
  return {
    effectiveDate: metadata.effectiveDate,
    renewalDeadline: metadata.renewalDeadline ?? null,
    optOutDeadline: metadata.optOutDeadline ?? null,
    parties: metadata.parties,
    governingLaw: metadata.governingLaw,
    venue: metadata.venue,
    definitions: metadata.definitions,
    slaReferences: metadata.slaReferences,
  };
});

const analyzeRisksAndGenerateSuggestions = ai.defineTool({
  name: 'analyzeRisksAndGenerateSuggestions',
  description: 'Analyzes contract text for potential risks and generates actionable redlines and clarifying questions.',
  inputSchema: z.object({
    contractText: z.string().describe('The text of the contract to analyze.'),
  }),
  outputSchema: z.object({
    riskItems: z.array(
      z.object({
        clauseText: z.string().describe('The text of the risky clause.'),
        riskCategory: z.string().describe('The category of risk associated with the clause.'),
        confidenceScore: z.number().describe('The confidence score (0-1) of the risk assessment.'),
        suggestedFix: z.string().describe('A suggested redline to mitigate the risk.'),
        clarifyingQuestion: z.string().describe('A clarifying question to ask about the clause.'),
        industryPrevalence: z.string().describe('Comparison to industry prevalence (e.g., "More common than 80% of similar MSAs").'),
      })
    ).describe('A list of clauses identified as potentially risky, with remediation and questions.'),
    overallRiskScore: z.number().describe('The overall risk score of the contract (0-100).'),
  }),
}, async input => {
  // TODO: Implement risk detection using CAUD-trained models and industry benchmarks
  // TODO: Implement generation of actionable redlines and clarifying questions
  const riskItems = [
    {
      clauseText: 'This contract will automatically renew for successive one year terms unless either party gives written notice of termination at least 30 days prior to the end of the then current term.',
      riskCategory: 'Auto-renewal Risk',
      confidenceScore: 0.85,
      suggestedFix: 'Increase the notice period to 60 days.',
      clarifyingQuestion: 'What is the rationale for the 30-day notice period?',
      industryPrevalence: 'More common than 70% of similar contracts.',
    },
    {
      clauseText: 'Neither party shall be liable for any failure to perform its obligations where such failure is as a result of Acts of God (including fire, flood, earthquake, storm, hurricane or other natural disaster), war, invasion, act of foreign enemies, hostilities (whether war is declared or not), civil war, rebellion, revolution, insurrection, military or usurped power or confiscation, terrorist activities, nationalisation, government sanction, blockage, embargo, labor dispute, strike, lockout or interruption or failure of electricity or telephone service.',
      riskCategory: 'Force Majeure Breadth',
      confidenceScore: 0.75,
      suggestedFix: 'Narrow the scope of force majeure events to exclude events within the parties\' reasonable control.',
      clarifyingQuestion: 'Are all of these force majeure events truly beyond the parties\' control?',
      industryPrevalence: 'Less common than 60% of similar contracts',
    },
    {
      clauseText: 'Customer shall indemnify, defend, and hold harmless Provider from and against any and all losses, damages, liabilities, deficiencies, claims, actions, judgments, settlements, interest, awards, penalties, fines, costs, or expenses of whatever kind, including reasonable attorneys\' fees, arising from or relating to any bodily injury, death, property damage, or damage to or loss of any products or services caused by or resulting from the gross negligence or willful misconduct of Customer.',
      riskCategory: 'Security Indemnification Gaps',
      confidenceScore: 0.9,
      suggestedFix: 'Add coverage for provider\'s negligence or willful misconduct.',
      clarifyingQuestion: 'Why does the indemnification only cover customer negligence?',
      industryPrevalence: 'More common than 90% of similar contracts',
    }
  ];
  const overallRiskScore = riskItems.reduce((acc, item) => acc + item.confidenceScore, 0) / riskItems.length * 100;

  return {
    riskItems: riskItems,
    overallRiskScore: overallRiskScore,
  };
});

const generateExecutiveAndSectionSummaries = ai.defineTool({
  name: 'generateExecutiveAndSectionSummaries',
  description: 'Generates an executive summary of the contract, both overall and per section, highlighting key risks.',
  inputSchema: z.object({
    contractText: z.string().describe('The text of the contract to analyze.'),
  }),
  outputSchema: z.object({
    executiveSummary: z.object({
      overall: z.string().describe('Overall plain-English summary of the contract risk.'),
      sections: z.array(z.object({
        sectionTitle: z.string(),
        summary: z.string(),
        highestRiskClause: z.string().optional().describe('The highest-risk clause in the section.')
      })).describe('Plain-English summaries per section of the contract.')
    }).describe('Executive summaries of the contract.'),
  }),
}, async input => {
  // TODO: Implement the logic to generate executive summaries, highlighting key risks
  return {
    executiveSummary: {
      overall: 'This MSA heavily favors the Provider due to broad force majeure and indemnification clauses. The auto-renewal terms also present a risk to the Customer.',
      sections: [
        { sectionTitle: 'Term', summary: 'The term is automatically renewed unless notice is given 30 days prior to the end of the term.', highestRiskClause: 'Auto-renewal clause' },
        { sectionTitle: 'Fees', summary: 'Fees are not specified in the document.', highestRiskClause: null },
        { sectionTitle: 'Renewal', summary: 'Renewal terms are automatically applied unless notice is given 30 days prior to the end of the term.', highestRiskClause: 'Renewal terms clause' },
        { sectionTitle: 'Modifications', summary: 'Modifications can be made unilaterally by the provider.', highestRiskClause: 'Unilateral modification clause' },
        { sectionTitle: 'Liability', summary: 'Liability is limited for the provider.', highestRiskClause: 'Liability clause' },
        { sectionTitle: 'Indemnification', summary: 'Indemnification is required by the customer.', highestRiskClause: 'Indemnification clause' },
        { sectionTitle: 'Dispute Resolution', summary: 'Dispute resolution is specified.', highestRiskClause: null },
      ]
    }
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

const assessSemanticBenchmarking = ai.defineTool({
  name: 'assessSemanticBenchmarking',
  description: 'Compares the risk items to industry prevalence via CAUD dataset and provides benchmarking insights.',
  inputSchema: z.object({
    riskItems: z.array(
      z.object({
        clauseText: z.string().describe('The text of the risky clause.'),
        riskCategory: z.string().describe('The category of risk associated with the clause.'),
      })
    ).describe('A list of clauses identified as potentially risky.'),
  }),
  outputSchema: z.array(z.string()).describe('Insights based on CAUD dataset.'),
  async run(input) {
    // TODO: Implement the logic to assess semantic benchmarking.
    return input.riskItems.map(item => `Risk for ${item.riskCategory} is within industry standards.`);
  }
});

const prompt = ai.definePrompt({
  name: 'analyzeContractRiskPrompt',
  tools: [extractContractMetadata, analyzeRisksAndGenerateSuggestions, generateExecutiveAndSectionSummaries, assessRegulatoryCompliance],
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

  Use the extractContractMetadata tool to identify key dates, parties involved, definitions, and other metadata within the contract.
  Use the analyzeRisksAndGenerateSuggestions tool to identify risks and generate actionable redlines and clarifying questions.
  Use the generateExecutiveAndSectionSummaries tool to create an overall and per-section plain-English summary.
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
  return output!;
});
