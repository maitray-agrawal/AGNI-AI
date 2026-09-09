from dataclasses import dataclass
from typing import List, Dict, Any, Optional
import uuid
import logging
from qdrant_client import QdrantClient
from qdrant_client.http.models import Distance, VectorParams, PointStruct

from backend.app.config import settings
from backend.app.rag.embeddings import local_embedder, EMBEDDING_DIM

logger = logging.getLogger("agni.rag.retriever")

COLLECTION_NAME = "mrpl_knowledge"


@dataclass
class DocumentChunk:
    document: str
    page: int
    section: str
    text: str
    score: float


class QdrantRetriever:
    """Embedded local Qdrant vector retrieval engine with exact citation provenance."""

    def __init__(self, storage_path: Optional[str] = None):
        self.storage_path = storage_path or str(settings.QDRANT_PATH)
        self.client = QdrantClient(path=self.storage_path)
        self._ensure_collection()

    def _ensure_collection(self):
        try:
            collections = self.client.get_collections().collections
            exists = any(c.name == COLLECTION_NAME for c in collections)
            if not exists:
                self.client.create_collection(
                    collection_name=COLLECTION_NAME,
                    vectors_config=VectorParams(size=EMBEDDING_DIM, distance=Distance.COSINE),
                )
                logger.info(f"Created Qdrant collection '{COLLECTION_NAME}' at {self.storage_path}")
                self._seed_default_industrial_knowledge()
        except Exception as e:
            logger.warning(f"Qdrant collection check failed: {e}")

    def _seed_default_industrial_knowledge(self):
        """Seeds demonstration corpus: synthetic/public industrial inspection procedures and API 570 / ISO 10816-3 guidelines; no proprietary MRPL information included."""
        sample_corpus = [
            {
                "document": "MRPL_CDU_Piping_Inspection_Manual.pdf",
                "page": 14,
                "section": "Section 4.2 - Minimum Wall Thickness & Retirement Criteria",
                "text": (
                    "For Carbon Steel Schedule 80 piping in Heavy Gas Oil (HGO) service (design temp > 300°C), "
                    "the minimum allowable retirement thickness (t_min) is calculated as 4.0 mm per API 570. "
                    "If the measured wall thickness (t_actual) drops below 4.5 mm (within 0.5 mm of retirement), "
                    "clearance for normal 12-month run CANNOT be granted. An immediate temporary engineered composite wrap "
                    "or piping spool replacement must be executed within 72 hours under plant shutdown or bypass protocol."
                ),
            },
            {
                "document": "MRPL_Rotating_Equipment_Maintenance_SOP.pdf",
                "page": 8,
                "section": "Section 3.1 - Centrifugal Pump Vibration Limits (ISO 10816-3)",
                "text": (
                    "For Class I/II process pumps (e.g. CDU Heavy Gas Oil Pump P-204 A/B), overall vibration severity limits are: "
                    "Zone A/B (Acceptable): < 4.5 mm/s RMS. "
                    "Zone C (Alarm - Restricted Operation): 4.5 mm/s to 7.1 mm/s RMS. "
                    "Zone D (Trip - Immediate Shutdown): > 7.1 mm/s RMS. "
                    "When vibration exceeds 7.1 mm/s with prominent 1x RPM and blade pass harmonics, immediate bearing replacement "
                    "and dynamic rotor balancing are mandatory prior to equipment restart."
                ),
            },
            {
                "document": "API_570_Piping_Inspection_Code.pdf",
                "page": 22,
                "section": "Section 7.1 - Corrosion Rate and Remaining Life Estimation",
                "text": (
                    "Remaining life is calculated as: Remaining Life = (t_actual - t_min) / Corrosion_Rate. "
                    "When remaining life is less than 2 years, inspection intervals must be reduced to 6 months or continuous "
                    "online UT thickness monitoring must be established. Accelerated sulfidic corrosion occurs in crude units "
                    "between 260°C and 425°C."
                ),
            },
            {
                "document": "MRPL_Engineering_Approval_Governance.pdf",
                "page": 5,
                "section": "Section 2.4 - Equipment Return-to-Service Clearance Authority",
                "text": (
                    "Return to service approval notes for critical rotating equipment (P-204, P-205, C-101) require joint sign-off "
                    "by the NDT Inspection Engineer, Mechanical Maintenance Lead, and Unit Operations Superintendent. "
                    "Approval notes must cite specific inspection findings, referenced manual standards, and mandatory action items."
                ),
            }
        ]

        points = []
        for idx, item in enumerate(sample_corpus):
            vec = local_embedder.embed_text(item["text"])
            point = PointStruct(
                id=idx + 1,
                vector=vec,
                payload=item,
            )
            points.append(point)

        try:
            self.client.upsert(collection_name=COLLECTION_NAME, points=points)
            logger.info(f"Seeded {len(points)} industrial SOP documents into Qdrant collection '{COLLECTION_NAME}'")
        except Exception as e:
            logger.error(f"Failed to seed Qdrant knowledge base: {e}")

    def retrieve(self, query: str, top_k: int = 5, filters: Optional[Dict[str, Any]] = None) -> List[DocumentChunk]:
        """Performs dense vector retrieval against local Qdrant store."""
        query_vec = local_embedder.embed_text(query)
        chunks = []
        try:
            # Modern qdrant-client 1.19+ uses query_points
            if hasattr(self.client, "query_points"):
                response = self.client.query_points(
                    collection_name=COLLECTION_NAME,
                    query=query_vec,
                    limit=top_k,
                )
                points = getattr(response, "points", [])
                for hit in points:
                    payload = hit.payload or {}
                    chunks.append(DocumentChunk(
                        document=payload.get("document", "Unknown Manual"),
                        page=payload.get("page", 1),
                        section=payload.get("section", "General"),
                        text=payload.get("text", ""),
                        score=float(hit.score if hasattr(hit, "score") else 1.0),
                    ))
            elif hasattr(self.client, "search"):
                search_results = self.client.search(
                    collection_name=COLLECTION_NAME,
                    query_vector=query_vec,
                    limit=top_k,
                )
                for hit in search_results:
                    payload = hit.payload or {}
                    chunks.append(DocumentChunk(
                        document=payload.get("document", "Unknown Manual"),
                        page=payload.get("page", 1),
                        section=payload.get("section", "General"),
                        text=payload.get("text", ""),
                        score=float(hit.score),
                    ))
            return chunks
        except Exception as e:
            logger.error(f"Retrieval error: {e}")
            return []


# Global retriever instance
qdrant_retriever = QdrantRetriever()


def retrieve(query: str, top_k: int = 5, filters: Optional[Dict[str, Any]] = None) -> List[DocumentChunk]:
    """Frozen interface contract for local knowledge retrieval."""
    return qdrant_retriever.retrieve(query=query, top_k=top_k, filters=filters)
