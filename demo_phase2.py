"""Phase 2 verification script -- tests ChromaDB, embeddings, and orchestrator."""
import asyncio
from backend.vectorstore.collections import get_resume_collection
from backend.agents.orchestrator import get_orchestrator
from backend.agents.tools.resume_tools import calculate_keyword_overlap

def test_chromadb():
    print("=" * 60)
    print("  TEST 1: ChromaDB + Sentence-Transformers")
    print("=" * 60)

    col = get_resume_collection()
    print(f"  Collection: {col._name}")
    print(f"  Initial count: {col.count()}")

    # Add test documents
    col.add_documents(
        ids=["test-resume-1", "test-resume-2"],
        documents=[
            "Python developer with 5 years experience in machine learning, NLP, and deep learning. Expert in PyTorch and TensorFlow.",
            "Frontend developer skilled in React, TypeScript, and Next.js. 3 years building responsive web applications.",
        ],
        metadatas=[
            {"user_id": "test", "role": "ML Engineer"},
            {"user_id": "test", "role": "Frontend Dev"},
        ],
    )
    print(f"  After adding 2 docs: {col.count()}")

    # Query -- should match ML resume more closely
    results = col.query("data scientist with NLP and deep learning experience", n_results=2)
    ids = results["ids"][0]
    distances = results["distances"][0]
    docs = results["documents"][0]

    print(f"\n  Query: 'data scientist with NLP and deep learning experience'")
    for i, (doc_id, dist, doc) in enumerate(zip(ids, distances, docs)):
        print(f"  #{i+1} [{doc_id}] distance={dist:.4f} -> {doc[:60]}...")

    # Verify ML resume is closer match
    assert ids[0] == "test-resume-1", "ML resume should be the top match!"
    print("\n  [PASS] Semantic search correctly ranks ML resume above frontend resume")

    # Cleanup
    col.delete_by_id("test-resume-1")
    col.delete_by_id("test-resume-2")
    print(f"  Cleaned up. Count: {col.count()}")


def test_orchestrator():
    print("\n" + "=" * 60)
    print("  TEST 2: LangGraph Orchestrator")
    print("=" * 60)

    graph = get_orchestrator()
    nodes = list(graph.get_graph().nodes.keys())
    print(f"  Graph nodes: {nodes}")
    assert "resume_parser" in nodes
    assert "ats_scorer" in nodes
    print("  [PASS] Orchestrator compiles with resume_parser + ats_scorer nodes")


def test_resume_tools():
    print("\n" + "=" * 60)
    print("  TEST 3: Resume Tools -- Keyword Overlap")
    print("=" * 60)

    result = calculate_keyword_overlap(
        resume_keywords=["Python", "PyTorch", "NLP", "Machine Learning", "Docker"],
        job_keywords=["Python", "TensorFlow", "NLP", "Machine Learning", "Kubernetes", "AWS"],
    )

    print(f"  Matched: {result['matched']}")
    print(f"  Missing: {result['missing']}")
    print(f"  Match %: {result['match_percentage']}%")
    assert result["match_percentage"] == 50.0
    print("  [PASS] Keyword overlap calculation works correctly")


if __name__ == "__main__":
    test_chromadb()
    test_orchestrator()
    test_resume_tools()

    print("\n" + "=" * 60)
    print("  PHASE 2 VERIFICATION COMPLETE -- ALL TESTS PASSED!")
    print("=" * 60)
