"use client";

interface RiskAnalysisProps {
  results: any;
}

export const RiskAnalysis: React.FC<RiskAnalysisProps> = ({ results }) => {
  return (
    <div>
      {results ? (
        <div>
          <p>
            <strong>Overall Risk Score:</strong> {results.overallRiskScore}
          </p>
          {results.riskClauses.map((clause: any, index: number) => (
            <div key={index} className="mb-4">
              <p>
                <strong>Clause {index + 1} Risk Category:</strong> {clause.riskCategory}
              </p>
              <p>
                <strong>Clause Text:</strong> {clause.clauseText}
              </p>
              <p>
                <strong>Confidence Score:</strong> {clause.confidenceScore}
              </p>
            </div>
          ))}
        </div>
      ) : (
        <p>No risk analysis available.</p>
      )}
    </div>
  );
};
/
