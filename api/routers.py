from typing import List, Dict

from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, BackgroundTasks
from sqlalchemy.orm import Session

from core.security import get_current_user, User
from api import dependencies
from models.clause import Clause
from models.contract import Contract
from models.legal_memo import LegalMemo
from models.obligation import Obligation
from models.right import Right
from models.risk_report import RiskReport
from services.clause_extraction import ClauseExtractionService
from services.document_metadata import get_document_metadata, DocumentMetadata
from services.obligation_mapping import ObligationMappingService
from services.risk_scoring import RiskScoringService
from core.config import settings
from utils.logging import logger
from fastapi.responses import JSONResponse
import traceback
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool
from sqlalchemy.exc import SQLAlchemyError
from api.dependencies import get_db
from services.document_ingestion import ingest_document, IngestionError
from models.contract import Contract as ContractModel  # Renamed to avoid collision
from services.document_retrieval import DocumentRetrievalService
import os
from services.document_upload import process_uploaded_file
from src.ai.flows.analyze_contract_risk import analyzeContractRisk, AnalyzeContractRiskInput, AnalyzeContractRiskOutput

router = APIRouter()


# Ingestion Endpoints
@router.post("/contracts", response_model=Contract, tags=["Ingestion"])
async def upload_contract(
    file: UploadFile = File(...),
    background_tasks: BackgroundTasks = BackgroundTasks(),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(dependencies.get_db),
):
    """
    Upload a contract document (PDF, DOCX, TXT) for analysis.
    Performs OCR/Zonal parsing, text normalization, and PII redaction.
    """
    try:
        file_content = await file.read()
        if not file_content:
            raise IngestionError("Uploaded file is empty.")

        # Determine file type and process accordingly
        file_type = file.content_type
        if file_type not in ["application/pdf", "text/plain", "application/vnd.openxmlformats-officedocument.wordprocessingml.document", "text/csv"]:
            raise IngestionError(f"Unsupported file type: {file_type}")

        # Save the file temporarily
        file_path = f"temp_files/{file.filename}"
        os.makedirs(os.path.dirname(file_path), exist_ok=True)  # Ensure directory exists

        with open(file_path, "wb") as f:
            f.write(file_content)

        contract = await process_uploaded_file(file_path, db)

        background_tasks.add_task(
            persist_contract, contract, db
        )  # Persist in background
        return contract
    except IngestionError as e:
        logger.error(f"Ingestion failed: {e}")
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        logger.exception("Unexpected error during upload")  # Log the full exception
        raise HTTPException(
            status_code=500, detail="Internal server error during upload."
        )

def persist_contract(contract: Contract, db: Session):
    """Persists the contract to the database."""
    try:
        db_contract = ContractModel(
            text=contract.text,
            metadata=contract.metadata,
            created_at=contract.metadata.get("created_at"),
        )  # Include created_at
        db.add(db_contract)
        db.commit()
        db.refresh(db_contract)
        logger.info(f"Contract persisted to database with ID: {db_contract.id}")
    except SQLAlchemyError as e:
        logger.error(f"Database error: {e}")
        db.rollback()
        raise
    except Exception as e:
        logger.exception("Unexpected error during contract persistence")
        db.rollback()
        raise


# Analysis Endpoints
@router.get(
    "/contracts/{contract_id}/clauses", response_model=List[Clause], tags=["Analysis"]
)
async def get_contract_clauses(
    contract_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(dependencies.get_db),
):
    """
    Returns typed clauses, graph edges, and precision scores for a given contract.
    """
    try:
        contract = db.get(ContractModel, contract_id)
        if not contract:
            raise HTTPException(status_code=404, detail="Contract not found")

        clause_extraction_service = ClauseExtractionService()
        clauses = clause_extraction_service.extract_clauses(contract.text)
        return clauses
    except Exception as e:
        logger.exception(f"Error extracting clauses from contract {contract_id}")
        raise HTTPException(
            status_code=500, detail="Error extracting clauses from contract"
        )


@router.get(
    "/contracts/{contract_id}/obligations",
    response_model=List[Obligation],
    tags=["Analysis"],
)
async def get_contract_obligations(
    contract_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(dependencies.get_db),
):
    """
    Returns structured obligations/rights JSON for a given contract.
    """
    try:
        contract = db.get(ContractModel, contract_id)
        if not contract:
            raise HTTPException(status_code=404, detail="Contract not found")

        clause_extraction_service = ClauseExtractionService()
        clauses = clause_extraction_service.extract_clauses(contract.text)

        obligation_mapping_service = ObligationMappingService()
        obligations, _ = obligation_mapping_service.map_obligations(clauses)  # Get obligations

        return obligations
    except Exception as e:
        logger.exception(
            f"Error mapping obligations/rights for contract {contract_id}"
        )
        raise HTTPException(
            status_code=500, detail="Error mapping obligations/rights"
        )


@router.get(
    "/contracts/{contract_id}/rights", response_model=List[Right], tags=["Analysis"]
)
async def get_contract_rights(
    contract_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(dependencies.get_db),
):
    """
    Returns structured obligations/rights JSON for a given contract.
    """
    try:
        contract = db.get(ContractModel, contract_id)
        if not contract:
            raise HTTPException(status_code=404, detail="Contract not found")

        clause_extraction_service = ClauseExtractionService()
        clauses = clause_extraction_service.extract_clauses(contract.text)

        obligation_mapping_service = ObligationMappingService()
        _, rights = obligation_mapping_service.map_obligations(
            clauses
        )  # Get rights

        return rights
    except Exception as e:
        logger.exception(
            f"Error mapping obligations/rights for contract {contract_id}"
        )
        raise HTTPException(
            status_code=500, detail="Error mapping obligations/rights"
        )


@router.get(
    "/contracts/{contract_id}/risk", response_model=RiskReport, tags=["Analysis"]
async def get_contract_risk_report(
    contract_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(dependencies.get_db),
):
    """
    Returns a per-clause and overall risk report with remediation suggestions and regulatory citations.
    """
    try:
        contract = db.get(ContractModel, contract_id)
        if not contract:
            raise HTTPException(status_code=404, detail="Contract not found")

        clause_extraction_service = ClauseExtractionService()
        clauses = clause_extraction_service.extract_clauses(contract.text)

        risk_scoring_service = RiskScoringService()
        risk_report = risk_scoring_service.score_clauses(clauses)

        return risk_report
    except Exception as e:
        logger.exception(f"Error generating risk report for contract {contract_id}")
        raise HTTPException(
            status_code=500, detail="Error generating risk report"
        )


@router.get(
    "/contracts/{contract_id}/metadata", response_model=DocumentMetadata, tags=["Analysis"]
)
async def get_contract_metadata(
    contract_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(dependencies.get_db),
):
    """
    Returns the metadata of a contract.
    """
    try:
        contract = db.get(ContractModel, contract_id)
        if not contract:
            raise HTTPException(status_code=404, detail="Contract not found")

        metadata = await get_document_metadata(contract.text)
        return metadata
    except Exception as e:
        logger.exception(f"Error extracting metadata for contract {contract_id}")
        raise HTTPException(
            status_code=500, detail="Error extracting metadata"
        )

@router.get(
    "/contracts/{contract_id}/compare", response_model=List[Contract], tags=["Analysis"]
)
async def compare_contract(
    contract_id: int,
    num_results: int = 3,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(dependencies.get_db),
):
    """
    Returns the top-N similar contracts from the database.
    """
    try:
        contract = db.get(ContractModel, contract_id)
        if not contract:
            raise HTTPException(status_code=404, detail="Contract not found")

        document_retrieval_service = DocumentRetrievalService()
        similar_contracts = await document_retrieval_service.retrieve_similar_documents(contract.text, num_results)
        return similar_contracts
    except Exception as e:
        logger.exception(f"Error retrieving similar contracts for contract {contract_id}")
        raise HTTPException(
            status_code=500, detail="Error retrieving similar contracts"
        )

@router.post("/analyze", response_model=AnalyzeContractRiskOutput, tags=["AI Analysis"])
async def analyze_contract_endpoint(
    input_data: AnalyzeContractRiskInput,
):
    """
    Analyzes a contract using the AI flow and returns the results.
    """
    try:
        results = await analyzeContractRisk(input_data)
        return results
    except Exception as e:
        logger.exception(f"Error during AI contract analysis: {e}")
        raise HTTPException(status_code=500, detail=f"AI analysis failed: {e}")


@router.get("/health", tags=["Metadata"])
async def health_check():
    """
    Component health (models, disk, DB).
    """
    return {"status": "ok"}


# Metrics and Monitoring (Example - requires Prometheus setup)
@router.get("/metrics", tags=["Metadata"])
async def metrics():
    """
    Prometheus metrics endpoint.
    """
    # In a real implementation, you would collect and format metrics here.
    return {"message": "Prometheus metrics endpoint (example)"}
'''''
@router.get("/ui", tags=["UI Dummy"])
async def ui_dummy():
    """
    UI endpoint.
    """
    # In a real implementation, you would collect and format metrics here.
    return {"message": "UI endpoint (example)"}
'''''
