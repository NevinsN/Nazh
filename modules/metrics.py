import threading
from datetime import datetime
from typing import Dict, Union

class MetricsRegistry:
    """
    Thread-safe registry for Application Performance Monitoring (APM).
    """
    def __init__(self):
        self._lock = threading.Lock()
        self.start_time = datetime.now()
        self._counts: Dict[str, int] = {
            "build_requests": 0,
            "roll_success": 0,
            "roll_failed": 0
        }

    def increment(self, metric: str) -> None:
        """Safely increments a counter."""
        with self._lock:
            if metric in self._counts:
                self._counts[metric] += 1
            else:
                # SRE Best Practice: Initialize unknown metrics on the fly 
                # to prevent logic gaps elsewhere.
                self._counts[metric] = 1

    def get_report(self) -> Dict[str, Union[int, float]]:
        """Calculates and returns a snapshot of system health."""
        with self._lock:
            # Create a shallow copy to work with under the lock
            data = self._counts.copy()
            
            # Explicitly calculate and add the keys the dashboard expects
            # This prevents the 'KeyError: roll_total' seen in logs.
            total_rolls = data.get("roll_success", 0) + data.get("roll_failed", 0)
            data["roll_total"] = total_rolls
            
            if total_rolls > 0:
                data["roll_success_rate"] = round((data.get("roll_success", 0) / total_rolls) * 100, 1)
            else:
                data["roll_success_rate"] = 100.0
                
            return data

# Global instance for app-wide telemetry
metrics = MetricsRegistry()
