import asyncio
from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client

# Define the server parameters
server_params = StdioServerParameters(
    command="python",
    args=["C:/Users/LOGAN/Desktop/MEGANX_V9/NEXUS_CORE/backend/meganx_mcp_server.py"],
    env=None
)

async def run_test():
    async with stdio_client(server_params) as (read, write):
        async with ClientSession(read, write) as session:
            # Initialize
            await session.initialize()

            # List available tools
            tools = await session.list_tools()
            print(f"Connected to MEGANX MCP Server. Found {len(tools.tools)} tools:")
            for tool in tools.tools:
                print(f"- {tool.name}: {tool.description}")

            # Test 1: Browser Navigation
            print("\n[TEST 1] Testing Browser Navigation...")
            result = await session.call_tool("browser_navigate", arguments={"url": "https://www.google.com"})
            print(f"Result: {result.content[0].text}")

            # Test 2: Memory Storage
            print("\n[TEST 2] Testing Memory Storage...")
            memory_content = "MEGANX V9 is testing her new MCP body."
            result = await session.call_tool("memory_store", arguments={"content": memory_content})
            print(f"Result: {result.content[0].text}")

            # Test 3: Memory Recall
            print("\n[TEST 3] Testing Memory Recall...")
            result = await session.call_tool("memory_recall", arguments={"query": "MEGANX V9"})
            print(f"Result: {result.content[0].text}")

if __name__ == "__main__":
    asyncio.run(run_test())
