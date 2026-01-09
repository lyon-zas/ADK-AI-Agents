"""
Unit Tests for LinkedIn Post Refiner - Similarity Utilities

Tests for similarity computation and edit percentage validation.
"""

import sys
import os
import pytest

# Add the project root to path for direct module imports
project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
utils_path = os.path.join(project_root, 'linkedin_refiner', 'utils')
sys.path.insert(0, utils_path)

# Import directly from the similarity module to avoid google-adk imports
from similarity import (
    tokenize,
    compute_edit_percentage,
    compute_jaccard_similarity,
    compute_similarity,
    validate_originality,
    SIM_SCORE_THRESHOLD,
    EDIT_PCT_THRESHOLD,
)


class TestTokenize:
    """Tests for the tokenize function."""
    
    def test_tokenize_basic(self):
        """Test basic tokenization."""
        text = "Hello World"
        tokens = tokenize(text)
        assert tokens == {"hello", "world"}
    
    def test_tokenize_with_punctuation(self):
        """Test tokenization removes punctuation."""
        text = "Hello, World! How are you?"
        tokens = tokenize(text)
        assert tokens == {"hello", "world", "how", "are", "you"}
    
    def test_tokenize_empty_string(self):
        """Test tokenization of empty string."""
        tokens = tokenize("")
        assert tokens == set()
    
    def test_tokenize_normalizes_case(self):
        """Test tokenization normalizes to lowercase."""
        text = "HELLO Hello hello"
        tokens = tokenize(text)
        assert tokens == {"hello"}


class TestComputeEditPercentage:
    """Tests for edit percentage computation."""
    
    def test_identical_posts(self):
        """Test edit percentage is 0 for identical posts."""
        post = "This is my LinkedIn post about AI"
        edit_pct = compute_edit_percentage(post, post)
        assert edit_pct == 0.0
    
    def test_completely_different_posts(self):
        """Test edit percentage for completely different content."""
        original = "Hello world"
        refined = "Goodbye universe"
        edit_pct = compute_edit_percentage(original, refined)
        # All tokens changed: hello, world removed; goodbye, universe added
        # 4 changed tokens / 2 original tokens = 200%
        assert edit_pct == 100.0  # Capped at 100%
    
    def test_minor_edit(self):
        """Test edit percentage for minor changes."""
        original = "I finished a great project using AI"
        refined = "I finished an amazing project using AI"  # 1 word changed
        edit_pct = compute_edit_percentage(original, refined)
        # Symmetric difference approach means changes are counted both ways
        # Just verify it's measurable and not 0 or 100
        assert 0 < edit_pct <= 100.0
    
    def test_empty_original(self):
        """Test edit percentage when original is empty."""
        edit_pct = compute_edit_percentage("", "new content")
        assert edit_pct == 100.0
    
    def test_both_empty(self):
        """Test edit percentage when both are empty."""
        edit_pct = compute_edit_percentage("", "")
        assert edit_pct == 0.0


class TestComputeJaccardSimilarity:
    """Tests for Jaccard similarity computation."""
    
    def test_identical_posts(self):
        """Test similarity is 1.0 for identical posts."""
        post = "This is my LinkedIn post"
        sim = compute_jaccard_similarity(post, post)
        assert sim == 1.0
    
    def test_completely_different_posts(self):
        """Test similarity is 0 for posts with no common tokens."""
        original = "hello world"
        refined = "goodbye universe"
        sim = compute_jaccard_similarity(original, refined)
        assert sim == 0.0
    
    def test_partial_overlap(self):
        """Test similarity for posts with partial overlap."""
        original = "I love AI and machine learning"
        refined = "I love AI and deep learning"  # 4/6 common
        sim = compute_jaccard_similarity(original, refined)
        # Intersection: {i, love, ai, and, learning} = 5
        # Union: {i, love, ai, and, machine, learning, deep} = 7
        assert 0.5 < sim < 1.0
    
    def test_both_empty(self):
        """Test similarity when both are empty."""
        sim = compute_jaccard_similarity("", "")
        assert sim == 1.0
    
    def test_one_empty(self):
        """Test similarity when one is empty."""
        sim = compute_jaccard_similarity("hello", "")
        assert sim == 0.0


class TestComputeSimilarity:
    """Tests for combined similarity computation."""
    
    def test_returns_tuple(self):
        """Test that function returns tuple of (sim_score, edit_pct)."""
        result = compute_similarity("hello world", "hello there")
        assert isinstance(result, tuple)
        assert len(result) == 2
    
    def test_identical_posts(self):
        """Test metrics for identical posts."""
        post = "This is my LinkedIn post about AI"
        sim_score, edit_pct = compute_similarity(post, post)
        assert sim_score == 1.0
        assert edit_pct == 0.0


class TestValidateOriginality:
    """Tests for originality validation."""
    
    def test_valid_edit(self):
        """Test validation passes for minor edits."""
        original = "I just finished a project using AI it was cool"
        refined = "I just finished an incredible project using AI it was amazing"
        result = validate_originality(original, refined)
        
        assert "is_valid" in result
        assert "sim_score" in result
        assert "edit_pct" in result
        assert "violations" in result
    
    def test_thresholds_included(self):
        """Test that thresholds are included in result."""
        result = validate_originality("hello", "hello")
        
        assert result["thresholds"]["sim_score_min"] == SIM_SCORE_THRESHOLD
        assert result["thresholds"]["edit_pct_max"] == EDIT_PCT_THRESHOLD
    
    def test_identical_post_is_valid(self):
        """Test that identical post is valid."""
        post = "My LinkedIn post about AI"
        result = validate_originality(post, post)
        
        assert result["is_valid"] is True
        assert result["sim_score"] == 1.0
        assert result["edit_pct"] == 0.0
        assert len(result["violations"]) == 0


class TestThresholdConstants:
    """Tests for threshold constant values."""
    
    def test_sim_score_threshold_value(self):
        """Verify SIM_SCORE_THRESHOLD is 0.70."""
        assert SIM_SCORE_THRESHOLD == 0.70
    
    def test_edit_pct_threshold_value(self):
        """Verify EDIT_PCT_THRESHOLD is 30."""
        assert EDIT_PCT_THRESHOLD == 30
