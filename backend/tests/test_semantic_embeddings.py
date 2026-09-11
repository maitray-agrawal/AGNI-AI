import socket
import pytest
import numpy as np

from backend.app.rag.embeddings import local_embedder, LocalEmbedder, EMBEDDING_DIM
from backend.app.rag.retriever import retrieve, qdrant_retriever


def test_embedding_generation_and_dimension():
    """Proves embedding generation succeeds locally and output dimension is 384."""
    text = "For Carbon Steel Schedule 80 piping in Heavy Gas Oil service, retirement thickness is 4.0 mm per API 570."
    vec = local_embedder.embed_text(text)

    assert isinstance(vec, list)
    assert len(vec) == 384
    assert len(vec) == EMBEDDING_DIM
    assert all(isinstance(x, float) for x in vec)


def test_embedding_normalization_for_cosine_similarity():
    """Proves embeddings are unit normalized (L2 norm = 1.0), making dot product equal to cosine similarity."""
    text = "Centrifugal process pump vibration severity limits Zone A/B under ISO 10816-3."
    vec = local_embedder.embed_text(text)

    norm = np.linalg.norm(vec)
    assert np.isclose(norm, 1.0, atol=1e-4), f"Expected unit norm ~1.0, got {norm}"


def test_batch_embedding_consistency():
    """Proves batch embedding works and produces identical vectors to sequential embedding."""
    texts = [
        "Piping minimum allowable wall thickness retirement criteria API 570.",
        "ISO 10816 vibration alarm and shutdown thresholds for centrifugal pumps.",
        "Corrosion rate remaining life assessment for crude distillation units.",
    ]
    batch_vecs = local_embedder.embed_batch(texts)

    assert len(batch_vecs) == len(texts)
    for i, t in enumerate(texts):
        single_vec = local_embedder.embed_text(t)
        assert len(batch_vecs[i]) == 384
        assert np.allclose(batch_vecs[i], single_vec, atol=1e-5), f"Batch mismatch at index {i}"


def test_semantic_similarity_paraphrased_industrial_queries():
    """Proves semantically similar/paraphrased industrial queries have higher cosine similarity than unrelated queries."""
    # Paraphrased query about pipe thickness / retirement without identical keyword overlap
    query = "allowable pipe wall thinning and corrosion retirement threshold"
    query_vec = np.array(local_embedder.embed_text(query), dtype=np.float32)

    # Relevant document (API 570 piping thickness)
    doc_relevant = (
        "For Carbon Steel Schedule 80 piping in Heavy Gas Oil (HGO) service (design temp > 300°C), "
        "the minimum allowable retirement thickness (t_min) is calculated as 4.0 mm per API 570. "
        "If the measured wall thickness (t_actual) drops below 4.5 mm (within 0.5 mm of retirement), "
        "clearance for normal 12-month run CANNOT be granted."
    )
    vec_relevant = np.array(local_embedder.embed_text(doc_relevant), dtype=np.float32)

    # Different industrial topic (Pump vibration limits)
    doc_different_topic = (
        "For Class I/II process pumps (e.g. CDU Heavy Gas Oil Pump P-204 A/B), overall vibration severity limits are: "
        "Zone A/B (Acceptable): < 4.5 mm/s RMS. Zone C (Alarm - Restricted Operation): 4.5 mm/s to 7.1 mm/s RMS. "
        "Zone D (Trip - Immediate Shutdown): > 7.1 mm/s RMS."
    )
    vec_different = np.array(local_embedder.embed_text(doc_different_topic), dtype=np.float32)

    # Completely unrelated topic
    doc_unrelated = "The weather forecast for coastal Karnataka predicts heavy monsoon rains and high humidity."
    vec_unrelated = np.array(local_embedder.embed_text(doc_unrelated), dtype=np.float32)

    sim_relevant = float(np.dot(query_vec, vec_relevant))
    sim_different = float(np.dot(query_vec, vec_different))
    sim_unrelated = float(np.dot(query_vec, vec_unrelated))

    assert sim_relevant > sim_different, (
        f"Relevant similarity ({sim_relevant:.4f}) should exceed different topic ({sim_different:.4f})"
    )
    assert sim_relevant > sim_unrelated, (
        f"Relevant similarity ({sim_relevant:.4f}) should exceed unrelated topic ({sim_unrelated:.4f})"
    )
    assert sim_relevant > 0.45, f"Expected strong semantic similarity, got {sim_relevant:.4f}"


def test_zero_network_access_during_embedding(monkeypatch):
    """Proves no network access is attempted or required during embedding inference."""
    def guarded_connect(*args, **kwargs):
        raise PermissionError("Air-gap violation: Network socket connection attempted during local embedding!")

    monkeypatch.setattr(socket.socket, "connect", guarded_connect)

    # Run single text and batch embedding with socket.connect disabled
    vec1 = local_embedder.embed_text("Air-gapped sovereign inference test query")
    assert len(vec1) == 384

    batch = local_embedder.embed_batch(["Air-gapped document A", "Air-gapped document B"])
    assert len(batch) == 2
    assert len(batch[0]) == 384


def test_no_silent_fallback_on_missing_model():
    """Proves that missing/invalid models raise an explicit, actionable RuntimeError rather than falling back to hash."""
    fake_embedder = LocalEmbedder(model_name="nonexistent-organization/nonexistent-model-xyz")
    with pytest.raises(RuntimeError) as exc_info:
        fake_embedder.embed_text("Test query with missing model")

    err_text = str(exc_info.value)
    assert "Failed to load local semantic embedding model" in err_text
    assert "air-gapped" in err_text or "sovereign" in err_text


def test_airgapped_rag_retrieval_end_to_end(monkeypatch):
    """Critical Acceptance Condition: Demonstrates that a fresh RAG query uses the semantic
    embedding model with the network blocked and still retrieves the expected local document.
    """
    def guarded_connect(*args, **kwargs):
        raise PermissionError("Air-gap violation: Network socket connection attempted during RAG retrieval!")

    monkeypatch.setattr(socket.socket, "connect", guarded_connect)

    # Query 1: Vibration limits
    vibration_chunks = retrieve("P-204 pump dynamic rotor balancing and vibration alarm limits ISO 10816", top_k=2)
    assert len(vibration_chunks) > 0
    top_chunk = vibration_chunks[0]
    assert "Rotating_Equipment" in top_chunk.document or "10816" in top_chunk.text
    assert top_chunk.score > 0.4

    # Query 2: Pipe wall thickness retirement
    thickness_chunks = retrieve("carbon steel piping wall thickness retirement criteria API 570", top_k=2)
    assert len(thickness_chunks) > 0
    top_chunk_2 = thickness_chunks[0]
    assert "Piping" in top_chunk_2.document or "API_570" in top_chunk_2.document
    assert top_chunk_2.score > 0.4


def test_qdrant_migration_purges_stale_legacy_points(tmp_path):
    """Simulates a legacy collection populated with obsolete hash-vector points and stale documents.
    Proves that QdrantRetriever migration:
    1. Replaces the collection safely.
    2. Purges all stale points (e.g. IDs 99, 100, 101).
    3. Guarantees dimension=384, distance=COSINE.
    4. Guarantees every indexed point has embedding_model == 'sentence-transformers/all-MiniLM-L6-v2'.
    5. Preserves valid semantic retrieval after migration.
    """
    from qdrant_client import QdrantClient
    from qdrant_client.http.models import VectorParams, Distance, PointStruct
    from backend.app.rag.retriever import QdrantRetriever, COLLECTION_NAME, INDUSTRIAL_CORPUS

    test_storage = str(tmp_path / "qdrant_legacy_test")
    raw_client = QdrantClient(path=test_storage)

    # 1. Create a legacy collection simulating old hash-vectorizer state
    raw_client.create_collection(
        collection_name=COLLECTION_NAME,
        vectors_config=VectorParams(size=384, distance=Distance.COSINE),
    )

    # Inject 2 legacy points without embedding_model tag + 3 extraneous stale points
    legacy_points = [
        PointStruct(
            id=1,
            vector=[0.01] * 384,
            payload={"document": "old_manual_v1.pdf", "text": "Legacy content 1"},
        ),
        PointStruct(
            id=2,
            vector=[-0.01] * 384,
            payload={"document": "old_manual_v2.pdf", "text": "Legacy content 2"},
        ),
        PointStruct(
            id=99,
            vector=[0.05] * 384,
            payload={"document": "stale_deprecated_file.pdf", "text": "Obsolete deprecated entry"},
        ),
        PointStruct(
            id=100,
            vector=[-0.05] * 384,
            payload={"document": "stale_vendor_spec.pdf", "text": "Obsolete vendor spec"},
        ),
        PointStruct(
            id=101,
            vector=[0.02] * 384,
            payload={"document": "stale_temp_memo.pdf", "text": "Obsolete temp memo"},
        ),
    ]
    raw_client.upsert(collection_name=COLLECTION_NAME, points=legacy_points)
    assert raw_client.count(COLLECTION_NAME).count == 5
    raw_client.close()

    # 2. Instantiate QdrantRetriever on this legacy storage
    # This must detect the legacy/stale points and trigger the safe migration
    migrated_retriever = QdrantRetriever(storage_path=test_storage)

    # 3. Verify collection attributes
    info = migrated_retriever.client.get_collection(COLLECTION_NAME)
    assert info.config.params.vectors.size == 384
    assert info.config.params.vectors.distance == Distance.COSINE

    # 4. Verify point count equals exact current corpus count (4, NOT 5 or 9)
    current_count = migrated_retriever.client.count(COLLECTION_NAME).count
    assert current_count == len(INDUSTRIAL_CORPUS)
    assert current_count == 4

    # 5. Verify stale IDs (99, 100, 101) have been completely purged
    stale_check = migrated_retriever.client.retrieve(
        collection_name=COLLECTION_NAME,
        ids=[99, 100, 101],
    )
    assert len(stale_check) == 0, f"Stale points were not purged! Found: {stale_check}"

    # 6. Verify every point has the verified embedding_model tag and genuine semantic vectors
    all_pts, _ = migrated_retriever.client.scroll(
        collection_name=COLLECTION_NAME,
        limit=10,
        with_payload=True,
        with_vectors=True,
    )
    assert len(all_pts) == 4
    for pt in all_pts:
        assert pt.payload.get("embedding_model") == local_embedder.model_name
        vec_norm = np.linalg.norm(pt.vector)
        assert np.isclose(vec_norm, 1.0, atol=1e-3)

    # 7. Verify semantic retrieval functions on the migrated collection
    results = migrated_retriever.retrieve("P-204 pump dynamic rotor balancing and vibration limits", top_k=1)
    assert len(results) == 1
    assert "Rotating_Equipment" in results[0].document
    assert results[0].score > 0.45
    migrated_retriever.client.close()


def test_qdrant_migration_failure_injection_preserves_previous_collection(tmp_path, monkeypatch):
    """Failure-injection test: Proves that if active collection replacement or staging upsert
    fails during migration:
    1. The system does not silently report successful migration and raises an explicit RuntimeError.
    2. Staging collection artifacts are aborted/cleaned up.
    3. The previous working collection and public alias remain intact and fully operational for retrieval.
    """
    from backend.app.rag.retriever import QdrantRetriever, COLLECTION_NAME

    test_storage = str(tmp_path / "qdrant_failure_injection_test")

    # 1. Initialize retriever so it sets up a working initial collection served via alias
    retriever = QdrantRetriever(storage_path=test_storage)
    initial_target = retriever._resolve_active_collection()
    assert initial_target is not None
    assert initial_target.startswith(f"{COLLECTION_NAME}_")

    # Verify baseline retrieval is working
    baseline_res = retriever.retrieve("ISO 10816 vibration severity limits for process pumps", top_k=1)
    assert len(baseline_res) > 0
    assert "Rotating_Equipment" in baseline_res[0].document
    initial_score = baseline_res[0].score
    assert initial_score > 0.4

    # 2. Inject failure on staging collection upsert
    original_upsert = retriever.client.upsert

    def failing_upsert(collection_name, points, **kwargs):
        # Allow operations on the active collection, fail specifically on the new staging collection
        if collection_name != initial_target:
            raise RuntimeError("Injected fault: simulated disk I/O error during staging upsert!")
        return original_upsert(collection_name=collection_name, points=points, **kwargs)

    monkeypatch.setattr(retriever.client, "upsert", failing_upsert)

    # 3. Trigger migration (forced rebuild)
    with pytest.raises(RuntimeError) as exc_info:
        retriever._ensure_collection(force_rebuild=True)

    assert "Injected fault: simulated disk I/O error during staging upsert!" in str(exc_info.value)

    # 4. Verify system did NOT switch alias to an unverified collection
    current_target = retriever._resolve_active_collection()
    assert current_target == initial_target, (
        f"Active collection changed despite migration failure! Found {current_target}, expected {initial_target}"
    )

    # 5. Verify the previous collection is still fully intact and functional
    post_failure_count = retriever.client.count(COLLECTION_NAME).count
    assert post_failure_count == 4

    post_failure_res = retriever.retrieve("ISO 10816 vibration severity limits for process pumps", top_k=1)
    assert len(post_failure_res) > 0
    assert post_failure_res[0].document == baseline_res[0].document
    assert np.isclose(post_failure_res[0].score, initial_score, atol=1e-4)

    # 6. Verify staging collections were cleaned up
    all_collections = [c.name for c in retriever.client.get_collections().collections]
    assert all_collections == [initial_target], f"Staging collection was not cleaned up! Remaining: {all_collections}"

    retriever.client.close()
