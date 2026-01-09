"""
LinkedIn Post Refiner Root Agent

This module defines the root agent for the LinkedIn post refinement application.
It uses a SequentialAgent pipeline with:
1. Draft Capture (stores user's post in state)
2. Criteria Research Phase (search, rank, select)
3. Refinement Loop (review and refine iteratively)
"""

from google.adk.agents import LoopAgent, SequentialAgent

from .subagents.draft_capture import draft_capture
from .subagents.criteria_searcher import criteria_searcher
from .subagents.criteria_ranker import criteria_ranker
from .subagents.criteria_selector import criteria_selector
from .subagents.post_reviewer import post_reviewer
from .subagents.post_refiner import post_refiner


# Create the Refinement Loop Agent
refinement_loop = LoopAgent(
    name="PostRefinementLoop",
    max_iterations=10,
    sub_agents=[
        post_reviewer,
        post_refiner,
    ],
    description="Iteratively reviews and refines a LinkedIn post until quality requirements are met",
)

# Create the Sequential Pipeline
root_agent = SequentialAgent(
    name="LinkedInPostRefinerPipeline",
    sub_agents=[
        draft_capture,       # Step 1: Capture user's draft into state
        criteria_searcher,   # Step 2: Search for LinkedIn best practices
        criteria_ranker,     # Step 3: Rank criteria by credibility and repetition
        criteria_selector,   # Step 4: Select most relevant criteria for the post
        refinement_loop,     # Step 5: Iteratively review and refine the post
    ],
    description="""
    A comprehensive LinkedIn post refinement pipeline that:
    1. Captures the user's draft post
    2. Researches best practices for viral LinkedIn posts using Google Search
    3. Ranks criteria based on source credibility and repetition frequency
    4. Selects the most impactful criteria for the user's specific post
    5. Iteratively reviews and refines the post until all criteria are met
    
    Usage: Provide your LinkedIn post draft and the system will refine it
    to maximize engagement, visibility, and professional impact.
    """,
)
