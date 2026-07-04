"""
Semantic Similarity and Relevance Scoring
Uses local embeddings to measure meaning preservation.
"""
from models.embedding_model import get_embedding_model, is_semantic_available
from sklearn.metrics.pairwise import cosine_similarity

def compute_semantic_similarity(text1: str, text2: str) -> float:
    """
    Computes cosine similarity between two texts.
    Returns -1.0 if semantic engine is unavailable.
    """
    if not is_semantic_available():
        return -1.0
    
    model = get_embedding_model()
    # Encode texts into vectors
    embeddings = model.encode([text1, text2], convert_to_numpy=True)
    
    # Calculate cosine similarity
    sim = cosine_similarity([embeddings[0]], [embeddings[1]])[0][0]
    return round(float(sim), 4)

def compute_section_relevance(section_text: str, task_text: str) -> float:
    """
    Measures how relevant a specific section is to the main task.
    Returns -1.0 if unavailable.
    """
    if not is_semantic_available() or not task_text.strip():
        return -1.0
        
    model = get_embedding_model()
    embeddings = model.encode([section_text, task_text], convert_to_numpy=True)
    sim = cosine_similarity([embeddings[0]], [embeddings[1]])[0][0]
    return round(float(sim), 4)