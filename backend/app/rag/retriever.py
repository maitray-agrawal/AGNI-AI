from dataclasses import dataclass
from typing import List, Dict, Any, Optional
import uuid
import logging
from qdrant_client import QdrantClient
from qdrant_client.http.models import (
    Distance,
    VectorParams,
    PointStruct,
    Filter,
    FilterSelector,
    PointIdsList,
    CreateAliasOperation,
    CreateAlias,
    DeleteAliasOperation,
    DeleteAlias,
)

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


INDUSTRIAL_CORPUS = [
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


class QdrantRetriever:
    """Embedded local Qdrant vector retrieval engine with exact citation provenance."""

    def __init__(self, storage_path: Optional[str] = None):
        self.storage_path = storage_path or str(settings.QDRANT_PATH)
        self.client = QdrantClient(path=self.storage_path)
        self._ensure_collection()

    def _resolve_active_collection(self) -> Optional[str]:
        """Resolves the physical collection name backing the public COLLECTION_NAME identifier."""
        try:
            aliases = self.client.get_aliases().aliases
            for a in aliases:
                if a.alias_name == COLLECTION_NAME:
                    return a.collection_name

            collections = [c.name for c in self.client.get_collections().collections]
            if COLLECTION_NAME in collections:
                return COLLECTION_NAME
        except Exception as e:
            logger.error(f"Failed to inspect Qdrant collections or aliases: {e}")
            raise RuntimeError(f"Cannot resolve active Qdrant collection for '{COLLECTION_NAME}': {e}") from e

        return None

    def _ensure_collection(self, force_rebuild: bool = False):
        """Ensures the knowledge base is healthy, migrated to the semantic model, and served via an alias."""
        try:
            active_target = self._resolve_active_collection()
            if not active_target or force_rebuild:
                reason = "initial initialization" if not active_target else "forced rebuild"
                logger.info(f"Initializing Qdrant semantic collection '{COLLECTION_NAME}' (Reason: {reason})...")
                self._migrate_and_replace_collection(active_target)
                return

            # Check collection configuration
            info = self.client.get_collection(active_target)
            current_dim = getattr(info.config.params.vectors, "size", None)
            current_dist = getattr(info.config.params.vectors, "distance", None)

            needs_migration = False
            reason = ""

            if current_dim != EMBEDDING_DIM:
                needs_migration = True
                reason = f"dimension mismatch (found {current_dim}, expected {EMBEDDING_DIM})"
            elif current_dist != Distance.COSINE:
                needs_migration = True
                reason = f"distance mismatch (found {current_dist}, expected {Distance.COSINE})"
            else:
                # Fully paginate through all points to ensure NO legacy hash vectors or stale points exist
                total_scanned = 0
                next_offset = None
                while True:
                    scroll_res = self.client.scroll(
                        collection_name=active_target,
                        offset=next_offset,
                        limit=100,
                        with_payload=True,
                    )
                    batch_pts, next_offset = scroll_res
                    total_scanned += len(batch_pts)
                    for p in batch_pts:
                        payload = p.payload or {}
                        if payload.get("embedding_model") != local_embedder.model_name:
                            needs_migration = True
                            reason = (
                                f"legacy or mismatched embedding model in point {p.id}: "
                                f"'{payload.get('embedding_model')}'"
                            )
                            break
                    if needs_migration or next_offset is None or not batch_pts:
                        break

                if not needs_migration and total_scanned != len(INDUSTRIAL_CORPUS):
                    needs_migration = True
                    reason = f"point count mismatch (found {total_scanned}, expected {len(INDUSTRIAL_CORPUS)})"

            if needs_migration:
                logger.info(f"Migrating Qdrant collection '{COLLECTION_NAME}' (Reason: {reason})...")
                self._migrate_and_replace_collection(active_target)
            else:
                logger.debug(f"Qdrant collection '{COLLECTION_NAME}' is active and verified.")

        except Exception as e:
            logger.error(f"Qdrant collection check/migration failed: {e}")
            raise

    def _migrate_and_replace_collection(self, current_target: Optional[str] = None):
        """Performs a staged, verified replacement of the collection using Qdrant collection aliases.

        Lifecycle:
        1. Pre-computes all new semantic vectors in memory before modifying storage.
        2. Builds a new versioned collection: f"{COLLECTION_NAME}_{uuid}".
        3. Fully validates the new collection (dim=384, dist=COSINE, point count, payload tags, semantic probe).
        4. Atomically switches the public alias COLLECTION_NAME to the verified collection.
        5. Deletes the previous collection only after successful activation.
        6. If staging or validation fails, previous active collection remains 100% untouched and operational.
        """
        new_col_name = f"{COLLECTION_NAME}_{uuid.uuid4().hex[:8]}"

        # Step 1: Pre-compute points and embeddings in memory before modifying storage
        new_points = []
        for idx, item in enumerate(INDUSTRIAL_CORPUS):
            item_payload = dict(item)
            item_payload["embedding_model"] = local_embedder.model_name
            vec = local_embedder.embed_text(item["text"])
            new_points.append(PointStruct(id=idx + 1, vector=vec, payload=item_payload))

        staging_created = False
        try:
            # Step 2: Build new versioned collection
            self.client.create_collection(
                collection_name=new_col_name,
                vectors_config=VectorParams(size=EMBEDDING_DIM, distance=Distance.COSINE),
            )
            staging_created = True
            self.client.upsert(collection_name=new_col_name, points=new_points)

            # Step 3: Fully validate new collection before switching alias
            new_info = self.client.get_collection(new_col_name)
            if new_info.config.params.vectors.size != EMBEDDING_DIM:
                raise RuntimeError(
                    f"New collection dimension validation failed: {new_info.config.params.vectors.size} != {EMBEDDING_DIM}"
                )
            if new_info.config.params.vectors.distance != Distance.COSINE:
                raise RuntimeError(
                    f"New collection distance validation failed: {new_info.config.params.vectors.distance} != {Distance.COSINE}"
                )

            count = self.client.count(new_col_name).count
            if count != len(new_points):
                raise RuntimeError(
                    f"New collection point count validation failed: {count} != {len(new_points)}"
                )

            # Verify every point has valid model tag via pagination
            total_verified = 0
            next_offset = None
            while True:
                scroll_res = self.client.scroll(
                    collection_name=new_col_name,
                    offset=next_offset,
                    limit=100,
                    with_payload=True,
                )
                batch_pts, next_offset = scroll_res
                total_verified += len(batch_pts)
                if not all(p.payload.get("embedding_model") == local_embedder.model_name for p in batch_pts):
                    raise RuntimeError("New collection point validation failed: missing/mismatched embedding_model tag!")
                if next_offset is None or not batch_pts:
                    break

            if total_verified != len(new_points):
                raise RuntimeError(f"Point pagination verification count mismatch ({total_verified} vs {len(new_points)})")

            # Semantic retrieval probe on new collection
            test_query_vec = new_points[0].vector
            if hasattr(self.client, "query_points"):
                test_res = self.client.query_points(new_col_name, query=test_query_vec, limit=1).points
            else:
                test_res = self.client.search(new_col_name, query_vector=test_query_vec, limit=1)
            if not test_res:
                raise RuntimeError("Semantic retrieval probe failed on new collection!")

            # Step 4: Switch public alias COLLECTION_NAME to new collection
            aliases = self.client.get_aliases().aliases
            existing_alias = next((a for a in aliases if a.alias_name == COLLECTION_NAME), None)

            if existing_alias:
                # Atomically switch alias from previous target to new collection
                self.client.update_collection_aliases(change_aliases_operations=[
                    DeleteAliasOperation(delete_alias=DeleteAlias(alias_name=COLLECTION_NAME)),
                    CreateAliasOperation(create_alias=CreateAlias(collection_name=new_col_name, alias_name=COLLECTION_NAME)),
                ])
                logger.info(
                    f"Atomically switched alias '{COLLECTION_NAME}' from '{existing_alias.collection_name}' to '{new_col_name}'"
                )
            else:
                # If COLLECTION_NAME existed as a legacy physical collection, remove it before creating alias
                collections = [c.name for c in self.client.get_collections().collections]
                if COLLECTION_NAME in collections:
                    try:
                        self.client.delete_collection(COLLECTION_NAME)
                    except Exception as e:
                        raise RuntimeError(f"Failed to delete legacy physical collection '{COLLECTION_NAME}': {e}") from e

                # Create new alias
                self.client.update_collection_aliases(change_aliases_operations=[
                    CreateAliasOperation(create_alias=CreateAlias(collection_name=new_col_name, alias_name=COLLECTION_NAME))
                ])
                logger.info(f"Created alias '{COLLECTION_NAME}' -> '{new_col_name}'")

            # Step 5: Post-activation check on public alias
            active_info = self.client.get_collection(COLLECTION_NAME)
            if active_info.config.params.vectors.size != EMBEDDING_DIM:
                raise RuntimeError(f"Public alias dimension mismatch: {active_info.config.params.vectors.size}")

            # Step 6: Clean up old collection only after successful activation
            if current_target and current_target != new_col_name and current_target != COLLECTION_NAME:
                try:
                    self.client.delete_collection(current_target)
                    logger.info(f"Purged previous collection '{current_target}' after successful alias activation.")
                except Exception as e:
                    logger.warning(f"Failed to delete superseded collection '{current_target}': {e}")

        except Exception as e:
            # If migration failed, clean up the staging collection so no partial artifacts remain
            if staging_created:
                try:
                    self.client.delete_collection(new_col_name)
                except Exception as cleanup_err:
                    logger.warning(f"Failed to clean up aborted staging collection '{new_col_name}': {cleanup_err}")
            raise

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
