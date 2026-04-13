import json
import os
import re

CACHE_FILE = "criteria_cache.json"

def get_cached_criteria() -> str:
    """Retrieves cached LinkedIn criteria if available."""
    if os.path.exists(CACHE_FILE):
        try:
            with open(CACHE_FILE, "r") as f:
                data = json.load(f)
                return json.dumps(data)
        except Exception:
            return ""
    return ""

def save_criteria_to_cache(criteria_json: str) -> str:
    """
    Saves a JSON string of LinkedIn criteria to the local cache file.
    Strips markdown code blocks if present.
    """
    try:
        # Strip markdown code blocks if the AI included them
        clean_json = criteria_json.strip()
        if clean_json.startswith("```"):
            # Use regex to find the content between the first and last triple backticks
            match = re.search(r"```(?:json)?\n?(.*?)\n?```", clean_json, re.DOTALL)
            if match:
                clean_json = match.group(1).strip()
        
        # Validate that it is indeed a JSON string
        data = json.loads(clean_json)
        with open(CACHE_FILE, "w") as f:
            json.dump(data, f, indent=2)
        return "Criteria saved to cache successfully."
    except Exception as e:
        return f"Error saving to cache: {str(e)}"
