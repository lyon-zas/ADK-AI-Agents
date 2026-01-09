"""
Tools for LinkedIn Post Reviewer Agent

This module provides tools for validating and controlling the refinement loop.
"""

from typing import Any, Dict

from google.adk.tools.tool_context import ToolContext


def count_characters(text: str, tool_context: ToolContext) -> Dict[str, Any]:
    """
    Tool to count characters in the provided text and provide length-based feedback.
    LinkedIn optimal length is between 1200-5000 characters for maximum engagement.

    Args:
        text: The text to analyze for character count
        tool_context: Context for accessing and updating session state

    Returns:
        Dict[str, Any]: Dictionary containing:
            - result: 'fail' or 'pass'
            - char_count: number of characters in text
            - message: feedback message about the length
    """
    char_count = len(text)
    MIN_LENGTH = 1200
    MAX_LENGTH = 5000

    print("\n----------- TOOL DEBUG -----------")
    print(f"Checking text length: {char_count} characters")
    print("----------------------------------\n")

    if char_count < MIN_LENGTH:
        chars_needed = MIN_LENGTH - char_count
        tool_context.state["length_status"] = "too_short"
        return {
            "result": "fail",
            "char_count": char_count,
            "chars_needed": chars_needed,
            "message": f"Post is too short ({char_count} chars). Add {chars_needed} more characters to reach optimal length of {MIN_LENGTH}.",
        }
    elif char_count > MAX_LENGTH:
        chars_to_remove = char_count - MAX_LENGTH
        tool_context.state["length_status"] = "too_long"
        return {
            "result": "fail",
            "char_count": char_count,
            "chars_to_remove": chars_to_remove,
            "message": f"Post is too long ({char_count} chars). Remove {chars_to_remove} characters to meet maximum length of {MAX_LENGTH}.",
        }
    else:
        tool_context.state["length_status"] = "optimal"
        return {
            "result": "pass",
            "char_count": char_count,
            "message": f"Post length is optimal ({char_count} characters).",
        }


def exit_loop(tool_context: ToolContext) -> Dict[str, Any]:
    """
    Call this function ONLY when the post meets ALL quality requirements,
    signaling the iterative refinement process should end.

    This should be called when:
    - The post meets the optimal length requirements
    - All selected criteria have been satisfied
    - The post is ready for publishing

    Args:
        tool_context: Context for tool execution

    Returns:
        Empty dictionary
    """
    print("\n----------- EXIT LOOP TRIGGERED -----------")
    print("Post refinement completed successfully!")
    print("All criteria met - loop will exit now")
    print("------------------------------------------\n")

    tool_context.actions.escalate = True
    return {"status": "success", "message": "Post meets all quality requirements. Refinement complete."}
