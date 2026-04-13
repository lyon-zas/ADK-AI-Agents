import os
import asyncio
from dotenv import load_dotenv

load_dotenv(os.path.join(os.path.dirname(__file__), "linkedin_refiner/.env"))

from google.adk import Runner
from google.adk.sessions.in_memory_session_service import InMemorySessionService
from google.genai import types
from linkedin_refiner.subagents.whatsapp_publisher.agent import whatsapp_publisher

async def main():
    print("🚀 Running FINAL verification to the new verified recipient...")
    
    runner = Runner(
        app_name="TestWhatsApp",
        agent=whatsapp_publisher,
        session_service=InMemorySessionService(),
        auto_create_session=True
    )

    mock_post = "🚀 FINAL TEST: The WhatsApp agent fix is now fully verified and working with your new account!"
    recipient = "2347085581953"  # Updated to the number in your allowed list!

    user_input = types.Content(
        role="user",
        parts=[types.Part(text=f"Send this finalized post to recipient number {recipient} via WhatsApp.")]
    )
    
    async for event in runner.run_async(
        user_id="test_user",
        session_id="test_session",
        new_message=user_input,
        state_delta={"current_post": mock_post}
    ):
        if event.content:
            for part in event.content.parts:
                if part.function_call:
                    print(f"\n[TOOL CALL]: {part.function_call.name}({part.function_call.args})\n")
                if part.function_response:
                    print(f"\n[TOOL RESPONSE]: {part.function_response.name} -> {str(part.function_response.response)[:400]}...\n")
                if part.text:
                    print(f"\n[TEXT]: {part.text}\n")

if __name__ == "__main__":
    asyncio.run(main())
