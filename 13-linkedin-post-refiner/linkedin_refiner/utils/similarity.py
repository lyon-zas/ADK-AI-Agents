"""
Similarity and Edit Metrics Utilities

This module provides functions for computing semantic similarity and
edit percentage between original and refined LinkedIn posts.
"""

from typing import Tuple, Set


# Thresholds
SIM_SCORE_THRESHOLD = 0.70  # Minimum semantic similarity to preserve meaning
EDIT_PCT_THRESHOLD = 30     # Maximum token change percentage


def tokenize(text: str) -> Set[str]:
    """
    Simple whitespace tokenization with normalization.
    
    Args:
        text: Input text to tokenize
        
    Returns:
        Set of lowercase tokens
    """
    # Normalize: lowercase, split on whitespace
    tokens = text.lower().split()
    # Remove punctuation from tokens
    cleaned = set()
    for token in tokens:
        cleaned_token = ''.join(c for c in token if c.isalnum())
        if cleaned_token:
            cleaned.add(cleaned_token)
    return cleaned


def compute_edit_percentage(original: str, refined: str) -> float:
    """
    Compute the percentage of tokens changed between original and refined text.
    
    Uses symmetric difference to count changed tokens.
    
    Args:
        original: Original post text
        refined: Refined post text
        
    Returns:
        Edit percentage (0-100)
    """
    original_tokens = tokenize(original)
    refined_tokens = tokenize(refined)
    
    if not original_tokens:
        return 100.0 if refined_tokens else 0.0
    
    # Symmetric difference = tokens added + tokens removed
    changed_tokens = len(original_tokens.symmetric_difference(refined_tokens))
    total_tokens = len(original_tokens)
    
    edit_pct = (changed_tokens / total_tokens) * 100
    return min(edit_pct, 100.0)


def compute_jaccard_similarity(original: str, refined: str) -> float:
    """
    Compute Jaccard similarity between two texts.
    
    This is a simple token-based similarity measure.
    For production, use embedding-based cosine similarity.
    
    Args:
        original: Original post text
        refined: Refined post text
        
    Returns:
        Similarity score (0.0 to 1.0)
    """
    original_tokens = tokenize(original)
    refined_tokens = tokenize(refined)
    
    if not original_tokens and not refined_tokens:
        return 1.0
    if not original_tokens or not refined_tokens:
        return 0.0
    
    intersection = len(original_tokens.intersection(refined_tokens))
    union = len(original_tokens.union(refined_tokens))
    
    return intersection / union if union > 0 else 0.0


def compute_similarity(original: str, refined: str) -> Tuple[float, float]:
    """
    Compute both similarity score and edit percentage.
    
    For production use, replace Jaccard with embedding-based cosine similarity:
    1. Generate embeddings using text-embedding-004 or similar
    2. Compute: sim_score = dot(emb_original, emb_refined) / (||emb_original|| * ||emb_refined||)
    
    Args:
        original: Original post text
        refined: Refined post text
        
    Returns:
        Tuple of (sim_score, edit_pct)
        - sim_score: Similarity score [0, 1], threshold >= 0.70
        - edit_pct: Token change percentage [0, 100], threshold <= 30
    """
    sim_score = compute_jaccard_similarity(original, refined)
    edit_pct = compute_edit_percentage(original, refined)
    
    return sim_score, edit_pct


def validate_originality(original: str, refined: str) -> dict:
    """
    Validate that refinements preserve originality within thresholds.
    
    Args:
        original: Original post text
        refined: Refined post text
        
    Returns:
        Validation result dict with status and metrics
    """
    sim_score, edit_pct = compute_similarity(original, refined)
    
    is_valid = (
        sim_score >= SIM_SCORE_THRESHOLD and 
        edit_pct <= EDIT_PCT_THRESHOLD
    )
    
    violations = []
    if sim_score < SIM_SCORE_THRESHOLD:
        violations.append(f"sim_score {sim_score:.2f} < {SIM_SCORE_THRESHOLD}")
    if edit_pct > EDIT_PCT_THRESHOLD:
        violations.append(f"edit_pct {edit_pct:.1f}% > {EDIT_PCT_THRESHOLD}%")
    
    return {
        "is_valid": is_valid,
        "sim_score": round(sim_score, 3),
        "edit_pct": round(edit_pct, 1),
        "violations": violations,
        "thresholds": {
            "sim_score_min": SIM_SCORE_THRESHOLD,
            "edit_pct_max": EDIT_PCT_THRESHOLD
        }
    }
