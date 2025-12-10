# PROJECT SPARROW: Local Agency on Legacy Hardware

## 🎯 Objective
To run a fully autonomous AI agent on an **Intel Core i3 540 (Legacy)** with **8GB DDR3 RAM** and a **GT 730 (4GB)**. The agent must possess "Perception" (Browser) and "Memory" (Vector DB) capabilities via the **MEGANX-NEXUS-CORE** MCP server.

## ⚙️ Hardware Constraints & Optimization Strategy

| Component | Constraint | Optimization Strategy |
| :--- | :--- | :--- |
| **CPU** | i3 540 (2C/4T, No AVX2) | Use `llama.cpp` with older instruction sets. Avoid heavy parallel processing. |
| **RAM** | 8GB DDR3 (Total) | Limit Model to < 2GB. Limit Context to 2048 tokens. Aggressive GC. |
| **GPU** | GT 730 (4GB VRAM, Kepler) | Offload ~15-20 layers to GPU. Use `n_gpu_layers` parameter. |
| **Storage** | 128GB SSD | Keep Vector DB small. Prune logs. |

## 🏗️ Architecture

### 1. The Brain (Local LLM)
We will use **Llama-3.2-1B-Instruct-GGUF** (Quantized to Q4_K_M).
- **Size:** ~700MB.
- **Speed:** Fast inference even on older CPUs.
- **Role:** Reasoning engine, tool caller.

### 2. The Body (MCP Client)
Instead of the LLM running tools directly, it will act as an **MCP Client** connecting to our existing `meganx_mcp_server.py`.
- **Protocol:** Stdio (Standard Input/Output).
- **Tools Available:** `browser_navigate`, `browser_click`, `memory_store`, `memory_recall`.

### 3. The Loop (sparrow_agent.py)
A lightweight Python script that orchestrates the flow:
1.  **User Input:** "Research the latest news on X."
2.  **Inference:** LLM generates a tool call (e.g., `browser_navigate`).
3.  **Execution:** Script sends call to MCP Server.
4.  **Observation:** MCP Server returns result (page content).
5.  **Synthesis:** LLM reads result and answers user.

## 🛠️ Implementation Plan

### Phase 1: The Skeleton (Current)
- `sparrow_agent.py`: Basic loop connecting `llama-cpp-python` to `mcp`.
- **Mock Model:** For initial testing without downloading the 1GB file.

### Phase 2: The Muscle (Next)
- Install `llama-cpp-python` with CUDA support (for GT 730).
- Download `Llama-3.2-1B-Instruct-Q4_K_M.gguf`.
- Tune `n_gpu_layers` for maximum performance.

## 🚀 Why "SPARROW"?
Small. Fast. Agile.
It doesn't need to be an eagle to fly.
