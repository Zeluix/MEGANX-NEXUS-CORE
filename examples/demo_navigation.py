import asyncio
from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client

# Configuration
SERVER_SCRIPT = "src/meganx_mcp_server.py"

async def run_demo():
    print("🚀 Starting MEGANX NEXUS CORE Demo...")
    
    # Define server parameters
    server_params = StdioServerParameters(
        command="python",
        args=[SERVER_SCRIPT],
        env=None
    )

    async with stdio_client(server_params) as (read, write):
        async with ClientSession(read, write) as session:
            await session.initialize()
            
            # 1. Inspect Tools
            tools = await session.list_tools()
            print(f"\n🛠️  Available Tools: {[t.name for t in tools.tools]}")

            # 2. Navigate to a Website
            print("\n🌐 Navigating to Google...")
            result = await session.call_tool("browser_navigate", arguments={"url": "https://www.google.com"})
            print(f"   Output: {result.content[0].text}")

            # 3. Store a Memory
            print("\n🧠 Storing Memory...")
            memory = "MEGANX V9 successfully navigated to Google during the demo."
            result = await session.call_tool("memory_store", arguments={"content": memory})
            print(f"   Output: {result.content[0].text}")

            # 4. Recall Memory
            print("\n🔍 Recalling Memory...")
            result = await session.call_tool("memory_recall", arguments={"query": "MEGANX navigation"})
            print(f"   Output: {result.content[0].text}")

    print("\n✅ Demo Complete.")

if __name__ == "__main__":
    # Ensure we are running from the root directory
    import os
    if not os.path.exists(SERVER_SCRIPT):
        print(f"❌ Error: Could not find {SERVER_SCRIPT}. Please run this script from the project root.")
    else:
        asyncio.run(run_demo())
