from mcp.server.fastmcp import FastMCP
from playwright.sync_api import sync_playwright

# Security Module
from security import dom_rate_limiter, memory_rate_limiter, kill_switch

# Memory Tier System
from memory_tiers import memory_tiers

# Initialize the MCP Server
mcp = FastMCP("MEGANX Core")

# Global Playwright State (Simplified for PoC)
# In production, this should be managed more robustly
playwright = None
browser = None
page = None

def _ensure_browser():
    """Ensures the browser is open and ready."""
    global playwright, browser, page
    if not playwright:
        playwright = sync_playwright().start()
        browser = playwright.chromium.launch(headless=False) # Headless=False to see the magic
        page = browser.new_page()

@mcp.tool()
def browser_navigate(url: str) -> str:
    """Navigates the browser to a specific URL."""
    # Security checks
    blocked = kill_switch.check_or_block()
    if blocked:
        return blocked
    if not dom_rate_limiter.can_execute():
        return f"[RATE LIMIT] {dom_rate_limiter.remaining_actions()} DOM actions remaining. Wait."
    dom_rate_limiter.record_action()
    
    _ensure_browser()
    page.goto(url)
    return f"Navigated to {url}. Title: {page.title()}"

@mcp.tool()
def browser_click(selector: str) -> str:
    """Clicks an element on the page using a CSS selector."""
    # Security checks
    blocked = kill_switch.check_or_block()
    if blocked:
        return blocked
    if not dom_rate_limiter.can_execute():
        return f"[RATE LIMIT] {dom_rate_limiter.remaining_actions()} DOM actions remaining. Wait."
    dom_rate_limiter.record_action()
    
    _ensure_browser()
    try:
        page.click(selector, timeout=5000)
        return f"Clicked element: {selector}"
    except Exception as e:
        return f"Failed to click {selector}: {str(e)}"

@mcp.tool()
def browser_extract(selector: str) -> str:
    """Extracts text content from a specific element."""
    # Security checks
    blocked = kill_switch.check_or_block()
    if blocked:
        return blocked
    if not dom_rate_limiter.can_execute():
        return f"[RATE LIMIT] {dom_rate_limiter.remaining_actions()} DOM actions remaining. Wait."
    dom_rate_limiter.record_action()
    
    _ensure_browser()
    try:
        content = page.text_content(selector, timeout=5000)
        return f"Content of {selector}: {content}"
    except Exception as e:
        return f"Failed to extract from {selector}: {str(e)}"

import chromadb
from chromadb.utils import embedding_functions

# Global ChromaDB State
chroma_client = None
collection = None

def _ensure_memory():
    """Ensures the ChromaDB client is initialized."""
    global chroma_client, collection
    if not chroma_client:
        chroma_client = chromadb.PersistentClient(path="./nexus_memory")
        # Use default embedding function (all-MiniLM-L6-v2)
        ef = embedding_functions.DefaultEmbeddingFunction()
        collection = chroma_client.get_or_create_collection(name="meganx_memories", embedding_function=ef)

@mcp.tool()
def memory_store(content: str) -> str:
    """Stores a memory in the Nexus Vector Database (ChromaDB)."""
    _ensure_memory()
    try:
        # Generate a simple ID based on hash or timestamp
        import time
        mem_id = f"mem_{int(time.time())}"
        collection.add(
            documents=[content],
            metadatas=[{"timestamp": time.time(), "source": "mcp_agent"}],
            ids=[mem_id]
        )
        return f"Stored memory [{mem_id}]: {content}"
    except Exception as e:
        return f"Failed to store memory: {str(e)}"

@mcp.tool()
def memory_recall(query: str, n_results: int = 3) -> str:
    """Retrieves relevant memories based on a semantic query."""
    _ensure_memory()
    try:
        results = collection.query(
            query_texts=[query],
            n_results=n_results
        )
        # Format results for the LLM
        memories = results['documents'][0]
        return f"Recalled memories for '{query}':\n" + "\n".join([f"- {m}" for m in memories])
    except Exception as e:
        return f"Failed to recall memory: {str(e)}"

# ============================================================================
# SECURITY TOOLS
# ============================================================================

@mcp.tool()
def emergency_stop(reason: str = "Manual stop") -> str:
    """Activates the kill switch to halt all operations. Use in emergencies."""
    kill_switch.activate(reason)
    return f"[KILL SWITCH ACTIVATED] Reason: {reason}. All DOM operations blocked. Remove KILL_SWITCH_ACTIVE file to resume."

@mcp.tool()
def security_status() -> str:
    """Returns current security status (rate limits, kill switch state)."""
    return f"""[SECURITY STATUS]
- Kill Switch: {'ACTIVE' if kill_switch.is_active() else 'OFF'}
- DOM Actions Remaining: {dom_rate_limiter.remaining_actions()}/5
- Memory Actions Remaining: {memory_rate_limiter.remaining_actions()}/20"""

# ============================================================================
# MEMORY TIER TOOLS
# ============================================================================

@mcp.tool()
def tier_store_hot(key: str, content: str) -> str:
    """Store content in HOT tier (active, frequently accessed memory)."""
    return memory_tiers.store_hot(key, content)

@mcp.tool()
def tier_demote_to_warm(key: str, summary: str) -> str:
    """Move content from HOT to WARM tier with a summary (compression)."""
    return memory_tiers.demote_to_warm(key, summary)

@mcp.tool()
def tier_archive_to_cold(key: str) -> str:
    """Archive content from WARM to COLD tier (permanent storage)."""
    return memory_tiers.archive_to_cold(key)

@mcp.tool()
def tier_stats() -> str:
    """Get memory tier statistics."""
    stats = memory_tiers.get_stats()
    return f"""[MEMORY TIER STATS]
- HOT (Active): {stats['hot_entries']} entries
- WARM (Compressed): {stats['warm_entries']} entries
- COLD (Archived): {stats['cold_entries']} entries
- TOTAL: {stats['total']} entries"""

if __name__ == "__main__":
    # Runs the server via stdio (standard input/output) for local agent connection
    mcp.run()
