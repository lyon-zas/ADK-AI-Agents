# LinkedIn Post Refiner Agent

A LinkedIn post refinement agent built with Google Agent Development Kit (ADK) that uses a SequentialAgent + LoopAgent pattern to research, evaluate, and refine LinkedIn posts for maximum engagement and professional impact.

## Overview

This agent builds upon the patterns learned in the ADK crash course, specifically the `12-loop-agent` example, to create a comprehensive post refinement system that:

1. **Researches Best Practices** - Uses Google Search to find current LinkedIn post criteria
2. **Ranks Criteria** - Scores criteria by source credibility and repetition
3. **Selects Relevant Criteria** - Picks the most impactful criteria for your specific post
4. **Refines Iteratively** - Reviews and improves your post until all requirements are met

## Architecture

```
LinkedInPostRefinerPipeline (SequentialAgent)
├── CriteriaSearcher (LlmAgent + google_search)
├── CriteriaRanker (LlmAgent)
├── CriteriaSelector (LlmAgent)
└── PostRefinementLoop (LoopAgent)
    ├── PostReviewer (LlmAgent + tools)
    └── PostRefiner (LlmAgent)
```

## Setup

1. Copy `.env` from another project and add your API key:
   ```env
   GOOGLE_GENAI_USE_VERTEXAI=FALSE
   GOOGLE_API_KEY=your_api_key_here
   ```

2. Install dependencies if not already installed:
   ```bash
   pip install google-adk
   ```

## Usage

Navigate to the project directory and run:

```bash
cd 13-linkedin-post-refiner
adk web
```

Then enter a prompt like:

```
Please refine my LinkedIn post draft:

"Just finished a great project using AI. It was really cool and I learned a lot. 
Would love to connect with others interested in AI!"
```

The system will:
1. Search for LinkedIn best practices
2. Rank and select the most relevant criteria
3. Review your post against these criteria
4. Refine until all requirements are met
5. Return your polished, engagement-optimized post

## State Flow

| Key | Set By | Used By |
|-----|--------|---------|
| `current_post` | User / PostRefiner | All agents |
| `criteria_list` | CriteriaSearcher | CriteriaRanker |
| `ranked_criteria` | CriteriaRanker | CriteriaSelector |
| `selected_criteria` | CriteriaSelector | PostReviewer |
| `review_feedback` | PostReviewer | PostRefiner |

## Loop Termination

The refinement loop ends when:
- All quality criteria are met (PostReviewer calls `exit_loop`)
- Maximum iterations reached (10)
