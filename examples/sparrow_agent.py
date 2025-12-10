import asyncio
import json
import sys
import os

# Add src to path to import server if needed, though we connect via stdio
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'src'))

from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client

# Configuration
SERVER_SCRIPT = "src/meganx_mcp_server.py"
MODEL_PATH = "models/Llama-3.2-1B-Instruct-Q4_K_M.gguf" # Placeholder

async def mock_llm_inference(user_input, context):
    """
    Simulates the LLM's decision making. 
    In the real version, this would call llama_cpp.Llama(model_path).create_chat_completion()
    """
    print(f"\n[SPARROW THINKING] Processing: '{user_input}'...")
    await asyncio.sleep(1) # Simulate inference time

    # Simple keyword-based logic for the POC
    if "google" in user_input.lower():
        return {
            "type": "tool_call",
            "tool": "browser_navigate",
            "args": {"url": "https://www.google.com"}
        }
    elif "remember" in user_input.lower():
        return {
            "type": "tool_call",
            "tool": "memory_store",
            "args": {"content": user_input}
        }
    else:
        return {
            "type": "text",
            "content": "I am Sparrow, your local agent. I can browse the web and remember things. Try asking me to 'go to google' or 'remember this'."
        }

async def run_sparrow():
    print("[SPARROW] AGENT v0.1 (Legacy Hardware Edition)")
    print(f"Target Hardware: i3 540 | 8GB RAM | GT 730")
    print("Initializing MCP Connection...")

    # Define server parameters
    server_params = StdioServerParameters(
        command="python",
        args=[SERVER_SCRIPT],
        env=None
    )

    async with stdio_client(server_params) as (read, write):
        async with ClientSession(read, write) as session:
            await session.initialize()
            tools = await session.list_tools()
            print(f"[OK] Connected to MEGANX CORE. Tools: {[t.name for t in tools.tools]}")
            
            # Main Loop
            while True:
                try:
                    user_input = input("\n[USER]: ")
                    if user_input.lower() in ["exit", "quit"]:
                        break

                    # 1. LLM Inference
                    decision = await mock_llm_inference(user_input, [])

                    # 2. Action Execution
                    if decision["type"] == "tool_call":
                        print(f"[TOOL CALL] {decision['tool']}({decision['args']})")
                        result = await session.call_tool(decision["tool"], arguments=decision["args"])
                        print(f"[OBSERVATION] {result.content[0].text}")
                    else:
                        print(f"[SPARROW]: {decision['content']}")

                except KeyboardInterrupt:
                    break
                except Exception as e:
                    print(f"[ERROR] Error: {e}")

if __name__ == "__main__":
    # Ensure we are running from the root directory
    if not os.path.exists(SERVER_SCRIPT):
        print(f"[ERROR] Error: Could not find {SERVER_SCRIPT}. Please run this script from the project root.")
    else:
        asyncio.run(run_sparrow())
python examples/sparrow_agent.py
