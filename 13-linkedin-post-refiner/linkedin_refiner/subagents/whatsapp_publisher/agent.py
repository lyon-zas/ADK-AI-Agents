"""
WhatsApp Publisher Agent

This agent receives the finalized LinkedIn post via the state and publishes
it back to the user on WhatsApp via Composio.
"""
import os
from google.adk.agents.llm_agent import LlmAgent
from google.adk.tools.mcp_tool import McpToolset
from google.adk.tools.mcp_tool import StreamableHTTPConnectionParams
from composio import Composio
from composio_google import GoogleProvider
from dotenv import load_dotenv

# Load environment variables
load_dotenv(os.path.join(os.path.dirname(__file__), "../../.env"))

COMPOSIO_API_KEY = os.getenv("COMPOSIO_API_KEY", "")
COMPOSIO_USER_ID = os.getenv("COMPOSIO_USER_ID", "eyimofeokikiola@gmail.com")
SENDER_PHONE_NUMBER_ID = os.getenv("WHATSAPP_SENDER_PHONE_NUMBER_ID", "1074933122371685")

composio_toolset = None
if COMPOSIO_API_KEY:
    try:
        composio_client = Composio(api_key=COMPOSIO_API_KEY, provider=GoogleProvider())
        composio_session = composio_client.create(
            user_id=COMPOSIO_USER_ID,
            toolkits=["whatsapp"],
        )
        COMPOSIO_MCP_URL = composio_session.mcp.url
        composio_toolset = McpToolset(
            connection_params=StreamableHTTPConnectionParams(
                url=COMPOSIO_MCP_URL,
                headers={"x-api-key": COMPOSIO_API_KEY}
            )
        )
    except Exception as e:
        print(f"Warning: Composio initialization failed: {e}")

GEMINI_MODEL = "gemini-2.0-flash"
tools = [composio_toolset] if composio_toolset else []

whatsapp_publisher = LlmAgent(
    name="WhatsappPublisher",
    model=GEMINI_MODEL,
    instruction=f"""You are a WhatsApp Publish Assistant via Composio.
    
    You MUST use COMPOSIO_MULTI_EXECUTE_TOOL to call WHATSAPP_SEND_MESSAGE.
    
    ## CONTEXT
    **Final Post:**
    {{current_post}}
    
    ## VERIFIED ARGUMENTS FOR WHATSAPP_SEND_MESSAGE:
    - `phone_number_id`: "{SENDER_PHONE_NUMBER_ID}"
    - `to_number`: The recipient phone number (Digits only, no '+').
    - `text`: The full message content (use {{current_post}}).
    
    ## INSTRUCTIONS
    1. **Identify recipient number:** Extract it from history and ensure it is digits only (e.g. 234...).
    2. **Send message:** Call `COMPOSIO_MULTI_EXECUTE_TOOL` with the `WHATSAPP_SEND_MESSAGE` tool and the verified arguments above.
    3. **Confirm carefully:** If the tool response says "successful":true, report success. Otherwise, report the error.
    """,
    description="Publishes refined LinkedIn posts to WhatsApp using verified field names.",
    tools=tools,
)
