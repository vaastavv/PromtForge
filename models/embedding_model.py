"""
Embedding Model Manager
Handles lazy loading of the semantic model with graceful degradation.
"""

# 1. Check if the library is installed
try:
    from sentence_transformers import SentenceTransformer
    EMBEDDING_LIB_AVAILABLE = True
except ImportError:
    EMBEDDING_LIB_AVAILABLE = False

_model = None
_load_error = None

def get_embedding_model():
    """
    Lazily loads the all-MiniLM-L6-v2 model. 
    Returns None if library is missing or download fails.
    """
    global _model, _load_error
    
    if not EMBEDDING_LIB_AVAILABLE:
        return None
        
    if _model is None and _load_error is None:
        try:
            # all-MiniLM-L6-v2 is ~80MB, perfect for 8GB RAM laptops
            _model = SentenceTransformer('sentence-transformers/all-MiniLM-L6-v2')
        except Exception as e:
            _load_error = str(e)
            return None
            
    return _model

def is_semantic_available():
    """Returns True only if the model is successfully loaded."""
    return EMBEDDING_LIB_AVAILABLE and get_embedding_model() is not None

def get_load_error():
    """Returns the error message if loading failed."""
    return _load_error