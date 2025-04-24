from typing import Dict, List
import re
import spacy
from spacy.language import Language
from utils.logging import logger
from typing_extensions import Dict, List, TypedDict


# spaCy model for NLP tasks
nlp: Language = spacy.load('en_core_web_lg')

class DocumentMetadata(TypedDict):
    fileSize: int
    pageCount: int
    wordCount: int
    detectedDates: List[str]
    parties: List[str]
    governingLaw: str | None
    venue: str | None
    definitions: Dict[str, str]
    slaReferences: List[str]

def extract_dates(text: str) -> List[str]:
    """
    Extracts dates from the contract text using regex.

    Args:
        text (str): The contract text to extract dates from.

    Returns:
        List[str]: A list of detected dates.
    """
    date_patterns = [
        r"\b(?:\d{1,2}[/-]\d{1,2}[/-]\d{2,4}|\w+ \d{1,2},? \d{4}|\d{1,2} \w+,? \d{4})\b",
        r"(January|February|March|April|May|June|July|August|September|October|November|December)\s+\d{1,2},\s+\d{4}"
    ]
    dates = []
    for pattern in date_patterns:
        dates.extend(re.findall(pattern, text))
    return dates

def extract_parties(text: str) -> List[str]:
    """
    Extracts parties from the contract text using NLP and some keyword matching.
    This is a basic implementation and can be significantly improved with better NER models.

    Args:
        text (str): The contract text to extract parties from.

    Returns:
        List[str]: A list of parties involved in the contract.
    """
    # Basic keyword-based approach (improve with NER)
    party_keywords = ["Inc", "LLC", "Corp", "Company", "Ltd"]
    parties = []
    for keyword in party_keywords:
        parties.extend(re.findall(r"(\w+ " + keyword + r")", text))
    return parties

def extract_governing_law(text: str) -> str | None:
    """
    Extracts the governing law from the contract text using regex.

    Args:
        text (str): The contract text to extract the governing law from.

    Returns:
        str | None: The governing law, if found.
    """
    pattern = r"This Agreement shall be governed by and construed in accordance with the laws of (.*?)\."
    match = re.search(pattern, text)
    if match:
        return match.group(1)
    return None

def extract_venue(text: str) -> str | None:
    """
    Extracts the venue for dispute resolution from the contract text using regex.

    Args:
        text (str): The contract text to extract the venue from.

    Returns:
        str | None: The venue for dispute resolution, if found.
    """
    pattern = r"any legal action or proceeding arising under this Agreement shall be brought exclusively in the federal or state courts located in (.*?)\."
    match = re.search(pattern, text)
    if match:
        return match.group(1)
    return None

def extract_definitions(text: str) -> Dict[str, str]:
    """
    Extracts definitions from the contract text using regex.

    Args:
        text (str): The contract text to extract definitions from.

    Returns:
        Dict[str, str]: A dictionary of definitions found in the contract.
    """
    pattern = r"\"(.*?)\"\s*means\s*(.*?)(?=\n|$)"
    definitions = dict(re.findall(pattern, text))
    return definitions

def extract_sla_references(text: str) -> List[str]:
    """
    Extracts SLA references from the contract text using regex.

    Args:
        text (str): The contract text to extract SLA references from.

    Returns:
        List[str]: A list of SLA references, if any.
    """
    pattern = r"\bSLA\b"  # Matches "SLA" as a whole word
    sla_references = re.findall(pattern, text)
    return sla_references

async def get_document_metadata(document: str) -> Dict:
    """
    Asynchronously retrieves metadata for a given document (file path or text content).

    Args:
        document (str): The document (file path or text content) for which to retrieve metadata.

    Returns:
        Dict: A dictionary containing the extracted metadata.

    To alter this function:
    1. Modify the `extract_dates`, `extract_parties`, `extract_governing_law`, `extract_venue`, `extract_definitions`, and `extract_sla_references` functions to extract additional metadata fields.
    2. Change the logic for extracting specific metadata fields.
    3. Add new functions to extract additional metadata fields.

    To improve the accuracy of this function:
    1. Improve the date parsing logic.
    2. Improve the party identification logic.
    3. Improve the governing law extraction logic.
    4. Improve the venue extraction logic.
    5. Improve the definition extraction logic.
    6. Improve the SLA reference extraction logic.
    """
    file_size = len(document)  # Placeholder
    page_count = 1  # Placeholder
    word_count = len(document.split())
    detected_dates = extract_dates(document)
    parties = extract_parties(document)
    governing_law = extract_governing_law(document)
    venue = extract_venue(document)
    definitions = extract_definitions(document)
    sla_references = extract_sla_references(document)

    metadata = {
        "fileSize": file_size,
        "pageCount": page_count,
        "wordCount": word_count,
        "detectedDates": detected_dates,
        "parties": parties,
        "governingLaw": governing_law,
        "venue": venue,
        "definitions": definitions,
        "slaReferences": sla_references,
    }
    return metadata
