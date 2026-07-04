"""
Embedding Model Manager
Handles safe, optional loading of the semantic model with graceful degradation.
"""

# 1. Safe Import Handling
try:
    from sentence_transformers import SentenceTransformer
    from sklearn.metrics.pairwise import cosine_similarity
    import numpy as np
    LIBS_AVAILABLE = True
except ImportError:
    LIBS_AVAILABLE = False

# Global state
_model = None
_load_error = None

def load_embedding_model():
    """
    Lazily loads the all-MiniLM-L6-v2 model. 
    Returns the model object, or None if it fails.
    """
    global _model, _load_error
    
    if not LIBS_AVAILABLE:
        _load_error = "sentence-transformers or scikit-learn not installed."
        return None
        
    if _model is None and _load_error is None:
        try:
            # all-MiniLM-L6-v2 is ~80MB, perfect for 8GB RAM laptops
            _model = SentenceTransformer('sentence-transformers/all-MiniLM-L6-v2')
        except Exception as e:
            _load_error = str(e)
            return None
            
    return _model

def is_embedding_available():
    """Returns True only if the model is successfully loaded and ready."""
    return LIBS_AVAILABLE and _model is not None

def get_load_error():
    """Returns the error message if loading failed."""
    return _load_error

def get_embedding(text: str):
    """Returns the embedding vector for a single text string."""
    if not is_embedding_available():
        return None
    return _model.encode(text, convert_to_numpy=True)

def get_embeddings(text_list: list):
    """Returns embedding vectors for a list of text strings."""
    if not is_embedding_available():
        return None
    return _model.encode(text_list, convert_to_numpy=True)

def cosine_similarity_score(text_a: str, text_b: str):
    """
    Computes the cosine similarity between two texts.
    Returns a float between -1.0 and 1.0, or None if unavailable.
    """
    if not is_embedding_available():
        return None
    
    emb_a = get_embedding(text_a).reshape(1, -1)
    emb_b = get_embedding(text_b).reshape(1, -1)
    
    sim = cosine_similarity(emb_a, emb_b)[0][0]
    return round(float(sim), 4)