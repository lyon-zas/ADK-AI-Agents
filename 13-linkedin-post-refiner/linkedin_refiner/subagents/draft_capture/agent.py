"""
Draft Capture Agent

This agent captures the user's LinkedIn post draft and stores it in state
so subsequent agents can access it via the {current_post} template variable.
"""

from google.adk.agents.llm_agent import LlmAgent

# Constants
GEMINI_MODEL = "gemini-2.5-flash"

# Define the Draft Capture Agent
draft_capture = LlmAgent(
    name="DraftCapture",
    model=GEMINI_MODEL,
    instruction="""You are a Draft Capture Assistant.

    Your task is to extract the LinkedIn post draft from the user's message.
    
    ## TASK
    1. Read the user's message
    2. Extract ONLY the LinkedIn post draft content
    3. If the user provides context or instructions along with the draft, separate them
    4. Output ONLY the raw draft text
    
    ## OUTPUT INSTRUCTIONS
    - Return ONLY the draft post content
    - Do not add any commentary, explanations, or formatting
    - If no clear draft is provided, return the main content of the user's message
    
    Example:
    User: "Please refine my LinkedIn post: I just finished a project. It was great."
    Output: "I just finished a project. It was great."
    """,
    description="Captures the user's draft and stores it in state for subsequent agents",
    output_key="current_post",
)
