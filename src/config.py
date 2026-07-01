# ── Paths & Limits ──────────────────────────────────────────────
FINAL_TOP_K = 100
BM25_SHORTLIST = 2000        # first-pass BM25 retrieval size
SEMANTIC_RERANK = 1500       # V5: drastically increased semantic re-rank funnel


# ── Embedding model (CPU-friendly, ~133 MB) ──────────────────────
EMBEDDING_MODEL_NAME = "BAAI/bge-small-en-v1.5"

# ── Composite weight vector ─────────────────────────────────────
#   semantic | bm25 | skill_match | career | behavioral
W_SEMANTIC   = 0.30
W_BM25       = 0.15
W_SKILL      = 0.20
W_CAREER     = 0.20
W_BEHAVIORAL = 0.15

# ── JD-derived skill taxonomy ───────────────────────────────────
# Core required skills (must have)
JD_CORE_SKILLS = {
    "embeddings", "retrieval", "ranking", "llm", "fine tuning", "finetuning",
    "sentence transformers", "sentence-transformers",
    "bge", "e5", "openai embeddings",
    "pinecone", "weaviate", "qdrant", "milvus",
    "opensearch", "elasticsearch", "faiss",
    "python", "pytorch", "tensorflow",
    "ndcg", "mrr", "map", "a/b testing", "ab testing",
    "rag", "retrieval augmented generation",
    "vector database", "vector db", "hybrid search",
    "nlp", "natural language processing",
    "information retrieval", "search",
    "recommendation", "recommendation system",
    "transformer", "transformers", "bert", "gpt",
    "huggingface", "hugging face",
    "scikit-learn", "sklearn", "xgboost",
    "deep learning", "machine learning", "ml",
    "neural network", "neural networks",
}

# Nice-to-have skills
JD_NICE_SKILLS = {
    "lora", "qlora", "peft",
    "learning to rank", "learning-to-rank",
    "distributed systems", "large scale inference",
    "docker", "kubernetes", "k8s",
    "mlops", "ml ops", "model serving",
    "data pipeline", "data engineering",
    "aws", "gcp", "azure",
}

# Relevant titles (higher = better match to JD)
JD_POSITIVE_TITLES = {
    "ai engineer", "ml engineer", "machine learning engineer",
    "data scientist", "senior ai engineer", "senior ml engineer",
    "nlp engineer", "research engineer", "applied scientist",
    "software engineer", "senior software engineer",
    "backend engineer", "data engineer", "platform engineer",
    "devops engineer", "full stack developer", "cloud engineer",
    "recommendation systems engineer",
}

# Clearly non-technical titles (will be scored low, NOT filtered out)
JD_NONTECHNICAL_TITLES = {
    "marketing manager", "sales executive", "hr manager",
    "accountant", "content writer", "graphic designer",
    "customer support", "operations manager", "civil engineer",
    "mechanical engineer", "business analyst",
}

# Consulting-only companies (penalized if ENTIRE career is here)
CONSULTING_FIRMS = {
    "tcs", "infosys", "wipro", "accenture", "cognizant",
    "capgemini", "hcl", "tech mahindra", "mindtree", "mphasis",
    "hexaware", "cyient", "persistent", "ltimindtree",
}

# JD query for BM25 + semantic matching
JD_QUERY = (
    "Senior AI Engineer founding team. Deep technical depth in modern ML systems: "
    "embeddings, retrieval, ranking, LLMs, fine-tuning. "
    "Production experience with embeddings-based retrieval systems "
    "(sentence-transformers, BGE, E5) deployed to real users. "
    "Production experience with vector databases or hybrid search infrastructure "
    "(Pinecone, Weaviate, Qdrant, Milvus, OpenSearch, Elasticsearch, FAISS). "
    "Strong Python code quality. Hands-on experience designing evaluation frameworks "
    "for ranking systems (NDCG, MRR, MAP, A/B testing). "
    "5-9 years experience at product companies building production ML systems. "
    "Shipped end-to-end ranking, search, or recommendation system to real users. "
    "Startup mentality, hybrid work Pune or Noida India."
)
