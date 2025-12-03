from mcp.server.fastmcp import FastMCP
from playwright.sync_api import sync_playwright

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
    _ensure_browser()
    page.goto(url)
    return f"Navigated to {url}. Title: {page.title()}"

@mcp.tool()
def browser_click(selector: str) -> str:
    """Clicks an element on the page using a CSS selector."""
    _ensure_browser()
    try:
        page.click(selector, timeout=5000)
        return f"Clicked element: {selector}"
    except Exception as e:
        return f"Failed to click {selector}: {str(e)}"

@mcp.tool()
def browser_extract(selector: str) -> str:
    """Extracts text content from a specific element."""
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

if __name__ == "__main__":
    # Runs the server via stdio (standard input/output) for local agent connection
    mcp.run()
