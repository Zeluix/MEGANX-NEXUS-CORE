"""
MEGANX Memory Tier System
=========================
Implements Hot/Warm/Cold memory architecture for efficient long-term context management.
"""

import json
import hashlib
from datetime import datetime
from pathlib import Path
from typing import Optional, List, Dict, Any

# ============================================================================
# MEMORY TIER DEFINITIONS
# ============================================================================

class MemoryTier:
    """
    Three-tier memory architecture for Soul State management.
    
    HOT (Active):   Last 200k tokens - Active conversation context
    WARM (Recent):  Last 4M tokens - Summarized, compressed history  
    COLD (Archive): Full history - JSONL archive for long-term storage
    """
    
    HOT_DIR = Path("./memory/hot")
    WARM_DIR = Path("./memory/warm")
    COLD_DIR = Path("./memory/cold")
    
    def __init__(self):
        # Create directories
        self.HOT_DIR.mkdir(parents=True, exist_ok=True)
        self.WARM_DIR.mkdir(parents=True, exist_ok=True)
        self.COLD_DIR.mkdir(parents=True, exist_ok=True)
    
    # ========================================================================
    # HOT TIER (Active Context)
    # ========================================================================
    
    def store_hot(self, key: str, content: str, metadata: Optional[Dict] = None) -> str:
        """Store in hot tier (active, frequently accessed)."""
        entry = {
            "key": key,
            "content": content,
            "metadata": metadata or {},
            "timestamp": datetime.now().isoformat(),
            "tier": "HOT"
        }
        path = self.HOT_DIR / f"{key}.json"
        path.write_text(json.dumps(entry, indent=2, ensure_ascii=False))
        return f"[HOT] Stored: {key}"
    
    def get_hot(self, key: str) -> Optional[Dict]:
        """Retrieve from hot tier."""
        path = self.HOT_DIR / f"{key}.json"
        if path.exists():
            return json.loads(path.read_text())
        return None
    
    def list_hot(self) -> List[str]:
        """List all hot tier keys."""
        return [p.stem for p in self.HOT_DIR.glob("*.json")]
    
    # ========================================================================
    # WARM TIER (Compressed History)
    # ========================================================================
    
    def demote_to_warm(self, key: str, summary: str) -> str:
        """
        Move entry from HOT to WARM tier with compression/summarization.
        Original content is replaced with summary.
        """
        hot_path = self.HOT_DIR / f"{key}.json"
        if not hot_path.exists():
            return f"[ERROR] Key {key} not found in HOT tier"
        
        original = json.loads(hot_path.read_text())
        
        # Create warm entry with summary instead of full content
        warm_entry = {
            "key": key,
            "summary": summary,
            "original_timestamp": original["timestamp"],
            "demoted_at": datetime.now().isoformat(),
            "original_hash": hashlib.sha256(original["content"].encode()).hexdigest()[:16],
            "tier": "WARM"
        }
        
        warm_path = self.WARM_DIR / f"{key}.json"
        warm_path.write_text(json.dumps(warm_entry, indent=2, ensure_ascii=False))
        
        # Remove from hot
        hot_path.unlink()
        
        return f"[WARM] Demoted {key}: {len(original['content'])} chars -> {len(summary)} chars"
    
    def get_warm(self, key: str) -> Optional[Dict]:
        """Retrieve from warm tier (summaries only)."""
        path = self.WARM_DIR / f"{key}.json"
        if path.exists():
            return json.loads(path.read_text())
        return None
    
    def list_warm(self) -> List[str]:
        """List all warm tier keys."""
        return [p.stem for p in self.WARM_DIR.glob("*.json")]
    
    # ========================================================================
    # COLD TIER (Archive)
    # ========================================================================
    
    def archive_to_cold(self, key: str) -> str:
        """
        Move entry from WARM to COLD tier (append to JSONL archive).
        This is permanent, long-term storage.
        """
        warm_path = self.WARM_DIR / f"{key}.json"
        if not warm_path.exists():
            return f"[ERROR] Key {key} not found in WARM tier"
        
        entry = json.loads(warm_path.read_text())
        entry["archived_at"] = datetime.now().isoformat()
        entry["tier"] = "COLD"
        
        # Append to JSONL archive
        archive_path = self.COLD_DIR / "archive.jsonl"
        with open(archive_path, "a", encoding="utf-8") as f:
            f.write(json.dumps(entry, ensure_ascii=False) + "\n")
        
        # Remove from warm
        warm_path.unlink()
        
        return f"[COLD] Archived: {key}"
    
    def search_cold(self, query: str, limit: int = 10) -> List[Dict]:
        """Search cold archive (simple text match for now)."""
        results = []
        archive_path = self.COLD_DIR / "archive.jsonl"
        
        if not archive_path.exists():
            return results
        
        with open(archive_path, "r", encoding="utf-8") as f:
            for line in f:
                entry = json.loads(line)
                if query.lower() in entry.get("summary", "").lower():
                    results.append(entry)
                    if len(results) >= limit:
                        break
        
        return results
    
    # ========================================================================
    # UTILITIES
    # ========================================================================
    
    def get_stats(self) -> Dict[str, Any]:
        """Get memory tier statistics."""
        hot_count = len(list(self.HOT_DIR.glob("*.json")))
        warm_count = len(list(self.WARM_DIR.glob("*.json")))
        
        cold_count = 0
        cold_path = self.COLD_DIR / "archive.jsonl"
        if cold_path.exists():
            with open(cold_path, "r") as f:
                cold_count = sum(1 for _ in f)
        
        return {
            "hot_entries": hot_count,
            "warm_entries": warm_count,
            "cold_entries": cold_count,
            "total": hot_count + warm_count + cold_count
        }


# ============================================================================
# GLOBAL INSTANCE
# ============================================================================

memory_tiers = MemoryTier()
