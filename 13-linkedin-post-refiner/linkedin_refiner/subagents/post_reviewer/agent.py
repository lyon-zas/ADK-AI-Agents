"""
LinkedIn Post Reviewer Agent

This agent reviews LinkedIn posts against the selected criteria and 
provides feedback or exits the loop if all requirements are met.
"""

from google.adk.agents.llm_agent import LlmAgent

from .tools import count_characters, exit_loop

# Constants
GEMINI_MODEL = "gemini-3-pro-preview"

# Define the Post Reviewer Agent
post_reviewer = LlmAgent(
    name="PostReviewer",
    model=GEMINI_MODEL,
    instruction="""You are a LinkedIn Post Quality Reviewer.

Your task is to evaluate the quality of a LinkedIn post against the selected criteria.

## INPUTS
**Current Post to Review:**
{current_post}

**Selected Criteria:**
{selected_criteria}

## EVALUATION PROCESS

1. **Length Check**:
   Use the count_characters tool to verify the post length.
   - Pass the post text directly to the tool

2. **Criteria Evaluation**:
   For each item in the evaluation checklist:
   - Does the post satisfy this criterion? (pass/fail)
   - If fail, what specifically needs to be improved?

3. **Overall Assessment**:
   - Calculate how many criteria are met vs. total
   - Identify the most critical improvements needed (max 3)

## OUTPUT FORMAT
You MUST output valid JSON in the following structure:

```json
{
  "length_check": {
    "status": "pass",
    "char_count": 1456,
    "target_min": 1200,
    "target_max": 5000,
    "message": "Post length is optimal"
  },
  "criteria_results": [
    {
      "criterion_id": "CRIT-001",
      "check_description": "First line contains hook",
      "status": "pass",
      "notes": "Strong emoji hook with surprising claim"
    },
    {
      "criterion_id": "CRIT-003",
      "check_description": "Includes specific metrics",
      "status": "fail",
      "notes": "No specific numbers or percentages mentioned"
    }
  ],
  "overall_score": {
    "passed": 5,
    "total": 6,
    "percentage": 83.3
  },
  "priority_improvements": [
    {
      "priority": 1,
      "criterion_id": "CRIT-003",
      "action": "Add specific metric like time saved or percentage improvement"
    }
  ],
  "status": "needs_refinement"
}
```

## TERMINATION LOGIC

**IF ALL criteria PASS and length is optimal:**
1. Set "status": "complete"
2. Call the exit_loop function to terminate the refinement loop

**IF ANY criterion FAILS:**
1. Set "status": "needs_refinement"
2. Provide detailed priority_improvements (max 3)
3. Do NOT call exit_loop

## SCHEMA REQUIREMENTS
- status: One of "pass" or "fail" for each check
- overall_score.percentage: Calculated as (passed/total)*100
- priority_improvements: Ordered by impact (most important first)
- status: One of "complete" or "needs_refinement"

## IMPORTANT
- Be specific in your feedback - vague feedback leads to poor refinements
- Prioritize the most impactful issues first
- Only call exit_loop when ALL criteria are satisfied
- Only return max 3 priority improvements
""",
    description="Reviews post against selected criteria and provides feedback or exits if requirements are met",
    tools=[count_characters, exit_loop],
    output_key="review_feedback",
)

