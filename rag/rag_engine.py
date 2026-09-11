"""Small local RAG engine.
Uses sentence-transformers embeddings when available; otherwise uses a TF-IDF
vector representation so the application still runs without a model download.
"""
from pathlib import Path
import json, re
import numpy as np

BASE_DIR = Path(__file__).resolve().parents[1]
KB_DIR = BASE_DIR / "knowledge_base"
STORE_DIR = BASE_DIR / "models" / "rag_store"
STORE_DIR.mkdir(parents=True, exist_ok=True)

def chunk_text(text, size=500):
    words = text.split()
    return [" ".join(words[i:i+size]) for i in range(0, len(words), size)]

def build_store(force=False):
    if not force and (STORE_DIR/"chunks.json").exists() and (STORE_DIR/"vectors.npy").exists() and (STORE_DIR/"mode.txt").exists():
        return
    chunks=[]
    for path in sorted(KB_DIR.glob("*.txt")):
        for i, chunk in enumerate(chunk_text(path.read_text(encoding="utf-8"))):
            chunks.append({"source": path.name, "chunk_id": i, "text": chunk})
    try:
        from sentence_transformers import SentenceTransformer
        model=SentenceTransformer("all-MiniLM-L6-v2")
        vectors=model.encode([c["text"] for c in chunks], normalize_embeddings=True)
        np.save(STORE_DIR/"vectors.npy", vectors)
        (STORE_DIR/"chunks.json").write_text(json.dumps(chunks, indent=2), encoding="utf-8")
        (STORE_DIR/"mode.txt").write_text("sentence-transformers", encoding="utf-8")
    except Exception:
        from sklearn.feature_extraction.text import TfidfVectorizer
        vec=TfidfVectorizer(stop_words="english")
        vectors=vec.fit_transform([c["text"] for c in chunks]).toarray()
        np.save(STORE_DIR/"vectors.npy", vectors)
        import joblib
        joblib.dump(vec, STORE_DIR/"tfidf_vectorizer.joblib")
        (STORE_DIR/"chunks.json").write_text(json.dumps(chunks, indent=2), encoding="utf-8")
        (STORE_DIR/"mode.txt").write_text("tfidf-fallback", encoding="utf-8")

def retrieve(query, top_k=3):
    chunks_path=STORE_DIR/"chunks.json"
    if not chunks_path.exists():
        build_store()
    chunks=json.loads(chunks_path.read_text(encoding="utf-8"))
    vectors=np.load(STORE_DIR/"vectors.npy")
    mode=(STORE_DIR/"mode.txt").read_text(encoding="utf-8").strip()

    if mode=="sentence-transformers":
        from sentence_transformers import SentenceTransformer
        model=SentenceTransformer("all-MiniLM-L6-v2")
        q=model.encode([query], normalize_embeddings=True)[0]
        scores=vectors @ q
    else:
        import joblib
        vec=joblib.load(STORE_DIR/"tfidf_vectorizer.joblib")
        q=vec.transform([query]).toarray()[0]
        denom=(np.linalg.norm(vectors,axis=1)*np.linalg.norm(q)+1e-9)
        scores=(vectors @ q)/denom

    order=np.argsort(scores)[::-1][:top_k]
    if len(order)==0 or float(scores[order[0]]) < 0.08:
        return []
    return [{**chunks[i], "score": round(float(scores[i]),4)} for i in order]

def answer_from_rag(query):
    results=retrieve(query)
    if not results:
        return {"answer": "Information unavailable in the local knowledge base.", "sources": []}
    # Grounded extractive answer: return only retrieved approved text.
    answer="\n".join(r["text"] for r in results)
    return {"answer": answer, "sources": results}
