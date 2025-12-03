# MEGANX NEXUS CORE Architecture

## Overview

MEGANX NEXUS CORE is an implementation of the **Model Context Protocol (MCP)** that provides a standardized interface for Large Language Models (LLMs) to interact with the external world (Web) and persistent internal state (Memory).

## System Components

### 1. The MCP Server (`src/meganx_mcp_server.py`)
The core of the system is a FastMCP server that exposes tools to any MCP-compliant client (Claude Desktop, Zed, etc.).

**Key Responsibilities:**
- **Tool Registration:** Exposes python functions as standardized MCP tools.
- **Request Handling:** Processes tool calls from the LLM.
- **State Management:** Manages the lifecycle of the browser and database connections.

### 2. Perception Module (Playwright)
We use **Playwright** for browser automation instead of simple HTTP requests to ensure high-fidelity interaction with modern, JavaScript-heavy web applications.

**Workflow:**
1.  **`browser_navigate(url)`**: Launches a headed/headless Chromium instance.
2.  **`browser_click(selector)`**: Simulates user interaction events.
3.  **`browser_extract(selector)`**: Retrieves text content from the DOM.

**Why Playwright?**
- **Dynamic Content:** Can render React/Vue/Angular apps.
- **Anti-Bot Evasion:** Simulates a real user agent more effectively than `requests` or `selenium`.
- **Visual Context:** Capable of taking screenshots (future feature).

### 3. Memory Module (ChromaDB)
We use **ChromaDB** as a local vector database to provide long-term semantic memory.

**Workflow:**
1.  **`memory_store(content)`**:
    - Receives text content.
    - Generates embeddings using `all-MiniLM-L6-v2`.
    - Stores the vector + metadata in `./nexus_memory`.
2.  **`memory_recall(query)`**:
    - Receives a semantic query.
    - Performs a nearest-neighbor search in the vector space.
    - Returns the top N most relevant text snippets.

## Data Flow

```mermaid
graph TD
    LLM[Claude / LLM] <-->|MCP Protocol| Server[MCP Server]
    Server <-->|Control| Browser[Playwright (Chromium)]
    Browser <-->|HTTP/JS| Web[The Internet]
    Server <-->|Read/Write| DB[(ChromaDB)]
    DB <-->|Embeddings| Disk[Local Storage]
```

## Security Considerations
- **Local Execution:** All code runs locally on the user's machine.
- **No External API Keys:** The core server does not require external cloud keys (unless using Supabase for sync).
- **Sandboxing:** Browser runs in a separate process.

## Future Roadmap
- **Stealth Mode:** Integration with `undetected-chromedriver` logic.
- **Hybrid Search:** Combining vector search with keyword search (BM25).
- **Multi-Agent:** Orchestration of multiple MCP servers.
