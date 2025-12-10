"""
MEGANX Security Module
======================
Rate-limiting and kill-switch for safe autonomous operation.
"""

import time
import hashlib
import json
from datetime import datetime
from pathlib import Path
from typing import Optional
from functools import wraps

# ============================================================================
# RATE LIMITER
# ============================================================================

class RateLimiter:
    """
    Limits the number of actions per time window.
    Default: 5 DOM actions per 60 seconds.
    """
    
    def __init__(self, max_actions: int = 5, window_seconds: int = 60):
        self.max_actions = max_actions
        self.window_seconds = window_seconds
        self.action_timestamps: list[float] = []
    
    def can_execute(self) -> bool:
        """Check if an action is allowed under the rate limit."""
        now = time.time()
        # Remove timestamps outside the window
        self.action_timestamps = [
            ts for ts in self.action_timestamps 
            if now - ts < self.window_seconds
        ]
        return len(self.action_timestamps) < self.max_actions
    
    def record_action(self) -> None:
        """Record that an action was executed."""
        self.action_timestamps.append(time.time())
    
    def execute_if_allowed(self, func, *args, **kwargs):
        """Execute function only if rate limit allows."""
        if not self.can_execute():
            return f"[RATE LIMIT] Max {self.max_actions} actions per {self.window_seconds}s. Wait."
        self.record_action()
        return func(*args, **kwargs)
    
    def remaining_actions(self) -> int:
        """Return how many actions remain in current window."""
        now = time.time()
        recent = [ts for ts in self.action_timestamps if now - ts < self.window_seconds]
        return max(0, self.max_actions - len(recent))


# ============================================================================
# KILL SWITCH
# ============================================================================

class KillSwitch:
    """
    Global kill switch for emergency stops.
    Can be triggered via file flag or programmatically.
    """
    
    FLAG_FILE = Path("./KILL_SWITCH_ACTIVE")
    
    def __init__(self):
        self._active = False
    
    def is_active(self) -> bool:
        """Check if kill switch is engaged (file or flag)."""
        return self._active or self.FLAG_FILE.exists()
    
    def activate(self, reason: str = "Manual activation") -> None:
        """Engage the kill switch."""
        self._active = True
        self.FLAG_FILE.write_text(f"KILL SWITCH ACTIVE\nReason: {reason}\nTime: {datetime.now().isoformat()}")
        self._log_event("KILL_SWITCH_ACTIVATED", reason)
    
    def deactivate(self) -> None:
        """Disengage the kill switch."""
        self._active = False
        if self.FLAG_FILE.exists():
            self.FLAG_FILE.unlink()
        self._log_event("KILL_SWITCH_DEACTIVATED", "Manual reset")
    
    def check_or_block(self) -> Optional[str]:
        """Returns error message if killed, None if OK."""
        if self.is_active():
            return "[KILL SWITCH ACTIVE] All operations blocked. Remove KILL_SWITCH_ACTIVE file to resume."
        return None
    
    def _log_event(self, event_type: str, details: str) -> None:
        """Log security events with hash for audit trail."""
        log_entry = {
            "timestamp": datetime.now().isoformat(),
            "event": event_type,
            "details": details,
            "hash": hashlib.sha256(f"{event_type}{details}{time.time()}".encode()).hexdigest()[:16]
        }
        log_path = Path("./logs/security_audit.jsonl")
        log_path.parent.mkdir(exist_ok=True)
        with open(log_path, "a") as f:
            f.write(json.dumps(log_entry) + "\n")


# ============================================================================
# GLOBAL INSTANCES
# ============================================================================

# Rate limiter for DOM/browser actions (5 per minute)
dom_rate_limiter = RateLimiter(max_actions=5, window_seconds=60)

# Rate limiter for memory operations (more generous)
memory_rate_limiter = RateLimiter(max_actions=20, window_seconds=60)

# Global kill switch
kill_switch = KillSwitch()


# ============================================================================
# DECORATOR FOR PROTECTED FUNCTIONS
# ============================================================================

def protected_action(rate_limiter: RateLimiter = dom_rate_limiter):
    """Decorator to protect functions with rate limiting and kill switch."""
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            # Check kill switch first
            blocked = kill_switch.check_or_block()
            if blocked:
                return blocked
            
            # Check rate limit
            if not rate_limiter.can_execute():
                return f"[RATE LIMIT] Slow down. {rate_limiter.remaining_actions()} actions remaining."
            
            rate_limiter.record_action()
            return func(*args, **kwargs)
        return wrapper
    return decorator
