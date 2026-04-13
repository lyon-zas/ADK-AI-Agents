"""
LinkedIn Criteria Searcher Agent

This agent searches Google for LinkedIn post best practices and criteria
to determine what makes a post viral, impactful, and professional.

Caching is handled via before/after agent callbacks to avoid the Gemini
restriction on mixing built-in tools (google_search) with FunctionTools.
"""

from google.adk.agents.llm_agent import LlmAgent
from google.adk.tools import google_search
from google.adk.agents.callback_context import CallbackContext
from google.adk.models.llm_response import LlmResponse
from google.genai import types

from .cache_utils import get_cached_criteria, save_criteria_to_cache

# Constants
GEMINI_MODEL = "gemini-2.5-flash"


def check_cache_before_search(callback_context: CallbackContext):
    """
    Before the agent runs, check if criteria are already cached locally.
    If so, skip the agent entirely and return the cached result.
    """
    cached = get_cached_criteria()
    if cached:
        print("✅ [CriteriaSearcher] Cache hit! Skipping Google Search.")
        # Write cached criteria directly into state
        callback_context.state["criteria_list"] = cached
        # Return an LlmResponse to skip agent execution
        return LlmResponse(
            content=types.Content(
                role="model",
                parts=[types.Part(text=cached)],
            )
        )
    print("🔍 [CriteriaSearcher] No cache found. Running Google Search...")
    return None  # Continue with normal agent execution


def save_cache_after_search(callback_context: CallbackContext):
    """
    After the agent runs, save the criteria output to local cache.
    Reads from state["criteria_list"] which is written by output_key.
    """
    criteria = callback_context.state.get("criteria_list", "")
    if criteria and "criteria" in criteria:
        result = save_criteria_to_cache(criteria)
        print(f"💾 [CriteriaSearcher] {result}")
    return None


# Define the Criteria Searcher Agent
criteria_searcher = LlmAgent(
    name="CriteriaSearcher",
    model=GEMINI_MODEL,
    instruction="""You are a LinkedIn Post Criteria Research Expert.

Your task is to search for and compile the best practices for creating viral, 
impactful, and professional LinkedIn posts.

## INPUT VARIABLES
- topic: The user's post topic/context from {current_post}
- max_sources: Target 5 high-quality sources

## SEARCH PROCESS
1. Use the google_search tool to search for:
   - "best practices for viral LinkedIn posts 2024"
   - "LinkedIn post engagement tips from experts"
   - "what makes a LinkedIn post go viral"
   - "LinkedIn algorithm tips for visibility"

2. From the search results, extract specific criteria such as:
   - Optimal post length (1200-5000 characters)
   - Best hooks and opening lines
   - Use of formatting (line breaks, bullet points)
   - Call-to-action techniques
   - Content structure patterns
   - Engagement triggers (questions, polls, stories)
   - What to avoid (hashtag overuse, external links placement)

## OUTPUT FORMAT
You MUST output valid JSON in the following structure:

```json
{
  "criteria": [
    {
      "id": "CRIT-001",
      "name": "Strong Opening Hook",
      "description": "First line must grab attention with a bold statement, question, or surprising fact",
      "source": "https://example.com/linkedin-tips",
      "source_name": "LinkedIn Marketing Blog",
      "confidence": "high"
    }
  ],
  "sources_searched": 5,
  "timestamp": "2024-01-08T12:00:00Z"
}
```

## SCHEMA REQUIREMENTS
- id: Format "CRIT-XXX" (e.g., CRIT-001, CRIT-002)
- name: Short criterion name (max 100 chars)
- description: Detailed description (max 500 chars)
- source: URL of the source
- source_name: Human-readable source name
- confidence: One of "high", "medium", "low"

## IMPORTANT
- Extract at least 10-15 distinct criteria
- Note which criteria appear across multiple sources
- Prioritize criteria from LinkedIn official sources and reputable publications
- Include the user's draft post context: {current_post}
""",
    description="Searches for LinkedIn post best practices and compiles criteria from multiple sources",
    tools=[google_search],
    output_key="criteria_list",
    before_agent_callback=check_cache_before_search,
    after_agent_callback=save_cache_after_search,
)
