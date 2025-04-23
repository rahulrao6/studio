from typing import List
from sqlalchemy.orm import Session
from models.contract import Contract
from sentence_transformers import SentenceTransformer, util
from core.config import settings
from utils.logging import logger

class DocumentRetrievalService:
    def __init__(self):
        try:
            self.model = SentenceTransformer('all-mpnet-base-v2')  # Or another suitable model
            logger.info("Sentence Transformer model loaded successfully.")
        except Exception as e:
            logger.error(f"Error loading Sentence Transformer model: {e}")
            self.model = None

    async def retrieve_similar_documents(self, query: str, top_n: int = 3, db: Session = None) -> List[Contract]:
        """
        Retrieves the top-N most similar documents to the given query from the database
        using semantic similarity search with Sentence Transformers.
        """
        if not self.model or not db:
            logger.warning("Semantic search is disabled (model or database not initialized).")
            return []

        try:
            # 1. Encode the search query
            query_embedding = self.model.encode(query, convert_to_tensor=True)

            # 2. Fetch all contracts (or a reasonable subset) from the database
            contracts: List[Contract] = db.query(Contract).all()  # Fetch all contracts

            if not contracts:
                logger.info("No contracts found in the database.")
                return []

            # 3. Encode the contract texts
            contract_texts = [contract.text for contract in contracts]
            contract_embeddings = self.model.encode(contract_texts, convert_to_tensor=True)

            # 4. Calculate cosine similarity
            cosine_scores = util.pytorch_cos_sim(query_embedding, contract_embeddings)[0]

            # 5. Combine contracts and their scores
            contract_scores = list(zip(contracts, cosine_scores.tolist()))

            # 6. Sort by similarity score
            sorted_contracts = sorted(contract_scores, key=lambda x: x[1], reverse=True)

            # 7. Return the top-N contracts
            top_contracts = [contract for contract, score in sorted_contracts[:top_n]]
            logger.info(f"Retrieved top {top_n} similar contracts.")
            return top_contracts

        except Exception as e:
            logger.exception("Error during semantic similarity search.")
            return []
