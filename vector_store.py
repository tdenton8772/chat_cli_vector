import faiss
import numpy as np
import os

class VectorStore:
    def add(self, text: str, embedding: list[float], metadata: dict = None):
        raise NotImplementedError

    def search(self, embedding: list[float], top_k: int = 5) -> list[dict]:
        raise NotImplementedError

class FaissVectorStore(VectorStore):
    def __init__(self, dim: int = 4096, persist_path: str = "faiss.index"):
        self.dim = dim
        self.persist_path = persist_path

        if os.path.exists(self.persist_path):
            print(f"🔁 Loading FAISS index from {self.persist_path}")
            self.index = faiss.read_index(self.persist_path)
            self.texts = self._load_texts()
        else:
            print("📦 Starting new FAISS index")
            self.index = faiss.IndexFlatL2(self.dim)
            self.texts = []

    def add(self, text: str, embedding: list[float], metadata: dict = None):
        emb_np = np.array([embedding]).astype("float32")
        self.index.add(emb_np)
        self.texts.append({
            "text": text,
            "metadata": metadata or {}
        })
        self._persist()

    def search(self, embedding: list[float], top_k: int = 5, conv_id: str = None) -> list[dict]:
        if self.index.ntotal == 0:
            return []

        emb_np = np.array([embedding]).astype("float32")
        D, I = self.index.search(emb_np, top_k * 2)  # over-fetch for filtering

        results = []
        for i in I[0]:
            if i >= len(self.texts):
                continue
            hit = self.texts[i]
            if conv_id and hit["metadata"].get("conv_id") != conv_id:
                continue
            results.append(hit)
            if len(results) >= top_k:
                break

        return results


    def _persist(self):
        faiss.write_index(self.index, self.persist_path)
        with open(self.persist_path + ".meta", "w") as f:
            import json
            json.dump(self.texts, f)

    def _load_texts(self):
        try:
            import json
            with open(self.persist_path + ".meta", "r") as f:
                return json.load(f)
        except Exception as e:
            print("⚠️ Failed to load FAISS metadata:", e)
            return []

    def debug_dump(self):
        print(f"\n📦 FAISS index contains {self.index.ntotal} vectors\n")
        for i, entry in enumerate(self.texts):
            print(f"{i+1}. {entry['text']}")
            if entry['metadata']:
                print(f"   ↪ Metadata: {entry['metadata']}")


