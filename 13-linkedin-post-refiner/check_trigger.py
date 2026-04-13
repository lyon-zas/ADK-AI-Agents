import os
from composio_google_adk import ComposioToolset
from dotenv import load_dotenv

load_dotenv(os.path.join(os.path.dirname(__file__), "linkedin_refiner/.env"))

# Using the toolset to inspect actions/triggers is often the most direct way
toolset = ComposioToolset()

try:
    # Most toolsets expose triggers or app names
    triggers = toolset.get_expected_triggers_for_app("whatsapp")
    print("\n--- WHATSAPP TRIGGERS ---")
    for t in triggers:
        print(f"Name: {t}")
        # If we can get more info
        # trigger_info = toolset.get_trigger_info(t)
except Exception as e:
    print(f"Error fetching triggers: {e}")
