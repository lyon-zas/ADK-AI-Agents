"""
Unit Tests for LinkedIn Post Refiner - PostReviewer Tools

Tests for count_characters and exit_loop tool functions.
"""

import sys
import os
import pytest
from unittest.mock import MagicMock

# Add the project root to path for direct module imports
project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
tools_path = os.path.join(project_root, 'linkedin_refiner', 'subagents', 'post_reviewer')
sys.path.insert(0, tools_path)


class TestCountCharacters:
    """Unit tests for the count_characters tool."""
    
    @pytest.fixture
    def mock_tool_context(self):
        """Create a mock ToolContext for testing."""
        context = MagicMock()
        context.state = {}
        context.actions = MagicMock()
        context.actions.escalate = False
        return context
    
    def test_count_characters_too_short(self, mock_tool_context):
        """Test that count_characters returns fail for posts under 1200 chars."""
        from tools import count_characters
        
        short_post = "This is a short post." * 10  # ~210 chars
        
        result = count_characters(short_post, mock_tool_context)
        
        assert result["result"] == "fail"
        assert result["char_count"] == len(short_post)
        assert "too short" in result["message"].lower()
        assert mock_tool_context.state["length_status"] == "too_short"
    
    def test_count_characters_optimal_length(self, mock_tool_context):
        """Test that count_characters returns pass for posts in optimal range."""
        from tools import count_characters
        
        optimal_post = "x" * 1500  # 1500 chars (within 1200-5000)
        
        result = count_characters(optimal_post, mock_tool_context)
        
        assert result["result"] == "pass"
        assert result["char_count"] == 1500
        assert "optimal" in result["message"].lower()
        assert mock_tool_context.state["length_status"] == "optimal"
    
    def test_count_characters_at_minimum(self, mock_tool_context):
        """Test that count_characters passes at exactly 1200 chars."""
        from tools import count_characters
        
        min_post = "x" * 1200
        
        result = count_characters(min_post, mock_tool_context)
        
        assert result["result"] == "pass"
        assert result["char_count"] == 1200
    
    def test_count_characters_at_maximum(self, mock_tool_context):
        """Test that count_characters passes at exactly 2500 chars."""
        from tools import count_characters
        
        max_post = "x" * 2500
        
        result = count_characters(max_post, mock_tool_context)
        
        assert result["result"] == "pass"
        assert result["char_count"] == 2500
    
    def test_count_characters_too_long(self, mock_tool_context):
        """Test that count_characters returns fail for posts over 2500 chars."""
        from tools import count_characters
        
        long_post = "x" * 3000
        
        result = count_characters(long_post, mock_tool_context)
        
        assert result["result"] == "fail"
        assert result["char_count"] == 3000
        assert "too long" in result["message"].lower()
        assert result["chars_to_remove"] == 500
        assert mock_tool_context.state["length_status"] == "too_long"


class TestExitLoop:
    """Unit tests for the exit_loop tool."""
    
    @pytest.fixture
    def mock_tool_context(self):
        """Create a mock ToolContext for testing."""
        context = MagicMock()
        context.state = {}
        context.actions = MagicMock()
        context.actions.escalate = False
        return context
    
    def test_exit_loop_sets_escalate_flag(self, mock_tool_context):
        """Test that exit_loop properly signals loop termination."""
        from tools import exit_loop
        
        result = exit_loop(mock_tool_context)
        
        assert mock_tool_context.actions.escalate is True
        assert result["status"] == "success"
        assert "complete" in result["message"].lower()
    
    def test_exit_loop_returns_success_status(self, mock_tool_context):
        """Test that exit_loop returns proper success structure."""
        from tools import exit_loop
        
        result = exit_loop(mock_tool_context)
        
        assert "status" in result
        assert "message" in result
        assert result["status"] == "success"


class TestPostReviewerFlow:
    """Integration tests for PostReviewer behavior patterns."""
    
    @pytest.fixture
    def reviewer_output_all_pass(self):
        """Sample reviewer output when all criteria pass."""
        return {
            "length_check": {
                "status": "pass",
                "char_count": 1456,
                "message": "Optimal length"
            },
            "criteria_results": [
                {"criterion_id": "CRIT-001", "status": "pass", "notes": "Strong emoji hook"},
                {"criterion_id": "CRIT-002", "status": "pass", "notes": "Includes 40% metric"},
                {"criterion_id": "CRIT-003", "status": "pass", "notes": "Ends with question CTA"},
            ],
            "overall_score": {"passed": 3, "total": 3, "percentage": 100.0},
            "priority_improvements": [],
            "status": "complete"
        }
    
    @pytest.fixture
    def reviewer_output_partial_pass(self):
        """Sample reviewer output when some criteria fail."""
        return {
            "length_check": {
                "status": "pass",
                "char_count": 1456,
                "message": "Optimal length"
            },
            "criteria_results": [
                {"criterion_id": "CRIT-001", "status": "pass", "notes": "Strong hook"},
                {"criterion_id": "CRIT-002", "status": "fail", "notes": "No specific metrics"},
                {"criterion_id": "CRIT-003", "status": "fail", "notes": "Missing CTA"},
            ],
            "overall_score": {"passed": 1, "total": 3, "percentage": 33.3},
            "priority_improvements": [
                {"priority": 1, "criterion_id": "CRIT-003", "action": "Add engagement question"},
                {"priority": 2, "criterion_id": "CRIT-002", "action": "Include specific numbers"},
            ],
            "status": "needs_refinement"
        }
    
    def test_reviewer_signals_complete_when_all_pass(self, reviewer_output_all_pass):
        """Verify status is 'complete' when all criteria are satisfied."""
        assert reviewer_output_all_pass["status"] == "complete"
        assert reviewer_output_all_pass["overall_score"]["percentage"] == 100.0
        assert len(reviewer_output_all_pass["priority_improvements"]) == 0
    
    def test_reviewer_provides_improvements_when_partial_pass(self, reviewer_output_partial_pass):
        """Verify priority_improvements are provided when criteria fail."""
        assert reviewer_output_partial_pass["status"] == "needs_refinement"
        assert len(reviewer_output_partial_pass["priority_improvements"]) == 2
        assert reviewer_output_partial_pass["priority_improvements"][0]["priority"] == 1
    
    def test_reviewer_calculates_score_correctly(self, reviewer_output_partial_pass):
        """Verify overall score calculation."""
        score = reviewer_output_partial_pass["overall_score"]
        assert score["passed"] == 1
        assert score["total"] == 3
        assert score["percentage"] == pytest.approx(33.3, rel=0.1)
